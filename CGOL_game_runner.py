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
# today_grid = pattern2
#The today_grid stores the current state of every cell. The tomorrow_grid is filled every cycle as the game decides what the
#next day will look like.
tomorrow_grid = copy.deepcopy(today_grid)
empty_count = {(0, 0): 0}
new_chunks = {}

#Converts relative position to absolute position. accepts X and Y of chunk, then X and Y of cell in chunk.
def get_abs_position(gapChunk, gapX, gapY):
    return (int(gapChunk[0]) * 8 + int(gapX), int(gapChunk[1]) * 8 + int(gapY))

#Converts absolute position to relative position. Accepts a list with X and Y of cell.
def get_rltv_position(grpX, grpY):
    return ((int(grpX) // 8, int(grpY) // 8), int(grpX) % 8, int(grpY) % 8)

srnd_cells = ((-1, 1), (0, 1), (1, 1), (-1, 0), (1, 0), (-1, -1), (0, -1), (1, -1))
#Find the states of all 8 cells surrounding this one. Accepts absolute position.
#TODO: If gsc() tries to find a cell that doesn't exist (meaning it is in a cloesd chunk), it will send a request to open that chunk.
def get_srnd_cells(gscXY):
    (gscX, gscY) = gscXY
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
            gscCell = get_rltv_position(gscX, gscY)
            currCell = today_grid[gscCell[0]][gscCell[1]][gscCell[2]]
            if(currCell == "live"):  # Check if cell is live before doing chunk tests
                needCell = None #bug?  (Jedi) I don't think so, since this a hacky yet efficient way to check if the chunk needs opening
                
                # gscCell values: ((currentChunkX, currentChunkY), cellX, cellY)
                if(gscCell[1] == 7): #Bug: change gscX to gscCell[1] and repeat for all lines below. > 7 should not be possible. (Jedi) Fixed.  It worked, thanks! Before, it got stuck in the bottom right corner of (1,1)
                    needCell = (gscCell[0][0]+1, gscCell[0][1]) # > 7 shouldn't be possible, but it breaks otherwise (Connor) that could indicate a glitch.
                if(gscCell[1] == 0): #I, Connor, changed if to elif, for slight efficiency improvement. I did same once more below.
                    needCell == (gscCell[0][0]-1, gscCell[0][1]) # (Jedi) Change to elif works, but what if it needs to expand to both sides? (Connor) It will check the other side when it iterates over the cells on that side.
                
                if(gscCell[2] == 7):
                    needCell = (gscCell[0][0], gscCell[0][1]+1)
                if(gscCell[2] == 0):
                    needCell = (gscCell[0][0], gscCell[0][1]-1)
                
                # Add chunk if needed
                if(needCell != None):
                    #TODO create a list of newly opened chunks.  (Jedi) Why? (Connor) Because the game must iterate over the cells in this new chunk TODAY, not tomorrow.
                    #bug? will it try to create multiple chunks with the same key? (resolved)
                    #  It will just set the current key to a value,  possibly inefficient, but I think it would be more inefficient
                    #  to search through all the chunks first.  This is the same method I used to prevent duplcates in Taxi.
                    if(not needCell in today_grid.keys()):
                        tomorrow_grid[needCell] = [['dead'] * 8] * 8  # Initalize an empty chunk
                    if(not needCell in empty_count.keys()): #(Connor) Should empty_count be global? What about in other functions?
                        empty_count[needCell] = 0
                else:
                    raise Exception('cell in center of chunk triggered new chunk program')
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
        pcProcessed = [] #I, Connor, edited this variable name
        for c in row:
            pcProcessed.append(1 if c == "live" else 0)
        print(pcProcessed)

def print_board(grid):
    for key,value in grid.items():
        print(str(key)+":\t"+str(empty_count[chunk])+"  # of ch. "+str(len(grid)))
        print_chunk(value)


#TODO create day loop:
while today_grid != {}:
    #begin building next day and assigning to tomorrow_grid:
    for chunk in today_grid.keys(): #iterates over every chunk key
        if(today_grid[chunk] == [['dead'] * 8] * 8):
            empty_count[chunk] += 1 #(Connor) should this variable be global?
            if(empty_count[chunk] >= 5): #(Connor) what does this do?
                del empty_count[chunk]
                continue
        else:
            empty_count[chunk] = 0

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