import multiprocessing as mp
from lib import convert_functions as cf
from lib import communication_functions as comms
from lib import test_patterns as tp
from lib import threading as libthread
import time

if __name__ == "__main__":
    kb = comms.KBHit()
    verbose = True
    showOutput = False
    ippipe, icpipe = mp.Pipe()
    oppipe, ocpipe = mp.Pipe()
    p = mp.Process(target=libthread.runner_thread, args=(ippipe, ocpipe, comms.get_socket(), verbose))
    camera_pos = (-1, 1)
    interval = 0.25
    p.start()
    icpipe.send({
        "type": "setgrid",
        # "data": tp.master_library["snark loop"]
        "data": cf.RLE_to_matrix("bo$2bo$3o!")
    })
    icpipe.send({
        "type": "setcamera",
        "data": camera_pos,
    })
    # icpipe.send({
    #     "type": "start",
    # })
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
                icpipe.send({
                    "type": "setcamera",
                    "data": camera_pos,
                })
            case "s":
                camera_pos = (camera_pos[0]-1, camera_pos[1])
                icpipe.send({
                    "type": "setcamera",
                    "data": camera_pos,
                })
            case "a":
                camera_pos = (camera_pos[0], camera_pos[1]-1)
                icpipe.send({
                    "type": "setcamera",
                    "data": camera_pos,
                })
            case "d":
                camera_pos = (camera_pos[0], camera_pos[1]+1)
                icpipe.send({
                    "type": "setcamera",
                    "data": camera_pos,
                })
            case "p":
                icpipe.send({
                    "type": "stop",
                })
            case "t":
                print("Starting")
                icpipe.send({
                    "type": "start",
                })
            case "g":
                skip = int(input("Number of gens to skip: "))
                icpipe.send({
                    "type": "setinterval",
                    "data": -1 * skip,
                })
            case "[":
                interval -= 0.05
                if(interval < 0): interval = 0
                icpipe.send({
                    "type": "setinterval",
                    "data": interval,
                })
            case "]":
                interval += 0.05
                icpipe.send({
                    "type": "setinterval",
                    "data": interval,
                })
            case "{":
                interval = 0
                icpipe.send({
                    "type": "setinterval",
                    "data": interval,
                })
            case "}":
                interval = 0.25
                icpipe.send({
                    "type": "setinterval",
                    "data": interval,
                })
            case "o":
                showOutput = not showOutput
            case "q":
                icpipe.send({
                    "type": "avadakadavra",
                })
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
        if not oppipe.poll():
            time.sleep(0.1)
            pass
        else:
            currGrid = oppipe.recv()
            if(showOutput): print(currGrid)
    print("Thread finished.")
    kb.set_normal_term()
