import asyncio
import websockets
import json
from lib import game_runner as runner
from lib import convert_functions as cf
from lib import test_patterns as tp
from lib.simulator import CGOLSimulator
import time

async def websocket_handler(websocket, simulator, verbose=False):
    """Handle websocket connection and messages"""
    try:
        if verbose:
            print("WebSocket connection established")

        async def send_grid():
            # Helper function to send grid through websocket
            curr_grid = simulator.process_grid()
            await websocket.send(json.dumps({
                "type": "grid",
                "data": curr_grid
            }))
            if verbose:
                print("Sent grid through websocket")

        while True:
            try:
                message = await websocket.recv()
                data = json.loads(message)

                match(data["type"]):
                    case "setgrid":
                        simulator.set_grid(data["data"])
                        await send_grid()
                    case "setinterval":
                        simulator.set_interval(data["data"])
                    case "setcamera":
                        if verbose:
                            print("Setting camera to ", data["data"])
                        simulator.camera_pos = data["data"]
                        await send_grid()
                    case "stop":
                        simulator.stop()
                    case "start":
                        if verbose:
                            print("Starting Main Loop")
                        simulator.start()
                    case "avadakadavra":
                        if verbose:
                            print("Received avadakadavra. Closing connection.")
                        await websocket.close()
                        return

                # Main simulation loop
                if simulator.running:
                    if verbose:
                        print("Running Main Loop")

                    simulator.tick()
                    await send_grid()

                    # Handle timing
                    if simulator.interval > 0:
                        await asyncio.sleep(simulator.interval)
                    else:
                        await asyncio.sleep(0.016)  # ~60fps

            except websockets.ConnectionClosed:
                print("WebSocket connection closed")
                break

    except Exception as e:
        print(f"Error in websocket handler: {e}")
        await websocket.close()

async def start_server(host="localhost", port=8765, verbose=False):
    """Start the WebSocket server"""
    simulator = CGOLSimulator(verbose=verbose)

    async def handler(websocket):
        await websocket_handler(websocket, simulator, verbose)

    async with websockets.serve(handler, host, port):
        if verbose:
            print(f"Compute WebSocket server started on ws://{host}:{port}")
        await asyncio.Future()  # run forever

def run_websocket_server(host="localhost", port=8765, verbose=False):
    """Run the WebSocket server in the main thread"""
    asyncio.run(start_server(host, port, verbose))
