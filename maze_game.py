import random
import time
import tkinter as tk
from collections import deque


WALL_THICKNESS = 3

BG_MAIN = "#0b1220"
BG_PANEL = "#111a2d"
TEXT_PRIMARY = "#e5eefc"
TEXT_ACCENT = "#7dd3fc"
WALL_COLOR = "#f8fafc"
CELL_DARK = "#0f1a2f"
CELL_LIGHT = "#12203a"
PATH_TRAIL = "#38bdf8"
GOAL_COLOR = "#22c55e"
PLAYER_COLOR = "#fb923c"
PLAYER_WIN_COLOR = "#facc15"
SOLVE_PATH_COLOR = "#f472b6"

DIFFICULTIES = {
    "Easy": {"rows": 12, "cols": 16, "cell": 34},
    "Medium": {"rows": 18, "cols": 24, "cell": 28},
    "Hard": {"rows": 24, "cols": 32, "cell": 22},
}


class MazeGame:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Maze Runner")
        self.root.resizable(False, False)
        self.root.configure(bg=BG_MAIN)

        self.timer_job = None
        self.rows = 0
        self.cols = 0
        self.cell_size = 0

        self.header = tk.Frame(root, bg=BG_PANEL, padx=10, pady=8)
        self.header.pack(fill="x", padx=8, pady=(8, 4))

        self.title_label = tk.Label(
            self.header,
            text="MAZE RUNNER",
            font=("Trebuchet MS", 16, "bold"),
            fg=TEXT_PRIMARY,
            bg=BG_PANEL,
        )
        self.title_label.pack(anchor="w")

        self.info_var = tk.StringVar(value="Choose a difficulty to start")
        self.info_label = tk.Label(
            self.header,
            textvariable=self.info_var,
            font=("Segoe UI", 10, "bold"),
            fg=TEXT_ACCENT,
            bg=BG_PANEL,
        )
        self.info_label.pack(anchor="w", pady=(4, 0))

        self.action_row = tk.Frame(self.header, bg=BG_PANEL)
        self.action_row.pack(anchor="e", pady=(6, 0))
        self.finish_btn = tk.Button(
            self.action_row,
            text="Finish Path (BFS)",
            font=("Segoe UI", 9, "bold"),
            bg="#1d4ed8",
            fg="#ffffff",
            activebackground="#1e40af",
            activeforeground="#ffffff",
            relief="flat",
            padx=10,
            pady=4,
            state="disabled",
            cursor="hand2",
            command=self.show_shortest_path,
        )
        self.finish_btn.pack(side="left", padx=(0, 8))

        self.canvas = tk.Canvas(
            root,
            width=680,
            height=500,
            bg=BG_MAIN,
            highlightthickness=2,
            highlightbackground="#334155",
        )
        self.canvas.pack(padx=8, pady=(0, 8))

        self.menu = tk.Frame(root, bg=BG_MAIN)
        self.menu.place(relx=0.5, rely=0.56, anchor="center")

        menu_title = tk.Label(
            self.menu,
            text="SELECT DIFFICULTY",
            font=("Segoe UI", 14, "bold"),
            fg=TEXT_PRIMARY,
            bg=BG_MAIN,
        )
        menu_title.pack(pady=(0, 10))

        for level in ("Easy", "Medium", "Hard"):
            btn = tk.Button(
                self.menu,
                text=level,
                width=18,
                font=("Segoe UI", 11, "bold"),
                bg="#1e293b",
                fg=TEXT_PRIMARY,
                activebackground="#334155",
                activeforeground="#ffffff",
                relief="flat",
                cursor="hand2",
                command=lambda lv=level: self.start_with_difficulty(lv),
            )
            btn.pack(pady=4)

        self.help_label = tk.Label(
            root,
            text="Controls: Arrows/WASD move | R restart | M menu | Use Finish Path button for shortest route",
            font=("Segoe UI", 9),
            fg="#a5b4fc",
            bg=BG_MAIN,
        )
        self.help_label.pack(pady=(0, 8))

        self.root.bind("<KeyPress>", self.on_keypress)

    def start_with_difficulty(self, difficulty: str) -> None:
        settings = DIFFICULTIES[difficulty]
        self.rows = settings["rows"]
        self.cols = settings["cols"]
        self.cell_size = settings["cell"]
        self.current_difficulty = difficulty

        self.menu.place_forget()
        self.finish_btn.config(state="normal")
        self.new_game()

    def show_menu(self) -> None:
        if self.timer_job is not None:
            self.root.after_cancel(self.timer_job)
            self.timer_job = None

        self.canvas.delete("all")
        self.info_var.set("Choose a difficulty to start")
        self.finish_btn.config(state="disabled")
        self.menu.place(relx=0.5, rely=0.56, anchor="center")

    def new_game(self) -> None:
        if self.timer_job is not None:
            self.root.after_cancel(self.timer_job)
            self.timer_job = None

        self.start_time = time.time()
        self.steps = 0
        self.won = False
        self.hint_path = []
        self.maze = self.generate_maze(self.rows, self.cols)
        self.player = [0, 0]
        self.goal = [self.rows - 1, self.cols - 1]

        canvas_w = self.cols * self.cell_size + 2
        canvas_h = self.rows * self.cell_size + 2
        self.canvas.config(width=canvas_w, height=canvas_h)

        self.draw()
        self.update_info()

    def generate_maze(self, rows: int, cols: int):
        maze = [[{"N": True, "S": True, "E": True, "W": True, "visited": False} for _ in range(cols)] for _ in range(rows)]

        stack = [(0, 0)]
        maze[0][0]["visited"] = True

        while stack:
            r, c = stack[-1]
            neighbors = []

            if r > 0 and not maze[r - 1][c]["visited"]:
                neighbors.append(("N", r - 1, c))
            if r < rows - 1 and not maze[r + 1][c]["visited"]:
                neighbors.append(("S", r + 1, c))
            if c > 0 and not maze[r][c - 1]["visited"]:
                neighbors.append(("W", r, c - 1))
            if c < cols - 1 and not maze[r][c + 1]["visited"]:
                neighbors.append(("E", r, c + 1))

            if neighbors:
                direction, nr, nc = random.choice(neighbors)
                if direction == "N":
                    maze[r][c]["N"] = False
                    maze[nr][nc]["S"] = False
                elif direction == "S":
                    maze[r][c]["S"] = False
                    maze[nr][nc]["N"] = False
                elif direction == "W":
                    maze[r][c]["W"] = False
                    maze[nr][nc]["E"] = False
                else:
                    maze[r][c]["E"] = False
                    maze[nr][nc]["W"] = False

                maze[nr][nc]["visited"] = True
                stack.append((nr, nc))
            else:
                stack.pop()

        for row in maze:
            for cell in row:
                del cell["visited"]

        return maze

    def can_move(self, dr: int, dc: int) -> bool:
        r, c = self.player
        cell = self.maze[r][c]
        if dr == -1 and not cell["N"]:
            return True
        if dr == 1 and not cell["S"]:
            return True
        if dc == -1 and not cell["W"]:
            return True
        if dc == 1 and not cell["E"]:
            return True
        return False

    def get_neighbors(self, r: int, c: int):
        cell = self.maze[r][c]
        if not cell["N"] and r > 0:
            yield (r - 1, c)
        if not cell["S"] and r < self.rows - 1:
            yield (r + 1, c)
        if not cell["W"] and c > 0:
            yield (r, c - 1)
        if not cell["E"] and c < self.cols - 1:
            yield (r, c + 1)

    def solve_shortest_path_bfs(self):
        start = tuple(self.player)
        target = tuple(self.goal)
        queue = deque([start])
        parent = {start: None}

        while queue:
            node = queue.popleft()
            if node == target:
                break
            for nxt in self.get_neighbors(node[0], node[1]):
                if nxt not in parent:
                    parent[nxt] = node
                    queue.append(nxt)

        if target not in parent:
            return []

        path = []
        cur = target
        while cur is not None:
            path.append(cur)
            cur = parent[cur]
        path.reverse()
        return path

    def show_shortest_path(self) -> None:
        if self.rows == 0 or self.cols == 0 or self.won:
            return
        self.hint_path = self.solve_shortest_path_bfs()
        self.draw()

    def on_keypress(self, event: tk.Event) -> None:
        key = event.keysym
        key_l = key.lower()

        if key_l == "m":
            self.show_menu()
            return

        if key_l == "r":
            if self.rows > 0 and self.cols > 0:
                self.new_game()
            return

        if self.rows == 0 or self.cols == 0:
            return

        if self.won:
            return

        moves = {
            "Up": (-1, 0),
            "Down": (1, 0),
            "Left": (0, -1),
            "Right": (0, 1),
            "w": (-1, 0),
            "s": (1, 0),
            "a": (0, -1),
            "d": (0, 1),
        }

        if key not in moves:
            return

        dr, dc = moves[key]
        if not self.can_move(dr, dc):
            return

        self.player[0] += dr
        self.player[1] += dc
        self.steps += 1
        self.hint_path = []

        if self.player == self.goal:
            self.won = True

        self.draw()
        self.update_info()

    def update_info(self) -> None:
        if self.rows == 0 or self.cols == 0:
            self.info_var.set("Choose a difficulty to start")
            return

        if self.won:
            elapsed = time.time() - self.start_time
            self.info_var.set(
                f"{self.current_difficulty} cleared! Steps: {self.steps} | Time: {elapsed:.1f}s | R restart | M menu"
            )
            if self.timer_job is not None:
                self.root.after_cancel(self.timer_job)
                self.timer_job = None
            return
        else:
            elapsed = time.time() - self.start_time
            self.info_var.set(
                f"{self.current_difficulty} | Steps: {self.steps} | Time: {elapsed:.1f}s | Reach E"
            )
            if self.timer_job is not None:
                self.root.after_cancel(self.timer_job)
            self.timer_job = self.root.after(150, self.update_info)

    def draw(self) -> None:
        self.canvas.delete("all")

        for r in range(self.rows):
            for c in range(self.cols):
                x1 = c * self.cell_size + 1
                y1 = r * self.cell_size + 1
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size
                cell = self.maze[r][c]

                tile_color = CELL_LIGHT if (r + c) % 2 == 0 else CELL_DARK
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=tile_color, outline="")

                if cell["N"]:
                    self.canvas.create_line(x1, y1, x2, y1, width=WALL_THICKNESS, fill=WALL_COLOR)
                if cell["S"]:
                    self.canvas.create_line(x1, y2, x2, y2, width=WALL_THICKNESS, fill=WALL_COLOR)
                if cell["W"]:
                    self.canvas.create_line(x1, y1, x1, y2, width=WALL_THICKNESS, fill=WALL_COLOR)
                if cell["E"]:
                    self.canvas.create_line(x2, y1, x2, y2, width=WALL_THICKNESS, fill=WALL_COLOR)

        if self.hint_path:
            for idx, (r, c) in enumerate(self.hint_path):
                cx = c * self.cell_size + self.cell_size / 2 + 1
                cy = r * self.cell_size + self.cell_size / 2 + 1
                rad = max(2, int(self.cell_size * 0.12))
                self.canvas.create_oval(cx - rad, cy - rad, cx + rad, cy + rad, fill=SOLVE_PATH_COLOR, outline="")
                if idx > 0:
                    pr, pc = self.hint_path[idx - 1]
                    px = pc * self.cell_size + self.cell_size / 2 + 1
                    py = pr * self.cell_size + self.cell_size / 2 + 1
                    self.canvas.create_line(px, py, cx, cy, fill=SOLVE_PATH_COLOR, width=max(2, int(self.cell_size * 0.18)))

        sx1 = 0 * self.cell_size + 8
        sy1 = 0 * self.cell_size + 8
        sx2 = sx1 + self.cell_size - 14
        sy2 = sy1 + self.cell_size - 14
        self.canvas.create_rectangle(sx1, sy1, sx2, sy2, fill=PATH_TRAIL, outline="")
        self.canvas.create_text((sx1 + sx2) / 2, (sy1 + sy2) / 2, text="S", fill=BG_MAIN, font=("Segoe UI", 9, "bold"))

        gx1 = self.goal[1] * self.cell_size + 6
        gy1 = self.goal[0] * self.cell_size + 6
        gx2 = gx1 + self.cell_size - 10
        gy2 = gy1 + self.cell_size - 10
        self.canvas.create_rectangle(gx1, gy1, gx2, gy2, fill=GOAL_COLOR, outline="")
        self.canvas.create_text((gx1 + gx2) / 2, (gy1 + gy2) / 2, text="E", fill=BG_MAIN, font=("Segoe UI", 10, "bold"))

        px1 = self.player[1] * self.cell_size + 7
        py1 = self.player[0] * self.cell_size + 7
        px2 = px1 + self.cell_size - 12
        py2 = py1 + self.cell_size - 12
        color = PLAYER_COLOR if not self.won else PLAYER_WIN_COLOR
        self.canvas.create_oval(px1, py1, px2, py2, fill=color, outline="")
        self.canvas.create_oval(px1 + 4, py1 + 4, px2 - 4, py2 - 4, fill="#fff7ed", outline="")


def main() -> None:
    root = tk.Tk()
    MazeGame(root)
    root.mainloop()


if __name__ == "__main__":
    main()
