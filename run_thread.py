import multiprocessing as mp
from lib import game_runner as runner
from lib import convert_functions as cf
from lib import communication_functions as comms
from lib import test_patterns as tp
import time

class QueueHandler:
    def __init__(self):
        self.queue = mp.Queue()
        print("QueueHandler: initialized.")
    def get_queue(self):
        return self.queue
    def put(self, item):
        self.queue.put(item)
        print("QueueHandler: put item.")
    def get(self):
        return self.queue.get()
    def empty(self):
        self.queue.empty()

class CGOLSimulator:
    def __init__(self,
        # queue, client,
        interval=0.25,
        starting_grid=None,
        camera_pos=(0, 7),
        verbose=False
    ):
        # self.queue = queue
        # self.client = client
        self.interval = interval
        self.starting_grid = starting_grid
        self.camera_pos = camera_pos
        self.current_grid = {}
        self.verbose = verbose
        self.running = False
        self.gen = 0
        if(self.starting_grid != None): self.running = True
        if(self.verbose): print("CGOLSimulator: initialized.")
    def set_grid(self, grid):
        self.starting_grid = grid
        self.current_grid = grid
        self.grid = grid
        self.gen = 0
        # self.running = True
        if(self.verbose): print("CGOLSimulator: set grid.")
    def set_interval(self, interval):
        self.interval = interval
        if(self.verbose): print("CGOLSimulator: set interval.")
    def stop(self):
        self.running = False
        if(self.verbose): print("CGOLSimulator: stopped.")
    def tick(self):
        if(self.verbose): print("CGOLSimulator: Ticking")
        if(self.interval < 0):
            print("CGOLSimulator: Negative interval. Skipping ", self.interval*-1, " generations.")
            for _ in range(self.interval*-1):
                self.current_grid = runner.next_gen(self.current_grid)
                self.gen += 1
        else:
            self.current_grid = runner.next_gen(self.current_grid)
            self.gen += 1
        if(self.verbose): print("CGOLSimulator: ticked.")
    def process_grid(self):
        gridStr = cf.grid_to_string(self.current_grid, self.camera_pos, (self.camera_pos[0]+7, self.camera_pos[1]-7))
        # print(len(gridStr.splitlines()[0]))
        # print(len(gridStr.splitlines()))
        return gridStr
    def start(self):
        if(self.verbose): print("CGOLSimulator: Starting")
        self.running = True

    # def send_message(self, message):
    #     self.queue.put(message)
    #     if(self.verbose): print("CGOLSimulator: sent message.")


def runner_thread(incoming, outgoing, client, verbose=False):
    simulator = CGOLSimulator(verbose=verbose)
    if(verbose): print("CGOL runner_thread: Runner thread created")
    # else: print("You're a wizard, Harry.")
    needsToDie = False
    while True:
        while incoming.poll():
            item = incoming.recv()
            match(item["type"]):
                case "setgrid":
                    simulator.set_grid(item["data"])
                    # simulator.start()
                case "setinterval":
                    simulator.set_interval(item["data"])
                case "setcamera":
                    if(verbose): print("CGOL runner_thread: Setting camera to ", item["data"])
                    simulator.camera_pos = item["data"]
                case "stop":
                    simulator.stop()
                case "start":
                    if(verbose): print("CGOL runner_thread: Starting Main Loop")
                    simulator.start()
                case "avadakadavra":
                    needsToDie = True
                    break
        if(needsToDie):
            if(verbose): print("CGOL runner_thread: Received avadakadavra. Exiting.")
            else: print("Fly away, Stanley. Be free!!")
            break

        if(simulator.running):
            if(verbose): print("CGOL runner_thread: Running Main Loop")
            curr_grid = simulator.process_grid()
            outgoing.send({
                "type": "grid",
                "data": curr_grid
            })
            if(verbose): print("Sent grid")
            try:
                comms.send_message(client, curr_grid)
            except:
                if(verbose): print("CGOL runner_thread: Error sending message. Not continuing")
                break
            simulator.tick()
            time.sleep(0 if simulator.interval < 0 else simulator.interval)

if __name__ == "__main__":
    kb = comms.KBHit()
    verbose = False
    showOutput = False
    ippipe, icpipe = mp.Pipe()
    oppipe, ocpipe = mp.Pipe()
    p = mp.Process(target=runner_thread, args=(ippipe, ocpipe, comms.get_socket(), verbose))
    camera_pos = (0, 7)
    interval = 0.25
    p.start()
    icpipe.send({
        "type": "setgrid",
        "data": tp.master_library["snark loop"]
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
                ppipe.send({
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
