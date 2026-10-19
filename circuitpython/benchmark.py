
import time
import displayio

def run(display, seconds=3):
    width = display.width
    height = display.height

    bitmap = displayio.Bitmap(width, height, 2)
    palette = displayio.Palette(2)
    palette[0] = 0x000000
    palette[1] = 0xFFFFFF

    group = displayio.Group()
    group.append(displayio.TileGrid(bitmap, pixel_shader=palette))
    display.root_group = group

    # Warm-up
    bitmap.fill(0)
    time.sleep(0.2)

    frames = 0
    start = time.monotonic()
    deadline = start + seconds

    while time.monotonic() < deadline:
        bitmap.fill(frames & 1)
        frames += 1

    elapsed = time.monotonic() - start
    pixels_per_second = frames * width * height / elapsed

    print("Display:", width, "x", height)
    print("Frames:", frames)
    print("Elapsed:", round(elapsed, 3), "seconds")
    print("FPS:", round(frames / elapsed, 2))
    print("Effective pixel updates/s:", round(pixels_per_second))
# Write your code here :-)
