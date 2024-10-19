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
        camera_pos=(-4, 4),
        verbose=False
    ):
        # self.queue = queue
        # self.client = client
        self.interval = interval
        self.starting_grid = starting_grid
        self.camera_pos = camera_pos
        self.current_grid = []
        self.verbose = verbose
        self.running = False
        self.gen = 0
        if(self.starting_grid != None): self.running = True
        if(self.verbose): print("CGOLSimulator: initialized.")
    def set_grid(self, grid):
        self.starting_grid = grid
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
        print("Ticking")
        self.current_grid = runner.next_gen(self.current_grid)
        self.gen += 1
        if(self.verbose): print("CGOLSimulator: ticked.")
    def process_grid(self):
        gridStr = cf.grid_to_string(self.current_grid, self.camera_pos, (self.camera_pos[0]+7, self.camera_pos[1]-7))
        print(len(gridStr.splitlines()[0]))
        print(len(gridStr.splitlines()))
        return gridStr
    def start(self):
        print("Starting")
        self.running = True

    # def send_message(self, message):
    #     self.queue.put(message)
    #     if(self.verbose): print("CGOLSimulator: sent message.")


def runner_thread(incoming, outgoing, client):
    simulator = CGOLSimulator(verbose=True)
    # simulator.set_grid(tp.master_library["snark loop"])
    # simulator.start()
    while True:
        while incoming.poll():
            print("Incoming data")
            item = incoming.recv()
            match(item["type"]):
                case "setgrid":
                    simulator.set_grid(item["data"])
                    simulator.start()
                    break;
                case "setinterval":
                    simulator.set_interval(item["data"])
                    break;
                case "stop":
                    simulator.stop()
                    break;
                case "start":
                    simulator.start()
                    break;

        if(simulator.running or True):
            print("Running Main Loop")
            curr_grid = simulator.process_grid()
            outgoing.send({
                "type": "grid",
                "data": curr_grid
            })
            try:
                comms.send_message(client, curr_grid)
            except:
                print("Error sending message. continuing")
            simulator.tick()
            time.sleep(simulator.interval)

if __name__ == "__main__":
    ppipe, cpipe = mp.Pipe()
    p = mp.Process(target=runner_thread, args=(cpipe, ppipe, comms.get_socket()))
    p.start()
    ppipe.send({
        "type": "setgrid",
        "data": tp.master_library["snark loop"]
    })
    ppipe.send({
        "type": "start",
    })
    while True:
        if not ppipe.poll():
            time.sleep(0.5)
            pass
        else:
            print("received data", ppipe.recv())
    print("Thread finished.")
