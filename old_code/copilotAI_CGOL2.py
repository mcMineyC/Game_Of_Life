#This is a program created by Windows Copilot AI designed to run the Game of Life.
#It is an improvment on the last version because this one uses chunks to run an infinite grid.

import pprint #added by me

class InfiniteGrid:
    def __init__(self):
        self.live_cells = set()

    def is_alive(self, x, y):
        return (x, y) in self.live_cells

    def set_cell(self, x, y, state):
        if state:
            self.live_cells.add((x, y))
        elif (x, y) in self.live_cells:
            self.live_cells.remove((x, y))

    def get_live_neighbors(self, x, y):
        directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
        return sum((x + dx, y + dy) in self.live_cells for dx, dy in directions)

    def step(self):
        new_live_cells = set()
        potential_cells = self.live_cells | set(
            (x + dx, y + dy) for x, y in self.live_cells for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]
        )
        for x, y in potential_cells:
            live_neighbors = self.get_live_neighbors(x, y)
            if (self.is_alive(x, y) and live_neighbors in (2, 3)) or (not self.is_alive(x, y) and live_neighbors == 3):
                new_live_cells.add((x, y))
        self.live_cells = new_live_cells

# Initialize the infinite grid
grid = InfiniteGrid()

# Define the glider pattern
glider_pattern = [(1, 0), (2, 1), (0, 2), (1, 2), (2, 2)]

# Set the initial live cells
for x, y in glider_pattern:
    grid.set_cell(x, y, True)

# Run the Game of Life for a few steps
for _ in range(5):
    grid.step()
    pprint.pprint(grid.live_cells) #added by me
    print('\n') #added by me

# The live cells can be accessed via grid.live_cells
