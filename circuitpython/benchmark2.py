
# benchmark2.py
# Display benchmarks for the LILYGO T-HMI running CircuitPython 10.3
#
# Run from the REPL:
#   import benchmark2
#   benchmark2.run()
#
# Uses the display initialized by display.py.

import time
import displayio
import display as tft

display = tft.display
WIDTH = display.width
HEIGHT = display.height


def wait_for_refresh():
    """Wait until CircuitPython completes a display refresh."""
    while not display.refresh():
        pass


def report(name, frames, elapsed, pixels_per_frame):
    fps = frames / elapsed
    pixel_rate = fps * pixels_per_frame

    print()
    print(name)
    print("  Frames:          ", frames)
    print("  Elapsed:         ", round(elapsed, 3), "s")
    print("  Effective FPS:   ", round(fps, 2))
    print("  Pixel updates/s: ", round(pixel_rate))


def full_screen_test(seconds=3):
    """Alternate the entire screen between black and white."""
    bitmap = displayio.Bitmap(WIDTH, HEIGHT, 2)
    palette = displayio.Palette(2)
    palette[0] = 0x000000
    palette[1] = 0xFFFFFF

    group = displayio.Group()
    group.append(displayio.TileGrid(bitmap, pixel_shader=palette))
    display.root_group = group

    bitmap.fill(0)
    wait_for_refresh()

    frames = 0
    start = time.monotonic()
    deadline = start + seconds

    while time.monotonic() < deadline:
        bitmap.fill(frames & 1)
        wait_for_refresh()
        frames += 1

    elapsed = time.monotonic() - start
    report("FULL SCREEN", frames, elapsed, WIDTH * HEIGHT)


def rectangle_test(seconds=3):
    """Move a small rectangle around the screen."""
    bitmap = displayio.Bitmap(40, 40, 2)
    palette = displayio.Palette(2)
    palette[0] = 0x000000
    palette[1] = 0xFF0000

    group = displayio.Group()
    tile = displayio.TileGrid(bitmap, pixel_shader=palette)
    group.append(tile)
    display.root_group = group

    bitmap.fill(1)
    tile.x = 0
    tile.y = 0
    wait_for_refresh()

    frames = 0
    start = time.monotonic()
    deadline = start + seconds

    while time.monotonic() < deadline:
        tile.x = (frames * 13) % (WIDTH - 40)
        tile.y = (frames * 7) % (HEIGHT - 40)
        wait_for_refresh()
        frames += 1

    elapsed = time.monotonic() - start
    report("MOVING RECTANGLE (40x40)", frames, elapsed, 40 * 40)


def run():
    print("T-HMI display benchmark")
    print("Resolution:", WIDTH, "x", HEIGHT)
    print("Refresh is synchronized with display.refresh().")

    full_screen_test()
    rectangle_test()

    # Restore the built-in CircuitPython terminal.
    display.root_group = displayio.CIRCUITPYTHON_TERMINAL

    print()
    print("Benchmark complete.")
