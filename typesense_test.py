import typesense, json

client = typesense.Client({
    'nodes': [{
        'host': '192.168.30.36',
        'port': '8108',
        'protocol': 'http'
    }],
    'api_key': 'xyz123',
    'connection_timeout_seconds': 2
})
lexicon_schema = {
  'name': 'lexicon',
  'fields': [
    {'name': 'id', 'type': 'string', 'facet': True},
    {'name': 'hash', 'type': 'string'},
    {'name': 'name', 'type': 'string' },
  ],
}

# client.collections['lexicon'].delete()

try:
    client.collections.create(lexicon_schema)
except typesense.exceptions.ObjectAlreadyExists:
    print('Collection already exists, skipping creation')

lexi = open('lexicon.jsonl', 'r')
client.collections['lexicon'].documents.import_(lexi.read().encode('utf-8'), {'action': 'upsert'})
lexi.close()

new_num = client.collections['lexicon'].retrieve()['num_documents']

print("Lexicon imported with", new_num, "documents.")

sparams = {
    'q': input("What do you want to generate? "),
    'query_by': 'name'
}
results = client.collections['lexicon'].documents.search(sparams)
doc = results["hits"][0]["document"]
print("Showing pattern "+doc["name"])


from PIL import Image, ImageDraw
import copy, CGOL_test_patterns
from CGOL_game_runner import get_abs_position
from regexes import RLE_to_matrix
from snark import snarky

# blank = [[False] * 64] * 64
# blank = copy.deepcopy(blank)


tru = (255,255,255)
fal = (000,000,000)


def pro_print_grid_image(ppgGrid, ppgDownLeft):
    i = Image.new("RGB", (64, 64))
    d = ImageDraw.Draw(i)
    d.rectangle([0, 0, 64, 64], fill="#ff0000")

    for ppgChunk, ppgCamChunk in zip(get_chunk_window((ppgDownLeft[0], ppgDownLeft[1]+7), (ppgDownLeft[0]+7, ppgDownLeft[1])), get_chunk_window((0, 7), (7, 0))):
        for ppgY in range(8):
                for ppgX in range(8):

                    tX,tY = get_abs_position(ppgCamChunk, ppgX, ppgY)

                    if ppgChunk in ppgGrid:
                        ppgCell = (tru if ppgGrid[ppgChunk][ppgX][ppgY] else fal)

                    else:
                        ppgCell = fal

                    i.putpixel((tX, 63-tY), ppgCell)

    return i


#accepts coordinates of two chunks and returns all chunks within the window.
def get_chunk_window(gcwUpLeft, gcwDownRight): #TODO remove asserts to improve speed
    assert type(gcwUpLeft) in (tuple, list) and len(gcwUpLeft) == 2, 'gcw parameter gcwUpLeft passed invalid argument'
    assert type(gcwDownRight) in (tuple, list) and len(gcwDownRight) == 2, 'gcw parameter gcwDownRight passed invalid argument'
    gcwOutput = []
    for gcwY, gcwCounter in zip(range(gcwUpLeft[1], gcwDownRight[1]-1, -1), range(99)):
        for gcwX in range(gcwUpLeft[0], gcwDownRight[0]+1):#correct?
            gcwOutput.append((gcwX, gcwY))
    #assert gcwOutput != [] #stupid?
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
im = pro_print_grid_image(RLE_to_matrix(doc["raw_rle"]), (0, 0))
# i = Image.new("RGB", (64, 64))
# d = ImageDraw.Draw(i)
# d.rectangle([0, 0, 64, 64], fill="#ff0000")
# i.putpixel((0, 63-0), fal)

im.save(doc["name"]+".png", "PNG")