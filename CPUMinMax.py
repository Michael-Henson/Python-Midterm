import random
import math

class MinMax:
    """
    Connect 4 CPU:
      - immediate win
      - immediate block
      - minimax with alpha-beta pruning + heuristic scoring
    """

    CPU = 0
    PLAYER = 1

    def __init__(self, name="CPU", depth=7, seed=None):
        self.depth = depth
        self.rng = random.Random(seed)

    # ---------- Public entry point ----------
    def MinMaxCalculate(self, board):
        valid_moves = board.get_valid_moves()
        if not valid_moves:
            return 0

        # 1) Immediate winning move
        for col in valid_moves:
            board.make_move(col, self.CPU)
            win = board.check_winner(self.CPU)
            board.undo_move()
            if win:
                return col

        # 2) Immediate block
        for col in valid_moves:
            board.make_move(col, self.PLAYER)
            opp_win = board.check_winner(self.PLAYER)
            board.undo_move()
            if opp_win:
                return col

        # 3) Search
        best_score = -math.inf
        best_cols = []
        ordered_moves = sorted(valid_moves, key=lambda c: abs(3 - c))
        alpha, beta = -math.inf, math.inf

        for col in ordered_moves:
            board.make_move(col, self.CPU)
            score = self._minimax(board, self.depth - 1, alpha, beta, maximizing=False)
            board.undo_move()

            if score > best_score:
                best_score = score
                best_cols = [col]
            elif score == best_score:
                best_cols.append(col)

            alpha = max(alpha, best_score)
            if alpha >= beta:
                break

        return best_cols[0] if best_cols else ordered_moves[0]

    # ---------- Minimax core ----------
    def _minimax(self, board, depth, alpha, beta, maximizing):
        # Terminal checks
        if board.check_winner(self.CPU):
            return 10_000_000 + depth  # depth bonus: faster wins
        if board.check_winner(self.PLAYER):
            return -10_000_000 - depth  # depth penalty: slower losses
        if board.is_full():
            return 0
        if depth == 0:
            return self._evaluate(board)

        valid_moves = board.get_valid_moves()
        if not valid_moves:
            return 0

        ordered_moves = sorted(valid_moves, key=lambda c: abs(3 - c))

        if maximizing:
            value = -math.inf
            for col in ordered_moves:
                board.make_move(col, self.CPU)
                value = max(value, self._minimax(board, depth - 1, alpha, beta, False))
                board.undo_move()

                alpha = max(alpha, value)
                if alpha >= beta:
                    break
            return value
        else:
            value = math.inf
            for col in ordered_moves:
                board.make_move(col, self.PLAYER)
                value = min(value, self._minimax(board, depth - 1, alpha, beta, True))
                board.undo_move()

                beta = min(beta, value)
                if alpha >= beta:
                    break
            return value

    # ---------- Heuristic evaluation ----------
    def _evaluate(self, board):
        """
        Positive = good for CPU, negative = good for Player.
        This heuristic is strong enough for good play with depth 6–9.
        """
        score = 0

        # Prefer center column occupation
        center_col = 3
        center_count_cpu = self._count_in_column(board, self.CPU, center_col)
        center_count_player = self._count_in_column(board, self.PLAYER, center_col)
        score += 6 * center_count_cpu
        score -= 6 * center_count_player

        # Score all windows of length 4
        score += self._score_windows(board)
        return score

    def _count_in_column(self, board, turn, col):
        count = 0
        for row in range(board.num_rows):
            if board.is_self_occupied(turn, col, row):
                count += 1
        return count

    def _score_windows(self, board):
        cpu = self.CPU
        player = self.PLAYER
        score = 0

        rows = board.num_rows
        cols = board.num_cols

        # Horizontal
        for row in range(rows):
            for col in range(cols - 3):
                window = [(col + i, row) for i in range(4)]
                score += self._score_window(board, window, cpu, player)

        # Vertical
        for col in range(cols):
            for row in range(rows - 3):
                window = [(col, row + i) for i in range(4)]
                score += self._score_window(board, window, cpu, player)

        # Diagonal /
        for col in range(cols - 3):
            for row in range(rows - 3):
                window = [(col + i, row + i) for i in range(4)]
                score += self._score_window(board, window, cpu, player)

        # Diagonal \
        for col in range(cols - 3):
            for row in range(3, rows):
                window = [(col + i, row - i) for i in range(4)]
                score += self._score_window(board, window, cpu, player)

        return score

    def _score_window(self, board, window, cpu, player):
        cpu_count = 0
        player_count = 0
        empty_count = 0

        for (c, r) in window:
            if board.is_self_occupied(cpu, c, r):
                cpu_count += 1
            elif board.is_self_occupied(player, c, r):
                player_count += 1
            else:
                empty_count += 1

        # If both occupy the window, it's not useful
        if cpu_count > 0 and player_count > 0:
            return 0

        # Weighting (tuned common scheme)
        if cpu_count == 4:
            return 100000
        if cpu_count == 3 and empty_count == 1:
            return 200
        if cpu_count == 2 and empty_count == 2:
            return 20

        if player_count == 4:
            return -100000
        if player_count == 3 and empty_count == 1:
            return -220  # slightly stronger defense
        if player_count == 2 and empty_count == 2:
            return -25

        return 0