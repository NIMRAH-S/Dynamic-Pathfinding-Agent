import tkinter as tk
from tkinter import ttk
import heapq
import random
import math
import time

CELL_SIZE = 28
DEFAULT_ROWS = 20
DEFAULT_COLS = 20
OBSTACLE_PROB = 0.30
DYNAMIC_OBSTACLE_PROB = 0.05
STEP_DELAY = 100  # ms

COLORS = {
    "empty":    "white",
    "wall":     "#2d2d2d",
    "start":    "#0077cc",
    "goal":     "#00aa44",
    "frontier": "#ffe066",
    "visited":  "#ffaa55",
    "path":     "#00e5ff",
    "agent":    "#ff3333",
}


class PathfindingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Dynamic Pathfinding Agent")
        self.root.resizable(False, False)

        self.rows = DEFAULT_ROWS
        self.cols = DEFAULT_COLS

        self.start = (0, 0)
        self.goal  = (self.rows - 1, self.cols - 1)

        self.algorithm      = tk.StringVar(value="A*")
        self.heuristic_type = tk.StringVar(value="Manhattan")
        self.draw_mode      = tk.StringVar(value="wall") 

        self.grid           = [[0] * self.cols for _ in range(self.rows)]
        self.path           = []
        self.agent_pos      = self.start
        self.path_index     = 0
        self.visited_nodes  = set()
        self.frontier_nodes = set()
        self.animating      = False
        self.exec_time      = 0.0

        self._build_ui()
        self.draw_grid()

    def _build_ui(self):
        top = tk.Frame(self.root, bg="#1e1e2e", pady=6)
        top.pack(fill="x")

        def lbl(parent, text):
            tk.Label(parent, text=text, bg="#1e1e2e", fg="white",
                     font=("Consolas", 10, "bold")).pack(side="left", padx=(10, 2))

        lbl(top, "Algorithm:")
        for alg in ["A*", "GBFS"]:
            tk.Radiobutton(top, text=alg, variable=self.algorithm, value=alg,
                           bg="#1e1e2e", fg="white", selectcolor="#444",
                           activebackground="#1e1e2e", font=("Consolas", 10)).pack(side="left")

        lbl(top, "Heuristic:")
        for h in ["Manhattan", "Euclidean"]:
            tk.Radiobutton(top, text=h, variable=self.heuristic_type, value=h,
                           bg="#1e1e2e", fg="white", selectcolor="#444",
                           activebackground="#1e1e2e", font=("Consolas", 10)).pack(side="left")

        lbl(top, "Rows:")
        self.rows_var = tk.StringVar(value=str(self.rows))
        tk.Entry(top, textvariable=self.rows_var, width=4,
                 font=("Consolas", 10)).pack(side="left")

        lbl(top, "Cols:")
        self.cols_var = tk.StringVar(value=str(self.cols))
        tk.Entry(top, textvariable=self.cols_var, width=4,
                 font=("Consolas", 10)).pack(side="left")

        tk.Button(top, text="Resize", command=self.resize_grid,
                  bg="#555", fg="white", font=("Consolas", 10),
                  relief="flat", padx=6).pack(side="left", padx=6)

        mid = tk.Frame(self.root, bg="#2a2a3e", pady=5)
        mid.pack(fill="x")

        def lbl2(text):
            tk.Label(mid, text=text, bg="#2a2a3e", fg="white",
                     font=("Consolas", 10, "bold")).pack(side="left", padx=(10, 2))

        lbl2("Draw:")
        modes = [("Wall", "wall"), ("Erase", "erase"),
                 ("Set Start", "set_start"), ("Set Goal", "set_goal")]
        for txt, val in modes:
            tk.Radiobutton(mid, text=txt, variable=self.draw_mode, value=val,
                           bg="#2a2a3e", fg="white", selectcolor="#444",
                           activebackground="#2a2a3e",
                           font=("Consolas", 10)).pack(side="left", padx=2)

        tk.Button(mid, text="Generate Map", command=self.generate_map,
                  bg="#226644", fg="white", font=("Consolas", 10),
                  relief="flat", padx=8).pack(side="left", padx=8)

        tk.Button(mid, text="Clear Grid", command=self.clear_grid,
                  bg="#664422", fg="white", font=("Consolas", 10),
                  relief="flat", padx=8).pack(side="left")

        tk.Button(mid, text="RUN", command=self.start_search,
                  bg="#0077cc", fg="white", font=("Consolas", 11, "bold"),
                  relief="flat", padx=10).pack(side="left", padx=8)

        self.dynamic_var = tk.BooleanVar(value=False)
        tk.Checkbutton(mid, text="Dynamic Obstacles", variable=self.dynamic_var,
                       bg="#2a2a3e", fg="white", selectcolor="#444",
                       activebackground="#2a2a3e",
                       font=("Consolas", 10)).pack(side="left", padx=6)

        self.metrics_var = tk.StringVar(value="Ready — generate a map or draw walls, then click RUN.")
        tk.Label(self.root, textvariable=self.metrics_var,
                 bg="#111122", fg="#aaffaa", font=("Consolas", 10),
                 anchor="w", padx=10, pady=4).pack(fill="x")

        self.canvas_frame = tk.Frame(self.root)
        self.canvas_frame.pack()
        self._make_canvas()

        leg = tk.Frame(self.root, bg="#1e1e2e", pady=4)
        leg.pack(fill="x")
        items = [("Start",   COLORS["start"]),   ("Goal",     COLORS["goal"]),
                 ("Wall",    COLORS["wall"]),     ("Frontier", COLORS["frontier"]),
                 ("Visited", COLORS["visited"]),  ("Path",     COLORS["path"]),
                 ("Agent",   COLORS["agent"])]
        for name, color in items:
            tk.Canvas(leg, width=14, height=14, bg=color,
                      highlightthickness=0).pack(side="left", padx=(8, 2))
            tk.Label(leg, text=name, bg="#1e1e2e", fg="white",
                     font=("Consolas", 9)).pack(side="left", padx=(0, 6))

    def _make_canvas(self):
        for w in self.canvas_frame.winfo_children():
            w.destroy()
        self.canvas = tk.Canvas(
            self.canvas_frame,
            width=self.cols * CELL_SIZE,
            height=self.rows * CELL_SIZE,
            highlightthickness=0
        )
        self.canvas.pack()
        self.canvas.bind("<Button-1>",  self._on_click)
        self.canvas.bind("<B1-Motion>", self._on_drag)

    def _cell(self, event):
        r = event.y // CELL_SIZE
        c = event.x // CELL_SIZE
        if 0 <= r < self.rows and 0 <= c < self.cols:
            return (r, c)
        return None

    def _on_click(self, event):
        pos = self._cell(event)
        if pos is None:
            return
        mode = self.draw_mode.get()
        if mode == "set_start":
            self.start = pos
            self._reset_search()
        elif mode == "set_goal":
            self.goal = pos
            self._reset_search()
        elif mode == "wall" and pos not in (self.start, self.goal):
            self.grid[pos[0]][pos[1]] = 1
        elif mode == "erase":
            self.grid[pos[0]][pos[1]] = 0
        self.draw_grid()

    def _on_drag(self, event):
        pos = self._cell(event)
        if pos is None or pos in (self.start, self.goal):
            return
        mode = self.draw_mode.get()
        if mode == "wall":
            self.grid[pos[0]][pos[1]] = 1
        elif mode == "erase":
            self.grid[pos[0]][pos[1]] = 0
        self.draw_grid()

    def resize_grid(self):
        try:
            r = max(5, min(40, int(self.rows_var.get())))
            c = max(5, min(60, int(self.cols_var.get())))
        except ValueError:
            return
        self.rows, self.cols = r, c
        self.start = (0, 0)
        self.goal  = (self.rows - 1, self.cols - 1)
        self.grid  = [[0] * self.cols for _ in range(self.rows)]
        self._reset_search()
        self._make_canvas()
        self.draw_grid()

    def generate_map(self):
        self.grid = [[0] * self.cols for _ in range(self.rows)]
        for r in range(self.rows):
            for c in range(self.cols):
                if (r, c) not in (self.start, self.goal):
                    self.grid[r][c] = 1 if random.random() < OBSTACLE_PROB else 0
        self._reset_search()
        self.draw_grid()

    def clear_grid(self):
        self.grid = [[0] * self.cols for _ in range(self.rows)]
        self._reset_search()
        self.draw_grid()

    def _reset_search(self):
        self.path           = []
        self.path_index     = 0
        self.agent_pos      = self.start
        self.visited_nodes  = set()
        self.frontier_nodes = set()
        self.animating      = False

    def heuristic(self, a, b):
        if self.heuristic_type.get() == "Manhattan":
            return abs(a[0] - b[0]) + abs(a[1] - b[1])
        return math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2)

    def neighbors(self, node):
        r, c = node
        for dr, dc in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < self.rows and 0 <= nc < self.cols:
                if self.grid[nr][nc] == 0:
                    yield (nr, nc)

    def search(self, from_node=None, to_node=None):
        """
        Run A* or GBFS from from_node to to_node.
        Returns (path_list, nodes_expanded_count).
        path_list includes from_node as first element.
        """
        if from_node is None:
            from_node = self.start
        if to_node is None:
            to_node = self.goal

        frontier  = []
        came_from = {from_node: None}
        g_cost    = {from_node: 0}
        visited   = set()
        nodes_exp = 0

        h0 = self.heuristic(from_node, to_node)
        heapq.heappush(frontier, (h0, 0, from_node))
        self.frontier_nodes = set([from_node])

        while frontier:
            f, g, current = heapq.heappop(frontier)

            if current in visited:
                continue
            visited.add(current)
            self.visited_nodes.add(current)
            self.frontier_nodes.discard(current)
            nodes_exp += 1

            if current == to_node:
                break

            for nb in self.neighbors(current):
                new_g = g + 1
                if nb not in g_cost or new_g < g_cost[nb]:
                    g_cost[nb]    = new_g
                    came_from[nb] = current
                    h_val = self.heuristic(nb, to_node)
                    f_val = (new_g + h_val) if self.algorithm.get() == "A*" else h_val
                    heapq.heappush(frontier, (f_val, new_g, nb))
                    self.frontier_nodes.add(nb)

        if to_node not in came_from:
            return [], nodes_exp

        path, cur = [], to_node
        while cur is not None:
            path.append(cur)
            cur = came_from[cur]
        path.reverse()
        return path, nodes_exp

    def start_search(self):
        if self.animating:
            return
        self._reset_search()

        t0 = time.time()
        self.path, n_exp = self.search(self.start, self.goal)
        self.exec_time   = (time.time() - t0) * 1000

        if not self.path:
            self.metrics_var.set("No path found! Try removing some walls.")
            self.draw_grid()
            return

        self.path_index = 0
        self.agent_pos  = self.start
        self.metrics_var.set(
            f"Nodes Expanded: {n_exp}  |  "
            f"Path Cost: {len(self.path) - 1}  |  "
            f"Time: {self.exec_time:.2f} ms"
        )
        self.draw_grid()
        self.animating = True
        self.root.after(STEP_DELAY, self.animate_agent)

    def animate_agent(self):
        if not self.animating:
            return

        if self.dynamic_var.get():
            self._try_spawn_obstacle()
            if not self.animating:   
                return

        if self.path_index < len(self.path):
            self.agent_pos   = self.path[self.path_index]
            self.path_index += 1
            self.draw_grid()

            if self.agent_pos == self.goal:
                self.animating = False
                self.metrics_var.set(self.metrics_var.get() + "   Goal Reached!")
                return

            self.root.after(STEP_DELAY, self.animate_agent)
        else:
            self.animating = False

    def _try_spawn_obstacle(self):
        """Randomly spawn one obstacle; replan if it blocks the remaining path."""
        if random.random() > DYNAMIC_OBSTACLE_PROB:
            return

        attempts = 0
        while attempts < 10:
            r   = random.randint(0, self.rows - 1)
            c   = random.randint(0, self.cols - 1)
            pos = (r, c)
            if (pos not in (self.start, self.goal) and
                    pos != self.agent_pos and
                    self.grid[r][c] == 0):
                self.grid[r][c] = 1
                
                remaining = set(self.path[self.path_index:])
                if pos in remaining:
                    self._replan_from_current()
                return
            attempts += 1

    def _replan_from_current(self):
        """Re-run search from the agent's CURRENT position (not from original start)."""
        t0 = time.time()
        new_path, n_exp  = self.search(self.agent_pos, self.goal)
        self.exec_time   = (time.time() - t0) * 1000

        if not new_path:
            self.animating = False
            self.metrics_var.set("Re-planning failed — no path available!")
            self.draw_grid()
            return

        self.path       = self.path[:self.path_index] + new_path
        
        self.metrics_var.set(
            f"Re-planned! Nodes: {n_exp}  |  "
            f"New total cost: {len(self.path) - 1}  |  "
            f"Time: {self.exec_time:.2f} ms"
        )
        self.draw_grid()

    def draw_grid(self):
        self.canvas.delete("all")
        path_set = set(self.path)

        for r in range(self.rows):
            for c in range(self.cols):
                x1, y1 = c * CELL_SIZE,        r * CELL_SIZE
                x2, y2 = x1 + CELL_SIZE, y1 + CELL_SIZE
                pos     = (r, c)

                if pos == self.agent_pos and self.animating:
                    color = COLORS["agent"]
                elif pos == self.start:
                    color = COLORS["start"]
                elif pos == self.goal:
                    color = COLORS["goal"]
                elif self.grid[r][c] == 1:
                    color = COLORS["wall"]
                elif pos in path_set:
                    color = COLORS["path"]
                elif pos in self.visited_nodes:
                    color = COLORS["visited"]
                elif pos in self.frontier_nodes:
                    color = COLORS["frontier"]
                else:
                    color = COLORS["empty"]

                self.canvas.create_rectangle(x1, y1, x2, y2,
                                             fill=color, outline="#cccccc",
                                             width=0.5)

        if self.animating and self.agent_pos:
            r, c = self.agent_pos
            cx   = c * CELL_SIZE + CELL_SIZE // 2
            cy   = r * CELL_SIZE + CELL_SIZE // 2
            rad  = CELL_SIZE // 2 - 3
            self.canvas.create_oval(cx - rad, cy - rad, cx + rad, cy + rad,
                                    fill=COLORS["agent"], outline="white", width=1.5)


if __name__ == "__main__":
    root = tk.Tk()
    PathfindingApp(root)
    root.mainloop()