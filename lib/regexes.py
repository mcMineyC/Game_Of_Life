import re

digits = ('0', '1', '2', '3', '4', '5', '6', '7', '8', '9')
empty_chunk = [[False] * 8] * 8

#                                      :(name_____):(paragraph_) (grid lines_______)
grid_paragraph_regex = re.compile(r"\n:([^\t\n:]+):([^\t\n]+\n)*((\t[\*\.]{2,}\n)+)")
#group[0] is name, group[2] is full plaintext pattern.
#This regex seems to operate 100% correctly, but it is a good idea to triple-check it.

grid_regex = re.compile(r'((\t[\*\.]{2,}\n)+)')#findall() works, but adds an extra line to the end. Fixable?

line_regex = re.compile(r'\t?([\*\.]{2,})\n') #only matches plaintext patterns whose live/dead characters are */. #IMPORTANT will not match final line unless final line ends with '\n'

whitespace_regex = re.compile(r'\s')

#                             (comments)    (x     )      (y     )                 (pattern      )
RLE_regex = re.compile(r'^\s?((#.+\n)*)x = ([0-9]+), y = ([0-9]+), rule = B3/S23\n([0-9bo\$\s]+!)\s?$', re.IGNORECASE)
#1st group is all comments, 3rd group is x value, 4 is y value, 5 is RLE

default_RLE_comment = '''#C [[ ZOOM 7 GRID COLOR GRID 31 31 31 COLOR DEADRAMP 31 0 0 COLOR ALIVE 255 255 255 COLOR ALIVERAMP 255 255 255 COLOR DEAD 0 0 47 COLOR BACKGROUND 0 0 0 GPS 10 WIDTH 937 HEIGHT 600 ]]''' #TODO modify window WIDTH and HEIGHT as needed

comment_regex = re.compile(r'#C \[\[ .+ \]\]')

comment_items_regex = re.compile(r'([A-Z ]+) ([0-9 ]+)|([A-Z][a-z]+)')

greedy_regex = re.compile(r'\$+')

line_expander = re.compile(r'(\d{1,})(\$)')
splitter_regex = re.compile(r'(\d{0,})([o|b])')

def regexes():
    print("Regexes are loaded.")
