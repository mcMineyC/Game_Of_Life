#this file houses all of the functions and regexes and such

#TODO remove print lines that are commented out
#TODO check for consistency in cell values and such
#NOTE: prefix all the regex strings with r to avoid escape character issues.
#      idk why this happens but it does. I found a random stackoverflow post
#      that said to do it and it worked. I added it to all current regexes
#      just make sure when you add new ones you do it too.  Example: r'(\d+)'

#NOTE do not include a newline at the end of a custom CGOL comment

import re
from lib import regexes as r
# Functions that convert pattern types:
#This function converts RLE to plaintext. It accepts the entire unedited RLE string. It does not preserve comments.
def easy_RLE_to_txt(erttRLE):
    global RLE_regex, whitespace_regex
    erttRLEfound = re.search(r.RLE_regex, erttRLE)
    if erttRLEfound != None:
        erttGroups = erttRLEfound.group(3, 4, 5)
        #remove whitespace
        erttRLEnoWS = ''
        for char in erttGroups[2]:
            if not char in ('\n', '\t', ' '):
                erttRLEnoWS = erttRLEnoWS + char
        return advanced_RLE_to_txt(int(erttGroups[0]), int(erttGroups[1]), erttRLEnoWS)


#This function converts RLE to plaintext. It accepts the pattern RLE, the X bound of the pattern, and the Y bound.
def advanced_RLE_to_txt(arttXBound, arttYBound, arttRLE):
    global line_regex, digits
    arttRLE = arttRLE.lower()
    arttOutput = ''
    arttInt = ''
    arttCharsInLine = 0

    for char in arttRLE:
        if  char in ('\n', '\t', ' '):
            continue
        if char in r.digits:
            arttInt += str(char)

        elif char == '$':
            if arttInt == '': arttInt = '1'
            for arttLine in range(int(arttInt)):
                arttOutput += '.' * (arttXBound-arttCharsInLine) + '\n'
                arttCharsInLine = 0
                arttInt = ''

        elif char == '!':
            arttOutput += '.' * (arttXBound-arttCharsInLine) + '\n'
            break

        else:# o is live, b is dead. Anything that is not b will be treated as o.
            arttState = '.' if char == 'b' else '*'
            if arttInt == '': arttInt = '1'
            arttOutput += arttState * int(arttInt)
            arttCharsInLine += int(arttInt)
            arttInt = ''

    #ensure that output is not flawed via asserts
    arttOutputLines = r.line_regex.findall(arttOutput)
    assert len(arttOutputLines) == arttYBound, str(len(arttOutputLines)) + ' != ' + str(arttYBound)
    for arttLine in arttOutputLines: assert len(arttLine) == arttXBound, str(len(arttLine)) + ' != ' + str(arttXBound)
    return arttOutput[:-1] #remove extra '\n' at the end of str


#converts list matrix to plaintext
def matrix_to_txt(mttGrid):
    #find bounds of grid by checking all chunks and recording the furthest ones
    mttUpMost = tuple(mttGrid.keys())[0][1]
    mttDownMost = tuple(mttGrid.keys())[0][1]
    mttLeftMost = tuple(mttGrid.keys())[0][0]
    mttRightMost = tuple(mttGrid.keys())[0][0]
    for mttChunk in mttGrid:
        if mttChunk[1] > mttUpMost: mttUpMost = mttChunk[1]
        elif mttChunk[1] < mttDownMost: mttDownMost = mttChunk[1]
        if mttChunk[0] > mttRightMost: mttRightMost = mttChunk[0]
        elif mttChunk[0] < mttLeftMost: mttLeftMost = mttChunk[0]
    mttHeight = (mttUpMost-mttDownMost+1)*8
    mttWidth = (mttRightMost-mttLeftMost+1)*8

    #create empty plaintext grid
    mttOutput = []
    for mttRow in range(mttWidth): mttOutput.append(['.'] * mttHeight) # X and Y got switched?

    #fill in live cells
    for mttChunk in mttGrid:
        #compensates chunk positions in mttOutput.
        mttZeroedChunk = (mttChunk[0] - mttDownMost, mttChunk[1] - mttLeftMost)
        for mttX in range(8):
            for mttY in range(8):
                if mttGrid[mttChunk][mttX][mttY]:
                    try: #overshoots index by 1? #TODO remove try
                        mttOutput[mttZeroedChunk[0] * 8 + mttX][mttZeroedChunk[1] * 8 + mttY] = '*' #basically uses abs pos.
                    except IndexError:
                        print('IndexError. These coords out of range: %s %s' % (mttChunk[0] * 8 + mttX, mttChunk[1] * 8 + mttY))
                        print(mttChunk, mttZeroedChunk, mttX, mttY)

    #TODO shave empty edges

    #convert to string.
    mttOutputStr = ''
    for mttY in range(len(mttOutput[0])-1, -1, -1): #inverts Y
        for mttX in range(len(mttOutput)):
            mttOutputStr += mttOutput[mttX][mttY]
        mttOutputStr += '\n'

    return mttOutputStr[:-1] # shave final '\n'


#converts txt to RLE and provides meta-data comments:
def txt_to_RLE(ttrInput, ttrComment=r.default_RLE_comment): #TODO accept comment to use in RLE instead of default.
    global line_regex, greedy_regex
    ttrInput += '\n'
    ttrLines = r.line_regex.findall(ttrInput)
    #get dimensions of txt
    ttrHeight = len(ttrLines)
    ttrWidth = len(ttrLines[0])
    #check if each line is equal in length
    for ttrLine in ttrLines: assert len(ttrLine) == ttrWidth, str(len(ttrLine)) + ' != ' + str(ttrWidth)

    ttrOutputRLE = ''
    for ttrLine in ttrLines:
        #ttrOutputRLE.append('')
        ttrRun = [ttrLine[0], 0]
        for ttrCell in ttrLine:
            if ttrCell == ttrRun[0]:
                ttrRun[1] += 1 #counts how many conxecutive chars are present
            else:#TODO fix for when ttrRun[0] == ''# probably unecessary now that line is: ttrRun = [ttrLine[0], 0]
                ttrState = 'b' if ttrRun[0] == '.' else 'o'
                ttrRunCount = '' if ttrRun[1] == 1 else str(ttrRun[1])
                ttrOutputRLE += ttrRunCount + ttrState
                ttrRun = [ttrCell, 1]
        if ttrRun[0] == '*':
            ttrRunCount = '' if ttrRun[1] == 1 else str(ttrRun[1])
            ttrOutputRLE += ttrRunCount + 'o'
        ttrOutputRLE += '$'
    ttrOutputRLE = ttrOutputRLE[:-1] + '!' #replace final char with ! instead of $

    #search for clusters of $ (e.g. '...$$$...') and convert to '...3$...'
    ttrDollars = r.greedy_regex.findall(ttrOutputRLE)
    ttrDollarCount = 0
    for ttrInstance in ttrDollars: #finds the longest instance
        if len(ttrInstance) > ttrDollarCount: ttrDollarCount = len(ttrInstance)
    for ttrDollarLen in range(ttrDollarCount, 1, -1): #uses .sub on all $clusters, starting with the longest ones
        ttrDollarSub = re.compile('\\$' * ttrDollarLen)
        ttrOutputRLE = ttrDollarSub.sub('%s$' % ttrDollarLen, ttrOutputRLE)

    ttrOutputHeader = 'x = %s, y = %s, rule = B3/S23\n' % (ttrWidth, ttrHeight)
    return ttrComment + ttrOutputHeader + ttrOutputRLE


#accepts entire raw RLE, returns a dict of meta-data from the "#C [[ ZOOM 7 ]]" comment
def comment_to_dict(ctdInput):
    global comment_regex, comment_items_regex, digits
    ctdTheComment = r.comment_regex.search(ctdInput).group()
    ctdCommentItems = r.comment_items_regex.findall(ctdTheComment)

    #clean up keys and values
    ctdList4Output = []
    for ctdItem in ctdCommentItems:
        ctdList4Output.append([ctdItem[0]]) #deepcopy needed?
        if ctdItem[1] != '':
            ctdList4Output[-1].append([])
            ctdInt = ''
            for ctdChar in ctdItem[1]:
                if ctdChar in r.digits:
                    ctdInt += ctdChar
                else:
                    ctdList4Output[-1][1].append(int(ctdInt))
                    ctdInt = ''
        else:
            ctdList4Output.append([ctdItem[0], ctdItem[2]])

    if ctdList4Output[0][0][0] == ' ': #clip off leading space of first key
        ctdList4Output[0][0] = ctdList4Output[0][0][1:]
    #Lowercase the keys
    for ctdItem in ctdList4Output:
        ctdItem[0] = ctdItem[0].lower()
        ctdItem[0] = ctdItem[0].replace(' ', '_') #remove spaces from values
        if len(ctdItem[1]) == 1:        #convert single item lists to items eg. numbers
            ctdItem[1] = ctdItem[1][0]

    ctdOutput = {}
    for ctdItem in ctdList4Output:
        ctdOutput[ctdItem[0]] = ctdItem[1]
    return ctdOutput


#Converts plaintext pattern to list matrix pattern
def txt_to_matrix(ttmGrid):
    global line_regex, empty_chunk
    ttmGrid += '\n'#regex will not catch final line if it does not end with '\n'

    #break up grid into lines
    ttmGridLines = r.line_regex.findall(ttmGrid)
    ttmGridLines.reverse()

    #get grid specs
    ttmCellWidth = len(ttmGridLines[0]) #If this line raises an error, it is because cfGridLines == []. cfGrid is invalid and likely missing \t or \n
    ttmCellHeight = len(ttmGridLines)
    if ttmCellWidth % 8 == 0:
        ttmChunkWidth = ttmCellWidth // 8
    else:
        ttmChunkWidth = ttmCellWidth // 8 + 1
    if ttmCellHeight % 8 == 0:
        ttmChunkHeight = ttmCellHeight // 8
    else:
        ttmChunkHeight = ttmCellHeight // 8 + 1

    #convert to dictionary
    ttmOutGrid = {}
    for ChunkY in range(ttmChunkHeight):
        for ChunkX in range(ttmChunkWidth):
            ttmOutGrid[(ChunkX, ChunkY)] = [[None for _ in range(8)] for _ in range(8)] #Suggested by Copilot
            #ttmOutGrid[(ChunkX, ChunkY)] = copy.deepcopy([[None]*8]*8) #my design. reference glitches?
            for CellY in range(8):
                for CellX in range(8):
                    try:
                        #                                                       7- is used because Y0 is at the bottom of the txt
                        #ttmOutGrid[(ChunkX, ChunkY)][CellX][CellY] = (True if ttmGridLines[7 - (ChunkY*8+CellY)][ChunkX*8+CellX]=='*' else False) #old code. fixed?
                        ttmOutGrid[(ChunkX, ChunkY)][CellX][CellY] = (True if ttmGridLines[ChunkY*8+CellY][ChunkX*8+CellX] == '*' else False)
                    except IndexError:
                        ttmOutGrid[(ChunkX, ChunkY)][CellX][CellY] = False
            #delete chunk if empty
            if ttmOutGrid[(ChunkX, ChunkY)] == r.empty_chunk:
                del ttmOutGrid[(ChunkX, ChunkY)]
    return ttmOutGrid


#Converts RLE to list matrix pattern
def RLE_to_matrix(rtmInput):
    return txt_to_matrix(easy_RLE_to_txt(rtmInput))

#Converts list-matrix to RLE and adds default comment line
def matrix_to_RLE(mtrMatrix, mtrComment=r.default_RLE_comment):
    return txt_to_RLE(matrix_to_txt(mtrMatrix), ttrComment=mtrComment)


#Other functions:


#Permanantly borrowed™ from CGOL_game_runner
#accepts grid and window for camera, prints grid to terminal.
def pro_print_grid(ppgGrid, ppgUpLeft, ppgDownRight):
    ppgOutput = ''
    for ppgChunkRow in get_chunk_window(ppgUpLeft, ppgDownRight):
        for ppgCellRow in range(7, -1, -1):
            for ppgChunk in ppgChunkRow:
                for ppgX in range(8):
                    if ppgChunk in ppgGrid:
                        ppgOutput = ppgOutput + ('[]' if ppgGrid[ppgChunk][ppgX][ppgCellRow] else '<>')
                    else:
                        ppgOutput += '::'

            ppgOutput += '\n'
    print(ppgOutput)


#This is sort of a combo of matrix_to_txt and pro_print_grid. It accepts a list-matrix, the coord of a chunk (camera window position), and
#returns a 64x64 plaintext grid.
def grid_to_string(gtsGrid, gtsUpLeft, gtsDownRight):
    gtsOutput = ''
    for gtsChunkRow in get_chunk_window(gtsUpLeft, gtsDownRight):
        for gtsCellRow in range(7, -1, -1):
            for gtsChunk in gtsChunkRow:
                for gtsX in range(8):
                    if gtsChunk in gtsGrid:
                        gtsOutput = gtsOutput + ('1' if gtsGrid[gtsChunk][gtsX][gtsCellRow] else '0') # Loaded chunks
                    else:
                        gtsOutput += '0' # Unloaded chunk

            gtsOutput += '\n'
    return gtsOutput

# WIP CENTERED THING THAT WON"T WORK
# def grid_to_string_centered(grid, coordinate, image_size=64):
#     center_chunk = (coordinate[0] // 8, coordinate[1] // 8)
#     center_chunk_offset = (coordinate[0] % 8, coordinate[1] % 8)
#     chunk_count = (image_size // 8) + 2
#     top_left_chunk = ((coordinate[0] // 8) - (chunk_count // 2), (coordinate[1] // 8) + (chunk_count // 2))
#     bottom_right_chunk = ((coordinate[0] // 8) + (chunk_count // 2), (coordinate[1] // 8) - (chunk_count // 2))
#     print(top_left_chunk, bottom_right_chunk)
#     gtsOutput = ''
#     for gtsChunkRow in range(top_left_chunk[1], bottom_right_chunk[1]-1, -1):
#         for gtsCellRow in range(7, -1, -1):
#             for gtsChunk in range(top_left_chunk[0], bottom_right_chunk[0]):
#                 for gtsX in range(8):
#                     if (gtsChunk, gtsChunkRow) in grid:
#                         gtsOutput = gtsOutput + ('1' if grid[(gtsChunk, gtsChunkRow)][gtsX][gtsCellRow] else '0') # Loaded chunks
#                     else:
#                         gtsOutput += '0' # Unloaded chunk

#             gtsOutput += '\n'
#     print(gtsOutput)
#     return gtsOutput


#accepts coordinates of two chunks and returns all chunks within the window.
def get_chunk_window(gcwUpLeft, gcwDownRight):
    assert type(gcwUpLeft) in (tuple, list) and len(gcwUpLeft) == 2, 'gcw parameter gcwUpLeft passed invalid argument' #TODO remove asserts for efficiency
    assert type(gcwDownRight) in (tuple, list) and len(gcwDownRight) == 2, 'gcw parameter gcwDownRight passed invalid argument'
    gcwOutput = []
    for gcwY, gcwCounter in zip(range(gcwUpLeft[1], gcwDownRight[1]-1, -1), range(99)): #idk why range(99) is used. shrug.
        gcwOutput.append([])
        for gcwX in range(gcwUpLeft[0], gcwDownRight[0]+1):
            gcwOutput[gcwCounter].append((gcwX, gcwY))
    assert gcwOutput != []
    return gcwOutput
