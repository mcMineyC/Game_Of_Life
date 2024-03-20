#These are test patterns for running in CGOL_game_runner.py
#Note that patterns will appear "sideways" if you try to draw it by eyeballing the list matrix.
#The list matrix as seen onscreen is a 90 degree rotation of the actual grid.

def rot90(original):
    return list(zip(*original[::-1]))

glider = {(0, 0): [
    ['dead', 'dead', 'dead', 'dead', 'dead', 'dead', 'dead', 'dead'], # (X == 0, Y == 0-7)
    ['dead', 'dead', 'dead', 'dead', 'dead', 'dead', 'dead', 'dead'], # (X == 1, Y == 0-7)
    ['dead', 'dead', 'dead', 'live', 'dead', 'dead', 'dead', 'dead'], # (X == 2, Y == 0-7)
    ['dead', 'dead', 'dead', 'dead', 'live', 'dead', 'dead', 'dead'], # (X == 3, Y == 0-7)
    ['dead', 'dead', 'live', 'live', 'live', 'dead', 'dead', 'dead'],
    ['dead', 'dead', 'dead', 'dead', 'dead', 'dead', 'dead', 'dead'],
    ['dead', 'dead', 'dead', 'dead', 'dead', 'dead', 'dead', 'dead'],
    ['dead', 'dead', 'dead', 'dead', 'dead', 'dead', 'dead', 'dead']]}

gliderv = {
    (0,0): rot90(rot90(rot90(glider[(0,0)])))
}
