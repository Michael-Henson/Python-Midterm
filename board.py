class ConnectFourBoard:
    def __init__(self):
        """Initialize a new board"""
        self.player_token = 'X'
        self.cpu_token = 'O'
        self.empty_token = ' '

        self.num_rows = 6
        self.num_cols = 7
        self.player_board = 0
        self.cpu_board = 0
        self.turn = 0 # 0 = cpu, 1 = player
    
    def display(self):
        '''Display the board state for the player'''
        for row in range(self.num_rows):
            for col in range(self.num_cols):
                if self.is_self_occupied(1, col, (5 - row)):
                    print(f"|{self.player_token}",end='')
                elif self.is_self_occupied(0, col, (5 - row)):
                    print(f"|{self.cpu_token}",end='')
                else:
                    print(f"|{self.empty_token}",end='')
            print("|")
        print(" 0 1 2 3 4 5 6")

    def is_self_occupied(self, turn, col, row): # returns True if that tile is occupied by the turn passed to it
        if turn == 0: # CUP check
            return (self.cpu_board >> (col * 7 + row)) & 1
        if turn == 1: # Player check
            return (self.player_board >> (col * 7 + row)) & 1
    
    def is_occupied(self, col, row): # not used at the moment
        return ((self.player_board | self.cpu_board) >> (col * 7 + row)) & 1
    
    def add_piece(self, turn, col):
        for row in range(self.num_rows):
            if turn == 1:
                if not(self.player_board & (1 << (col * 7 + row))) and not(self.cpu_board & (1 << (col * 7 + row))):
                    self.player_board = self.player_board | (1 << (col * 7 + row))
                    return 1
            elif turn == 0:
                if not(self.player_board & (1 << (col * 7 + row))) and not(self.cpu_board & (1 << (col * 7 + row))):
                    self.cpu_board = self.cpu_board | (1 << (col * 7 + row))
                    return 1
            
        print("Invalid Move, column is full")
        return 0
    
    def check_winner(self, turn):
        """Check whether someone has won the game."""
        for row in range(self.num_rows):
            for col in range(self.num_cols):

                # Horizontal (→): Checks if all symbols right of each tile match
                if col <= self.num_cols - 4:
                    if all(self.is_self_occupied(turn, col + i, row) for i in range(4)):
                        return True
                    
                # Vertical (↓): Checks if all symbols down of each tile match
                if row <= self.num_rows - 4:
                    if all(self.is_self_occupied(turn, col, row + i) for i in range(4)):
                        return True

                # Diagonal down-right (↘): Checks if all symbols down right of each tile match
                if row <= self.num_rows - 4 and col <= self.num_cols - 4:
                    if all(self.is_self_occupied(turn, col + i, row + i) for i in range(4)):
                        return True

                # Diagonal down-left (↙): Checks if all symbols down left of each tile match
                if row <= self.num_rows - 4 and col >= 3:
                    if all(self.is_self_occupied(turn, col - i, row + i) for i in range(4)):
                        return True
        return False