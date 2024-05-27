from PIL import Image, ImageDraw
import copy, CGOL_test_patterns
from CGOL_game_runner import get_abs_position

# blank = [[False] * 64] * 64
# blank = copy.deepcopy(blank)

tru = (255,255,255)
fal = (000,000,000)

#accepts position of lower left chunk of camera window. returns x and y absolute values
def camera_difference(cdInputChunk):
    return (cdInputChunk[0]*8, cdInputChunk[1]*8)

def pro_print_grid_image(ppgGrid, ppgUpLeft, ppgDownRight):
    i = Image.new("RGB", (64, 64))
    d = ImageDraw.Draw(i)
    d.rectangle([0, 0, 64, 64], fill="#ff0000")
    # print(get_chunk_window(ppgUpLeft, ppgDownRight))
    for ppgChunk in get_chunk_window(ppgUpLeft, ppgDownRight):
        for ppgCellRow in range(8):
                for ppgX in range(8):
                    tX,tY = get_abs_position(ppgChunk, ppgX, ppgCellRow)
                    difference = (16, 16)
                    final = (tX+difference[0], tY+difference[1])
                    inv = (final[0], 63-final[1])
                    #difference = camera_difference((1, 2))#put camera position here
                    
                    if ppgChunk in ppgGrid:
                        #inverted_cell_row = 7-ppgCellRow
                        i.putpixel(inv, (tru if ppgGrid[ppgChunk][ppgX][ppgCellRow] else fal))
                    else:
                        i.putpixel(inv, fal)

    return i


#accepts coordinates of two chunks and returns all chunks within the window.
def get_chunk_window(gcwUpLeft, gcwDownRight):
    assert type(gcwUpLeft) in (tuple, list) and len(gcwUpLeft) == 2, 'gcw parameter gcwUpLeft passed invalid argument'
    assert type(gcwDownRight) in (tuple, list) and len(gcwDownRight) == 2, 'gcw parameter gcwDownRight passed invalid argument'
    gcwOutput = []
    for gcwY, gcwCounter in zip(range(gcwUpLeft[1], gcwDownRight[1]-1, -1), range(99)):
        for gcwX in range(gcwUpLeft[0], gcwDownRight[0]+1):#correct?
            gcwOutput.append((gcwX, gcwY))
    assert gcwOutput != []
    return gcwOutput

def matrixToImage(matrix, aliveColor, deadColor):
    i = Image.new("RGB", (64, 64))
    d = ImageDraw.Draw(i)
    d.rectangle([0, 0, 64, 64], fill="#000000")
    for y in range(0, len(matrix)):
        for x in range(0, len(matrix[y])):
            i.putpixel((x, y), (tru if matrix[x][y] else fal))
    return i

#im = matrixToImage(CGOL_test_patterns.master_library["glider"][(0,0)],tru,fal)
im = pro_print_grid_image(CGOL_test_patterns.master_library["glider"], (0, 7), (7, 0))
# i = Image.new("RGB", (64, 64))
# d = ImageDraw.Draw(i)
# d.rectangle([0, 0, 64, 64], fill="#ff0000")
# i.putpixel((0, 63-0), fal)

im.save("glider.png", "PNG")