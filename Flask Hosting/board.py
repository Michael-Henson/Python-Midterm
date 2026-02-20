class ConnectFourBoard:
    def __init__(self):
        """Initialize a new board"""
        self.player_token = 'X'
        self.cpu_token = 'O'
        self.empty_token = ' '
        
        self.history = []    

        self.num_rows = 6
        self.num_cols = 7
        self.player_board = 0
        self.cpu_board = 0
        self.turn = 0 # 0 = cpu, 1 = player
        self.heights = [0] * self.num_cols
    
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

    # returns True if that tile is occupied by the turn passed to it
    def is_self_occupied(self, turn, col, row):
        if turn == 0: # CUP check
            return bool((self.cpu_board >> (col * 7 + row)) & 1)
        if turn == 1: # Player check
            return bool((self.player_board >> (col * 7 + row)) & 1)
    
    def check_winner(self, turn: int) -> bool:
        """
        Fast bitboard win check for Connect 4.

        Bit layout assumption (matches your code):
        - 7 bits per column (rows 0..5 used, row 6 unused/sentinel)
        - bit index = col*7 + row
        Shifts:
        - vertical:   1
        - horizontal: 7
        - diag \ :    8
        - diag / :    6
        """
        if turn == 0:
            bb = self.cpu_board
        elif turn == 1:
            bb = self.player_board
        else:
            raise ValueError("turn must be 0 (cpu) or 1 (player)")

        # Vertical (same column): shift by 1
        m = bb & (bb >> 1)
        if m & (m >> 2):
            return True

        # Horizontal (across columns): shift by 7
        m = bb & (bb >> 7)
        if m & (m >> 14):
            return True

        # Diagonal / : up-right (col+1, row+1) => shift by 8
        m = bb & (bb >> 8)
        if m & (m >> 16):
            return True

        # Diagonal \ : up-left (col-1, row+1) => shift by 6
        m = bb & (bb >> 6)
        if m & (m >> 12):
            return True

        return False
    
    def is_full(self) -> bool:
        """
        Board is full when every column's top playable cell is occupied.

        Bit layout:
        bit index = col*7 + row
        top playable row = row 5
        """
        occupied = self.player_board | self.cpu_board

        # Build mask of top cells (row 5 in each column)
        top_mask = 0
        for col in range(self.num_cols):
            top_mask |= 1 << (col * 7 + 5)

        return (occupied & top_mask) == top_mask
    
    def make_move(self, col: int, turn: int) -> int:
        """
        Drop a piece into column `col` for `turn` (0=CPU, 1=Player).
        Returns the row where the piece lands.
        Raises ValueError if the move is invalid.
        """
        if col < 0 or col >= self.num_cols:
            raise ValueError("Column out of range")

        row = self.heights[col]
        if row >= self.num_rows:  # column full (num_rows = 6)
            raise ValueError("Column is full")

        bit = 1 << (col * 7 + row)

        # Safety: shouldn't happen if heights is correct
        if (self.player_board | self.cpu_board) & bit:
            raise RuntimeError("Inconsistent heights: target bit already occupied")

        if turn == 0:
            self.cpu_board |= bit
        elif turn == 1:
            self.player_board |= bit
        else:
            raise ValueError("turn must be 0 (cpu) or 1 (player)")

        self.heights[col] += 1
        self.history.append((col, row, turn))
        return row
    
    def undo_move(self) -> None:
        """
        Undo the last move made by make_move().
        """
        if not self.history:
            raise ValueError("No moves to undo")

        col, row, turn = self.history.pop()
        bit = 1 << (col * 7 + row)

        if turn == 0:
            self.cpu_board &= ~bit
        else:
            self.player_board &= ~bit

        self.heights[col] -= 1

    def get_valid_moves(self):
        return [c for c in range(self.num_cols) if self.heights[c] < self.num_rows]