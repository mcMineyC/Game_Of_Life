from PIL import Image, ImageDraw
import copy, CGOL_test_patterns
from regexes_converts import RLE_to_matrix
from CGOL_test_patterns import master_library

# blank = [[False] * 64] * 64
# blank = copy.deepcopy(blank)


tru = (255,255,255)
fal = (000,000,000)

#Converts relative position to absolute position. accepts X and Y of chunk, then X and Y of cell in chunk.
def get_abs_position(gapChunk, gapX, gapY):
    return (int(gapChunk[0]) * 8 + int(gapX), int(gapChunk[1]) * 8 + int(gapY))

def get_chunk_window_list(gcwUpLeft, gcwDownRight): #TODO return single list instead of list matrix
    assert type(gcwUpLeft) in (tuple, list) and len(gcwUpLeft) == 2, 'gcw parameter gcwUpLeft passed invalid argument' #TODO remove asserts for efficiency
    assert type(gcwDownRight) in (tuple, list) and len(gcwDownRight) == 2, 'gcw parameter gcwDownRight passed invalid argument'
    gcwOutput = []
    for gcwY in range(gcwUpLeft[1], gcwDownRight[1]-1, -1):
        for gcwX in range(gcwUpLeft[0], gcwDownRight[0]+1):
            gcwOutput.append((gcwX, gcwY))
    assert gcwOutput != []
    return gcwOutput


def pro_print_grid_image(ppgGrid, ppgDownLeft):
    i = Image.new("RGB", (64, 64))
    d = ImageDraw.Draw(i)
    d.rectangle([0, 0, 64, 64], fill="#ff0000")

    for ppgChunk, ppgCamChunk in zip(get_chunk_window_list((ppgDownLeft[0], ppgDownLeft[1]+7), (ppgDownLeft[0]+7, ppgDownLeft[1])), get_chunk_window_list((0, 7), (7, 0))):
        for ppgY in range(8):
                for ppgX in range(8):
                    tX,tY = get_abs_position(ppgCamChunk, ppgX, ppgY)

                    if ppgChunk in ppgGrid:
                        ppgCell = (tru if ppgGrid[ppgChunk][ppgX][ppgY] else fal)

                    else:
                        ppgCell = fal

                    i.putpixel((tX, 63-tY), ppgCell)

    return i



def matrixToImage(matrix, aliveColor, deadColor): #TODO this is probably trash
    i = Image.new("RGB", (64, 64))
    d = ImageDraw.Draw(i)
    d.rectangle([0, 0, 64, 64], fill="#000000")
    for y in range(0, len(matrix)):
        for x in range(0, len(matrix[y])):
            i.putpixel((x, y), (tru if matrix[x][y] else fal))
    return i


#im = matrixToImage(CGOL_test_patterns.master_library["glider"][(0,0)],tru,fal)
im = pro_print_grid_image(master_library['snark loop'], (0, 1))
# i = Image.new("RGB", (64, 64))
# d = ImageDraw.Draw(i)
# d.rectangle([0, 0, 64, 64], fill="#ff0000")
# i.putpixel((0, 63-0), fal)

im.save("Snark.png", "PNG")