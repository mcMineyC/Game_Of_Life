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
        self.genskip = 0
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
        if(interval < 0):
            print("CGOLSimulator: Negative interval. Skipping ", abs(interval), " generations.")
            self.genskip = abs(interval)
        else:
            self.interval = interval
            if(self.verbose): print("CGOLSimulator: set interval.")
    def stop(self):
        self.running = False
        if(self.verbose): print("CGOLSimulator: stopped.")
    def tick(self):
        if(self.verbose): print("CGOLSimulator: Ticking")
        if(self.genskip > 0):
            if(self.verbose): print("CGOLSimulator: Negative interval. Skipping ", self.interval*-2, " generations.")
            for x in range(self.genskip):
                self.current_grid = runner.next_gen(self.current_grid)
                self.gen += 1
            self.genskip = 0
        else:
            self.current_grid = runner.next_gen(self.current_grid)
            self.gen += 1
        if(self.verbose): print("CGOLSimulator: ticked.")
    def autofocus(self, mode="center"):
        if not self.current_grid:
            return self.camera_pos
        x_coords = [x for x, y in self.current_grid.keys()]
        y_coords = [y for x, y in self.current_grid.keys()]
        center_x = sum(x_coords) // len(x_coords)
        center_y = sum(y_coords) // len(y_coords)

        if mode == "center":
            print("centering")
            # Always center on pattern
            self.camera_pos = (center_x - 3, center_y + 3)
            return self.camera_pos
        elif mode == "follow":
            print("following")
        # Follow mode - only move camera when pattern leaves view
            window_left = self.camera_pos[0]
            window_right = self.camera_pos[0] + 7
            window_top = self.camera_pos[1]
            window_bottom = self.camera_pos[1] - 7

            pattern_left = min(x_coords)
            pattern_right = max(x_coords)
            pattern_top = max(y_coords)
            pattern_bottom = min(y_coords)
            # Check if pattern extends beyond window bounds
            if (pattern_left < window_left or
                pattern_right > window_right or
                pattern_top > window_top or
                pattern_bottom < window_bottom):
                    # Align left edge of pattern with window
                    self.camera_pos = (pattern_left, center_y + 3)
                    return (pattern_left, center_y + 3)
        print("no change")
        return self.camera_pos
    def process_grid(self):
        gridStr = cf.grid_to_string(self.current_grid, self.camera_pos, (self.camera_pos[0]+7, self.camera_pos[1]-7))
        # print(len(gridStr.splitlines()[0]))
        # print(len(gridStr.splitlines()))
        return gridStr
    def start(self):
        if(self.verbose): print("CGOLSimulator: Starting")
        self.running = True
    def doGens(self, numGens):
        for x in range(numGens):
            self.tick()
        if(self.verbose): print("CGOLSimulator: Done doing"+str(numGens)+"generations.")

    # def send_message(self, message):
    #     self.queue.put(message)
    #     if(self.verbose): print("CGOLSimulator: sent message.")
