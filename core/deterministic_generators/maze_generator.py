import random
from typing import List, Tuple


class MazeGenerator:
    def __init__(self, rows: int = 8, cols: int = 8):
        self.rows = rows
        self.cols = cols
        self.grid = [[1] * (2 * cols + 1) for _ in range(2 * rows + 1)]

    def generate(self) -> "MazeGenerator":
        visited = [[False] * self.cols for _ in range(self.rows)]

        def carve(r, c):
            visited[r][c] = True
            self.grid[2 * r + 1][2 * c + 1] = 0
            dirs = [(0, 1), (1, 0), (0, -1), (-1, 0)]
            random.shuffle(dirs)
            for dr, dc in dirs:
                nr, nc = r + dr, c + dc
                if 0 <= nr < self.rows and 0 <= nc < self.cols and not visited[nr][nc]:
                    self.grid[2 * r + 1 + dr][2 * c + 1 + dc] = 0
                    carve(nr, nc)

        carve(0, 0)
        self.grid[1][0] = 0
        self.grid[2 * self.rows - 1][2 * self.cols] = 0
        return self

    def solve(self) -> List[Tuple[int, int]]:
        start = (1, 0)
        end = (2 * self.rows - 1, 2 * self.cols)
        path = []
        visited = set()

        def dfs(r, c):
            if (r, c) in visited:
                return False
            visited.add((r, c))
            path.append((r, c))
            if (r, c) == end:
                return True
            for dr, dc in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                nr, nc = r + dr, c + dc
                if 0 <= nr < len(self.grid) and 0 <= nc < len(self.grid[0]):
                    if self.grid[nr][nc] == 0:
                        if dfs(nr, nc):
                            return True
            path.pop()
            return False

        dfs(*start)
        return path

    def show(self, show_solution: bool = False) -> str:
        solution = set(self.solve()) if show_solution else set()
        symbols = {0: "  ", 1: "██"}
        if show_solution:
            symbols[2] = "··"
        lines = []
        for r in range(len(self.grid)):
            row = []
            for c in range(len(self.grid[0])):
                if show_solution and (r, c) in solution and self.grid[r][c] == 0:
                    row.append(symbols[2])
                else:
                    row.append(symbols.get(self.grid[r][c], "██"))
            lines.append("".join(row))
        return "\n".join(lines)

    def to_page_data(self, title: str = "Лабіринт") -> dict:
        solution = self.solve()
        return {
            "title": title,
            "grid": self.grid,
            "rows": len(self.grid),
            "cols": len(self.grid[0]),
            "solution": solution,
            "start": (1, 0),
            "end": (len(self.grid) - 2, len(self.grid[0]) - 1),
        }
