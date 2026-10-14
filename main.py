
import tkinter as tk
import random, csv
from pathlib import Path
from collections import deque

CELL = 48
DELAY = 250
COLORS = ["#f4c542", "#42a5f5", "#b388ff", "#ff9848", "#32c9a0", "#f47bb8"]
BG, PANEL, BLUE = "#101722", "#1c293b", "#38a9ff"


def generate(T):
    N = max(6, 2 * T + 2)
    g = [["." for _ in range(N)] for _ in range(N)]

    route = [(0, c) for c in range(N)]
    route += [(r, N - 1) for r in range(1, N)]

    for r in range(N):
        for c in range(N):
            if (r, c) not in route and random.random() < 0.25:
                g[r][c] = "#"

    g[0][0], g[N-1][N-1] = "S", "E"

    for i in range(T):
        g[0][2*i+1] = chr(97+i)
        g[0][2*i+2] = "DOOR_" + chr(65+i)

    return g


def solve(g):
    N = len(g)
    q = deque([((0, 0, 0), 0)])
    parent = {(0, 0, 0): None}
    directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]

    while q:
        (r, c, keys), dist = q.popleft()

        if (r, c) == (N-1, N-1):
            path, s = [], (r, c, keys)
            while s is not None:
                path.append(s[:2])
                s = parent[s]
            return dist, path[::-1]

        for dr, dc in directions:
            nr, nc = r+dr, c+dc
            if not (0 <= nr < N and 0 <= nc < N):
                continue

            cell = g[nr][nc]
            if cell == "#":
                continue

            nk = keys

            if isinstance(cell, str) and cell.startswith("DOOR_"):
                bit = 1 << (ord(cell[-1]) - 65)
                if not keys & bit:
                    continue
            elif len(cell) == 1 and "a" <= cell <= "f":
                nk |= 1 << (ord(cell) - 97)

            state = (nr, nc, nk)
            if state not in parent:
                parent[state] = (r, c, keys)
                q.append((state, dist+1))

    return -1, []


def save_csv(g, path):
    out = [row[:] for row in g]

    for r, c in path:
        v = g[r][c]
        if v == ".":
            out[r][c] = "x"
        elif isinstance(v, str) and v.startswith("DOOR_"):
            out[r][c] = f"x({v[-1]})"
        elif len(v) == 1 and "a" <= v <= "f":
            out[r][c] = f"x({v})"

    file = Path(__file__).resolve().parent / "maze_solution.csv"
    with open(file, "w", newline="", encoding="utf-8") as f:
        csv.writer(f).writerows(out)
    print("CSV saved:", file)


class MazeApp:
    def __init__(self, root, T):
        self.root, self.T = root, T
        root.title("MazeQuest - Keys & Doors")
        root.configure(bg=BG)

        tk.Label(root, text="MAZE QUEST", bg=BG, fg=BLUE,
                 font=("Arial", 22, "bold")).pack(pady=10)

        self.status = tk.Label(root, bg=BG, fg="white",
                               font=("Arial", 11))
        self.status.pack()

        self.canvas = tk.Canvas(root, bg=BG, highlightthickness=0)
        self.canvas.pack(padx=15, pady=10)

        self.inventory = tk.Label(root, bg=PANEL, fg="white",
                                  font=("Arial", 11), padx=10, pady=8)
        self.inventory.pack(fill="x", padx=15)

        buttons = tk.Frame(root, bg=BG)
        buttons.pack(pady=12)

        for text, cmd in [
            ("▶ Start", self.start),
            ("Ⅱ Pause / Resume", self.pause),
            ("↻ Restart", self.restart),
            ("Show Path", self.show_path),
            ("New Maze", self.new_maze)
        ]:
            tk.Button(buttons, text=text, command=cmd,
                      bg=PANEL, fg="white", activebackground=BLUE,
                      relief="flat", padx=9, pady=8).pack(side="left", padx=3)

        self.new_maze()

    def new_maze(self):
        if hasattr(self, "job") and self.job:
            self.root.after_cancel(self.job)
        self.job = None
        self.running = self.paused = False
        self.g = generate(self.T)
        self.dist, self.path = solve(self.g)
        self.i, self.keys, self.opened = 0, set(), set()
        self.seen = set()
        save_csv(self.g, self.path)
        self.draw()

    def draw(self):
        self.canvas.delete("all")
        N = len(self.g)
        cell = min(CELL, 600 // N)
        self.cell = cell
        self.canvas.config(width=N*cell, height=N*cell)

        for r in range(N):
            for c in range(N):
                v = self.g[r][c]
                x, y = c*cell, r*cell
                color, label = "#f7f9fc", ""

                if v == "#":
                    color = "#263449"
                elif v == "S":
                    color, label = "#20bd78", "S"
                elif v == "E":
                    color, label = "#ed5262", "E"
                elif isinstance(v, str) and v.startswith("DOOR_"):
                    k = v[-1].lower()
                    color = "#ffffff" if k in self.opened else COLORS[ord(k)-97]
                    label = "✓" if k in self.opened else v[-1]
                elif len(v) == 1 and "a" <= v <= "f":
                    color = "#f7f9fc" if v in self.keys else COLORS[ord(v)-97]
                    label = "" if v in self.keys else v

                if (r, c) in self.seen and v not in ("S", "E"):
                    if not (isinstance(v, str) and v.startswith("DOOR_")
                            and v[-1].lower() in self.opened):
                        if not (len(v) == 1 and v in self.keys):
                            color = "#a9d9ff"

                self.canvas.create_rectangle(x, y, x+cell, y+cell,
                                             fill=color, outline="#526177")
                if label:
                    self.canvas.create_text(x+cell/2, y+cell/2, text=label,
                                            fill="#172235",
                                            font=("Arial", max(9, cell//3), "bold"))

        if self.i > 0 and self.path:
            r, c = self.path[min(self.i-1, len(self.path)-1)]
            m = cell*0.22
            self.canvas.create_oval(c*cell+m, r*cell+m,
                                    (c+1)*cell-m, (r+1)*cell-m,
                                    fill="#ffffff", outline=BLUE, width=3)

        self.inventory.config(
            text="Keys: " + (", ".join(sorted(self.keys)) or "None")
            + f"       |       Steps: {max(0, self.i-1)}"
            + f"       |       Shortest path: {self.dist}"
        )

    def start(self):
        if self.dist < 0:
            self.status.config(text="No solution found")
            return
        if self.i >= len(self.path):
            self.restart()
        self.running, self.paused = True, False
        self.status.config(text="Solving maze...")
        self.animate()

    def pause(self):
        if not self.running:
            return
        self.paused = not self.paused
        if not self.paused:
            self.animate()
        else:
            self.status.config(text="Paused")

    def restart(self):
        if self.job:
            self.root.after_cancel(self.job)
        self.job = None
        self.i, self.keys, self.opened, self.seen = 0, set(), set(), set()
        self.running = self.paused = False
        self.status.config(text="Ready")
        self.draw()

    def animate(self):
        if not self.running or self.paused:
            return
        if self.i >= len(self.path):
            self.running = False
            self.status.config(text="Maze solved!")
            return

        r, c = self.path[self.i]
        v = self.g[r][c]
        self.seen.add((r, c))

        if isinstance(v, str) and v.startswith("DOOR_"):
            self.opened.add(v[-1].lower())
            self.status.config(text=f"Door {v[-1]} unlocked!")
        elif len(v) == 1 and "a" <= v <= "f":
            self.keys.add(v)
            self.status.config(text=f"Key {v} collected!")

        self.i += 1
        self.draw()
        self.job = self.root.after(DELAY, self.animate)

    def show_path(self):
        if self.job:
            self.root.after_cancel(self.job)
        self.job = None
        self.running = self.paused = False
        self.seen = set(self.path)
        self.keys = {self.g[r][c] for r, c in self.path
                     if len(self.g[r][c]) == 1
                     and "a" <= self.g[r][c] <= "f"}
        self.opened = {self.g[r][c][-1].lower() for r, c in self.path
                       if isinstance(self.g[r][c], str)
                       and self.g[r][c].startswith("DOOR_")}
        self.i = len(self.path)
        self.status.config(text="Shortest path highlighted")
        self.draw()


def main():
    while True:
        try:
            T = int(input("Enter number of key/door pairs (1-6): "))
            if 1 <= T <= 6:
                break
        except ValueError:
            pass
        print("Enter an integer from 1 to 6.")

    root = tk.Tk()
    MazeApp(root, T)
    root.mainloop()


if __name__ == "__main__":
    main()
