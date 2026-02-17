from CPUMinMax import MinMax

engine = MinMax(depth=9)

def CPU_Choice(board):
    return engine.MinMaxCalculate(board)