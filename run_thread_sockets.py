import websockets
import asyncio
from lib import convert_functions as cf
from lib import communication_functions as comms
from lib import test_patterns as tp
import time
import json

async def main():
    kb = comms.KBHit()
    verbose = True
    showOutput = False
    autofocus = False
    camera_pos = (-1, 1)
    interval = 0.25
    # url = "ws://localhost:5001"
    url = "ws://matrix.local:5001"
    # Connect to WebSocket
    async with websockets.connect(url) as websocket:
        # Initial setup
        await websocket.send(json.dumps({
            "type": "setrle",
            # "data": "bo$2bo$3o!"
            # "data": cf.matrix_to_RLE(tp.master_library["snark loop"])
            # "data": input("Enter RLE: ")
            "data": "4bo$3b3o$2b2ob2o2$bobobobo2bo$2o3bo3b3o$2o3bo6bo$10bobo$8bobo$9bo2bo$12bo!"
        }))

        await websocket.send(json.dumps({
            "type": "setcamera",
            "x": camera_pos[0],
            "y": camera_pos[1],
        }))
        await websocket.send(json.dumps({
            "type": "setinterval",
            "data": 0.25,
        }))
        await websocket.send(json.dumps({
            "type": "stop",
        }))

        said = False
        while True:
            if(not said):
                print("> ", end="", flush=True)
                said = True

            inputStr = ""
            if(kb.kbhit()):
                inputStr = kb.getch()
                print(inputStr)
            if(inputStr != ""):
                said = False

            match(inputStr):
                case "s":
                    camera_pos = (camera_pos[0]+1, camera_pos[1])
                    await websocket.send(json.dumps({
                        "type": "setcamera",
                        "x": camera_pos[0],
                        "y": camera_pos[1]
                    }))
                case "w":
                    camera_pos = (camera_pos[0]-1, camera_pos[1])
                    await websocket.send(json.dumps({
                        "type": "setcamera",
                        "x": camera_pos[0],
                        "y": camera_pos[1]
                    }))
                case "a":
                    camera_pos = (camera_pos[0], camera_pos[1]-1)
                    await websocket.send(json.dumps({
                        "type": "setcamera",
                        "x": camera_pos[0],
                        "y": camera_pos[1]
                    }))
                case "d":
                    camera_pos = (camera_pos[0], camera_pos[1]+1)
                    await websocket.send(json.dumps({
                        "type": "setcamera",
                        "x": camera_pos[0],
                        "y": camera_pos[1]
                    }))
                case "p":
                    await websocket.send(json.dumps({
                        "type": "stop",
                    }))
                case "t":
                    print("Starting")
                    await websocket.send(json.dumps({
                        "type": "start",
                    }))
                case "g":
                    kb.set_normal_term()
                    skip = int(input("Number of gens to skip: "))
                    kb.init_term()
                    await websocket.send(json.dumps({
                        "type": "setinterval",
                        "data": -1 * skip,
                    }))
                case "i":
                    kb.set_normal_term()
                    skip = int(input("Number of gens to do: "))
                    kb.init_term()
                    await websocket.send(json.dumps({
                        "type": "dogens",
                        "data": skip,
                    }))
                case "[":
                    interval -= 0.05
                    if(interval < 0): interval = 0
                    await websocket.send(json.dumps({
                        "type": "setinterval",
                        "data": interval,
                    }))
                case "]":
                    interval += 0.05
                    await websocket.send(json.dumps({
                        "type": "setinterval",
                        "data": interval,
                    }))
                case "{":
                    interval = 0
                    await websocket.send(json.dumps({
                        "type": "setinterval",
                        "data": interval,
                    }))
                case "}":
                    interval = 0.25
                    await websocket.send(json.dumps({
                        "type": "setinterval",
                        "data": interval,
                    }))
                case "o":
                    showOutput = not showOutput
                case "x":
                    await websocket.send(json.dumps({
                        "type": "setautofocus",
                        "data": "follow",
                    }))
                case "c":
                    await websocket.send(json.dumps({
                        "type": "setautofocus",
                        "data": "center",
                    }))
                case "v":
                    await websocket.send(json.dumps({
                        "type": "setautofocus",
                        "data": "none",
                    }))
                case "q":
                    await websocket.send(json.dumps({
                        "type": "avadakadavra",
                    }))
                    break
                case "h":
                    print("""
    Commands:
    \tw: move camera up
    \ts: move camera down
    \ta: move camera left
    \td: move camera right
    \tp: pause/stop
    \tt: start
    \tg: skip n gens
    \t[: speed up
    \t]: slow down
    \t{: As fast as possible
    \t}: Reset (0.25)
    \to: toggle output
    \tq: quit
    \th: print this
    """)

            try:
                # Set a timeout for receiving messages
                message = await asyncio.wait_for(websocket.recv(), timeout=0.1)
                data = json.loads(message)
                if data["type"] == "grid":
                    currGrid = data["data"]
                    if(showOutput):
                        print(currGrid)
                elif data["type"] == "info":
                    print("New message from server:", data["message"])
                elif data["type"] == "camerapos":
                    camera_pos = (data["data"]["x"], data["data"]["y"])
                    if(showOutput): print("Camera at position", camera_pos)
            except asyncio.TimeoutError:
                pass

    print("Connection closed.")
    kb.set_normal_term()

if __name__ == "__main__":
    asyncio.run(main())
