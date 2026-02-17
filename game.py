from board import ConnectFourBoard
from cpu import CPU_Choice
from input_validator import validate_input, validate_char, validate_int, ValidationError
import os

class ConnectFourGame:
    """Represents a Connect 4 game. Manages board and players."""

    def __init__(self):
        """Initialize a new game"""
        # Set up board
        self.board = ConnectFourBoard()

    
    
    def start(self, turn):

        if turn == 0:
                self.board.make_move(3, 0)
        
        self.board.display()


        playing = True
        while playing: # main game loop
            

            while True: # loop until valid input
                userInput = input("Where would you like to play: ")
                try:
                    Player_Col = validate_int(userInput, min_val=0, max_val=6)
                    break
                except ValidationError as e:
                    print(e)

            try:
                self.board.make_move(Player_Col, 1)
            except ValueError as e:
                print(e)
                continue

            # self.board.display()

            if self.board.check_winner(1):
                playing = False
                print("Player Wins!")
                break

            if self.board.is_full():
                playing = False
                print("Tie Game!")
                break

            CPU_col = CPU_Choice(self.board)
            self.board.make_move(CPU_col, 0)

            os.system('cls')

            self.board.display()

            if self.board.check_winner(0):
                playing = False
                print("CPU Wins!")
                break

            if self.board.is_full():
                playing = False
                print("Tie Game!")
                break

if __name__ == "__main__":
    os.system('cls')
    running = True
    while running:
        game = ConnectFourGame()
        while True: # loop until valid input
            userInput = input("Would you like to go first? (y or n): ")
            try:
                userInput = validate_char(userInput, {'y', 'n'})
                break
            except ValidationError as e:
                print(e)
        if userInput == 'y':
            game.start(1)
        elif userInput == 'n':
            game.start(0)
        
        while True: # loop until valid input
            userInput = input("Would you like to play again? (y or n): ")
            try:
                userInput = validate_char(userInput, {'y', 'n'})
                break
            except ValidationError as e:
                print(e)
        if userInput == 'n':
            print("Thanks For Playing!")
            running = False
            break
    