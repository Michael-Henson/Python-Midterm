class ConnectFourBoard:
    def __init__(self):
        """Initialize a new board"""
        self.player_token = 'X'
        self.cpu_token = 'O'
        self.empty_token = ' '

        self.num_rows = 6
        self.num_cols = 7
        self.player_board = 0
        self.cpu_board = 1
        self.turn = 0 # 0 = cpu, 1 = player
    
    def display(self):
        for row in range(self.num_rows):
            for col in range(self.num_cols):
                if self.is_self_occupied(self.player_board, col, (5 - row)):
                    print(f"|{self.player_token}",end='')
                elif self.is_self_occupied(self.cpu_board, col, (5 - row)):
                    print(f"|{self.cpu_token}",end='')
                else:
                    print(f"|{self.empty_token}",end='')
            print("|")

    def is_self_occupied(self, board, col, row):
        return (board >> (col * 7 + row)) & 1
    
    def is_occupied(self, col, row):
        return ((self.player_board | self.cpu_board) >> (col * 7 + row)) & 1
    
    def add_piece(self, col):
        for row in range(self.num_rows):
            if not(self.player_board & (1 << (col * 7 + row))) and not(self.cpu_board & (1 << (col * 7 + row))):
                self.player_board = self.player_board | (1 << (col * 7 + row))
                return 1
            
        print("Invalid Move, column is full")
        return 0


