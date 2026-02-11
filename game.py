from board import ConnectFourBoard
from input_validator import validate_input, validate_char, validate_int, ValidationError

class ConnectFourGame:
    """Represents a Connect 4 game. Manages board and players."""

    def __init__(self):
        """Initialize a new game"""
        # Set up board
        self.board = ConnectFourBoard()

    
    
    def start(self):
        # self.board.display()
        playing = True
        while playing: # main game loop

            while True: # loop until valid input
                userInput = input("Where would you like to play: ")
                try:
                    col = validate_int(userInput, min_val=0, max_val=6)
                    break
                except ValidationError as e:
                    print(e)

            valid = self.board.add_piece(col)
            if not valid:
                continue

            self.board.display()
            # check win

            # CPU turn here

            self.board.display()
            # check win

        
    
if __name__ == "__main__":
    # prompt
    game = ConnectFourGame()
    game.start()