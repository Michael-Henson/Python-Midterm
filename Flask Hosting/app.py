from __future__ import annotations

import uuid
from threading import Lock
from dataclasses import dataclass

from flask import Flask, jsonify, request, make_response, render_template

from board import ConnectFourBoard
from CPUAlgorithm import MinMax


app = Flask(__name__)

# In-memory game store (fine for a live presentation demo).
# For a production/multi-server environment you’d use Redis or a DB.
games_lock = Lock()
games: dict[str, "Game"] = {}


@dataclass
class Game:
    board: ConnectFourBoard
    ai: MinMax
    # You can add statistics here later if you want (nodes searched, depth, etc.)

def start_new_game_cpu_first() -> Game:
    g = Game(board=ConnectFourBoard(), ai=MinMax())

    # CPU plays first move immediately (so clients always see CPU start)
    cpu_col = g.ai.MinMaxCalculate(g.board)
    if cpu_col in g.board.get_valid_moves():
        g.board.make_move(cpu_col, 0)  # CPU = 0

    return g


def get_game_id() -> str:
    gid = request.cookies.get("c4_gid")
    if not gid:
        gid = str(uuid.uuid4())
    return gid


def get_or_create_game(gid: str) -> Game:
    with games_lock:
        g = games.get(gid)
        if g is None:
            g = start_new_game_cpu_first()
            games[gid] = g
        return g


def board_to_matrix(board: ConnectFourBoard) -> list[list[str]]:
    """
    Returns a 6x7 matrix of 'X' (player), 'O' (CPU), ' ' (empty).
    Row 0 is the TOP visually.
    Your bitboard uses row 0 as bottom, so we flip for display.
    """
    out = []
    for vis_row in range(board.num_rows):  # 0..5 (top->bottom visually)
        r = (board.num_rows - 1) - vis_row  # map to internal row
        row_cells = []
        for c in range(board.num_cols):
            if board.is_self_occupied(1, c, r):
                row_cells.append(board.player_token)  # 'X'
            elif board.is_self_occupied(0, c, r):
                row_cells.append(board.cpu_token)     # 'O'
            else:
                row_cells.append(board.empty_token)   # ' '
        out.append(row_cells)
    return out


def game_status(game: Game) -> dict:
    board = game.board

    winner = None
    if board.check_winner(1):
        winner = "PLAYER"
    elif board.check_winner(0):
        winner = "CPU"
    elif board.is_full():
        winner = "DRAW"

    return {
        "grid": board_to_matrix(board),
        "valid_moves": board.get_valid_moves(),
        "winner": winner,
    }


@app.get("/")
def index():
    gid = get_game_id()
    _ = get_or_create_game(gid)
    resp = make_response(render_template("index.html"))
    resp.set_cookie("c4_gid", gid, samesite="Lax")
    return resp


@app.get("/api/state")
def api_state():
    gid = get_game_id()
    game = get_or_create_game(gid)
    resp = jsonify(game_status(game))
    resp.set_cookie("c4_gid", gid, samesite="Lax")
    return resp


@app.post("/api/reset")
def api_reset():
    gid = get_game_id()
    with games_lock:
        games[gid] = start_new_game_cpu_first()
    resp = jsonify(game_status(games[gid]))
    resp.set_cookie("c4_gid", gid, samesite="Lax")
    return resp


@app.post("/api/move")
def api_move():
    gid = get_game_id()
    game = get_or_create_game(gid)
    board = game.board
    ai = game.ai

    data = request.get_json(silent=True) or {}
    if "col" not in data:
        return jsonify({"error": "Missing 'col'"}), 400

    # If already over, just return current state
    status = game_status(game)
    if status["winner"] is not None:
        return jsonify(status)

    try:
        col = int(data["col"])
    except Exception:
        return jsonify({"error": "Column must be an integer"}), 400

    if col not in board.get_valid_moves():
        return jsonify({"error": "Invalid move"}), 400

    # 1) Player move
    try:
        board.make_move(col, 1)  # PLAYER = 1
    except Exception as e:
        return jsonify({"error": str(e)}), 400

    # Check if player ended the game
    status = game_status(game)
    if status["winner"] is not None:
        return jsonify(status)

    # 2) CPU move
    cpu_col = ai.MinMaxCalculate(board)
    if cpu_col in board.get_valid_moves():  # safety
        board.make_move(cpu_col, 0)  # CPU = 0

    return jsonify(game_status(game))


if __name__ == "__main__":
    # For local testing:
    app.run(host="0.0.0.0", port=5000, debug=True)