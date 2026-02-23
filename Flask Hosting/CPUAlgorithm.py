import math
from opening_book import BOOK


class MinMax:
    """
    Connect 4 CPU using:
      - negamax
      - alpha-beta
      - transposition table
      - 'suicide move' filter
      - opening book (play 8 positions in opening_book.py)
    """

    # TT flags
    depth_max = 8 # determines how deep the algorithm scans. Larger number is smarter but slower
    
    EXACT = 0
    LOWER = 1
    UPPER = 2

    # turn designations
    CPU = 0
    PLAYER = 1

    # score multipliers
    MATE_SCORE = 10_000_000 # largest score
    BOOK_SCORE = 5_000_000  # below mate score, above heuristic

    def __init__(self, shared_tt=None, tt_lock=None):
        self.tt = shared_tt if shared_tt is not None else {}
        self.tt_lock = tt_lock

    def tt_key(self, board, to_move: int):
        # IMPORTANT: This assumes score sign is derived from to_move inside _negamax.
        return (board.cpu_board, board.player_board, to_move)

    # Opening book lookup
    def book_lookup(self, board, to_move: int):
        moves_played = (board.cpu_board | board.player_board).bit_count()
        # checks if it is move 8
        if moves_played != 8:
            return None

        # toggle for turn
        if to_move == self.CPU:
            x_board = board.cpu_board
            o_board = board.player_board
        else:
            x_board = board.player_board
            o_board = board.cpu_board

        v = BOOK.get((x_board, o_board))
        if v is not None:
            return v

        # Mirror fallback (Connect 4 is symmetric under horizontal reflection)
        mx = self.mirror_bitboard(x_board)
        mo = self.mirror_bitboard(o_board)
        return BOOK.get((mx, mo))
    
    def mirror_bitboard(self, bb: int) -> int:
        out = 0
        for col in range(7):
            mcol = 6 - col
            for row in range(6):
                bit = 1 << (col * 7 + row)
                if bb & bit:
                    out |= 1 << (mcol * 7 + row)
        return out

    # ---------- game entry point ----------
    def MinMaxCalculate(self, board):
        moves_played = (board.cpu_board | board.player_board).bit_count()
        empties = 42 - moves_played

        # variable depth
        if moves_played < 8:
            max_depth = 8 # opening: doesnt need to go past opening book
        elif empties <= self.depth_max:
            max_depth = empties # endgame: doent need to extened past the end of the game
        else:
            max_depth = self.depth_max # midmage: past opening book before endgame

        # TT size cap
        if len(self.tt) > 2_000_000:
            self.tt.clear()

        # check for playable positions
        valid_moves = board.get_valid_moves()
        if not valid_moves:
            return 0

        '''
        Decision making starts here

        - Priority
        1. Imediate win
        2. Immediate block
        3. Stored TT move
        4. New Calculation
        '''
        # Immediate win
        for col in valid_moves:
            board.make_move(col, self.CPU)
            win = board.check_winner(self.CPU)
            board.undo_move()
            if win:
                return col

        # Immediate block
        for col in valid_moves:
            board.make_move(col, self.PLAYER)
            opp_win = board.check_winner(self.PLAYER)
            board.undo_move()
            if opp_win:
                return col

        # Root move ordering baseline: center first
        base_order = sorted(valid_moves, key=lambda c: abs(3 - c))

        # If TT already has a best move for the root, try it first
        root_key = self.tt_key(board, self.CPU)
        root_tt = self.tt.get(root_key)
        if root_tt is not None:
            _, _, _, root_best = root_tt
            if root_best in valid_moves:
                base_order.remove(root_best)
                base_order.insert(0, root_best)

        # Iterative deepening: depth 1 to self.depth
        best_move = base_order[0]
        best_score = -math.inf

        for d in range(1, max_depth + 1):
            alpha, beta = -math.inf, math.inf
            cur_best_move = best_move
            cur_best_score = -math.inf

            # Try last iteration's best move first
            ordered = base_order[:]
            if cur_best_move in ordered:
                ordered.remove(cur_best_move)
                ordered.insert(0, cur_best_move)

            for col in ordered:
                # make move, calculate score, undo move, repeat
                board.make_move(col, self.CPU)

                # after CPU move, it's PLAYER to move; negate because negamax return is from side-to-move
                score = -self.negamax(board, d - 1, -beta, -alpha, self.PLAYER)

                board.undo_move()

                # check if move is better than stored best
                if score > cur_best_score:
                    cur_best_score = score
                    cur_best_move = col

                alpha = max(alpha, cur_best_score)
                if alpha >= beta:
                    break

            best_move = cur_best_move
            best_score = cur_best_score

            # Optional early exit: if we found a forced win at this depth, keep it
            if best_score >= self.MATE_SCORE - 1000:
                break

        return best_move

    # ---------- Negamax ----------
    def negamax(self, board, depth, alpha, beta, to_move):
        """
        Returns a score in negamax form where higher is better for the side to move,
        but the sign is derived from to_move so TT is consistent:
          color = +1 when to_move==CPU, -1 when to_move==PLAYER
          return color * (CPU-perspective score)
        """
        # Derive sign from to_move (this removes a whole class of TT sign bugs)
        color = 1 if to_move == self.CPU else -1

        # Terminal checks
        if board.check_winner(self.CPU):
            return color * (self.MATE_SCORE + depth)
        if board.check_winner(self.PLAYER):
            return color * (-self.MATE_SCORE - depth)
        if board.is_full():
            return 0

        # Opening book (exact at ply 8 for side-to-move)
        bk = self.book_lookup(board, to_move)
        if bk is not None:
            return color * (bk * self.BOOK_SCORE)

        # gives beter score for having more tiles in the middle
        if depth == 0:
            return color * self.evaluate(board)

        # generates TT key
        key = self.tt_key(board, to_move)

        # --- TT lookup (bounds + best move) ---
        if self.tt_lock:
            with self.tt_lock:
                tt_entry = self.tt.get(key)
        else:
            tt_entry = self.tt.get(key)
        tt_best = None
        alpha_orig = alpha
        beta_orig = beta

        if tt_entry is not None:
            tt_depth, tt_flag, tt_value, tt_best = tt_entry
            if tt_depth >= depth:
                if tt_flag == self.EXACT:
                    return tt_value
                elif tt_flag == self.LOWER:
                    alpha = max(alpha, tt_value)
                elif tt_flag == self.UPPER:
                    beta = min(beta, tt_value)
                if alpha >= beta:
                    return tt_value

        valid_moves = board.get_valid_moves()
        if not valid_moves:
            return 0

        # --- Move ordering: TT best first, then center preference ---
        ordered_moves = sorted(valid_moves, key=lambda c: abs(3 - c))
        if tt_best is not None and tt_best in valid_moves:
            ordered_moves.remove(tt_best)
            ordered_moves.insert(0, tt_best)

        best_value = -math.inf
        best_move = ordered_moves[0]

        opp = self.PLAYER if to_move == self.CPU else self.CPU

        for col in ordered_moves:
            board.make_move(col, to_move)

            # check if moves instantly wins
            if board.check_winner(to_move):
                # better score for faster wins
                score = self.MATE_SCORE + depth
                board.undo_move()

                if score > best_value:
                    best_value = score
                    best_move = col
                alpha = max(alpha, best_value)
                if alpha >= beta:
                    break
                continue

            # check for imediate opponent winning moves
            if depth <= 2:
                bad = False
                for rcol in board.get_valid_moves():
                    board.make_move(rcol, opp)
                    if board.check_winner(opp):
                        bad = True
                    board.undo_move()
                    if bad:
                        break
                if bad:
                    board.undo_move()
                    continue
            # run for next depth up
            score = -self.negamax(board, depth - 1, -beta, -alpha, opp)
            board.undo_move()

            if score > best_value:
                best_value = score
                best_move = col

            alpha = max(alpha, best_value)
            if alpha >= beta:
                break

        # --- TT store: EXACT / LOWER / UPPER ---
        if best_value <= alpha_orig:
            flag = self.UPPER
        elif best_value >= beta_orig:
            flag = self.LOWER
        else:
            flag = self.EXACT

        if self.tt_lock:
            with self.tt_lock:
                self.tt[key] = (depth, flag, best_value, best_move)
        else:
            self.tt[key] = (depth, flag, best_value, best_move)
        return best_value

    # ---------- Heuristic evaluation ----------
    def evaluate(self, board):
        # Positive = good for CPU, negative = good for Player.
        score = 0

        # Prefer center column occupation
        center_col = 3
        score += 6 * self.count_in_column(board, self.CPU, center_col)
        score -= 6 * self.count_in_column(board, self.PLAYER, center_col)

        score += self.score_windows(board)
        return score

    def count_in_column(self, board, turn, col):
        count = 0
        for row in range(board.num_rows):
            if board.is_self_occupied(turn, col, row):
                count += 1
        return count

    def score_windows(self, board):
        cpu = self.CPU
        player = self.PLAYER
        score = 0

        rows = board.num_rows
        cols = board.num_cols

        # Horizontal
        for row in range(rows):
            for col in range(cols - 3):
                window = [(col + i, row) for i in range(4)]
                score += self.score_window(board, window, cpu, player)

        # Vertical
        for col in range(cols):
            for row in range(rows - 3):
                window = [(col, row + i) for i in range(4)]
                score += self.score_window(board, window, cpu, player)

        # Diagonal /
        for col in range(cols - 3):
            for row in range(rows - 3):
                window = [(col + i, row + i) for i in range(4)]
                score += self.score_window(board, window, cpu, player)

        # Diagonal \
        for col in range(cols - 3):
            for row in range(3, rows):
                window = [(col + i, row - i) for i in range(4)]
                score += self.score_window(board, window, cpu, player)

        return score

    def score_window(self, board, window, cpu, player):
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

        # Weighting
        if cpu_count == 4:
            return 100000
        if cpu_count == 3 and empty_count == 1:
            return 200
        if cpu_count == 2 and empty_count == 2:
            return 20

        if player_count == 4:
            return -100000
        if player_count == 3 and empty_count == 1:
            return -220
        if player_count == 2 and empty_count == 2:
            return -25

        return 0