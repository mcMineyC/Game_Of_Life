#This program searches the lexicon for patterns and saves them to the master library.
#It also accepts a "human" grid and converts it the the "computer" format.

#TODO code func that converts RLE to txt
#TODO test run everything in search and txt convert

import re, json, pprint, copy

lexicon_file = open("Game_Of_Life/lexicon.txt", 'r')
lexicon_str = lexicon_file.read()
lexicon_file.close()

#                                      :(name_____):(paragraph_) (grid lines_______)
grid_paragraph_regex = re.compile("""\n:([^\t\n:]+):([^\t\n]+\n)*((\t[\*\.]{2,}\n)+)""")
#This regex seems to operate 100% correctly, but it is a good idea to triple-check it.

grid_regex = re.compile('((\t[\*\.]{2,}\n)+)')#findall() works, but adds an extra line to the end. Fixable?

line_regex = re.compile('\t([\*\.]{2,})\n') #only matches patterns whose live/dead characters are */.


#Converts plaintext pattern to list matrix pattern
def convert_format(cfGrid):
    global line_regex

    #break up grid into lines
    cfGridLines = line_regex.findall(cfGrid)
    print(cfGridLines)

    #get grid specs
    cfCellWidth = len(cfGridLines[0]) #If this line raises an error, it is because cfGridLines == []. cfGrid is invalid and likely missing \t or \n
    cfCellHeight = len(cfGridLines)
    if cfCellWidth % 8 == 0:
        cfChunkWidth = cfCellWidth // 8
    else:
        cfChunkWidth = cfCellWidth // 8 + 1
    if cfCellHeight % 8 == 0:
        cfChunkHeight = cfCellHeight // 8
    else:
        cfChunkHeight = cfCellHeight // 8 + 1

    print(cfChunkWidth, cfChunkHeight, cfCellWidth, cfCellHeight)

    #convert to dictionary
    cfOutGrid = {}
    for ChunkRowY in range(cfChunkHeight):
        for ChunkX in range(cfChunkWidth):
            cfOutGrid[(ChunkX, ChunkRowY)] = [[None for _ in range(8)] for _ in range(8)] #Suggested by Copilot
            #cfOutGrid[(ChunkX, ChunkRowY)] = copy.deepcopy([[None]*8]*8) #my design. reference glitches?
            for CellRowY in range(8):
                for CellX in range(8):
                    try:
                        cfOutGrid[(ChunkX, ChunkRowY)][CellX][CellRowY] = cfGridLines[ChunkRowY*8+CellRowY][ChunkX*8+CellX]
                    except IndexError:
                        cfOutGrid[(ChunkX, ChunkRowY)][CellX][CellRowY] = '.'
                        #print(ChunkX, ChunkRowY)
    return cfOutGrid
#TODO output is inverted, needs fixing


#stolen from CGOL_game_runner
#accepts grid and window for camera, prints grid.
def pro_print_grid(ppgGrid, ppgUpLeft, ppgDownRight):
    ppgOutput = ''
    for ppgChunkRow in get_chunk_window(ppgUpLeft, ppgDownRight):
        for ppgCellRow in range(7, -1, -1):
            for ppgChunk in ppgChunkRow:
                for ppgX in range(8):
                    if ppgChunk in ppgGrid:
                        ppgOutput = ppgOutput + cell_convert(ppgGrid[ppgChunk][ppgX][ppgCellRow], '[]', '<>')
                    else:
                        ppgOutput = ppgOutput + cell_convert('.', '[]', '::')
            ppgOutput = ppgOutput + '\n'

    print(ppgOutput)

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
    gcwOutput = []
    for gcwY, gcwCounter in zip(range(gcwUpLeft[1], gcwDownRight[1]-1, -1), range(99)):
        gcwOutput.append([])
        for gcwX in range(gcwUpLeft[0], gcwDownRight[0]+1):#correct?
            gcwOutput[gcwCounter].append((gcwX, gcwY))
    return gcwOutput




test_var = convert_format('\t**.......\n\t.*.......\n\t.*.*.....\n\t..**.....\n\t.....**..\n\t.....*.*.\n\t.......*.\n\t.......**\n')
print(test_var)
pro_print_grid(test_var, (3, 0), (0, 3))


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