from PIL import Image
from PIL import ImageDraw
import io
import os, socket, json, sys

"""
from rgbmatrix import RGBMatrix, RGBMatrixOptions

# Configuration for the matrix
options = RGBMatrixOptions()
options.rows = 64
options.cols = 64
options.chain_length = 1
options.parallel = 1
options.hardware_mapping = 'regular'  # If you have an Adafruit HAT: 'adafruit-hat'

matrix = RGBMatrix(options = options)
matrix.Clear()
matrix.SetImage(im, 0, 0)
"""
print(sys.argv)
socket_path = '/tmp/matrix_connector'

class ScrewyError(Exception):
    pass

try:
    os.unlink(socket_path)
except OSError:
    if os.path.exists(socket_path):
        raise ScrewyError("Summin' screwy happn'd 'ere")

server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
server.bind(socket_path)
server.listen(1)

# accept connections
while True:
    print('Server is listening for incoming connections...')
    connection, client_address = server.accept()
    
    try:
        while True:
            data = connection.recv(1024)
            if not data:
                break
            inn = Image.open(io.BytesIO(data))
            if len(sys.argv) >= 2 and sys.argv[1] == "yes":
                from rgbmatrix import RGBMatrix, RGBMatrixOptions

                # Configuration for the matrix
                options = RGBMatrixOptions()
                options.rows = 64
                options.cols = 64
                options.chain_length = 1
                options.parallel = 1
                options.hardware_mapping = 'regular'  # If you have an Adafruit HAT: 'adafruit-hat'
                options.disable_hardware_pulsing = True
                matrix = RGBMatrix(options = options)
                matrix.Clear()
                matrix.SetImage(inn, 0, 0)
            else:
                inn.save("snark_transferred.png", "PNG")
            # Send a response back to the client
            response = json.dumps({"success": True})
            connection.sendall(response.encode())
    except Exception:
        print("Ooop, error happened")
        response = json.dumps({"success": False})
        connection.sendall(response.encode())