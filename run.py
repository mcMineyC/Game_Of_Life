import CGOL_game_runner as runner
import CGOL_test_patterns as tp
import socket, json, time, struct
import regexes_converts as rc


socket_path = '/tmp/matrix_connector'
client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
client.connect(socket_path)

curr_grid = tp.master_library["snark loop"]
gen = 0
for x in range(500):
    n_gen = runner.next_gen(curr_grid)
    strr = rc.grid_to_string(n_gen, (0, 4), (4, 0))
    # print()
    # print(strr)
    message = strr.encode("utf-8")
    print("Sending message of length: " + str(len(message)))
    try:
        print("Sending message length...")
        client.sendall(struct.pack("!I", len(message)))
        print("Sending message...")
        client.sendall(message)
    except:
        print("Error sending message.")
        exit(1)
    response = client.recv(1024)
    response = json.loads(response)
    if(response["success"]):
        print("Image successfully sent!!!! :partying-face:")
    else:
        raise Exception("Something bad happened in the matrix connector")
    curr_grid = n_gen
    time.sleep(0.5)
