import random
import math

class MinMax:
    """
    A reasonably strong Connect 4 CPU using:
      - immediate win
      - immediate block
      - minimax with alpha-beta + heuristic scoring
    """
    def __init__(self, name="CPU", depth=8, seed=None):
        self.depth = depth
        self.rng = random.Random(seed)

    def MinMaxCalculate(self, board):
        