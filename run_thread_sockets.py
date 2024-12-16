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
    camera_pos = (-1, 1)
    interval = 0.25

    # Connect to WebSocket
    async with websockets.connect('ws://localhost:5001') as websocket:
        # Initial setup
        await websocket.send(json.dumps({
            "type": "setgrid",
            "data": cf.RLE_to_matrix("bo$2bo$3o!")
        }))

        await websocket.send(json.dumps({
            "type": "setcamera",
            "data": camera_pos,
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
                case "w":
                    camera_pos = (camera_pos[0]+1, camera_pos[1])
                    await websocket.send(json.dumps({
                        "type": "setcamera",
                        "data": camera_pos,
                    }))
                case "s":
                    camera_pos = (camera_pos[0]-1, camera_pos[1])
                    await websocket.send(json.dumps({
                        "type": "setcamera",
                        "data": camera_pos,
                    }))
                case "a":
                    camera_pos = (camera_pos[0], camera_pos[1]-1)
                    await websocket.send(json.dumps({
                        "type": "setcamera",
                        "data": camera_pos,
                    }))
                case "d":
                    camera_pos = (camera_pos[0], camera_pos[1]+1)
                    await websocket.send(json.dumps({
                        "type": "setcamera",
                        "data": camera_pos,
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
                    skip = int(input("Number of gens to skip: "))
                    await websocket.send(json.dumps({
                        "type": "setinterval",
                        "data": -1 * skip,
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
            except asyncio.TimeoutError:
                pass

    print("Connection closed.")
    kb.set_normal_term()

if __name__ == "__main__":
    asyncio.run(main())
