import tkinter as tk
import heapq
import time
import random
import math

CELL_SIZE = 25
ROWS = 20
COLS = 20

COLORS = {
    "empty": "#ffffff",
    "wall": "#2c2c2c",
    "start": "#1e90ff",
    "goal": "#2ecc71",
    "path": "#f1c40f",
    "grid": "#cccccc",
    "bg": "#f5f6fa",
    "panel": "#dcdde1"
}

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Dynamic Pathfinding Agent")
        self.root.configure(bg=COLORS["bg"])
        self.root.resizable(False, False)

        self.start = (0, 0)
        self.goal = (ROWS - 1, COLS - 1)

        self.algorithm = tk.StringVar(value="A*")
        self.heuristic_type = tk.StringVar(value="Manhattan")

        self.grid = [[0 for _ in range(COLS)] for _ in range(ROWS)]

        self.create_controls()
        self.create_canvas()
        self.create_legend()

        self.draw_grid()

    def create_controls(self):
        panel = tk.Frame(self.root, bg=COLORS["panel"], padx=10, pady=8)
        panel.pack(fill="x")

        tk.Label(panel, text="Algorithm:", bg=COLORS["panel"]).pack(side=tk.LEFT, padx=5)
        tk.OptionMenu(panel, self.algorithm, "A*", "GBFS").pack(side=tk.LEFT)

        tk.Label(panel, text="Heuristic:", bg=COLORS["panel"]).pack(side=tk.LEFT, padx=10)
        tk.OptionMenu(panel, self.heuristic_type, "Manhattan", "Euclidean").pack(side=tk.LEFT)

        tk.Button(panel, text="Generate Map", command=self.generate_map).pack(side=tk.LEFT, padx=10)
        tk.Button(panel, text="Run Search", command=self.run_search).pack(side=tk.LEFT)

        self.metrics = tk.Label(
            self.root,
            text="Ready",
            bg=COLORS["panel"],
            anchor="w",
            padx=10
        )
        self.metrics.pack(fill="x", pady=(2, 0))

    def create_canvas(self):
        frame = tk.Frame(self.root, bg=COLORS["bg"], padx=10, pady=10)
        frame.pack()

        self.canvas = tk.Canvas(
            frame,
            width=COLS * CELL_SIZE,
            height=ROWS * CELL_SIZE,
            bg=COLORS["bg"],
            highlightthickness=0
        )
        self.canvas.pack()

    def create_legend(self):
        legend = tk.Frame(self.root, bg=COLORS["bg"], pady=5)
        legend.pack()

        def item(color, text):
            f = tk.Frame(legend, bg=COLORS["bg"])
            f.pack(side=tk.LEFT, padx=8)
            tk.Label(f, bg=color, width=2, height=1).pack(side=tk.LEFT)
            tk.Label(f, text=text, bg=COLORS["bg"]).pack(side=tk.LEFT, padx=4)

        item(COLORS["start"], "Start")
        item(COLORS["goal"], "Goal")
        item(COLORS["wall"], "Obstacle")
        item(COLORS["path"], "Path")

    def heuristic(self, a, b):
        if self.heuristic_type.get() == "Manhattan":
            return abs(a[0] - b[0]) + abs(a[1] - b[1])
        return math.sqrt((a[0] - b[0])**2 + (a[1] - b[1])**2)

    def neighbors(self, node):
        r, c = node
        moves = [(1,0),(-1,0),(0,1),(0,-1)]
        for dr, dc in moves:
            nr, nc = r + dr, c + dc
            if 0 <= nr < ROWS and 0 <= nc < COLS and self.grid[nr][nc] == 0:
                yield (nr, nc)

    def generate_map(self):
        for r in range(ROWS):
            for c in range(COLS):
                if (r, c) not in (self.start, self.goal):
                    self.grid[r][c] = 1 if random.random() < 0.3 else 0
        self.metrics.config(text="New map generated")
        self.draw_grid()

    def run_search(self):
        start_time = time.time()

        frontier = []
        heapq.heappush(frontier, (0, self.start))
        came_from = {}
        g_cost = {self.start: 0}
        visited = 0

        while frontier:
            _, current = heapq.heappop(frontier)
            visited += 1

            if current == self.goal:
                break

            for neighbor in self.neighbors(current):
                new_g = g_cost[current] + 1
                if neighbor not in g_cost or new_g < g_cost[neighbor]:
                    g_cost[neighbor] = new_g
                    came_from[neighbor] = current

                    f = new_g + self.heuristic(neighbor, self.goal) \
                        if self.algorithm.get() == "A*" \
                        else self.heuristic(neighbor, self.goal)

                    heapq.heappush(frontier, (f, neighbor))

        elapsed = (time.time() - start_time) * 1000
        self.draw_grid()
        self.draw_path(came_from)

        self.metrics.config(
            text=f"Visited: {visited} | Cost: {g_cost.get(self.goal, 'N/A')} | Time: {elapsed:.2f} ms"
        )

    def draw_path(self, came_from):
        current = self.goal
        while current in came_from:
            r, c = current
            self.canvas.create_rectangle(
                c*CELL_SIZE, r*CELL_SIZE,
                (c+1)*CELL_SIZE, (r+1)*CELL_SIZE,
                fill=COLORS["path"], outline=""
            )
            current = came_from[current]

    def draw_grid(self):
        self.canvas.delete("all")
        for r in range(ROWS):
            for c in range(COLS):
                color = COLORS["empty"]
                if self.grid[r][c] == 1:
                    color = COLORS["wall"]
                if (r, c) == self.start:
                    color = COLORS["start"]
                elif (r, c) == self.goal:
                    color = COLORS["goal"]

                self.canvas.create_rectangle(
                    c*CELL_SIZE, r*CELL_SIZE,
                    (c+1)*CELL_SIZE, (r+1)*CELL_SIZE,
                    fill=color, outline=COLORS["grid"]
                )

root = tk.Tk()
App(root)
root.mainloop()