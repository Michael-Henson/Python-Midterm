from board import ConnectFourBoard
from input_validator import validate_char, validate_int, ValidationError
from CPUAlgorithm import MinMax
import os

class ConnectFourGame:
    """Represents a Connect 4 game. Manages board and players."""

    def __init__(self):
        """Initialize a new game"""
        # Set up board
        self.board = ConnectFourBoard()

    
    
    def check_board_state(self, turn):
        #checks if a winning move was made
        if self.board.check_winner(turn): 
            if turn == 1: print("Player Wins!")
            if turn == 0: print("CPU Wins!")
            return False

        if self.board.is_full():
            print("Tie Game!")
            return False
        return True
    
    def start(self, turn):
        round = 1
        CPU = MinMax()
        # if CPU goes first, play middle
        if turn == 0:
                self.board.make_move(3, 0)
                round += 1
        
        # clear the terminal and display the board state
        os.system('cls')
        self.board.display()

        # main game loop
        playing = True
        while playing: 
            
            # loop until valid user input for play column
            while True: 
                userInput = input("Where would you like to play: ")
                try:
                    Player_Col = validate_int(userInput, min_val=0, max_val=6)
                    break
                except ValidationError as e:
                    print(e)

            # attempt to play in user's choice, continue if invalid
            try:
                self.board.make_move(Player_Col, 1)
            except ValueError as e:
                print(e)
                continue
            
            # check if the Player won or tied
            playing = self.check_board_state(1) 
            if not playing: break

            round += 1

            # CPU Turn
            CPU_col = CPU.MinMaxCalculate(self.board)
            self.board.make_move(CPU_col, 0)

            # clear the terminal and display the board state
            os.system('cls')
            self.board.display()

            # check if the CPU won or tied
            playing = self.check_board_state(0) 
            if not playing: break

            round += 1

if __name__ == "__main__":
    
    # loop while playing the game
    running = True
    while running:
        game = ConnectFourGame()
        os.system('cls')

        # loop until valid user input for turn order
        while True: 
            userInput = input("Would you like to go first? (y or n): ")
            try:
                userInput = validate_char(userInput, {'y', 'n'})
                break
            except ValidationError as e:
                print(e)

        # starts game with either Player (1) first or CPU (0), goes to ConnectFourGame
        if userInput == 'y':
            game.start(1)
        elif userInput == 'n':
            game.start(0)
        
        # loop until valid input for play again
        while True: 
            userInput = input("Would you like to play again? (y or n): ")
            try:
                userInput = validate_char(userInput, {'y', 'n'})
                break
            except ValidationError as e:
                print(e)

        # end the game if user input 'n'
        if userInput == 'n':
            print("Thanks For Playing!")
            running = False
            break
    