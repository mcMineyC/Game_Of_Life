#This program runs John Conway's Game of Life. It accepts a pattern to run, and calculates the next "day."
#The game is run on a grid of cells. Each cell can be either 'live' or 'dead'

import pprint #just for testing convenience
import copy, json, time
from CGOL_test_patterns import LWSSspaceship as pattern


empty_chunk = [['dead'] * 8] * 8
#This is the master dictionary. It contains all open chunks on the grid. A chunk is an 8x8 square of cells on the grid.
#Each chunk is made up of a list matrix of cells.
#An absolute coordinate is one that just has the position of a cell.
#A relative coordinate is the coordinate of a cell within a specific chunk. These below are relative coordinates.
#The relative coordinate of a cell within a chunk does not change based on what quadrant the chunk is in. The bottom 
#left cell in a chunk is always (0, 0).
#To retrieve a cell from today_grid, use the following format: today_grid[chunk][X][Y]
today_grid = {(0, 0): copy.deepcopy((empty_chunk))}
today_grid = pattern #just for testing purposes
# today_grid = pattern2
#The today_grid stores the current state of every cell. The tomorrow_grid is filled every cycle as the game decides what the
#next day will look like.
tomorrow_grid = {}
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
    global srnd_cells, today_grid, empty_chunk, new_chunks, is_new
    gscOutput = []
    for gscPosition in srnd_cells:
        #finds the relative position of one of the cells surrounding the chosen cell
        gscOuterCell = get_rltv_position(gscX + gscPosition[0], gscY + gscPosition[1])
        try:
            #retrieves the state of the above mentioned cell from today_grid and appends to gscOutput
            gscOutput.append(today_grid[gscOuterCell[0]][gscOuterCell[1]][gscOuterCell[2]])
        except:
            if gscOuterCell[0] in today_grid: #sanity check. TODO delete for final program
                raise Exception('Eureka! Error on line 46:\ngscOutput.append(today_grid[gscOuterCell[0]][gscOuterCell[1]][gscOuterCell[2]])')
            gscOutput.append('dead')
            gscCell = get_rltv_position(gscX, gscY)
            if today_grid[gscCell[0]][gscCell[1]][gscCell[2]] == "live" and is_new == False:  # Check if cell is live before doing chunk tests
                # Open an empty chunk
                new_chunks[gscOuterCell[0]] = copy.deepcopy(empty_chunk)
                #TODO Optimize: program unecessarily opens 3 chunks when processing a cell in the corner of a chunk.

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

def print_chunk(pcChunk):
    for row in pcChunk:
        pcProcessed = []
        for c in row:
            pcProcessed.append('E' if c == "live" else ':')
        print(pcProcessed)

def print_board(pbGrid):
    for key,value in grid.items():
        print(str(key)+":\t"+str(empty_count[chunk])+"  # of ch. "+str(len(pbGridrid)))
        print_chunk(value)

def connor_print(cpGrid): #note: prints sideways.
    for chunk in cpGrid: #iterates over every chunk key
        for Xcoord in range(8): #iterates over every X coordinate in chunk
            for Ycoord in range(8): #iterates over every Y coordinate
                if cpGrid[chunk][Xcoord][Ycoord] == 'live':
                    cpGrid[chunk][Xcoord][Ycoord] = 'E'
                elif cpGrid[chunk][Xcoord][Ycoord] == 'dead':
                    cpGrid[chunk][Xcoord][Ycoord] = ':'
                else:
                    raise Exception('AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA')
    pprint.pprint(cpGrid)


day = 0
#Daily loop:
connor_print(copy.deepcopy(today_grid))
while today_grid != {}:

    #begin building next day and assigning to tomorrow_grid:
    is_new = False #cuts off unecessary processing in get_srnd_cells()

    #remove empty chunks from today_grid
    for chunk in copy.deepcopy(today_grid):
        if today_grid[chunk] == empty_chunk:
            del today_grid[chunk]
            print('closed chunk: ' + str(chunk))

    for chunk in today_grid: #iterates over every chunk key
        tomorrow_grid[chunk] = []
        for Xcoord in range(8): #iterates over every X coordinate in chunk
            tomorrow_grid[chunk].append([])
            for Ycoord in range(8): #iterates over every Y coordinate
                #add cell to tomorrow_grid;          getNewState;  state of current cell              states of surrounding cells
                tomorrow_grid[chunk][Xcoord].append(cell_next_day(today_grid[chunk][Xcoord][Ycoord], get_srnd_cells(get_abs_position(chunk, Xcoord, Ycoord))))

    #connor_print(copy.deepcopy(tomorrow_grid))
    #add newly any newly opened chunks to today_grid
    is_new = True
    #print('new_chunks.keys() == ' + str(new_chunks.keys()))
    for addition in new_chunks:
        today_grid[addition] = copy.deepcopy(new_chunks[addition])
        print('opened chunk: ' + str(addition))
    #Iterate over all cells in newly opened chunks:
    for chunk in copy.deepcopy(new_chunks): #iterates over every chunk key
        tomorrow_grid[chunk] = []
        for Xcoord in range(8): #iterates over every X coordinate in chunk
            tomorrow_grid[chunk].append([])
            for Ycoord in range(8): #iterates over every Y coordinate
                #add cell to tomorrow_grid;          getNewState;  state of current cell              states of surrounding cells
                tomorrow_grid[chunk][Xcoord].append(cell_next_day(today_grid[chunk][Xcoord][Ycoord], get_srnd_cells(get_abs_position(chunk, Xcoord, Ycoord))))


    #this code below can either be at the front or the back of this loop. It prgresses the master dictionary to the next day.
    day += 1
    today_grid = copy.deepcopy(tomorrow_grid)
    tomorrow_grid = {}
    new_chunks = {}
    time.sleep(0.1)
    print(day)
    #print_board(today_grid)
    #pprint.pprint(today_grid)
    connor_print(copy.deepcopy(today_grid))
    print("\n")



print('Grid is empty. Program ended.')



#print(get_srnd_cells(get_abs_position((1, 0), 0, 6)))

#Coding tip: Local variables do not have underscores and are prefixed by the name of their domain.
#TODO [I believe this task is completed] I have been frequently switching between using x and y as a single tuple and 
#     x and y being separate. double check all code to make sure that functions are consistent.
#TODO: Optimization: make loops shorter, e.g. use while instead of for. Remove unecessary variables. What else?