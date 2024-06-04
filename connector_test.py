import socket, io, json, struct, random
import matrix_to_image
import CGOL_test_patterns


socket_path = '/tmp/matrix_connector'

# Create the Unix socket client
client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

# Connect to the server
client.connect(socket_path)

data = {
    "now": "",
}
o = ""
for y in range(64):
    for x in range(64):
        o += ("1" if (y%2 == 0 and random.randint(0,1) == 1) else "0")
    o += "\n" if (y != 63) else ""
data["now"] = o
data_bytes = json.dumps(data).encode("utf-8")
client.sendall(struct.pack("!I", len(data_bytes)))
client.sendall(data_bytes)
print("sent")
# Receive a response from the server
response = client.recv(1024)
client.close()
response = json.loads(response)
if(response["success"]):
    print("Image successfully sent!!!! :partying-face:")
