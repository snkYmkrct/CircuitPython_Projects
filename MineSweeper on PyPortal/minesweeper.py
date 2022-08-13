import random 
import re

class Board:
    def __init__(self, dim_size, num_bombs):
        self.dim_size = dim_size
        self.num_bombs = num_bombs

        # helper funtion to create the board and plant the bombs
        self.board = self.make_new_board()

        self.assign_values_to_board()

        self.dug = set() # empty set of tuples (row,col) of locations already dug
    
    def make_new_board(self):
        # 2D board = list of lists is easiest
        board = [[None for _ in range(self.dim_size)] for _ in range(self.dim_size)]
        # [ [None, None, ... None],
        #   [None, None, ... None],
        #    ...
        #   [None, None, ... None] ]
        # each spot on the board has a unique id between 0 and (dim_size*dim_size)-1

        bombs_planted = 0
        while bombs_planted < self.num_bombs:
            loc = random.randint(0, self.dim_size**2 - 1)
            row = loc // self.dim_size
            col = loc % self.dim_size

            if board[row][col] == '*':
                # location already has a bomb
                continue

            board[row][col] = '*'
            bombs_planted += 1

        return board

    def assign_values_to_board(self):
        # for each cell that doesn't have a bomb, show how many bombs it "sees" in the neighbours 
        for r in range(self.dim_size):
            for c in range(self.dim_size):
                if self.board[r][c] == '*':
                    # bomb, ignore it
                    continue
                self.board[r][c] = self.get_num_neighbouring_bombs(r,c)

    def get_num_neighbouring_bombs(self, row, col):
        # iterate through all 8 positions around current one (with out of bounds check)
        num_neighbouring_bombs = 0
        for r in range(max(0, row-1), min(self.dim_size-1, row+1) + 1):
            for c in range(max(0, col-1), min(self.dim_size-1, col+1) + 1):
                if (r == row) and (c == col):
                    continue
                if self.board[r][c] == '*':
                    num_neighbouring_bombs += 1

        return num_neighbouring_bombs    

    def dig(self, row, col):
        # returns True if no bomb, False if bomb found
        self.dug.add((row, col))

        if self.board[row][col] == '*':
            return False

        if self.board[row][col] > 0:
            return True
        
        # if location is 0, dig all undug neighbours until reaching location next to a bomb
        for r in range(max(0, row-1), min(self.dim_size-1, row+1) + 1):
            for c in range(max(0, col-1), min(self.dim_size-1, col+1) + 1):
                if (r, c) in self.dug:
                    continue
                self.dig(r, c)
                
        return True

    def __str__(self):
        # return a string printout of the board

        visible_board = [[None for _ in range(self.dim_size)] for _ in range(self.dim_size)]
        for row in range(self.dim_size):
            for col in range(self.dim_size):
                if (row, col) in self.dug:
                    visible_board[row][col] = str(self.board[row][col])
                else:
                    visible_board[row][col] = ' '  # yet unchecked location
        
        # put this together in a string
        string_rep = ''
        # get max column widths for printing
        widths = []
        for idx in range(self.dim_size):
            columns = map(lambda x: x[idx], visible_board)
            widths.append(
                len(
                    max(columns, key = len)
                )
            )

        # print the csv strings
        indices = [i for i in range(self.dim_size)]
        indices_row = '   '
        cells = []
        for idx, col in enumerate(indices):
            format = '%-' + str(widths[idx]) + "s"
            cells.append(format % (col))
        indices_row += '  '.join(cells)
        indices_row += '  \n'
        
        for i in range(len(visible_board)):
            row = visible_board[i]
            string_rep += f'{i} |'
            cells = []
            for idx, col in enumerate(row):
                format = '%-' + str(widths[idx]) + "s"
                cells.append(format % (col))
            string_rep += ' |'.join(cells)
            string_rep += ' |\n'

        str_len = int(len(string_rep) / self.dim_size)
        string_rep = indices_row + '-'*str_len + '\n' + string_rep + '-'*str_len

        return string_rep


def play(dim_size = 10, num_bombs = 10):

    board = Board(dim_size, num_bombs)

    safe = True
    while len(board.dug) < (board.dim_size ** 2 - num_bombs):
        print(board)
        user_input = re.split(",(\\s)*", input("Where would you like to dig? Input as row, col ") ) 
        # pattern to split the input by the comma, and ignore white spaces
        row, col = int(user_input[0]), int(user_input[-1]) # take first and last elements, to avoid split extras (?)

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
    

