#This program searches the lexicon for patterns and saves them to the master library.
#It also accepts a "human" grid and converts it the the "computer" format.

import re, pprint

lexicon_file = open("Game_Of_Life/lexicon.txt", 'r')
lexicon_str = lexicon_file.read()

#                                (:name: )   (paragraph lines)end(grid lines)
grid_paragraph_regex = re.compile("""(\n\n:([^\t\n:])+:([^\t\n]+\n)*\.?\n\t(\t?[\*\.]{2,}\n)+)""")

grid_regex = re.compile('((\t[\*\.]{2,}\n)+)')#findall() works, but adds an extra line to the end. Fixable?

line_regex = re.compile('\t?[\*\.]{2,}\n') #only matches patterns whose live/dead characters are */.

#this function essentially reverses the pro_print_grid() function.
#cfLives is a tuple of all possible live characters, and cfDeads is those of dead.
#def convert_format(cfGrid, cfLives, cfDeads):
    #TODO break up grid into lines
    #findall?
#    while '\n' in cfGrid:
    #TODO check if grid is valid
    #TODO convert to dictionary



#print(convert_format())

all_grids = grid_regex.findall(lexicon_str)
#thingy = grid_regex.search(lexicon_str)
#print('\n'+thingy.group())
print(len(all_grids))
print('word1''word 2''does this really work???')
print(all_grids[len(all_grids) - 1][0])