import random
from typing import List, Tuple, Optional


class SimpleWordSearch:
    def __init__(self, size: int = 10):
        self.size = size
        self.grid = [["" for _ in range(size)] for _ in range(size)]
        self.words = []
        self.placements = []

    def generate(self, words: List[str]) -> "SimpleWordSearch":
        self.words = words
        self.grid = [["" for _ in range(self.size)] for _ in range(self.size)]
        self.placements = []

        for word in words:
            cleaned = word.upper().replace(" ", "").replace("-", "")
            if not cleaned:
                continue
            placed = False
            attempts = 0
            while not placed and attempts < 100:
                direction = random.choice(["E", "S", "SE", "NE"])
                row = random.randint(0, self.size - 1)
                col = random.randint(0, self.size - 1)

                if self._can_place(cleaned, row, col, direction):
                    self._do_place(cleaned, row, col, direction)
                    placed = True
                attempts += 1

        for r in range(self.size):
            for c in range(self.size):
                if self.grid[r][c] == "":
                    self.grid[r][c] = random.choice("АБВГДЕЖЗИКЛМНОПРСТУФХЦЧШЩ")

        return self

    def _can_place(self, word: str, row: int, col: int, direction: str) -> bool:
        dr, dc = {"E": (0, 1), "S": (1, 0), "SE": (1, 1), "NE": (-1, 1)}[direction]
        for i, ch in enumerate(word):
            r, c = row + dr * i, col + dc * i
            if r < 0 or r >= self.size or c < 0 or c >= self.size:
                return False
            if self.grid[r][c] not in ("", ch):
                return False
        return True

    def _do_place(self, word: str, row: int, col: int, direction: str):
        dr, dc = {"E": (0, 1), "S": (1, 0), "SE": (1, 1), "NE": (-1, 1)}[direction]
        start = (row, col)
        end = (row + dr * (len(word) - 1), col + dc * (len(word) - 1))
        for i, ch in enumerate(word):
            r, c = row + dr * i, col + dc * i
            self.grid[r][c] = ch
        self.placements.append((word, start, end, direction))

    def show(self) -> str:
        lines = []
        header = "  " + " ".join(f"{c:1}" for c in "АБВГДЕЖЗИКЛМНОПРСТУФ")
        lines.append(header[:self.size * 2 + 2])
        for i, row in enumerate(self.grid):
            line = f"{i:2} " + " ".join(f"{c:1}" for c in row)
            lines.append(line)
        lines.append("")
        lines.append("Знайди слова: " + ", ".join(self.words))
        return "\n".join(lines)

    def answer_key(self) -> str:
        result = []
        for word, start, end, direction in self.placements:
            result.append(f"{word}: ({start[0]+1},{start[1]+1}) -> ({end[0]+1},{end[1]+1}) {direction}")
        return "\n".join(result)

    def to_page_data(self, title: str = "Word Search") -> dict:
        return {
            "title": title,
            "grid": ["".join(row) for row in self.grid],
            "words": self.words,
            "size": self.size,
            "answer_key": self.answer_key(),
        }
