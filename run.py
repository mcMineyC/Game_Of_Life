import CGOL_game_runner as runner
import CGOL_test_patterns as tp
import socket, io, json, time
import matrix_to_image


socket_path = '/tmp/matrix_connector'
client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
client.connect(socket_path)

curr_grid = tp.master_library["snark loop"]
gen = 0
for x in range(500):
    n_gen = runner.next_gen(curr_grid)
    gen+=1
    i = matrix_to_image.pro_print_grid_image(n_gen, (0, 0))
    message = io.BytesIO()
    i.save(message, "PNG")
    message = message.getvalue()
    client.sendall(message)
    response = client.recv(1024)
    response = json.loads(response)
    if(response["success"]):
        print("Image successfully sent!!!! :partying-face:")
    else:
        raise Exception("Something bad happened in the matrix connector")
    curr_grid = n_gen
    time.sleep(5)