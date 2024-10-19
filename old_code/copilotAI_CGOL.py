#This is a program created by Windows Copilot AI designed to run the Game of Life.

def print_grid(grid):
    for row in grid:
        print(' '.join(str(cell) for cell in row))

def get_live_neighbors(grid, x, y):
    directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
    live_neighbors = 0
    for dx, dy in directions:
        nx, ny = x + dx, y + dy
        if 0 <= nx < len(grid) and 0 <= ny < len(grid[0]):
            live_neighbors += grid[nx][ny]
    return live_neighbors

def game_of_life_step(grid):
    new_grid = [[0 for _ in range(len(grid[0]))] for _ in range(len(grid))]
    for x in range(len(grid)):
        for y in range(len(grid[0])):
            live_neighbors = get_live_neighbors(grid, x, y)
            if grid[x][y] == 1 and live_neighbors in (2, 3):
                new_grid[x][y] = 1
            elif grid[x][y] == 0 and live_neighbors == 3:
                new_grid[x][y] = 1
    return new_grid

# Example starting pattern
starting_pattern = [
    [0, 1, 0, 0, 0],
    [0, 0, 1, 0, 0],
    [1, 1, 1, 0, 0],
    [0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0]
]

# Run the Game of Life
current_grid = starting_pattern
print("Starting pattern:")
print_grid(current_grid)

steps = 12  # Number of steps to simulate
for step in range(steps):
    current_grid = game_of_life_step(current_grid)
    print(f"After step {step + 1}:")
    print_grid(current_grid)
