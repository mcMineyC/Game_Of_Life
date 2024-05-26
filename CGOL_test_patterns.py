#These are test patterns for running in CGOL_game_runner.py
#Note that patterns will appear "sideways" if you try to draw it by eyeballing the list matrix.
#The list matrix as seen onscreen is a 90 degree rotation of the actual grid.
#TODO change 'live'/'dead' to True/False

import pprint

master_library = {

'glider': {(0, 0): [
    [False, False, False, False, False, False, False, False], # (X == 0, Y == 0-7)
    [False, False, False, False, False, False, False, False], # (X == 1, Y == 0-7)
    [False, False, False, True, False, False, False, False], # (X == 2, Y == 0-7)
    [False, False, False, False, True, False, False, False], # (X == 3, Y == 0-7)
    [False, False, True, True, True, False, False, False],
    [False, False, False, False, False, False, False, False],
    [False, False, False, False, False, False, False, False],
    [False, False, False, False, False, False, False, False]]},

'pattern2': {(0, 0): [
    ['dead', 'dead', 'dead', 'dead', 'dead', 'dead', 'dead', 'dead'], # (X == 0, Y == 0-7)
    ['dead', 'dead', 'dead', 'dead', 'dead', 'dead', 'dead', 'dead'], # (X == 1, Y == 0-7)
    ['dead', 'dead', 'dead', 'dead', 'dead', 'dead', 'dead', 'dead'], # (X == 2, Y == 0-7)
    ['dead', 'dead', 'dead', 'dead', 'dead', 'dead', 'dead', 'dead'], # (X == 3, Y == 0-7)
    ['dead', 'dead', 'dead', 'dead', 'dead', 'dead', 'dead', 'dead'],
    ['dead', 'dead', 'dead', 'dead', 'dead', 'dead', 'dead', 'dead'],
    ['dead', 'dead', 'dead', 'dead', 'dead', 'dead', 'dead', 'dead'],
    ['live', 'live', 'live', 'live', 'live', 'live', 'live', 'live']]},

'square_on_edge': {(0, 0): [
    ['dead', 'dead', 'dead', 'dead', 'dead', 'dead', 'dead', 'dead'], # (X == 0, Y == 0-7)
    ['dead', 'dead', 'dead', 'dead', 'dead', 'dead', 'dead', 'dead'], # (X == 1, Y == 0-7)
    ['dead', 'dead', 'dead', 'dead', 'dead', 'dead', 'dead', 'dead'], # (X == 2, Y == 0-7)
    ['dead', 'dead', 'dead', 'dead', 'dead', 'dead', 'dead', 'dead'], # (X == 3, Y == 0-7)
    ['dead', 'dead', 'dead', 'dead', 'dead', 'dead', 'dead', 'dead'],
    ['dead', 'dead', 'dead', 'dead', 'dead', 'dead', 'dead', 'dead'],
    ['dead', 'dead', 'dead', 'dead', 'live', 'live', 'dead', 'dead'],
    ['dead', 'dead', 'dead', 'dead', 'live', 'live', 'dead', 'dead']]},

'pattern1': {(0, 0): [
    ['dead', 'dead', 'dead', 'dead', 'dead', 'dead', 'dead', 'dead'], # (X == 0, Y == 0-7)
    ['dead', 'dead', 'dead', 'dead', 'dead', 'dead', 'dead', 'dead'], # (X == 1, Y == 0-7)
    ['dead', 'dead', 'dead', 'dead', 'dead', 'dead', 'dead', 'dead'], # (X == 2, Y == 0-7)
    ['dead', 'dead', 'dead', 'dead', 'dead', 'dead', 'dead', 'dead'], # (X == 3, Y == 0-7)
    ['dead', 'dead', 'dead', 'dead', 'live', 'dead', 'dead', 'dead'],
    ['dead', 'dead', 'dead', 'live', 'dead', 'live', 'dead', 'dead'],
    ['dead', 'dead', 'dead', 'live', 'live', 'live', 'dead', 'dead'],
    ['dead', 'dead', 'dead', 'dead', 'dead', 'dead', 'dead', 'dead']]},

'glider13': {(0, 0): [
          ['dead', 'dead', 'dead', 'dead', 'dead', 'dead', 'dead', 'dead'],
          ['dead', 'dead', 'dead', 'dead', 'dead', 'dead', 'dead', 'dead'],
          ['dead', 'dead', 'dead', 'dead', 'dead', 'dead', 'dead', 'dead'],
          ['dead', 'dead', 'dead', 'dead', 'dead', 'dead', 'dead', 'dead'],
          ['dead', 'dead', 'dead', 'dead', 'dead', 'dead', 'dead', 'dead'],
          ['dead', 'dead', 'dead', 'dead', 'dead', 'dead', 'dead', 'dead'],
          ['dead', 'dead', 'dead', 'dead', 'dead', 'live', 'dead', 'live'],
          ['dead', 'dead', 'dead', 'dead', 'dead', 'dead', 'live', 'live']],
 (0, 1): [['dead', 'dead', 'dead', 'dead', 'dead', 'dead', 'dead', 'dead'],
          ['dead', 'dead', 'dead', 'dead', 'dead', 'dead', 'dead', 'dead'],
          ['dead', 'dead', 'dead', 'dead', 'dead', 'dead', 'dead', 'dead'],
          ['dead', 'dead', 'dead', 'dead', 'dead', 'dead', 'dead', 'dead'],
          ['dead', 'dead', 'dead', 'dead', 'dead', 'dead', 'dead', 'dead'],
          ['dead', 'dead', 'dead', 'dead', 'dead', 'dead', 'dead', 'dead'],
          ['dead', 'dead', 'dead', 'dead', 'dead', 'dead', 'dead', 'dead'],
          ['dead', 'dead', 'dead', 'dead', 'dead', 'dead', 'dead', 'dead']],
 (1, 0): [['dead', 'dead', 'dead', 'dead', 'dead', 'dead', 'live', 'dead'],
          ['dead', 'dead', 'dead', 'dead', 'dead', 'dead', 'dead', 'dead'],
          ['dead', 'dead', 'dead', 'dead', 'dead', 'dead', 'dead', 'dead'],
          ['dead', 'dead', 'dead', 'dead', 'dead', 'dead', 'dead', 'dead'],
          ['dead', 'dead', 'dead', 'dead', 'dead', 'dead', 'dead', 'dead'],
          ['dead', 'dead', 'dead', 'dead', 'dead', 'dead', 'dead', 'dead'],
          ['dead', 'dead', 'dead', 'dead', 'dead', 'dead', 'dead', 'dead'],
          ['dead', 'dead', 'dead', 'dead', 'dead', 'dead', 'dead', 'dead']]},

'MWSSspaceship': {(0, 0): [
    ['dead', 'dead', 'dead', 'dead', 'dead', 'dead', 'dead', 'dead'], # (X == 0, Y == 0-7)
    ['dead', 'dead', 'dead', 'dead', 'dead', 'dead', 'dead', 'dead'], # (X == 1, Y == 0-7)
    ['dead', 'dead', 'dead', 'dead', 'live', 'dead', 'dead', 'dead'], # (X == 2, Y == 0-7)
    ['dead', 'dead', 'live', 'dead', 'dead', 'dead', 'live', 'dead'], # (X == 3, Y == 0-7)
    ['dead', 'live', 'dead', 'dead', 'dead', 'dead', 'dead', 'dead'],
    ['dead', 'live', 'dead', 'dead', 'dead', 'dead', 'live', 'dead'],
    ['dead', 'live', 'live', 'live', 'live', 'live', 'dead', 'dead'],
    ['dead', 'dead', 'dead', 'dead', 'dead', 'dead', 'dead', 'dead']]},

'LWSSspaceship': {(0, 0): [
    ['dead', 'dead', 'dead', 'dead', 'dead', 'dead', 'dead', 'dead'], # (X == 0, Y == 0-7)
    ['dead', 'dead', 'dead', 'dead', 'dead', 'dead', 'dead', 'dead'], # (X == 1, Y == 0-7)
    ['dead', 'live', 'dead', 'dead', 'live', 'dead', 'dead', 'dead'], # (X == 2, Y == 0-7)
    ['dead', 'dead', 'dead', 'dead', 'dead', 'live', 'dead', 'dead'], # (X == 3, Y == 0-7)
    ['dead', 'live', 'dead', 'dead', 'dead', 'live', 'dead', 'dead'],
    ['dead', 'dead', 'live', 'live', 'live', 'live', 'dead', 'dead'],
    ['dead', 'dead', 'dead', 'dead', 'dead', 'dead', 'dead', 'dead'],
    ['dead', 'dead', 'dead', 'dead', 'dead', 'dead', 'dead', 'dead']]}

}

"""
print_settings = pprint.PrettyPrinter(depth=None, width=150, sort_dicts=True, compact=True)

print_settings.pprint(master_library)
"""