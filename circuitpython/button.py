import board
import digitalio
import time

button = digitalio.DigitalInOut(board.GPIO10)
button.direction = digitalio.Direction.INPUT
button.pull = None  # External 100k pull-up is installed

while True:
    print("Pressed" if not button.value else "Released")
    time.sleep(0.2)
