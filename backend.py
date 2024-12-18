import threading, sys, time
import asyncio
import websockets
from flask import Flask, jsonify, request
import typesense, json, queue
from lib import threading as libthread
from lib import communication_functions as comms
from lib import test_patterns as tp
from lib import game_runner as runner
from lib import convert_functions as cf
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
    pats = json.load(open('data/lexicon.json'))
    try:
        return json.dumps({"success": True, "result": pats[request.args.get('id')]})
    except:
        print("Error: Pattern not found")
        return json.dumps({"success": False, "error": "Pattern not found in lexicon"})

@app.route('/patterns/get-named')
def get_pattern_by_id(): # GET /patterns/get-named?id=xyz
    print("Sending pattern by ID")
    pats = json.load(open('data/patterns.json'))
    try:
        return json.dumps({"success": True, "result": pats[request.args.get('id')]})
    except:
        print("Error: Pattern not found")
        return json.dumps({"success": False, "error": "Pattern not found"})

# WebSocket handling function (using websockets)
async def handle_websocket(websocket, path):
    with clients_lock:
        clients.add(websocket)
    try:
        async for message in websocket:
            logger.debug(f"Received message from WebSocket client: {message}")
            try:
                if message[0:1] == "{":
                    print("Deserializing message")
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
    start_server = websockets.serve(handle_websocket, "0.0.0.0", port+1)
    await start_server
    print("Started WebSocket server on port "+str(port+1))
    verbose = False
    showOutput = False
    ippipe, icpipe = mp.Pipe()
    oppipe, ocpipe = mp.Pipe()
    p = mp.Process(target=libthread.runner_thread, args=(ippipe, ocpipe, comms.get_socket(), verbose))
    p.start()
    icpipe.send({
        "type": "setgrid",
        "data": tp.master_library["snark loop"]
    })
    icpipe.send({
        "type": "setcamera",
        "data": camera_pos,
    })

    while True:
        try:
            # Process message queue
            try:
                message = message_queue.get_nowait()
                # print("Message queue gotten "+str(message))

                if message["type"] == "broadcast":
                    await broadcast(message["message"])
                elif message["type"] == "start":
                    await broadcast(json.dumps({"type": "info", "message": "Starting simulator"}))
                    # print("Starting CGOL simulator")
                    icpipe.send({"type": "start"})
                elif message["type"] == "stop":
                    await broadcast(json.dumps({"type": "info", "message": "Stopping simulator"}))
                    # print("Stopping CGOL simulator")
                    icpipe.send({"type": "stop"})
                elif message["type"] == "setrle":
                    await broadcast(json.dumps({"type": "info", "message": "Setting grid"}))
                    # print("Setting grid")
                    icpipe.send({
                        "type": "setgrid",
                        "data": convert_functions.RLE_to_matrix(message["data"])
                    })
                    await broadcast(json.dumps({"type": "info", "message": "Set grid"}))
                elif message["type"] == "setinterval":
                    await broadcast(json.dumps({"type": "info", "message": "Setting interval"}))
                    # print("Setting interval")
                    icpipe.send({
                        "type": "setinterval",
                        "data": message["data"]
                    })
                elif message["type"] == "setcamera":
                    # print("Setting camera")
                    icpipe.send({
                        "type": "setcamera",
                        "data": (message["x"], message["y"])
                    })
                    await broadcast(json.dumps({"type": "info", "message": f"Set camera to {message['x']}, {message['y']}."}))

            except queue.Empty:
                # print("No message in queue")
                # Check pipe if no messages in queue
                if oppipe.poll():
                    # print("Received message from CGOL simulator")
                    pipe_data = oppipe.recv()
                    has_clients = len(clients) > 0
                    if has_clients:  # Only broadcast if we have clients
                        await broadcast(json.dumps(pipe_data))
                    # print("Sent message to clients")

                # Sleep only when both queue and pipe are empty
                has_clients = len(clients) > 0
                # print("Has clients: "+str(has_clients))
                # print("Sleeping")
                await asyncio.sleep(0.1 if has_clients else 0.5)

        except Exception as e:
            logger.error(f"Error in message processing: {e}", exc_info=True)
            await asyncio.sleep(0.1)

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
    print("Broadcasted message")

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

if __name__ == "__main__":
    try:
        http_thread = threading.Thread(target=run_http, daemon=True)
        websocket_thread = threading.Thread(target=run_websocket, daemon=True)

        http_thread.start()
        websocket_thread.start()

        # Keep the main thread running
        while True:
            try:
                time.sleep(1)
            except KeyboardInterrupt:
                print("\nShutting down gracefully...")
                sys.exit(0)

    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)
