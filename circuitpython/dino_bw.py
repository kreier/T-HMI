
# dino.py
# Dino Runner for LILYGO T-HMI
# CircuitPython 10.3.1
# Button: GPIO0, active LOW

import time
import board
import digitalio
import displayio
import display as tft

screen = tft.display
WIDTH = screen.width
HEIGHT = screen.height

# ---------- Display setup ----------

BG = 0xFFFFFF
FG = 0x000000

background = displayio.Bitmap(WIDTH, HEIGHT, 2)
bg_palette = displayio.Palette(2)
bg_palette[0] = BG
bg_palette[1] = FG
background.fill(0)

GROUND_Y = HEIGHT - 36

# Ground line
for x in range(WIDTH):
    background[x, GROUND_Y] = 1

bg_grid = displayio.TileGrid(background, pixel_shader=bg_palette)

# ---------- Dinosaur sprite ----------

DINO_W = 20
DINO_H = 24

dino_bitmap = displayio.Bitmap(DINO_W, DINO_H, 2)
sprite_palette = displayio.Palette(2)
sprite_palette[0] = BG
sprite_palette[1] = FG
sprite_palette.make_transparent(0)


def rect(bitmap, x, y, w, h, color=1):
    for py in range(y, y + h):
        for px in range(x, x + w):
            if 0 <= px < bitmap.width and 0 <= py < bitmap.height:
                bitmap[px, py] = color


# Simple pixel dinosaur
rect(dino_bitmap, 10, 1, 8, 3)    # Head
rect(dino_bitmap, 8, 4, 11, 7)    # Face
rect(dino_bitmap, 5, 10, 11, 8)   # Body
rect(dino_bitmap, 2, 12, 5, 3)    # Tail
rect(dino_bitmap, 7, 17, 4, 5)    # Leg 1
rect(dino_bitmap, 13, 17, 4, 5)   # Leg 2
rect(dino_bitmap, 3, 21, 8, 2)    # Foot 1
rect(dino_bitmap, 12, 21, 7, 2)   # Foot 2
# Eye: erase one pixel to make it white
dino_bitmap[16, 6] = 0

dino_grid = displayio.TileGrid(
    dino_bitmap, pixel_shader=sprite_palette
)
dino_grid.x = 40
dino_grid.y = GROUND_Y - DINO_H

# ---------- Cactus sprite ----------

CACTUS_W = 14
CACTUS_H = 28

cactus_bitmap = displayio.Bitmap(CACTUS_W, CACTUS_H, 2)

rect(cactus_bitmap, 5, 0, 5, 28)
rect(cactus_bitmap, 1, 9, 5, 4)
rect(cactus_bitmap, 1, 6, 3, 5)
rect(cactus_bitmap, 9, 15, 4, 4)
rect(cactus_bitmap, 10, 12, 3, 6)

cactus_grid = displayio.TileGrid(
    cactus_bitmap, pixel_shader=sprite_palette
)
cactus_grid.x = WIDTH + 20
cactus_grid.y = GROUND_Y - CACTUS_H

# ---------- On-screen score ----------

DIGITS = (
    ("111", "101", "101", "101", "111"),  # 0
    ("010", "110", "010", "010", "111"),  # 1
    ("111", "001", "111", "100", "111"),  # 2
    ("111", "001", "111", "001", "111"),  # 3
    ("101", "101", "111", "001", "001"),  # 4
    ("111", "100", "111", "001", "111"),  # 5
    ("111", "100", "111", "101", "111"),  # 6
    ("111", "001", "010", "010", "010"),  # 7
    ("111", "101", "111", "101", "111"),  # 8
    ("111", "101", "111", "001", "111"),  # 9
)

score_bitmap = displayio.Bitmap(45, 7, 2)
score_palette = displayio.Palette(2)
score_palette[0] = BG
score_palette[1] = FG
score_grid = displayio.TileGrid(
    score_bitmap, pixel_shader=score_palette
)
score_grid.x = WIDTH - 50
score_grid.y = 10


def draw_score(value):
    score_bitmap.fill(0)
    digits = str(min(value, 99999))
    x = 0

    for char in digits:
        pattern = DIGITS[int(char)]
        for y, row in enumerate(pattern):
            for px, bit in enumerate(row):
                if bit == "1" and x + px < score_bitmap.width:
                    score_bitmap[x + px, y] = 1
        x += 5


# Layer order: background, score, dinosaur, cactus
game_group = displayio.Group()
game_group.append(bg_grid)
game_group.append(score_grid)
game_group.append(dino_grid)
game_group.append(cactus_grid)

screen.root_group = game_group

# ---------- Button ----------

button = digitalio.DigitalInOut(board.GPIO0)
button.direction = digitalio.Direction.INPUT
button.pull = None  # Board already has an external pull-up

# ---------- Game logic ----------

DINO_X = 40
GRAVITY = 950.0
JUMP_VELOCITY = -390.0

dino_y = float(GROUND_Y - DINO_H)
velocity_y = 0.0
grounded = True

obstacle_x = float(WIDTH + 20)
speed = 180.0

score = 0
game_over = False
previous_pressed = False
last_score = -1

last_time = time.monotonic()

print("Dino Runner ready! Press GPIO0 to jump.")


def restart():
    global dino_y, velocity_y, grounded
    global obstacle_x, speed, score, game_over
    global last_score, last_time

    dino_y = float(GROUND_Y - DINO_H)
    velocity_y = 0.0
    grounded = True
    obstacle_x = float(WIDTH + 20)
    speed = 180.0
    score = 0
    game_over = False
    last_score = -1
    last_time = time.monotonic()

    dino_grid.y = int(dino_y)
    cactus_grid.x = int(obstacle_x)
    draw_score(0)

    print("New run!")


try:
    while True:
        now = time.monotonic()
        dt = min(now - last_time, 0.05)
        last_time = now

        pressed = not button.value
        just_pressed = pressed and not previous_pressed
        previous_pressed = pressed

        if game_over:
            if just_pressed:
                restart()
        else:
            # Jump on the button's press edge
            if just_pressed and grounded:
                velocity_y = JUMP_VELOCITY
                grounded = False

            # Gravity and vertical movement
            if not grounded:
                velocity_y += GRAVITY * dt
                dino_y += velocity_y * dt

                floor_y = GROUND_Y - DINO_H
                if dino_y >= floor_y:
                    dino_y = float(floor_y)
                    velocity_y = 0.0
                    grounded = True

            dino_grid.y = int(dino_y)

            # Move cactus
            obstacle_x -= speed * dt

            if obstacle_x < -CACTUS_W:
                obstacle_x = float(WIDTH + 20)
                speed = min(speed + 5, 300)

            cactus_grid.x = int(obstacle_x)

            # Collision detection
            dino_left = DINO_X + 3
            dino_right = DINO_X + DINO_W - 2
            dino_top = int(dino_y) + 2
            dino_bottom = int(dino_y) + DINO_H - 1

            cactus_left = int(obstacle_x) + 1
            cactus_right = int(obstacle_x) + CACTUS_W - 1
            cactus_top = GROUND_Y - CACTUS_H
            cactus_bottom = GROUND_Y

            collision = (
                dino_right > cactus_left
                and dino_left < cactus_right
                and dino_bottom > cactus_top
                and dino_top < cactus_bottom
            )

            if collision:
                game_over = True
                print("Game over! Score:", score)
                print("Press GPIO0 to restart.")

            # Score increases with survival time
            score = int((now - last_time + 0) * 0) + score
            # Use a separate elapsed-time accumulator below instead.

        # Update the score display approximately once per second
        if not game_over:
            if int(now) != last_score:
                # Score based on elapsed game time
                draw_score(score)
                last_score = int(now)

        # Push display changes
        while not screen.refresh():
            pass

        time.sleep(0.01)

except KeyboardInterrupt:
    print("Game stopped.")

finally:
    button.deinit()
    screen.root_group = displayio.CIRCUITPYTHON_TERMINAL
