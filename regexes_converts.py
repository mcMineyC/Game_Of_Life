#this file houses all of the functions and regexes and such

#TODO remove print lines that are commented out
#TODO check for consistency in cell values and such
#NOTE: prefix all the regex strings with r to avoid escape character issues.
#      idk why this happens but it does. I found a random stackoverflow post
#      that said to do it and it worked. I added it to all current regexes 
#      just make sure when you add new ones you do it too.  Example: r'(\d+)'

import re

digits = ('0', '1', '2', '3', '4', '5', '6', '7', '8', '9')
empty_chunk = [[False] * 8] * 8

#                                      :(name_____):(paragraph_) (grid lines_______)
grid_paragraph_regex = re.compile(r"\n:([^\t\n:]+):([^\t\n]+\n)*((\t[\*\.]{2,}\n)+)")
#This regex seems to operate 100% correctly, but it is a good idea to triple-check it.

grid_regex = re.compile(r'((\t[\*\.]{2,}\n)+)')#findall() works, but adds an extra line to the end. Fixable?

line_regex = re.compile(r'\t?([\*\.]{2,})\n') #only matches plaintext patterns whose live/dead characters are */. #IMPORTANT will not match final line unless final line ends with '\n'

whitespace_regex = re.compile(r'\s')

#                             (comments)    (x     )      (y     )                 (pattern      )
RLE_regex = re.compile(r'^\s?((#.+\n)*)x = ([0-9]+), y = ([0-9]+), rule = B3/S23\n([0-9bo\$\s]+!)\s?$', re.IGNORECASE)
#1st group is all comments, 3rd group is x value, 4 is y value, 5 is RLE
#TODO remove for final porduct
RLE_thing = """#C [[ ZOOM 16 GRID COLOR GRID 192 192 192 COLOR DEADRAMP 255 220 192 COLOR ALIVE 0 0 0 COLOR ALIVERAMP 0 0 0 COLOR DEAD 192 220 255 COLOR BACKGROUND 255 255 255 GPS 10 WIDTH 937 HEIGHT 600 ]]
x = 65, y = 65, rule = B3/S23
27b2o$27bobo$29bo4b2o$25b4ob2o2bo2bo$25bo2bo3bobob2o$28bobobobo$29b2obobo$33bo2$19b2o$20bo8bo$20bobo5b2o$21b2o$35bo$36bo$34b3o2$25bo$25b2o$24bobo4b2o22bo$31bo21b3o$32b3o17bo$34bo17b2o2$45bo$46b2o12b2o$45b2o14bo$3b2o56bob2o$4bo9b2o37bo5b3o2bo$2bo10bobo37b2o3bo3b2o$2b5o8bo5b2o35b2obo$7bo13bo22b2o15bo$4b3o12bobo21bobo12b3o$3bo15b2o22bo13bo$3bob2o35b2o5bo8b5o$b2o3bo3b2o37bobo10bo$o2b3o5bo37b2o9bo$2obo56b2o$3bo14b2o$3b2o12b2o$19bo2$11b2o17bo$12bo17b3o$9b3o21bo$9bo22b2o4bobo$38b2o$39bo2$28b3o$28bo$29bo$42b2o$35b2o5bobo$35bo8bo$44b2o2$31bo$30bobob2o$30bobobobo$27b2obobo3bo2bo$27bo2bo2b2ob4o$29b2o4bo$35bobo$36b2o!"""

#zoom is the most unpredictable value TODO change default values to something mono
default_RLE_comment = '#C [[ ZOOM 16 GRID COLOR GRID 192 192 192 COLOR DEADRAMP 255 220 192 COLOR ALIVE 0 0 0 COLOR ALIVERAMP 0 0 0 COLOR DEAD 192 220 255 COLOR BACKGROUND 255 255 255 GPS 10 WIDTH 937 HEIGHT 600 ]]\n'

comment_regex = re.compile(r'#C \[\[ .+ \]\]')

comment_items_regex = re.compile(r'([A-Z ]+) ([0-9 ]+)|([A-Z][a-z]+)')
#                                 beginning (key____ (value________________ ))+ end
#comment_items_regex = re.compile('#C \[\[ (([A-Z ]+) ([0-9 ]+)|([A-Z][a-z]+) )+\]\]')
# = re.compile('#C \[\[ (([A-Z ]+) ([0-9 ]+) )+\]\]')

greedy_regex = re.compile(r'\$+')


#This function converts RLE to plaintext. It accepts the entire unedited RLE string. It does not preserve comments.
def easy_RLE_to_txt(erttRLE):
    global RLE_regex, whitespace_regex
    erttRLEfound = re.search(RLE_regex, erttRLE)
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
        if char in digits:
            arttInt += char

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
    arttOutputLines = line_regex.findall(arttOutput)
    assert len(arttOutputLines) == arttYBound, str(len(arttOutputLines)) + ' != ' + str(arttYBound)
    for arttLine in arttOutputLines: assert len(arttLine) == arttXBound, str(len(arttLine)) + ' != ' + str(arttXBound)
    return arttOutput[:-1] #remove extra '\n' at the end of str

#converts list matrix to plaintext
def matrix_to_txt(mttGrid):
    #inverts Y axis
    def get_abs_positionY(gapChunk, gapX, gapY, gapYHeight):
        return (gapChunk[0] * 8 + gapX, gapYHeight - (gapChunk[1] * 8 + gapY) -1) #TODO this does not work
    
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
    for mttRow in range(mttHeight): mttOutput.append(['.'] * mttWidth) # needs to copy deeper?
    #mttOutput = [['.'] * mttWidth] * mttHeight
    print(mttHeight, mttWidth)
    #mttOutput = ('.' * (mttRightMost-mttLeftMost+1)*8 + '\n') * (mttUpMost-mttDownMost+1)*8

    #fill in live cells
    for mttChunk in mttGrid:
        for mttX in range(8):
            for mttY in range(8):
                if mttGrid[mttChunk][mttX][mttY]:
                    mttTxtPosition = get_abs_positionY(mttChunk, mttX, mttY, mttHeight)
                    try:
                        mttOutput[mttTxtPosition[0]][mttTxtPosition[1]] = '*'
                    except:
                        print('error! This position does not exist: [%s][%s]' % (mttTxtPosition[0], mttTxtPosition[1]))
    #TODO shave empty edges

    #convert to string
    mttOutputStr = ''
    for mttLine in mttOutput: mttOutputStr += ''.join(mttLine) + '\n'

    return mttOutputStr[:-1] # shave final '\n'




#converts txt to RLE and provides meta-data comments:
def txt_to_RLE(ttrInput):
    global line_regex, default_RLE_comment, greedy_regex
    ttrInput += '\n'
    ttrLines = line_regex.findall(ttrInput)
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
    ttrDollars = greedy_regex.findall(ttrOutputRLE)
    ttrDollarCount = 0
    for ttrInstance in ttrDollars: #finds the longest instance
        if len(ttrInstance) > ttrDollarCount: ttrDollarCount = len(ttrInstance)
    for ttrDollarLen in range(ttrDollarCount, 1, -1): #uses .sub on all $clusters, starting with the longest ones
        ttrDollarSub = re.compile('\\$' * ttrDollarLen)
        ttrOutputRLE = ttrDollarSub.sub('%s$' % ttrDollarLen, ttrOutputRLE)

    ttrOutputHeader = 'x = %s, y = %s, rule = B3/S23\n' % (ttrWidth, ttrHeight)
    return default_RLE_comment + ttrOutputHeader + ttrOutputRLE

#accepts raw RLE and returns a dict of process meta data, hash, etc.
#def raw_RLE_to_processed(rrtpInput):

#accepts entire raw RLE, returns a dict of meta-data from the "#C [[ ZOOM 7 ]]" comment
def comment_to_dict(ctdInput):
    global comment_regex, comment_items_regex, digits
    ctdTheComment = comment_regex.search(ctdInput).group()
    # print(ctdTheComment)
    ctdCommentItems = comment_items_regex.findall(ctdTheComment)
    # print(ctdCommentItems)
    # print()
    #clean up keys and values
    ctdList4Output = []
    for ctdItem in ctdCommentItems:
        ctdList4Output.append([ctdItem[0]]) #deepcopy needed?
        if ctdItem[1] != '':
            ctdList4Output[-1].append([])
            ctdInt = ''
            for ctdChar in ctdItem[1]:
                if ctdChar in digits:
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
    ttmGridLines = line_regex.findall(ttmGrid)
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
    #print(ttmChunkWidth, ttmChunkHeight, ttmCellWidth, ttmCellHeight)

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
                        #print(7 - (ChunkY*8+CellY), ChunkX*8+CellX, ttmGridLines[7 - (ChunkY*8+CellY)][ChunkX*8+CellX])
                    except IndexError:
                        ttmOutGrid[(ChunkX, ChunkY)][CellX][CellY] = False
            #delete chunk if empty
            if ttmOutGrid[(ChunkX, ChunkY)] == empty_chunk:
                del ttmOutGrid[(ChunkX, ChunkY)]
    return ttmOutGrid





#Converts RLE to list matrix pattern
#TODO It probably works, but idk I just plugged two things together
def RLE_to_matrix(rle):
    return txt_to_matrix(easy_RLE_to_txt(rle))

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




#This is from the top of CGOL_search.py
def str_match(smInput1, smInput2): #TODO remove for finished product. only for testing
    smOutput = ''
    for smChar1, smChar2 in zip(smInput1, smInput2):
        if smChar1 == smChar2:
            smOutput += smChar1
        else:
            smOutput += '_'
    return smOutput

def append_to_py_dict(atpdFileName, atpdKey, atpdValue): #TODO probably delete this
    atpdFileObjct = open(atpdFileName, 'r')
    atpdFileContents = dict(atpdFileObjct.read())
    atpdFileObjct.close()
    atpdFileContents[atpdKey] = atpdValue
    atpdFileObjct = open(atpdFileName, 'w')
    atpdFileObjct.write(atpdFileContents)
    atpdFileObjct.close()

'''
#test; TODO delete later
from CGOL_game_runner import next_gen
import time
from CGOL_test_patterns import master_library

day = 0
daGrid = master_library['2-engine Cordership']
while day != 550:
    print(day)
    pro_print_grid(daGrid, (0, 3), (8, -2))
    #time.sleep(0.1)
    daGrid = next_gen(daGrid)
    day += 1
'''
"""
from CGOL_test_patterns import master_library

print(matrix_to_txt(master_library['glider']))
#"""
