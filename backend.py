import threading, sys, time, os
import asyncio
import websockets
from flask import Flask, jsonify, request
import typesense, json, queue
# from lib import threading as libthread
from lib import compute_node
from lib import communication_functions as comms
from lib import test_patterns as tp
from lib import game_runner as runner
from lib import convert_functions as cf
from lib.patterns import lexicon
import multiprocessing as mp
from lib import convert_functions
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

port = 5000
client = typesense.Client({
    'nodes': [{
        'host': '192.168.30.36',
        'port': '8108',
        'protocol': 'http'
    }],
    'api_key': 'xyz123',
    'connection_timeout_seconds': 2
})

# Initialize Flask app
app = Flask(__name__)

# Queue for communicattion between the HTTP and WebSocket threads
message_queue = queue.Queue()

# WebSocket clients list
clients = set()

# Threading lock for clients set
clients_lock = threading.Lock()

# HTTP route (handled by Flask)
@app.route('/status')
def status(): # GET /status
    print("Status: OK")
    return '{"status":"OK"}'

@app.route('/')
def index():
    return jsonify(message="Hello from Flask HTTP server")

@app.route('/send_message/<msg>')
def send_message(msg):
    """ HTTP route to add message to the queue """
    message_queue.put(msg)  # Add the message to the queue
    return jsonify(status="Message queued for WebSocket clients", message=msg)

@app.route('/lexicon/get')
def get_lexicon(): # GET /lexicon/get
    print("Sending lexicon")
    pats = json.load(open('data/lexicon_list.json'))
    return json.dumps({
        'patterns': pats
    })

@app.route('/lexicon/search')
def search_lexicon(): # GET /lexicon/search?q=term
    print("Searching lexicon")
    r = client.collections['lexicon'].documents.search({
        'q': request.args.get('q'),
        'query_by': 'name',
    })
    results = r['hits']
    list = []
    for i in results:
        i['document']['comments'] = json.loads(i['document']['comments'])
        list.append(i['document'])
    return json.dumps({
        'patterns': list
    }, indent=4)

@app.route('/lexicon/get-named')
def get_lexicon_by_id(): # GET /lexicon/get-named?id=xyz
    print("Sending pattern from lexicon by ID")
    try:
        return json.dumps({"success": True, "result": lexicon[request.args.get('id')]})
    except:
        print("Error: Pattern not found")
        return json.dumps({"success": False, "error": "Pattern not found in lexicon"})

@app.route('/patterns/get-named')
def get_pattern_by_id(): # GET /patterns/get-named?id=xyz
    print("Sending pattern by ID")
    pats = json.load(open('data/patterns.json'))
    try:
        return json.dumps({"success": True, "result": lexicon[request.args.get('id')]})
    except:
        print("Error: Pattern not found")
        return json.dumps({"success": False, "error": "Pattern not found"})

# WebSocket handling function (using websockets)
async def handle_websocket(websocket):
    with clients_lock:
        clients.add(websocket)
    try:
        async for message in websocket:
            logger.debug(f"Received message from WebSocket client: {message}")
            try:
                if message[0:1] == "{":
                    # print("Deserializing message")
                    message = json.loads(message)
                    json_message = True
                else:
                    json_message = False

                if json_message and message["type"] == "sesame":
                    print("Received sesame")
                    message_queue.put({"type": "broadcast", "message": "Hello from WebSocket server"})
                elif message == "sesame":
                    message_queue.put({"type": "broadcast", "message": "Hello. Sesame!"})
                elif json_message:
                    message_queue.put(message)
                else:
                    message_queue.put({"type": "broadcast", "message": f"echo: {message}"})

            except Exception as e:
                logger.error(f"Error processing client message: {e}")
                await asyncio.sleep(0.1)

        print("WebSocket connection closed")
    except websockets.exceptions.ConnectionClosed:
        print("Connection closed")
    finally:
        with clients_lock:
            clients.remove(websocket)

# Function to run the Flask HTTP server
def run_http():
    app.run(host="0.0.0.0", port=port, threaded=True)

camera_pos = (0, 7)
interval = 0.25

# Function to run the WebSocket server and process messages from the queue
async def websocket_server():
    global camera_pos, interval
    start_server = websockets.serve(handle_websocket, "0.0.0.0", port+1)
    await start_server
    print("Started WebSocket server on port "+str(port+1))
    verbose = False

    # Create websocket connection to simulator
    simulator_uri = "ws://192.168.30.41:8765"  # Port for simulator websocket
    while True:
        try:
            async with websockets.connect(simulator_uri) as simulator_ws:
                print("Connected to simulator")
                # Initial setup
                await simulator_ws.send(json.dumps({
                    "type": "setrle",
                    "data": "bo$2bo$3o!"
                }))
                await simulator_ws.send(json.dumps({
                    "type": "setcamera",
                    "x": camera_pos[0],
                    "y": camera_pos[1],
                }))

                while True:
                    try:
                        # Process message queue
                        try:
                            message = message_queue.get_nowait()

                            if message["type"] == "broadcast":
                                await broadcast(message["message"])
                            elif message["type"] in ["start", "stop", "setrle", "setinterval", "setcamera"]:
                                if(message["type"] == "setcamera"):
                                    camera_pos = (message["x"], message["y"])
                                elif message["type"] == "setinterval" and message["data"] > 0:
                                    interval = message["data"]
                                # Forward these messages directly to simulator
                                await simulator_ws.send(json.dumps(message))
                                await broadcast(json.dumps({
                                    "type": "info",
                                    "message": f"Sent {message['type']} command to simulator"
                                }))

                        except queue.Empty:
                            pass

                        # Check for simulator updates
                        try:
                            simulator_message = await asyncio.wait_for(
                                simulator_ws.recv(),
                                timeout=0.1
                            )
                            if len(clients) > 0:  # Only broadcast if we have clients
                                await broadcast(simulator_message)
                                print("Sent grid update to clients")
                        except asyncio.TimeoutError:
                            pass

                        # Sleep based on client state
                        has_clients = len(clients) > 0
                        await asyncio.sleep(0.1 if has_clients else 0.5)

                    except websockets.ConnectionClosed:
                        print("Lost connection to simulator. Attempting to reconnect...")
                        break  # Break inner loop to attempt reconnection
                    except Exception as e:
                        logger.error(f"Error in message processing: {e}", exc_info=True)
                        await asyncio.sleep(0.1)
        except (websockets.ConnectionClosed, ConnectionRefusedError) as e:
            print(f"Failed to connect to compute node: {e}")
            await asyncio.sleep(5)  # Wait before retrying

def run_simulator():
    """Function to run the simulator process"""
    compute_node.run_websocket_server(port=8765, verbose=True)


async def broadcast(message):
    # print("Broadcasting message")
    with clients_lock:
        # Make a copy of clients to avoid modifying while iterating
        current_clients = list(clients)

    # Process sends outside the lock
    tasks = []
    for websocket in current_clients:
        try:
            tasks.append(websocket.send(message))
        except websockets.exceptions.ConnectionClosed:
            with clients_lock:
                if websocket in clients:
                    clients.remove(websocket)

    if tasks:
        await asyncio.gather(*tasks)
    # print("Broadcasted message")

def run_websocket():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(websocket_server())
        loop.run_forever()  # Add this line to keep processing events
    except Exception as e:
        logger.error(f"WebSocket server error: {e}", exc_info=True)
    finally:
        loop.close()


def monitor_process(process):
    """Monitor a process and exit if it dies"""
    while True:
        if not process.is_alive():
            print("Simulator process died! Shutting down...")
            os._exit(1)  # Force exit the entire program
        time.sleep(1)

if __name__ == "__main__":
    try:
        # Create threads for HTTP and WebSocket servers
        http_thread = threading.Thread(target=run_http, daemon=True)
        websocket_thread = threading.Thread(target=run_websocket, daemon=True)

        # Create process for simulator
        simulator_process = mp.Process(
            target=run_simulator,
            daemon=True
        )

        # Create monitor thread
        monitor_thread = threading.Thread(
            target=monitor_process,
            args=(simulator_process,),
            daemon=True
        )

        # Start everything
        simulator_process.start()
        http_thread.start()
        websocket_thread.start()
        monitor_thread.start()

        # Keep the main thread running
        while True:
            try:
                time.sleep(1)
            except KeyboardInterrupt:
                print("\nShutting down gracefully...")
                simulator_process.terminate()
                sys.exit(0)

    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)
