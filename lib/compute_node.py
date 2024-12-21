import asyncio
import websockets
import json
from lib import game_runner as runner
from lib import convert_functions as cf
from lib import test_patterns as tp
from lib.simulator import CGOLSimulator
import time

default_state = {
    "interval": 0.25,
    "starting_grid": tp.master_library["empty"],
    "camera_pos": (0, 0),
    "autofocus": "none"
}

async def websocket_handler(websocket, simulator, verbose=False):
    autofocus = False
    """Handle websocket connection and messages"""
    try:
        if verbose:
            print("compute connection established")

        async def send_grid():
            # Helper function to send grid through websocket
            if(autofocus != "none"):
                if(verbose): print("Auto-focusing")
                x, y = simulator.autofocus(autofocus)
                await websocket.send(json.dumps({
                    "type": "camerapos",
                    "data": {
                        "x": x,
                        "y": y
                    },
                }))
            curr_grid = simulator.process_grid()
            await websocket.send(json.dumps({
                "type": "grid",
                "data": curr_grid
            }))
            if verbose:
                print("Sent grid through websocket")

        while True:
            try:
                # Handle messages without blocking
                message = None
                try:
                    message = await asyncio.wait_for(websocket.recv(), timeout=0.01)
                except asyncio.TimeoutError:
                    pass

                if message:
                    data = json.loads(message)
                    match(data["type"]):
                        case "setrle":
                            print("Setting RLE to " + data["data"])
                            simulator.set_grid(cf.RLE_to_matrix(data["data"]))
                            await send_grid()
                        case "setinterval":
                            simulator.set_interval(data["data"])
                        case "setcamera":
                            if verbose:
                                print("Setting camera to ", (data["x"], data["y"]))
                            simulator.camera_pos = (data["x"], data["y"])
                            await send_grid()
                        case "stop":
                            simulator.stop()
                        case "start":
                            if verbose:
                                print("Starting Main Loop")
                            simulator.start()
                        case "dogens":
                            if verbose:
                                print("Running", data["data"], "generations")
                            simulator.doGens(data["data"])
                            await send_grid()
                        case "setautofocus":
                            autofocus = data["data"]
                            if(verbose):
                                print("Autofocusing with mode", data["data"])
                            x, y = simulator.autofocus(data["data"])
                            # await websocket.send(json.dumps({
                            #     "type": "camerapos",
                            #     "data": {
                            #         "x": x,
                            #         "y": y
                            #     },
                            # }))
                            await send_grid()
                        case "avadakadavra":
                            if verbose:
                                print("Received avadakadavra. Closing connection.")
                            await websocket.close()
                            return

                # Main simulation loop
                if simulator.running:
                    if verbose:
                        print("Running Main Loop")
                    print(str(simulator.current_grid))

                    simulator.tick()
                    if(autofocus != "none"):
                        simulator.autofocus(autofocus)
                    await send_grid()

                    # Handle timing
                    if simulator.interval > 0:
                        await asyncio.sleep(simulator.interval)
                    else:
                        await asyncio.sleep(0.016)  # ~60fps

            except websockets.ConnectionClosed:
                simulator.stop()
                simulator.set_grid(default_state["starting_grid"])
                simulator.camera_pos = default_state["camera_pos"]
                autofocus = default_state["autofocus"]
                print("compute connection closed. Setting default state.")
                break

    except Exception as e:
        print(f"Error in compute websocket handler: {str(e)}")
        if verbose:
            import traceback
            traceback.print_exc()
        await websocket.close()

async def start_server(host="localhost", port=8765, verbose=False):
    """Start the WebSocket server"""
    simulator = CGOLSimulator(verbose=verbose)

    async def handler(websocket):
        await websocket_handler(websocket, simulator, verbose)

    async with websockets.serve(handler, host, port, max_queue=1):
        if verbose:
            print(f"Compute server started on ws://{host}:{port}")
        await asyncio.Future()  # run forever

def run_websocket_server(host="0.0.0.0", port=8765, verbose=False):
    """Run the WebSocket server in the main thread"""
    asyncio.run(start_server(host, port, verbose))
