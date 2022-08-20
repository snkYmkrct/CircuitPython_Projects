# game running on the PyPortal Titano

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
gc.collect()

THEMECOLORS = 2 # number of colors in the game theme palette
INGROUPxOFFSET = 40  # x position of the play board inside the dysplayed group
INGROUPyOFFSET = 60  # y position of the play board inside the dysplayed group
HTILES = 20
VTILES = 12
TILESIZE = 20

# game sprite sheet
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


# using the built in PyPortal screen, with no rotation
display = board.DISPLAY
display.rotation = 0

# enable touch screen, Titano screen resolution
touch_screen = adafruit_touchscreen.Touchscreen(board.TOUCH_XL, board.TOUCH_XR,
                                      board.TOUCH_YD, board.TOUCH_YU,
                                      calibration=((7391, 60392), (8696, 56799)),
                                      size=(480, 320))


# Create a theme palette for the game
theme_palette = displayio.Palette(THEMECOLORS)
theme_palette[0] = 0xe5d9ff
theme_palette[1] = 0xff00bf

# bitmap that can use the color in the theme palette
background_color = displayio.Bitmap(display.width, display.height, THEMECOLORS)
# single tile grid to show the background color
background = displayio.TileGrid(background_color, pixel_shader=theme_palette)


# create a frame for the game board
game_board_frame = RoundRect(32, 52, 416, 256, 8, fill=0x000000, outline=0xFF00FF, stroke=3)

# create the buttons  0xC0C0C0
font = bitmap_font.load_font("/fonts/SairaStencilOne-Regular-17.bdf")

new_game_button = Button(x=42, y=10, width=110, height=35, fill_color=0xFFFFFF, label_color=0xFF00FF, outline_color=0x000000,
                    style=Button.SHADOWROUNDRECT, label="New Game", label_font=font)

main_menu_button = Button(x=328, y=10, width=110, height=35, fill_color=0xFFFFFF, label_color=0xFF00FF, outline_color=0x000000,
                    style=Button.SHADOWROUNDRECT, label="Main Menu", label_font=font)

# create the text labels
bomb_number_box = RoundRect(265, 14, 35, 28, 7, fill=0xFFFFFF, outline=0x000000, stroke=2)

bomb_number_text_in = Label(font=font, x=272, y=28, text="15", color=0xFF00FF, background_color=None)

bomb_number_text_out = Label(font=font, x=170, y=28, text="Bombs left:", color=0x000000, background_color=None)


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
                            default_tile = 9, # starts with a fully undiscovered board
                            x = INGROUPxOFFSET,  # position of the game board inside the parent group
                            y = INGROUPyOFFSET)


# dot to test the touch screen
test_circle = vectorio.Circle(pixel_shader=theme_palette,
            color_index = 1,
            radius=3,
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

minesweeper_group.append(test_circle)

display.show(minesweeper_group)


source_index = 0
while True:
    point = touch_screen.touch_point
    time.sleep(.2)

    if point is not None:
        print(" ")
        print(point)
        test_circle.x = point[0]
        test_circle.y = point[1]

        if new_game_button.contains(point):
            print ("new game button")

        if main_menu_button.contains(point):
            print ("main menu button")

        if (point[0] in range( INGROUPxOFFSET, INGROUPxOFFSET + HTILES*TILESIZE + 1)) and \
            (point[1] in range( INGROUPyOFFSET, INGROUPyOFFSET + VTILES*TILESIZE + 1)):
        #if game_board.contains(point):  # use this after CP 8.0
            print("On the game board")
            xx = (point[0] - INGROUPxOFFSET) // TILESIZE
            yy = (point[1] - INGROUPyOFFSET) // TILESIZE
            print(xx,yy)
            game_board[xx,yy] = (game_board[xx,yy] + 1) % 16
            test_circle.x = -10
            test_circle.y = -10
            # import neko_code  vs  supervisor use ???
#     pass
#     for i in range(game_board.width):
#         for j in range(game_board.height):
#             game_board[i,j] = source_index % 16
#     source_index += 1
#     time.sleep(2)
