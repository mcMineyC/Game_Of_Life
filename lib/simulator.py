from lib import game_runner as runner
from lib import convert_functions as cf
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
            for _ in range(abs(int(self.interval))):
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
