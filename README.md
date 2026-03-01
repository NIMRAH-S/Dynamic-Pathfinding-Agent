# Dynamic Pathfinding Agent

## Description
This project implements a Dynamic Pathfinding Agent that navigates a 
grid-based environment using informed search algorithms. The agent 
can adapt in real-time to randomly appearing obstacles by re-planning 
its path from its current position.

Algorithms implemented:
- A* Search (optimal, uses f(n) = g(n) + h(n))
- Greedy Best-First Search (fast, uses f(n) = h(n))

Heuristics available:
- Manhattan Distance
- Euclidean Distance

## Features
- Adjustable grid size (rows and columns)
- Random map generation with 30% obstacle density
- Interactive wall drawing and erasing by clicking/dragging
- Set custom Start and Goal positions
- Algorithm and heuristic selection before running
- Dynamic obstacle mode — obstacles spawn during agent movement
- Automatic re-planning from agent's current position
- Color-coded visualization (frontier, visited, path, agent)
- Real-time metrics dashboard:
  - Nodes Expanded
  - Path Cost
  - Execution Time (ms)

## Requirements
- Python 3.x
- Tkinter (built-in with Python — no installation required)

No additional packages need to be installed.

## How to Run
1. Clone the repository:
   git clone <your-repo-url>

2. Navigate to the project folder:
   cd AI_A2_23F-0734

3. Verify Python is installed:
   python --version

4. Run the program:
   python main.py

## Controls
| Control | Action |
|---|---|
| Draw (radio) | Click/drag on grid to place walls |
| Erase (radio) | Click/drag to remove walls |
| Set Start (radio) | Click any cell to move the start point |
| Set Goal (radio) | Click any cell to move the goal point |
| Generate Map | Randomly fills grid with ~30% obstacles |
| Clear Grid | Removes all walls |
| Rows / Cols + Resize | Change grid dimensions |
| Dynamic Obstacles | Toggle real-time obstacle spawning |
| RUN | Start the search and animate the agent |

## Author
Nimrah Shahid
Course: AI 2002 – Artificial Intelligence (Spring 2026)