#This program runs John Conway's Game of Life. It accepts a pattern to run, and calculates the next "day."
#The game is run on a grid of cells. Each cell can be either live (True) or dead (False)

import pprint #just for testing convenience
import copy, json, time
from CGOL_test_patterns import master_library

'''
#TODO create func to initialize global vars
def initialize_game_runner:
    from CGOL_game_runner import 
'''


empty_chunk = [[False] * 8] * 8
#This is the master dictionary. It contains all open chunks on the grid. A chunk is an 8x8 square of cells on the grid.
#Each chunk is made up of a list matrix of cells.
#An absolute coordinate is one that just has the position of a cell.
#A relative coordinate is the coordinate of a cell within a specific chunk. These below are relative coordinates.
#The relative coordinate of a cell within a chunk does not change based on what quadrant the chunk is in. The bottom 
#left cell in a chunk is always (0, 0).
#To retrieve a cell from today_grid (ngInputGrid), use the following format: today_grid[chunk][X][Y]
new_super_grid = master_library['glider'] #just for testing purposes
# today_grid = pattern2
#The today_grid (ngInputGrid) stores the current state of every cell. The tomorrow_grid (ngOutputGrid) is filled every cycle as the game decides what the
#next day will look like.






#Converts relative position to absolute position. accepts X and Y of chunk, then X and Y of cell in chunk.
def get_abs_position(gapChunk, gapX, gapY):
    return (int(gapChunk[0]) * 8 + int(gapX), int(gapChunk[1]) * 8 + int(gapY))

#Converts absolute position to relative position. Accepts a list with X and Y of cell.
def get_rltv_position(grpX, grpY):
    return ((int(grpX) // 8, int(grpY) // 8), int(grpX) % 8, int(grpY) % 8)

#Find the states of all 8 cells surrounding this one. Accepts absolute position.
def get_srnd_cells(gscXY, gscIsNew, gscMasterGrid): #gscIsNew cuts off unecessary processing when 
    (gscX, gscY) = gscXY
    global empty_chunk
    #nonlocal ngInputGrid, ngNewChunks

    gscOutput = []
    gscNewChunks = {}
    for gscPosition in ((-1, 1), (0, 1), (1, 1), (-1, 0), (1, 0), (-1, -1), (0, -1), (1, -1)): #iterates over all 8 surrounding cells
        #finds the relative position of one of the cells surrounding the chosen cell
        gscOuterCell = get_rltv_position(gscX + gscPosition[0], gscY + gscPosition[1])
        try:
            #retrieves the state of the above mentioned cell from gscMasterGrid and appends to gscOutput
            gscOutput.append(gscMasterGrid[gscOuterCell[0]][gscOuterCell[1]][gscOuterCell[2]]) #can you see me?
        except KeyError:
            if gscOuterCell[0] in gscMasterGrid: #sanity check. TODO delete for final program
                raise Exception('Eureka! Error on line 46(?):\ngscOutput.append(gscMasterGrid[gscOuterCell[0]][gscOuterCell[1]][gscOuterCell[2]])')
            gscOutput.append(False)
            gscCell = get_rltv_position(gscX, gscY)
            if gscMasterGrid[gscCell[0]][gscCell[1]][gscCell[2]] and not gscIsNew:  # Check if cell is live band if chunk is new
                # Open an empty chunk
                gscNewChunks[gscOuterCell[0]] = copy.deepcopy(empty_chunk)
                #TODO Optimize: program unecessarily opens 3 chunks when processing a cell in the corner of a chunk.

    return (gscOutput, gscNewChunks)


#Accepts state of a cell along with the states of its 8 neighbors; returns new state for cell.
def cell_next_day(cndCellState, cndSrndngCells):
    cndLive = cndSrndngCells.count(True)
    if cndCellState == True:
        if cndLive == 2 or cndLive == 3:
            return True
    else: # is dead
        if cndLive == 3:
            return True
    return False






#accepts grid and window for camera, prints grid.
def pro_print_grid(ppgGrid, ppgUpLeft, ppgDownRight):
    ppgOutput = ''
    print(get_chunk_window(ppgUpLeft, ppgDownRight))
    for ppgChunkRow in get_chunk_window(ppgUpLeft, ppgDownRight):
        for ppgCellRow in range(7, -1, -1):
            for ppgChunk in ppgChunkRow:
                for ppgX in range(8):
                    if ppgChunk in ppgGrid:
                        ppgOutput = ppgOutput + ('[]' if ppgGrid[ppgChunk][ppgX][ppgCellRow] else '<>')
                    else:
                        ppgOutput += '::'
                    print(ppgChunk, ppgCellRow, ppgX, ppgOutput[-2:])

            ppgOutput += '\n'

    print(ppgOutput)


#accepts coordinates of two chunks and returns all chunks within the window.
def get_chunk_window(gcwUpLeft, gcwDownRight):
    assert type(gcwUpLeft) in (tuple, list) and len(gcwUpLeft) == 2, 'gcw parameter gcwUpLeft passed invalid argument'
    assert type(gcwDownRight) in (tuple, list) and len(gcwDownRight) == 2, 'gcw parameter gcwDownRight passed invalid argument'
    gcwOutput = []
    for gcwY, gcwCounter in zip(range(gcwUpLeft[1], gcwDownRight[1]-1, -1), range(99)):
        gcwOutput.append([])
        for gcwX in range(gcwUpLeft[0], gcwDownRight[0]+1):#correct?
            gcwOutput[gcwCounter].append((gcwX, gcwY))
    assert gcwOutput != []
    return gcwOutput





#TODO put each gen run into a func that uses global vars:
#accepts full grid and returns the next generation of the grid.
def next_gen(ngInputGrid):
    global empty_chunk
    ngOutputGrid = {}
    start_time = time.perf_counter() #test speed #TODO remove for final product

    #remove empty chunks from ngInputGrid
    for chunk in copy.deepcopy(ngInputGrid):
        if ngInputGrid[chunk] == empty_chunk:
            del ngInputGrid[chunk]

    for chunk in ngInputGrid: #iterates over every chunk key
        ngOutputGrid[chunk] = []
        for Xcoord in range(8): #iterates over every X coordinate in chunk
            ngOutputGrid[chunk].append([])
            for Ycoord in range(8): #iterates over every Y coordinate
                #find states of surrounding cells
                ngSrndCells, ngNewChunks = get_srnd_cells(get_abs_position(chunk, Xcoord, Ycoord), False, ngInputGrid)
                #find new state of cell and add to ngOutputGrid
                ngOutputGrid[chunk][Xcoord].append(cell_next_day(ngInputGrid[chunk][Xcoord][Ycoord], ngSrndCells))

    #add newly any newly opened chunks to ngInputGrid
    for addition in ngNewChunks:
        ngInputGrid[addition] = copy.deepcopy(ngNewChunks[addition])
        #print('opened chunk: ' + str(addition))
    #Iterate over all cells in newly opened chunks:
    for chunk in copy.deepcopy(ngNewChunks): #iterates over every chunk key
        ngOutputGrid[chunk] = []
        for Xcoord in range(8): #iterates over every X coordinate in chunk
            ngOutputGrid[chunk].append([])
            for Ycoord in range(8): #iterates over every Y coordinate
                #find states of surrounding cells
                ngSrndCells, ngNewChunks = get_srnd_cells(get_abs_position(chunk, Xcoord, Ycoord), True, ngInputGrid)
                #find new state of cell and add to ngOutputGrid
                ngOutputGrid[chunk][Xcoord].append(cell_next_day(ngInputGrid[chunk][Xcoord][Ycoord], ngSrndCells))

    #this code below can either be at the front or the back of this loop. It prgresses the master dictionary to the next day.
    end_time = time.perf_counter()
    print(end_time - start_time)
    return ngOutputGrid





"""
day = 0
#Daily loop:
while day != 1:

    print(day)
    #print_board(today_grid)
    #pprint.pprint(today_grid)
    #connor_print(copy.deepcopy(today_grid))
    pro_print_grid(new_super_grid, (0, 4), (5, 0))
    print(new_super_grid)

    new_super_grid = next_gen(new_super_grid)
    day += 1

    time.sleep(0.2)




print('Grid is empty. Program ended.')
"""


#Coding tip: Local variables do not have underscores and are prefixed by the name of their domain.

#TODO: Optimization: make loops shorter, e.g. use while instead of for. Remove unecessary variables and asserts (such as the one in get_window(). What else?
#TODO speed test
#TODO check for consistency in cell values and such