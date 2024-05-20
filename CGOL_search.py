#This program searches the lexicon for patterns and saves them to the master library.
#It also accepts a "human" grid and converts it to the "computer" format.
#NOTE: The functions and regexes are in regexes.py now

#Why's this here still?
#TODO test run everything in search and txt convert

master_dict = {
    '#hash': {
        'hash': '#hash',
        'name': 'glider',
        'creator_name': 'Connor',
        'xbound': 3,
        'ybound': 3,
        'rle': 'bo$2bo$3o!',
        'comments': {
            'zoom': 7, 
            'color deadramp': [255, 220, 192], 
            'grid color grid': [192, 192, 192]
        }
    }
}