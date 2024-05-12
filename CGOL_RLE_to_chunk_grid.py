#This program accepts an RLE (Run Length Encoded) string and converts it to
# #the dictionary chunk list matrix that CGOL_game_runner.py uses.

import re

#TODO use regex to break up RLE into pieces: comment, header, RLE pattern. Reject RLE with improper syntax.
RLE_regex = re.compile(r'()')
#TODO weed out unecessary whitespace
#TODO convert RLE pattern to chunk list matrix
#TODO read comment lines to extract color and camera settings