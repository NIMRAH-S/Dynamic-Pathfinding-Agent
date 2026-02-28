import tkinter as tk

CELL_SIZE = 25
ROWS = 20
COLS = 20

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Dynamic Pathfinding Agent")

        self.start = (0, 0)
        self.goal = (19, 19)

        self.canvas = tk.Canvas(root, width=COLS*CELL_SIZE,
                                height=ROWS*CELL_SIZE)
        self.canvas.pack()

        self.grid = [[0 for _ in range(COLS)] for _ in range(ROWS)]

        self.draw_grid()

    def draw_grid(self):
        for r in range(ROWS):
            for c in range(COLS):
                color = "white"

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