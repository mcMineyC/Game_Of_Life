import socket, json, time, struct

def get_socket():
    socket_path = '/tmp/matrix_connector'
    client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    client.connect(socket_path)
    return client

def send_message(client, strr):
    message = strr.encode("utf-8")
    try:
        # print("Sending message of length: " + str(len(message)))
        # print("Sending message length...")
        client.sendall(struct.pack("!I", len(message)))
        # print("Sending message...")
        client.sendall(message)
    except:
        # print("Error sending message.")
        exit(1)
    response = client.recv(1024)
    response = json.loads(response)
    if(response["success"]):
        # print("Image successfully sent!!!! :partying-face:")
        return True
    else:
        raise Exception("Something bad happened in the matrix connector")
        return False
