from CPUMinMax import MinMax
class CPUPlayer:

    def CPU_Choice(board):
        choice1 = MinMax.MinMaxCalculate(board)
        # run top down minmax
        return 0