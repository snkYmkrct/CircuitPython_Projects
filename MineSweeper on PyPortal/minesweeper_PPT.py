import time
import board
import displayio
import vectorio
import terminalio
import adafruit_imageload
import adafruit_touchscreen
from adafruit_bitmap_font import bitmap_font
from adafruit_display_text.bitmap_label import Label
from adafruit_button import Button
from adafruit_display_shapes.roundrect import RoundRect
import gc
import supervisor
from random import seed, randint
seed(int(time.monotonic()))


# ==================== Game and UI constants ====================

DEBUGENABLED = True

BLACK = 0x000000
WHITE = 0xFFFFFF
LAVENDER = 0xE5D9FF
PINK = 0xFF00FF
RED = 0xFF0000

THEMECOLORS = 3 # number of colors in the game theme palette
INGROUPXOFFSET = 40  # x position of the play board inside the dysplayed group
INGROUPYOFFSET = 60  # y position of the play board inside the dysplayed group
HTILES = 20  # number of tiles on the horizontal
VTILES = 12  # number of tiles on the vertical
TILESIZE = 20 # size of the tile square

# Minesweeper sprite sheet
ZERO = 0
ONE = 1
TWO = 2
THREE = 3
FOUR = 4
FIVE = 5
SIX = 6
SEVEN = 7
EIGHT = 8
NEWTILE = 9
EXPLODED = 10
FLAG = 11
NOTABOMB = 12
MAYBE = 13
BOMB = 14

NUMBEROFBOMBS = 30


# ==================== Creating the Minesweeper Game UI ====================

# using the built in PyPortal Titano screen, with no rotation
display = board.DISPLAY
display.rotation = 0

# enabling the touch screen, Titano screen resolution
touch_screen = adafruit_touchscreen.Touchscreen(board.TOUCH_XL, board.TOUCH_XR,
                                      board.TOUCH_YD, board.TOUCH_YU,
                                      calibration=((7391, 60392), (8696, 56799)),
                                      size=(480, 320))


# Creating a theme palette for the game
theme_palette = displayio.Palette(THEMECOLORS)
theme_palette[0] = LAVENDER
theme_palette[1] = PINK
theme_palette[2] = RED

# bitmap that can use the colors in the theme palette
background_color = displayio.Bitmap(display.width, display.height, THEMECOLORS)
# single tile grid to show the background color
background = displayio.TileGrid(background_color, pixel_shader=theme_palette)

# Creating the UI buttons
font = bitmap_font.load_font("/fonts/SairaStencilOne-Regular-17.bdf")

new_game_button = Button(x=42, y=10, width=110, height=35,
                    fill_color=WHITE, label_color=PINK, outline_color=BLACK, selected_fill=PINK, selected_label=WHITE,
                    style=Button.SHADOWROUNDRECT, label="New Game", label_font=font)

main_menu_button = Button(x=328, y=10, width=110, height=35,
                    fill_color=WHITE, label_color=PINK, outline_color=BLACK, selected_fill=PINK, selected_label=WHITE,
                    style=Button.SHADOWROUNDRECT, label="Main Menu", label_font=font)

# Creating the UI text labels
bomb_number_box = RoundRect(266, 15, 35, 28, 7, fill=WHITE, outline=BLACK, stroke=2)

bomb_number_text_in = Label(font=font, x=273, y=28, text='{:2d}'.format(NUMBEROFBOMBS), color=PINK, background_color=None)

bomb_number_text_out = Label(font=font, x=170, y=28, text="Bombs left:", color=BLACK, background_color=None)


# Creating a rounded rectangle frame for the game board
game_board_frame = RoundRect(INGROUPXOFFSET-8, INGROUPYOFFSET-8,
                            HTILES*TILESIZE+16, VTILES*TILESIZE+16, 8, fill=BLACK, outline=PINK, stroke=3)

# load the .bmp image containing the icons for the game
# it's a 80x80 pixels image, with icons arranged in a 4x4 grid of squares
game_sprite_sheet, game_palette = adafruit_imageload.load("/MineSweeperSpriteSheet.bmp",
                                          bitmap=displayio.Bitmap,
                                          palette=displayio.Palette)

# Create a game board as a tile grid
game_board = displayio.TileGrid(game_sprite_sheet, pixel_shader=game_palette,
                            width = HTILES,   # number of tiles on the horizontal
                            height = VTILES,  # number of tiles on the vertical
                            tile_width = TILESIZE, # each icon is a square 20x20 pixels in size
                            tile_height = TILESIZE,
                            default_tile = NEWTILE, # starts with a fully undiscovered board
                            x = INGROUPXOFFSET,  # position of the game board inside the parent group
                            y = INGROUPYOFFSET)


# dot to test the touch screen
if DEBUGENABLED:
    test_circle = vectorio.Circle(pixel_shader=theme_palette,
                                    color_index = 2, radius=3,
                                    x=-10,  # negative values so it starts off the edge of the display
                                    y=-10)  # won't get shown until the location moves onto the display


# create a group to display on the screen
minesweeper_group = displayio.Group()

# add all the defined elements in the order they should appear
minesweeper_group.append(background)
minesweeper_group.append(game_board_frame)
minesweeper_group.append(game_board)
minesweeper_group.append(new_game_button)
minesweeper_group.append(main_menu_button)
minesweeper_group.append(bomb_number_box)
minesweeper_group.append(bomb_number_text_in)
minesweeper_group.append(bomb_number_text_out)
if DEBUGENABLED:
    minesweeper_group.append(test_circle)

display.show(minesweeper_group)


# ==================== Defining the game methods ====================

def print_bomb_list():
    for y in range(VTILES):
        bomb_string = ""
        for x in range(HTILES):
            if bomb_list[x][y] == BOMB:
                bomb_string = bomb_string + "  " + "*"
            else:
                bomb_string = bomb_string + "  " + str(bomb_list[x][y])

        print(bomb_string)
    gc.collect()

def get_number_bomb_neighbours(param_x, param_y):
    # Iterating through all 8 positions around current one (with out of bounds check)
    num_neighbouring_bombs = 0
    for x in range( max(0, param_x-1), min(HTILES-1, param_x+1) + 1 ):
        for y in range( max(0, param_y-1), min(VTILES-1, param_y+1) + 1 ):
            if (x == param_x) and (y == param_y):
                continue
            if bomb_list[x][y] == BOMB:
                num_neighbouring_bombs += 1

    return num_neighbouring_bombs


def start_new_game():
    # Is the game in progress, False means either win or loss
    global is_game_running
    is_game_running = True

    # Number of bombs marked as flagged on the game board, maximum NUMBEROFBOMBS
    global flagged_bombs
    flagged_bombs = 0

    # Filling the UI game board matrix with the default tiles
    for x in range(HTILES):
        for y in range(VTILES):
            game_board[x,y] = NEWTILE

    # Creating the data game board as a matrix
    # Keeping same x-y orientation as the display matrix, for ease of use
    global bomb_list
    bomb_list = []
    for _ in range(HTILES):
        l = []
        for _ in range(VTILES):
            l.append(None)
        bomb_list.append(l)

    # Planting the bombs
    bombs_planted = 0
    while (bombs_planted < NUMBEROFBOMBS):
        # choose a random location
        random_x = randint(0, HTILES-1)
        random_y = randint(0, VTILES-1)
        if bomb_list[random_x][random_y] == BOMB:
            # location already contains a bomb
            continue
        bomb_list[random_x][random_y] = BOMB
        bombs_planted += 1

    # Filling the rest of the game matrix with info about the neighbouring bombs
    for x in range(HTILES):
        for y in range(VTILES):
            if bomb_list[x][y] == BOMB:
                continue
            bomb_list[x][y] = get_number_bomb_neighbours(x,y)

    if DEBUGENABLED:
        print_bomb_list()

    # Already dug locations on the board
    global locations_dug
    locations_dug = set()

    gc.collect()

def dig_board(param_x, param_y):
    global flagged_bombs
    # Adding current location to the set, marking it as already explored
    locations_dug.add((param_x, param_y))

    # If current location is a bomb, bad luck, lost the game
    if bomb_list[param_x][param_y] == BOMB:
        return False

    # change the game board to the correct tile
    game_board[param_x, param_y] = bomb_list[param_x][param_y]

    # If current location is a number > 0, that means there are neighbouring bombs, show the number
    if bomb_list[param_x][param_y] > 0:
        return True

    # If location is 0, dig all unexplored neighbours until reaching location next to a bomb
    dig_stack = [(param_x, param_y)]
    while dig_stack:
        (pop_x, pop_y) = dig_stack.pop()
        for x in range( max(0, pop_x-1), min(HTILES-1, pop_x+1) + 1 ):
            for y in range( max(0, pop_y-1), min(VTILES-1, pop_y+1) + 1 ):
                if (x, y) in locations_dug:  # already explored location, ignore
                    continue
                if bomb_list[x][y] == BOMB:  # bomb in unexplored location, ignore
                    continue

                locations_dug.add((x, y))
                if game_board[x, y] == FLAG:
                    flagged_bombs -= 1
                    bomb_number_text_in.text = '{:2d}'.format(NUMBEROFBOMBS-flagged_bombs)
                game_board[x, y] = bomb_list[x][y]

                if bomb_list[x][y] > 0:
                    # location neighbouring bombs, show on board, and ignore after adding to explored locations
                    continue

                # location is 0, no neighbouring bombs, continue exploration
                dig_stack.append((x, y))

    gc.collect()
    return True

def game_over(param_x, param_y, win):
    if win == True:
        pass
    else:
        pass


# Starting new game on UI load
start_new_game()

while True:
    point = touch_screen.touch_point
    time.sleep(.2)

    if point is not None:
        if DEBUGENABLED:
            print(" ")
            print(point)
            test_circle.x = point[0]
            test_circle.y = point[1]

        if new_game_button.contains(point):
            if DEBUGENABLED:
                print ("new game button")
            new_game_button.selected = True
            start_new_game()
            new_game_button.selected = False

        if main_menu_button.contains(point):
            if DEBUGENABLED:
                print ("main menu button")
            main_menu_button.selected = True
            supervisor.set_next_code_file('code.py')
            time.sleep(0.2)
            main_menu_button.selected = False
            supervisor.reload()

        if (point[0] in range( INGROUPXOFFSET, INGROUPXOFFSET + HTILES*TILESIZE)) and \
            (point[1] in range( INGROUPYOFFSET, INGROUPYOFFSET + VTILES*TILESIZE)):
        # if game_board.contains(point):  # use this after CP 8.0

            if is_game_running:
                xx = (point[0] - INGROUPXOFFSET) // TILESIZE
                yy = (point[1] - INGROUPYOFFSET) // TILESIZE

                if game_board[xx,yy] == NEWTILE:
                    flagged_bombs += 1
                    game_board[xx,yy] = FLAG
                    bomb_number_text_in.text = '{:2d}'.format(NUMBEROFBOMBS-flagged_bombs)
                elif game_board[xx,yy] == FLAG:
                    flagged_bombs -= 1
                    bomb_number_text_in.text = '{:2d}'.format(NUMBEROFBOMBS-flagged_bombs)
                    is_game_running = dig_board(xx, yy)

                if not is_game_running:
                    # The game is lost, reveal the board
                    game_over(xx, yy, False)
                elif len(locations_dug) == (HTILES*VTILES - NUMBEROFBOMBS):
                    # All locations have been explored or flagged as bombs - incorrect flagging should have been revealed by now
                    is_game_running = False
                    game_over(xx, yy, True)

            if DEBUGENABLED:
                print("On the game board")
                print(xx,yy)
                # test_circle.x = -10
                # test_circle.y = -10
                # print(locations_dug)
                print(len(locations_dug))



