#This program searches the lexicon for patterns and saves them to the master library.
#It also accepts a "human" grid and converts it the the "computer" format.

#TODO test run everything in search and txt convert

import re, json, pprint, copy, hashlib

def MD5hash(MD5Input):
    return hashlib.md5(MD5Input.encode()).hexdigest()

#move me lower down later
def str_match(smInput1, smInput2):
    smOutput = ''
    for smChar1, smChar2 in zip(smInput1, smInput2):
        if smChar1 == smChar2:
            smOutput += smChar1
        else:
            smOutput += '_'
    return smOutput

lexicon_file = open("Game_Of_Life/lexicon.txt", 'r')
lexicon_str = lexicon_file.read()
lexicon_file.close()

#                                      :(name_____):(paragraph_) (grid lines_______)
grid_paragraph_regex = re.compile("""\n:([^\t\n:]+):([^\t\n]+\n)*((\t[\*\.]{2,}\n)+)""")
#This regex seems to operate 100% correctly, but it is a good idea to triple-check it.

grid_regex = re.compile('((\t[\*\.]{2,}\n)+)')#findall() works, but adds an extra line to the end. Fixable?

line_regex = re.compile('\t?([\*\.]{2,})\n') #only matches plaintext patterns whose live/dead characters are */.

whitespace_regex = re.compile('\s')

#                             (comments)    (x     )      (y     )                 (pattern      )
RLE_regex = re.compile('''^\s?((#.+\n)*)x = ([0-9]+), y = ([0-9]+), rule = B3/S23\n([0-9bo\$\s]+!)\s?$''', re.IGNORECASE)
#1st group is all comments, 3rd group is x value, 4 is y value, 5 is RLE
RLE_thing = """#C [[ ZOOM 16 GRID COLOR GRID 192 192 192 COLOR DEADRAMP 255 220 192 COLOR ALIVE 0 0 0 COLOR ALIVERAMP 0 0 0 COLOR DEAD 192 220 255 COLOR BACKGROUND 255 255 255 GPS 10 WIDTH 937 HEIGHT 600 ]]
x = 65, y = 65, rule = B3/S23
27b2o$27bobo$29bo4b2o$25b4ob2o2bo2bo$25bo2bo3bobob2o$28bobobobo$29b2obobo$33bo2$19b2o$20bo8bo$20bobo5b2o$21b2o$35bo$36bo$34b3o2$25bo$25b2o$24bobo4b2o22bo$31bo21b3o$32b3o17bo$34bo17b2o2$45bo$46b2o12b2o$45b2o14bo$3b2o56bob2o$4bo9b2o37bo5b3o2bo$2bo10bobo37b2o3bo3b2o$2b5o8bo5b2o35b2obo$7bo13bo22b2o15bo$4b3o12bobo21bobo12b3o$3bo15b2o22bo13bo$3bob2o35b2o5bo8b5o$b2o3bo3b2o37bobo10bo$o2b3o5bo37b2o9bo$2obo56b2o$3bo14b2o$3b2o12b2o$19bo2$11b2o17bo$12bo17b3o$9b3o21bo$9bo22b2o4bobo$38b2o$39bo2$28b3o$28bo$29bo$42b2o$35b2o5bobo$35bo8bo$44b2o2$31bo$30bobob2o$30bobobobo$27b2obobo3bo2bo$27bo2bo2b2ob4o$29b2o4bo$35bobo$36b2o!"""

#zoom is the most unpredictable value
default_RLE_comment = '#C [[ ZOOM 16 GRID COLOR GRID 192 192 192 COLOR DEADRAMP 255 220 192 COLOR ALIVE 0 0 0 COLOR ALIVERAMP 0 0 0 COLOR DEAD 192 220 255 COLOR BACKGROUND 255 255 255 GPS 10 WIDTH 937 HEIGHT 600 ]]\n'
prefered_RLE_comment = ''

greedy_regex = re.compile('\$+')


#def pattern conversion functions

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
    global line_regex
    arttRLE = arttRLE.lower()
    arttDigits = ('0', '1', '2', '3', '4', '5', '6', '7', '8', '9')
    arttOutput = ''
    arttInt = ''
    arttCharsInLine = 0

    for char in arttRLE:
        if  char in ('\n', '\t', ' '):
            continue
        if char in arttDigits:
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

#TODO make function that converts matrix to txt

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
    print('ttrDollarCount == ' + str(ttrDollarCount))
    for ttrDollarLen in range(ttrDollarCount, 1, -1): #uses .sub on all $clusters, starting with the longest ones
        ttrDollarSub = re.compile('\$' * ttrDollarLen)
        ttrOutputRLE = ttrDollarSub.sub('%s$' % ttrDollarLen, ttrOutputRLE)

    ttrOutputHeader = 'x = %s, y = %s, rule = B3/S23\n' % (ttrWidth, ttrHeight)
    return default_RLE_comment + ttrOutputHeader + ttrOutputRLE


junk_var = easy_RLE_to_txt(RLE_thing)
junk_var2 = txt_to_RLE(junk_var)
print(RLE_thing)
print(junk_var)
print()
print(junk_var2)
print(RLE_thing == junk_var2)
#print(str_match(RLE_thing, junk_var2))

#TODO make function that accepts raw RLE and returns a dict of process meta data, hash, etc.
    #TODO make function that accepts entire RLE string, and converts the comments into a dictionary with values.
#TODO make function that accepts processed data and returns a raw RLE string (including comments)





#Converts plaintext pattern to list matrix pattern
def txt_to_matrix(ttmGrid):
    global line_regex

    #break up grid into lines
    ttmGridLines = line_regex.findall(ttmGrid)

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
                    #print('\t\t' + str((ChunkX, ChunkY, CellX, CellY)))
                    try:
                        #                                                       7- is used because Y0 is at the bottom of the txt
                        ttmOutGrid[(ChunkX, ChunkY)][CellX][CellY] = ttmGridLines[7 - (ChunkY*8+CellY)][ChunkX*8+CellX]
                    except IndexError:
                        ttmOutGrid[(ChunkX, ChunkY)][CellX][CellY] = '.'
    return ttmOutGrid
#TODO output is inverted (on y axis), needs fixing #I think I fixed this?


#stolen from CGOL_game_runner
#accepts grid and window for camera, prints grid.
def pro_print_grid(ppgGrid, ppgUpLeft, ppgDownRight):
    ppgOutput = ''
    #print(get_chunk_window(ppgUpLeft, ppgDownRight))
    for ppgChunkRow in get_chunk_window(ppgUpLeft, ppgDownRight):
        #print('\t\tppg did something!!')
        for ppgCellRow in range(7, -1, -1):
            #print('\t\t\tppg did something!!')
            for ppgChunk in ppgChunkRow:
                #print('\t\t\t\tppg did something!!')
                for ppgX in range(8):
                    #print('\t\t\t\t\tppg did something!!')
                    if ppgChunk in ppgGrid:
                        ppgOutput = ppgOutput + cell_convert(ppgGrid[ppgChunk][ppgX][ppgCellRow], '[]', '<>')
                    else:
                        ppgOutput = ppgOutput + cell_convert('.', '[]', '::')
            ppgOutput = ppgOutput + '\n'

    print(ppgOutput)# + '\n^above is the pattern^')

#accepts state (live or dead) and returns state as single character based on the two characters given.
def cell_convert(ccState, ccLive, ccDead):
    if ccState == '*':
        return ccLive
    elif ccState == '.':
        return ccDead
    else:
        raise Exception("cell_convert() given invalid ccState parameter: %s\nccState must equal either 'live' or 'dead'" % ccState)

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




#create JSON lexicon

"""
test_var = txt_to_matrix('\t***\n\t..*\n\t.*.\n')
print(test_var)
pro_print_grid(test_var, (-1, 1), (1, -1))
"""

'''
#store contents of lexicon.txt to lexicon_array.json with proper formatting

#search lexicon
lexicon_paragraphs = grid_paragraph_regex.findall(lexicon_str)

#convert to desired Python format
json_master_library = {}
for paragraph in lexicon_paragraphs:
    json_master_library[paragraph[0]] = paragraph[2]#use convert_format() once it is finished

#write to lexicon_array.json
json_str = json.dumps(json_master_library)
json_file = open("Game_Of_Life/lexicon_array.json", 'w')
json_file.write(json_str)
json_file.close()
'''
#TODO remove print lines that are commented out
#TODO check for consistency in cell values and such


master_dict = {'#hash':
                    {'hash': '#hash',
                    'name': 'glider',
                    'X_bound': 3,
                    'Y_bound': 3,
                    'RLE_code': 'bo$2bo$3o!',
                    'comment_dict': {
                        'zoom': 7, 'color deadramp': [255, 220, 192], 'grid color grid': [192, 192, 192]
                        }
                    }
                }