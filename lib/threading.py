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
    if verbose:
        print("CGOL runner_thread: Runner thread created")

    needsToDie = False
    last_grid_update = time.time()
    MIN_UPDATE_INTERVAL = 0.016  # Minimum time between grid updatesa, ~60fps
    IDLE_SLEEP = 0.1  # Sleep time when not running
    def send_grid():
        # Helper function to consistently send grid through both channels
        curr_grid = simulator.process_grid()
        outgoing.send({
            "type": "grid",
            "data": curr_grid
        })
        if verbose:
            print("Sent grid to pipe")
        try:
            comms.send_message(client, curr_grid)
            if verbose:
                print("Sent grid to comms socket")
        except Exception as e:
            if verbose:
                print(f"CGOL runner_thread: Error sending message to comms socket: {e}")

    while True:

        # Process incoming messages
        while incoming.poll():
            item = incoming.recv()
            match(item["type"]):
                case "setgrid":
                    simulator.set_grid(item["data"])
                    send_grid()
                case "setinterval":
                    simulator.set_interval(item["data"])
                case "setcamera":
                    if verbose:
                        print("CGOL runner_thread: Setting camera to ", item["data"])
                    simulator.camera_pos = item["data"]
                    send_grid()
                case "stop":
                    simulator.stop()
                case "start":
                    if verbose:
                        print("CGOL runner_thread: Starting Main Loop")
                    simulator.start()
                case "avadakadavra":
                    needsToDie = True
                    break
        if needsToDie:
            if verbose:
                print("CGOL runner_thread: Received avadakadavra. Exiting.")
            else:
                print("Fly away, Stanley. Be free!!")
            break

        # Main simulation loop
        if simulator.running:
            if verbose:
                print("CGOL runner_thread: Running Main Loop")

            simulator.tick()

            send_grid()

            # Use the simulator interval directly for sleep
            if simulator.interval > 0:
                time.sleep(simulator.interval)
            else:
                time.sleep(MIN_UPDATE_INTERVAL)
        else:
            # Sleep longer when not running
            time.sleep(IDLE_SLEEP)
