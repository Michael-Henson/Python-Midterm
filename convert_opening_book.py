# convert_opening_book.py
from pathlib import Path

IN_FILE = r"c:\Users\13mic\Downloads\connect+4\connect-4.data\connect-4.data"
OUT_FILE = "opening_book.py"

RESULT_MAP = {"win": 1, "draw": 0, "loss": -1}

def encode_bitboards(cells_42):
    """
    cells_42: list of 42 strings: ['b','b',...]
    Ordering in file is column-major, bottom->top, col 0..6:
      index = col*6 + row (row 0 bottom .. row 5 top)

    Your bit index is:
      bit = col*7 + row
    """
    x_board = 0
    o_board = 0
    for col in range(7):
        for row in range(6):
            v = cells_42[col * 6 + row]
            bit = 1 << (col * 7 + row)
            if v == "x":
                x_board |= bit
            elif v == "o":
                o_board |= bit
    return x_board, o_board

def main():
    lines = Path(IN_FILE).read_text().splitlines()

    # Write as a dict literal in a .py for fast import
    out = []
    out.append("# Auto-generated from connect-4.data\n")
    out.append("OPENING_PLY = 8\n")
    out.append("BOOK = {\n")

    count = 0
    for line in lines:
        parts = line.strip().split(",")
        if len(parts) != 43:
            continue
        cells = parts[:42]
        result = parts[42].strip().lower()
        if result not in RESULT_MAP:
            continue
        x_board, o_board = encode_bitboards(cells)
        out.append(f"    ({x_board}, {o_board}): {RESULT_MAP[result]},\n")
        count += 1

    out.append("}\n")
    out.append(f"SIZE = {count}\n")

    Path(OUT_FILE).write_text("".join(out))
    print(f"Wrote {OUT_FILE} with {count} entries.")

if __name__ == "__main__":
    main()