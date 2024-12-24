import threading, sys, time, os
import asyncio
import websockets
from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin
import typesense, json, queue
# from lib import threading as libthread
from lib import compute_node, simulator
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
cors = CORS(app)
app.config["CORS_HEADERS"] = "Content-Type"

# Queue for communicattion between the HTTP and WebSocket threads
message_queue = queue.Queue()

# WebSocket clients list
clients = set()

# Threading lock for clients set
clients_lock = threading.Lock()
matrix_client = comms.get_socket()
connections = {
        "status": "OK",
        "connector": True,
        "compute": False,
        "clients": False,
}

# HTTP route (handled by Flask)
@app.route('/status')
@cross_origin()
def status(): # GET /status
    print("Status: OK")
    return jsonify(connections)

@app.route('/')
@cross_origin()
def index():
    return jsonify(message="Hello from Flask HTTP server")

@app.route('/send_message/<msg>')
@cross_origin()
def send_message(msg):
    """ HTTP route to add message to the queue """
    message_queue.put(msg)  # Add the message to the queue
    return jsonify(status="Message queued for WebSocket clients", message=msg)

@app.route('/lexicon/get')
@cross_origin()
def get_lexicon(): # GET /lexicon/get
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 50))
    print("Sending lexicon page", page)

    pats = json.load(open('data/lexicon_list.json'))

    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page

    paginated_pats = pats[start_idx:end_idx]

    return json.dumps({
        'patterns': paginated_pats,
        'total': len(pats),
        'page': page,
        'per_page': per_page,
        'total_pages': (len(pats) + per_page - 1) // per_page
    })

@app.route('/lexicon/search')
@cross_origin()
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
@cross_origin()
def get_lexicon_by_id(): # GET /lexicon/get-named?id=xyz
    print("Sending pattern from lexicon by ID")
    try:
        return json.dumps({"success": True, "result": lexicon[request.args.get('id')]})
    except:
        print("Error: Pattern not found")
        return json.dumps({"success": False, "error": "Pattern not found in lexicon"})

@app.route('/patterns/get-named')
@cross_origin()
def get_pattern_by_id(): # GET /patterns/get-named?id=xyz
    print("Sending pattern by ID")
    pats = json.load(open('data/patterns.json'))
    try:
        return json.dumps({"success": True, "result": lexicon[request.args.get('id')]})
    except:
        print("Error: Pattern not found")
        return json.dumps({"success": False, "error": "Pattern not found"})

@app.route('/patterns/get')
@cross_origin()
def get_patterns(): # GET /patterns/get
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 50))
    print("Sending patterns page", page)

    pats = json.load(open('data/patterns.json'))

    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page

    paginated_pats = pats[start_idx:end_idx]

    return json.dumps({
        'patterns': paginated_pats,
        'total': len(pats),
        'page': page,
        'per_page': per_page,
        'total_pages': (len(pats) + per_page - 1) // per_page
    })

@app.route('/patterns/search')
@cross_origin()
def search_patterns(): # GET /patterns/search?q=term
    print("Searching patterns")
    r = client.collections['patterns'].documents.search({
        'q': request.args.get('q'),
        'query_by': 'name',
    })
    results = r['hits']
    list = []
    # for i in results:
    #     i['document']['comments'] = json.loads(i['document']['comments'])
    #     list.append(i['document'])
    return json.dumps({
        'patterns': list
    }, indent=4)

@app.route('/run')
@cross_origin()
def run(): # GET /run
    print("Running simulation")
    message_queue.put({"type": "stop"})
    message_queue.put({"type": "setrle", "data": request.args.get('rle')})
    message_queue.put({"type": "setinterval", "data": float(request.args.get('interval', 0.25))})
    message_queue.put({"type": "setcamera", "x": 0, "y": 0})
    message_queue.put({"type": "start"})
    return jsonify(success=True, status="Simulation started")

@app.route('/stop')
@cross_origin()
def stop(): # GET /stop
    print("Stopping simulation")
    message_queue.put({"type": "stop"})
    return jsonify(success=True, status="Simulation stopped")

@app.route('/translate', methods=['POST'])
@cross_origin()
def translate(): # POST /translate
    data = request.get_json()
    intype = data.get('from')
    outtype = data.get('to')
    indata = data.get('data')

    if intype not in ['rle', 'txt'] or outtype not in ['rle', 'txt']:
        return jsonify(success=False, error="Invalid input or output type")

    try:
        if intype == 'rle' and outtype == 'txt':
            result = cf.easy_RLE_to_txt(indata)
        elif intype == 'txt' and outtype == 'rle':
            result = cf.txt_to_RLE(indata)
        else:
            result = indata # Same format, no conversion needed

        return jsonify(success=True, result=result)
    except Exception as e:
        return jsonify(success=False, error=str(e))


# WebSocket handling function (using websockets)
async def handle_websocket(websocket):
    global timer_start
    with clients_lock:
        clients.add(websocket)
        if len(clients) == 0:
            print("No clients connected")
            connections["clients"] = False
        else:
            connections["clients"] = True
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
                    print("Queued message")
                    timer_start = time.time()
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

timer_start = time.time()
camera_pos = (0,0)
interval = 0.25
autofocus = False

# Function to run the WebSocket server and process messages from the queue
async def websocket_server(verbose=False):
    global camera_pos, interval, client, timer_start
    start_server = websockets.serve(handle_websocket, "0.0.0.0", port+1, origins=None)
    await start_server
    print("Started WebSocket server on port "+str(port+1))

    simulator_uri = "ws://192.168.30.41:8765"
    while True:
        try:
            async with websockets.connect(simulator_uri, max_queue=1) as simulator_ws:
                print("Connected to simulator")
                connections["compute"] = True
                # Initial setup
                # await simulator_ws.send(json.dumps({
                #     "type": "setrle",
                #     "data": "bo$2bo$3o!"
                # }))
                # await simulator_ws.send(json.dumps({
                #     "type": "setcamera",
                #     "x": camera_pos[0],
                #     "y": camera_pos[1],
                # }))
                await simulator_ws.send(json.dumps({
                    "type": "setinterval",
                    "data": 0.25,
                }))

                while True:
                    # Process all pending messages in queue first
                    while not message_queue.empty():
                        message = message_queue.get_nowait()
                        print("Time since last message:", time.time() - timer_start)
                        if verbose:
                            print("Processing message from queue:", message)

                        if message["type"] == "broadcast":
                            await broadcast(message["message"])
                        elif message["type"] in ["start", "stop", "setrle", "setinterval", "setcamera", "dogens", "setautofocus"]:
                            if message["type"] == "setcamera":
                                camera_pos = (message["x"], message["y"])
                            elif message["type"] == "setinterval" and message["data"] > 0:
                                interval = message["data"]
                            elif message["type"] == "setautofocus":
                                print("Autofocus:", message["data"])
                                autofocus = message["data"]

                            # Forward these messages directly to simulator
                            await simulator_ws.send(json.dumps(message))
                            await broadcast(json.dumps({
                                "type": "info",
                                "message": f"Sent {message['type']} command to simulator"
                            }))

                    # Check for simulator updates
                    try:
                        simulator_message = await asyncio.wait_for(
                            simulator_ws.recv(),
                            timeout=0.1
                        )
                        if simulator_message[0:1] == "{":
                            simulator_message = json.loads(simulator_message)

                        if simulator_message["type"] == "grid":
                            if verbose:
                                print("Received grid from simulator")
                            try:
                                comms.send_message(matrix_client, simulator_message["data"])
                                if verbose:
                                    print("Sent grid to comms socket")
                            except Exception as e:
                                connections["connector"] = False
                                if verbose:
                                    print(f"Error sending message to comms socket: {e}")
                        elif simulator_message["type"] == "camerapos":
                            camera_pos = simulator_message["data"]
                            camera_pos = (camera_pos["x"], camera_pos["y"])
                            await broadcast(json.dumps(simulator_message))
                            if verbose:
                                print("Received camera from simulator")
                        elif simulator_message["type"] == "info":
                            if verbose:
                                print("Received info from simulator")

                        if len(clients) > 0:
                            await broadcast(json.dumps(simulator_message))
                            if verbose:
                                print("Sent grid update to clients")

                    except asyncio.TimeoutError:
                        pass  # No simulator message available

                    # Small delay to prevent CPU spinning
                    await asyncio.sleep(0.01)

        except (websockets.ConnectionClosed, ConnectionRefusedError) as e:
            connections["compute"] = False
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
