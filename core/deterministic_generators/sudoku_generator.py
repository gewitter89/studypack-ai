import random
import copy
from typing import List, Optional


class SudokuGenerator:
    """Deterministic 4x4 and 6x6 children's Sudoku generator."""

    def __init__(self, size: int = 4, difficulty: str = "easy", seed: int = 0):
        self.size = size
        self.difficulty = difficulty
        self.rng = random.Random(seed)
        self.grid: List[List[int]] = [[0] * size for _ in range(size)]
        self.solution: List[List[int]] = [[0] * size for _ in range(size)]

    def _is_valid(self, grid: List[List[int]], row: int, col: int, num: int) -> bool:
        if num in grid[row]:
            return False
        if num in [grid[r][col] for r in range(self.size)]:
            return False
        box_sz = 2
        box_r = (row // box_sz) * box_sz
        box_c = (col // box_sz) * box_sz
        for r in range(box_r, box_r + box_sz):
            for c in range(box_c, box_c + box_sz):
                if grid[r][c] == num:
                    return False
        return True

    def _solve_grid(self, grid: List[List[int]]) -> bool:
        for r in range(self.size):
            for c in range(self.size):
                if grid[r][c] == 0:
                    nums = list(range(1, self.size + 1))
                    self.rng.shuffle(nums)
                    for n in nums:
                        if self._is_valid(grid, r, c, n):
                            grid[r][c] = n
                            if self._solve_grid(grid):
                                return True
                            grid[r][c] = 0
                    return False
        return True

    def generate(self) -> "SudokuGenerator":
        self.solution = [[0] * self.size for _ in range(self.size)]
        self._solve_grid(self.solution)

        clues_by_diff = {"easy": 10, "medium": 7, "hard": 5}
        clues = min(clues_by_diff.get(self.difficulty, 10), self.size * self.size - 2)

        self.grid = copy.deepcopy(self.solution)
        cells = [(r, c) for r in range(self.size) for c in range(self.size)]
        self.rng.shuffle(cells)
        blanks_needed = self.size * self.size - clues
        for i in range(min(blanks_needed, len(cells))):
            r, c = cells[i]
            self.grid[r][c] = 0
        return self

    def to_page_data(self, title: str = "") -> dict:
        return {
            "type": "sudoku",
            "title": title or f"Судоку {self.size}×{self.size}",
            "grid": self.grid,
            "solution": self.solution,
            "size": self.size,
            "box_size": 2,
            "difficulty": self.difficulty,
        }
