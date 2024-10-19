#This program runs John Conway's Game of Life. It accepts a pattern to run, and calculates the next "day."
#The game is run on a grid of cells. Each cell can be either live (True) or dead (False)

import copy, time

empty_chunk = [[False] * 8] * 8
#This is the master dictionary. It contains all open chunks on the grid. A chunk is an 8x8 square of cells on the grid.
#Each chunk is made up of a list matrix of cells.
#An absolute coordinate is one that just has the position of a cell.
#A relative coordinate is the coordinate of a cell within a specific chunk. These below are relative coordinates.
#The relative coordinate of a cell within a chunk does not change based on what quadrant the chunk is in. The bottom 
#left cell in a chunk is always (0, 0).
#To retrieve a cell from today_grid (ngInputGrid), use the following format: today_grid[chunk][X][Y]
#The today_grid (ngInputGrid) stores the current state of every cell. The tomorrow_grid (ngOutputGrid) is filled every cycle as the game decides what the
#next day will look like.


#Converts relative position to absolute position. accepts X and Y of chunk, then X and Y of cell in chunk.
def get_abs_position(gapChunk, gapX, gapY):
    return (int(gapChunk[0]) * 8 + int(gapX), int(gapChunk[1]) * 8 + int(gapY))

#Converts absolute position to relative position. Accepts a list with X and Y of cell.
def get_rltv_position(grpX, grpY):
    return ((int(grpX) // 8, int(grpY) // 8), int(grpX) % 8, int(grpY) % 8)

#Find the states of all 8 cells surrounding this one. Accepts absolute position.
def get_srnd_cells(gscXY, gscIsNew, gscMasterGrid): #gscIsNew cuts off unecessary processing when main code does second loop over new chunks
    (gscX, gscY) = gscXY
    global empty_chunk

    gscOutput = []
    gscNewChunks = {}
    for gscPosition in ((-1, 1), (0, 1), (1, 1), (-1, 0), (1, 0), (-1, -1), (0, -1), (1, -1)): #iterates over all 8 surrounding cells
        #finds the relative position of one of the cells surrounding the chosen cell
        gscOuterCell = get_rltv_position(gscX + gscPosition[0], gscY + gscPosition[1])
        try:
            #retrieves the state of the above mentioned cell from gscMasterGrid and appends to gscOutput
            gscOutput.append(gscMasterGrid[gscOuterCell[0]][gscOuterCell[1]][gscOuterCell[2]]) #can you see me?
        except KeyError:
            gscOutput.append(False)
            gscCell = get_rltv_position(gscX, gscY)
            if gscMasterGrid[gscCell[0]][gscCell[1]][gscCell[2]] and not gscIsNew:  # Check if cell is live and if chunk is new
                # Open an empty chunk
                #TODO newChunks is a dictionary. It should be a list.
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




#accepts full grid and returns the next generation of the grid.
def next_gen(ngInputGrid):
    global empty_chunk
    ngOutputGrid = {}
    start_time = time.perf_counter() #test speed #TODO remove for final product

    #remove empty chunks from ngInputGrid
    for chunk in copy.deepcopy(ngInputGrid):
        if ngInputGrid[chunk] == empty_chunk:
            del ngInputGrid[chunk]
            #print('closed chunk: ' + str(chunk))

    #stores 2nd output of gsc. This is a list of chunks that directly border live cells. All these chunks get opened in the second pass.
    ngNewChunks = {}

    for chunk in ngInputGrid: #iterates over every chunk key
        ngOutputGrid[chunk] = []
        for Xcoord in range(8): #iterates over every X coordinate in chunk
            ngOutputGrid[chunk].append([])
            for Ycoord in range(8): #iterates over every Y coordinate
                #find states of surrounding cells
                ngSrndCells, ngAnyNewChunks = get_srnd_cells(get_abs_position(chunk, Xcoord, Ycoord), False, ngInputGrid)
                ngNewChunks |= ngAnyNewChunks
                #find new state of cell and add to ngOutputGrid
                ngOutputGrid[chunk][Xcoord].append(cell_next_day(ngInputGrid[chunk][Xcoord][Ycoord], ngSrndCells))

    #add newly any newly opened chunks to ngInputGrid
    for addition in ngNewChunks:
        ngInputGrid[addition] = copy.deepcopy(ngNewChunks[addition])
        #print('opened chunk: ' + str(addition))

    #Iterate over all cells in newly opened chunks:
    for chunk in ngNewChunks: #iterates over every chunk key
        ngOutputGrid[chunk] = []
        for Xcoord in range(8): #iterates over every X coordinate in chunk
            ngOutputGrid[chunk].append([])
            for Ycoord in range(8): #iterates over every Y coordinate
                #find states of surrounding cells
                ngSrndCells = get_srnd_cells(get_abs_position(chunk, Xcoord, Ycoord), True, ngInputGrid)[0] #glitchy with returned index?
                #find new state of cell and add to ngOutputGrid
                ngOutputGrid[chunk][Xcoord].append(cell_next_day(ngInputGrid[chunk][Xcoord][Ycoord], ngSrndCells))

    end_time = time.perf_counter()
    #print(end_time - start_time)
    return ngOutputGrid





#Coding tip: Local variables do not have underscores and are prefixed by the name of their domain.

#TODO: Optimization: make loops shorter, e.g. use while instead of for. Remove unecessary variables and asserts (such as the one in get_window(). What else?
#TODO speed test
#TODO give iterators similar names for optimization?
#TODO optimize remove int() from position convert functions