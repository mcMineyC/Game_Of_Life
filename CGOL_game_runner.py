#This program runs John Conway's Game of Life. It accepts a pattern to run, and calculates the next "day."
#The game is run on a grid of cells. Each cell can be either 'live' or 'dead'

import pprint #just for testing convenience
import copy
import time
import json
from CGOL_test_patterns import glider as pattern1

#This is the master dictionary. It contains all open chunks on the grid. A chunk is an 8x8 square of cells on the grid.
#Each chunk is made up of a list matrix of cells.
#An absolute coordinate is one that just has the position of a cell.
#A relative coordinate is the coordinate of a cell within a specific chunk. These below are relative coordinates.
#The relative coordinate of a cell within a chunk does not change based on what quadrant the chunk is in. The bottom 
#left cell in a chunk is always (0, 0).
#To retrieve a cell from today_grid, use the following format: today_grid[chunk][X][Y]
today_grid = {(0, 0): [['dead'] * 8] * 8}
today_grid = pattern1 #just for testing purposes
#The today_grid stores the current state of every cell. The tomorrow_grid is filled every cycle as the game decides what the
#next day will look like.
tomorrow_grid = copy.deepcopy(today_grid)

#Converts relative position to absolute position. accepts X and Y of chunk, then X and Y of cell in chunk.
def get_abs_position(gapChunk, gapX, gapY):
    return (int(gapChunk[0]) * 8 + int(gapX), int(gapChunk[1]) * 8 + int(gapY))

#Converts absolute position to relative position. Accepts a list with X and Y of cell.
def get_rltv_position(grpX, grpY):
    return ((int(grpX) // 8, int(grpY) // 8), int(grpX) % 8, int(grpY) % 8)

srnd_cells = ((-1, 1), (0, 1), (1, 1), (-1, 0), (1, 0), (-1, -1), (0, -1), (1, -1))
#Find the states of all 8 cells surrounding this one. Accepts absolute position.
#TODO: If gsc() tries to find a cell that doesn't exist (meaning it is in a cloesd chunk), it will send a request to open that chunk.
def get_srnd_cells(gscTuple):
    (gscX, gscY) = gscTuple
    global srnd_cells, today_grid
    gscOutput = []
    for gscPosition in srnd_cells:
        #finds the relative position of one of the cells surrounding the chosen cell
        gscOuterCell = get_rltv_position(gscX + gscPosition[0], gscY + gscPosition[1])
        try:
            #retrieves the state of the above mentioned cell from today_grid and appends to gscOutput
            gscOutput.append(today_grid[gscOuterCell[0]][gscOuterCell[1]][gscOuterCell[2]])
        except:
            gscOutput.append('dead')
            # print('open new chunk')
            gscCell = get_rltv_position(gscX, gscY)
            currCell = today_grid[gscCell[0]][gscCell[1]][gscCell[2]]
            if(currCell == "live"):  # Check if cell is live before doing chunk tests
                needCell = (0,0)
                if(gscX >= 7):
                    needCell = (gscCell[0][0]+1, gscCell[0][1])
                
                if(gscX <= 0):
                    needCell = (gscCell[0][0]-1, gscCell[0][1])
                
                if(gscY <= 0):
                    needCell = (gscCell[0][0], gscCell[0][1]-1)
                
                if(gscY >= 7):
                    needCell = (gscCell[0][0], gscCell[0][1]+1)
                
                # Add chunk if needed
                if(needCell != (0,0)):
                    tomorrow_grid[needCell] = [['dead'] * 8] * 8  # Initalize an empty chunk
            
            
            #TODO (DONE) send request to open new chunk, but only if this cell is live.
            #   get current side the cell is at (probably through gscPosition)
            #   Compute the chunks that need to open
            #   Append those chunks with their tuple key
    return gscOutput

#Accepts state of a cell along with the states of its 8 neighbors; returns new state for cell.
def cell_next_day(cndCellState, cndSrndngCells):
    cndLive = cndSrndngCells.count('live')
    if cndCellState == 'live':
        if cndLive == 2 or cndLive == 3:
            return 'live'
    else: # is dead
        if cndLive == 3:
            return 'live'
    return 'dead'

def print_chunk(chunk):
    for row in chunk:
        processed = []
        for c in row:
            processed.append(1 if c == "live" else 0)
        print(processed)

def print_board(grid):
    for key,value in grid.items():
        print(str(key)+":")
        print_chunk(value)

#TODO create day loop:
while today_grid != {}:
    #begin building next day and assigning to tomorrow_grid:
    for chunk in today_grid.keys(): #iterates over every chunk key
        tomorrow_grid[chunk] = []
        for Xcoord in range(8): #iterates over every X coordinate in chunk
            tomorrow_grid[chunk].append([])
            for Ycoord in range(8): #iterates over every Y coordinate
               #add cell to tomorrow_grid;          getNewState;  state of current cell              states of surrounding cells
                tomorrow_grid[chunk][Xcoord].append(cell_next_day(today_grid[chunk][Xcoord][Ycoord], get_srnd_cells(get_abs_position(chunk, Xcoord, Ycoord))))
    #TODO: Iterate over all cells in any new opened chunks.
    #this code below can either be at the front or the back of this loop. It prgresses the master dictionary to the next day.
    today_grid = copy.deepcopy(tomorrow_grid)
    tomorrow_grid = {}
    time.sleep(0.5)  # I (Jedi) added this to test the loop
    print("\n\n")
    print_board(today_grid)


#Coding tip: Local variables do not have underscores and are prefixed by the name of their domain.
#TODO [I believe this task is completed] I have been frequently switching between using x and y as a single tuple and 
#     x and y being separate. double check all code to make sure that functions are consistent.