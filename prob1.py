# To check the output , there will be a file "test1_maze.html" therefore run that file in the browser.

import argparse
import csv
import glob
import os
import random
import sys
from collections import deque

DOOR_CHARS = "ABCDGF"
DIRS = [(-1, 0), (1, 0), (0, -1), (0, 1)]

ANSI_PAIR = [208, 129, 33, 226, 205, 94]
HTML_PAIR = ["#ff9800", "#9c27b0", "#2196f3", "#ffeb3b", "#ff69b4", "#8d6e63"]

def key_idx(ch):
    return ord(ch) - ord("a") if "a" <= ch <= "f" else -1

def door_idx(ch):
    return DOOR_CHARS.find(ch) if ch in DOOR_CHARS else -1

def solve(grid):
    n = len(grid)
    start = None
    for r in range(n):
        for c in range(n):
            if grid[r][c] == "S":
                start = (r, c)
    if start is None:
        return -1, []

    s0 = (start[0], start[1], 0)
    parent = {s0: None}
    dist = {s0: 0}
    q = deque([s0])
    while q:
        cur = q.popleft()
        r, c, mask = cur
        if grid[r][c] == "E":
            path = []
            while cur is not None:
                path.append((cur[0], cur[1]))
                cur = parent[cur]
            return dist[(r, c, mask)], path[::-1]
        for dr, dc in DIRS:
            nr, nc = r + dr, c + dc
            if not (0 <= nr < n and 0 <= nc < n):
                continue
            ch = grid[nr][nc]
            if ch == "#":
                continue
            di = door_idx(ch)
            if di >= 0 and not (mask >> di) & 1:
                continue
            nm = mask
            ki = key_idx(ch)
            if ki >= 0:
                nm |= 1 << ki
            nxt = (nr, nc, nm)
            if nxt not in parent:
                parent[nxt] = cur
                dist[nxt] = dist[cur] + 1
                q.append(nxt)
    return -1, []

def read_csv(filename):
    grid = []
    with open(filename, newline="") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            if "," in line:
                row = [(t.strip()[:1] or ".") for t in line.split(",")]
            else:
                row = list(line)
            grid.append("".join(row))
    n = len(grid)
    if n == 0:
        raise ValueError("empty grid")
    if any(len(r) != n for r in grid):
        raise ValueError("grid is not N x N")
    flat = "".join(grid)
    if flat.count("S") != 1 or flat.count("E") != 1:
        raise ValueError("grid needs exactly one 'S' and one 'E'")
    return grid

def write_csv(filename, grid):
    with open(filename, "w", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        for row in grid:
            w.writerow(list(row))

def generate_maze(n, t, seed=None):
    if not 1 <= t <= 6:
        raise ValueError("T must be between 1 and 6")
    if n * n < 2 + 2 * t:
        raise ValueError("grid too small for T keys and T doors")
    rng = random.Random(seed)
    wall_prob = 0.30
    for attempt in range(1, 5001):
        if attempt % 250 == 0 and wall_prob > 0.05:
            wall_prob -= 0.05
        g = [["#" if rng.random() < wall_prob else "." for _ in range(n)] for _ in range(n)]
        cells = rng.sample(range(n * n), 2 + 2 * t)
        specials = ["S", "E"]
        for i in range(t):
            specials += [chr(ord("a") + i), DOOR_CHARS[i]]
        for pos, ch in zip(cells, specials):
            g[pos // n][pos % n] = ch
        grid = ["".join(r) for r in g]
        if solve(grid)[0] != -1:
            return grid
    raise RuntimeError("could not generate a solvable maze")

def pair_id(ch):
    k = key_idx(ch)
    return k if k >= 0 else door_idx(ch)

def print_coloured(grid, path):
    path_set = set(path)
    for r, row in enumerate(grid):
        line = ""
        for c, ch in enumerate(row):
            on_path = (r, c) in path_set
            fg, bold, txt = "\033[30m", "", "  "
            if ch == "#":
                bg = "\033[40m"
            elif ch == "S":
                bg, txt = "\033[42m", "S "
            elif ch == "E":
                bg, txt, fg = "\033[41m", "E ", "\033[97m"
            elif pair_id(ch) >= 0:
                bg, txt = f"\033[48;5;{ANSI_PAIR[pair_id(ch)]}m", ch + " "
                if on_path:
                    bold = "\033[1;4m"
            elif on_path:
                bg, txt = "\033[46m", "x "
            else:
                bg = "\033[107m"
            line += f"{bg}{fg}{bold}{txt}\033[0m"
        print(line)
    print("Legend: white=open, black=wall, green=S, red=E, cyan(x)=path, coloured letters=key/door pairs (bold+underlined if used on path)")

def write_html(filename, grid, path, dist):
    path_set = set(path)
    rows = []
    for r, row in enumerate(grid):
        cells = []
        for c, ch in enumerate(row):
            on_path = (r, c) in path_set
            bg, color, txt = "#fff", "#000", ""
            if ch == "#":
                bg = "#000"
            elif ch == "S":
                bg, txt = "#4caf50", "S"
            elif ch == "E":
                bg, color, txt = "#f44336", "#fff", "E"
            elif pair_id(ch) >= 0:
                bg, txt = HTML_PAIR[pair_id(ch)], ch
            elif on_path:
                bg, txt = "#80deea", "x"
            cls = "p" if on_path else ""
            cells.append(f"<td class='{cls}' style='background:{bg};color:{color}'>{txt}</td>")
        rows.append("<tr>" + "".join(cells) + "</tr>")
    html = (
        "<!DOCTYPE html><html><head><meta charset='utf-8'><title>Maze</title><style>"
        "body{font-family:sans-serif}table{border-collapse:collapse}"
        "td{width:36px;height:36px;text-align:center;font-weight:bold;border:1px solid #888}"
        ".p{outline:3px solid #00bcd4;outline-offset:-3px}</style></head><body>"
        f"<h3>Shortest path length: {dist}</h3><table>{''.join(rows)}</table>"
        "<p>White=open, Black=wall, Green=S, Red=E, each key/door pair has its own colour, cyan outline = path taken.</p></body></html>"
    )
    with open(filename, "w", encoding="utf-8") as f:
        f.write(html)

def process(grid, base):
    dist, path = solve(grid)
    print(f"\n=== {base} ===")
    print(f"Shortest path length: {dist}\n")

    out = [list(r) for r in grid]
    for r, c in path:
        if out[r][c] == ".":
            out[r][c] = "x"
    out = ["".join(r) for r in out]

    print_coloured(grid, path)
    written = []
    if dist != -1:
        write_csv(base + "_output.csv", out)
        written.append(base + "_output.csv")
    else:
        print("No path exists, so no output CSV was written.")
    write_html(base + "_maze.html", grid, path, dist)
    written.append(base + "_maze.html")
    print("Files written:", ", ".join(written))
    return dist

def find_default_input():
    for cand in ("test1.csv", os.path.join("tests", "test1.csv"),
                 os.path.join(os.path.dirname(os.path.abspath(__file__)), "test1.csv"),
                 os.path.join(os.path.dirname(os.path.abspath(__file__)), "tests", "test1.csv")):
        if os.path.exists(cand):
            return cand
    return "test1.csv"

def main():
    ap = argparse.ArgumentParser(description="Maze with keys and doors")
    ap.add_argument("csv_file", nargs="?", help="input CSV (default: test1.csv)")
    ap.add_argument("--all", action="store_true", help="process every test*.csv in the folder")
    ap.add_argument("--random", type=int, metavar="N", help="generate a random N x N maze")
    ap.add_argument("--T", type=int, default=2, help="key/door types for --random (1..6)")
    ap.add_argument("--seed", type=int, default=None, help="random seed for --random")
    args = ap.parse_args()

    try:
        if args.random:
            grid = generate_maze(args.random, args.T, args.seed)
            write_csv("generated_maze.csv", grid)
            print("Generated maze saved to generated_maze.csv")
            process(grid, "generated_maze")
        elif args.all:
            files = glob.glob("test*.csv") or glob.glob(os.path.join("tests", "test*.csv"))
            files = sorted(f for f in files if not f.endswith("_output.csv"))
            if not files:
                sys.exit("No test*.csv files found")
            for f in files:
                process(read_csv(f), os.path.splitext(f)[0])
        else:
            f = args.csv_file or find_default_input()
            process(read_csv(f), os.path.splitext(f)[0])
    except (OSError, ValueError, RuntimeError) as e:
        sys.exit(f"Error: {e}")

if __name__ == "__main__":
    main()