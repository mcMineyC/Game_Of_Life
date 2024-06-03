import socket, io, json
import matrix_to_image
import CGOL_test_patterns


socket_path = '/tmp/matrix_connector'

# Create the Unix socket client
client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

# Connect to the server
client.connect(socket_path)

"""
# Send a message to the server
i = matrix_to_image.pro_print_grid_image(CGOL_test_patterns.master_library["snark loop"], (0, 0))
message = io.BytesIO()
i.save(message, "PNG")
message = message.getvalue()
client.sendall(message)
"""
o = ""
for x in range(64):
    for y in range(64):
        o += "1"
    o += "\n"
client.sendall(o.encode())
print("sent")
# Receive a response from the server
response = client.recv(1024)
client.close()
response = json.loads(response)
if(response["success"]):
    print("Image successfully sent!!!! :partying-face:")
