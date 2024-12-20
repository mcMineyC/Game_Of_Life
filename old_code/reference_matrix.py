from PIL import Image
from PIL import ImageDraw
import io
import random, time
import os, socket, json, sys

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
current_canvas = matrix.CreateFrameCanvas()
next_canvas = matrix.CreateFrameCanvas()

def create_random_image():
    image = Image.new('RGB', (64, 64))
    draw = ImageDraw.Draw(image)
    for x in range(64):
        for y in range(64):
            color = (255, 255, 255) if random.random() > 0.5 else (0, 0, 0)
            draw.point((x, y), fill=color)
    return image

current_canvas.SetImage(create_random_image())
matrix.SwapOnVSync(current_canvas)

while True:
    next_canvas.SetImage(create_random_image())
    matrix.SwapOnVSync(next_canvas)
    time.sleep(0.1)
