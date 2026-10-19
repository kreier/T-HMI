
import board
import digitalio
import time
import displayio
import paralleldisplaybus
from adafruit_st7789 import ST7789

# Enable T-HMI peripheral power
pwr_en = digitalio.DigitalInOut(board.GPIO10)
pwr_en.direction = digitalio.Direction.OUTPUT
pwr_en.value = True

# pwr_on = digitalio.DigitalInOut(board.GPIO14)
# pwr_on.direction = digitalio.Direction.OUTPUT
# pwr_on.value = True

time.sleep(0.2)

displayio.release_displays()

display_bus = paralleldisplaybus.ParallelBus(
    data_pins=(
        board.GPIO48,
        board.GPIO47,
        board.GPIO39,
        board.GPIO40,
        board.GPIO41,
        board.GPIO42,
        board.GPIO45,
        board.GPIO46,
    ),
    write=board.GPIO8,
    command=board.GPIO7,
    chip_select=board.GPIO6,
    reset=None,
    read=None,
    frequency=2_000_000,
)

display = ST7789(
    display_bus,
    rotation=90,
    width=320,
    height=240,
    rowstart=0,
    colstart=0,
    backlight_pin=board.GPIO38,
    invert=False,
)
