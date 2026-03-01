import tkinter as tk
import heapq
import time
import random
import math

CELL_SIZE = 25
ROWS = 20
COLS = 20

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Dynamic Pathfinding Agent")

        self.start = (0, 0)
        self.goal = (19, 19)

        self.algorithm = tk.StringVar(value="A*")
        self.heuristic_type = tk.StringVar(value="Manhattan")

        self.grid = [[0 for _ in range(COLS)] for _ in range(ROWS)]

        self.create_controls()

        self.canvas = tk.Canvas(root, width=COLS*CELL_SIZE,
                                height=ROWS*CELL_SIZE)
        self.canvas.pack()

        self.draw_grid()

    def create_controls(self):
        frame = tk.Frame(self.root)
        frame.pack()

        tk.OptionMenu(frame, self.algorithm, "A*", "GBFS").pack(side=tk.LEFT)
        tk.OptionMenu(frame, self.heuristic_type, "Manhattan", "Euclidean").pack(side=tk.LEFT)

        tk.Button(frame, text="Generate Map", command=self.generate_map).pack(side=tk.LEFT)
        tk.Button(frame, text="Run Search", command=self.run_search).pack(side=tk.LEFT)

        self.metrics = tk.Label(self.root, text="")
        self.metrics.pack()

    def heuristic(self, a, b):
        if self.heuristic_type.get() == "Manhattan":
            return abs(a[0]-b[0]) + abs(a[1]-b[1])
        else:
            return math.sqrt((a[0]-b[0])**2 + (a[1]-b[1])**2)

    def neighbors(self, node):
        r, c = node
        moves = [(1,0),(-1,0),(0,1),(0,-1)]
        result = []
        for dr, dc in moves:
            nr, nc = r+dr, c+dc
            if 0 <= nr < ROWS and 0 <= nc < COLS:
                if self.grid[nr][nc] == 0:
                    result.append((nr, nc))
        return result

    def generate_map(self):
        for r in range(ROWS):
            for c in range(COLS):
                if (r, c) != self.start and (r, c) != self.goal:
                    self.grid[r][c] = 1 if random.random() < 0.3 else 0
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

                    if self.algorithm.get() == "A*":
                        f = new_g + self.heuristic(neighbor, self.goal)
                    else:
                        f = self.heuristic(neighbor, self.goal)

                    heapq.heappush(frontier, (f, neighbor))

        end_time = time.time()

        self.draw_grid()
        self.draw_path(came_from)

        self.metrics.config(
            text=f"Visited: {visited} | "
                 f"Cost: {g_cost.get(self.goal, 'N/A')} | "
                 f"Time: {round((end_time-start_time)*1000,2)} ms"
        )

    def draw_path(self, came_from):
        current = self.goal
        while current in came_from:
            r, c = current
            self.canvas.create_rectangle(
                c*CELL_SIZE, r*CELL_SIZE,
                (c+1)*CELL_SIZE, (r+1)*CELL_SIZE,
                fill="yellow"
            )
            current = came_from[current]

    def draw_grid(self):
        self.canvas.delete("all")
        for r in range(ROWS):
            for c in range(COLS):
                color = "white"

                if self.grid[r][c] == 1:
                    color = "black"

                if (r, c) == self.start:
                    color = "blue"
                elif (r, c) == self.goal:
                    color = "green"

                self.canvas.create_rectangle(
                    c*CELL_SIZE, r*CELL_SIZE,
                    (c+1)*CELL_SIZE, (r+1)*CELL_SIZE,
                    fill=color, outline="gray"
                )

root = tk.Tk()
app = App(root)
root.mainloop()