from lib import game_runner as runner
from lib import test_patterns as tp
import socket, json, time, struct
from lib import convert_functions as rc
from lib import communication_functions as cf

client = cf.get_socket()
curr_grid = tp.master_library["snark loop"]
gen = 0
for x in range(500):
    n_gen = runner.next_gen(curr_grid)
    strr = rc.grid_to_string_centered(n_gen, (0, 0))
    # print(strr)
    cf.send_message(client, strr)
    curr_grid = n_gen
    break
    time.sleep(0.5)
