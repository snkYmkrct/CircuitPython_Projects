# Text implementation of the game, working on PC

import random 
import re
from minesweeper_board import Board

def play(dim_size = 10, num_bombs = 10):

    board = Board(dim_size, num_bombs)

    safe = True
    while len(board.dug) < (board.dim_size ** 2 - num_bombs):
        print(board)
        user_input = re.split(",(\\s)*", input("Where would you like to dig? Input as row, col ") ) 
        # pattern to split the input by the comma, and ignore white spaces

        try:
            row, col = int(user_input[0]), int(user_input[-1]) # take first and last elements, to avoid split extras (?)
        except ValueError:
            print("Invalid format, try again.")
            continue
        else:   
            if row < 0 or row >= board.dim_size or col < 0 or col >= board.dim_size:
                print("Invalid location, try again.")
                continue

        safe = board.dig(row, col)

        if not safe:
            # YOU. LOST. GAME. OVER
            break
    
    if safe: 
        print("You won! YAY!!!")
        print(board)
    else:
        print("GAME. OVER")
        board.dug = [(r,c) for r in range(board.dim_size) for c in range(board.dim_size)]
        print(board)



if __name__ == '__main__': 
    play()
    

