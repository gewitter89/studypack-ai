from __future__ import annotations

import random
from typing import List, Dict


SHAPE_POOL = ["circle", "square", "triangle", "star", "heart", "diamond", "cross", "moon"]
COLOR_POOL = ["red", "blue", "yellow", "green", "orange", "purple", "pink", "brown"]

SHAPE_POOL_UK = ["коло", "квадрат", "трикутник", "зірка", "серце", "ромб", "хрест", "місяць"]
COLOR_POOL_UK = ["червоний", "синій", "жовтий", "зелений", "помаранчевий", "фіолетовий", "рожевий", "коричневий"]

SHAPE_POOL_RU = ["круг", "квадрат", "треугольник", "звезда", "сердце", "ромб", "крест", "луна"]
COLOR_POOL_RU = ["красный", "синий", "жёлтый", "зеленый", "оранжевый", "фиолетовый", "розовый", "коричневий"]


def _pools(language: str) -> tuple:
    if language in ("uk", "uk+en"):
        return SHAPE_POOL_UK, COLOR_POOL_UK
    if language in ("en",):
        return SHAPE_POOL, COLOR_POOL
    return SHAPE_POOL_RU, COLOR_POOL_RU


class FindDifferencesGenerator:
    def __init__(self, rows: int = 4, cols: int = 4, num_diffs: int = 5,
                 difficulty: str = "easy", seed: int = 0):
        self.rows = rows
        self.cols = cols
        self.num_diffs = min(num_diffs, rows * cols - 2)
        self.difficulty = difficulty
        self.seed = seed
        self.grid_a: List[List[Dict[str, str]]] = []
        self.grid_b: List[List[Dict[str, str]]] = []
        self.differences: List[Dict] = []

    def generate(self) -> "FindDifferencesGenerator":
        rng = random.Random(self.seed)
        shapes, colors = _pools("uk")

        grid_a = []
        grid_b = []
        for _ in range(self.rows):
            row_a = []
            row_b = []
            for _ in range(self.cols):
                sh = rng.choice(shapes)
                co = rng.choice(colors)
                row_a.append({"shape": sh, "color": co})
                row_b.append({"shape": sh, "color": co})
            grid_a.append(row_a)
            grid_b.append(row_b)

        coords = [(r, c) for r in range(self.rows) for c in range(self.cols)]
        rng.shuffle(coords)
        diff_coords = coords[: self.num_diffs]
        differences = []
        diff_types_used = ["color", "shape", "missing"]
        for r, c in diff_coords:
            original = grid_a[r][c].copy()
            dtype = rng.choice(diff_types_used)
            if dtype == "color":
                new_color = rng.choice([x for x in colors if x != original["color"]])
                grid_b[r][c]["color"] = new_color
                differences.append({
                    "row": r, "col": c, "type": dtype,
                    "before": original, "after": grid_b[r][c].copy(),
                })
            elif dtype == "shape":
                new_shape = rng.choice([x for x in shapes if x != original["shape"]])
                grid_b[r][c]["shape"] = new_shape
                differences.append({
                    "row": r, "col": c, "type": dtype,
                    "before": original, "after": grid_b[r][c].copy(),
                })
            else:
                grid_b[r][c] = {"shape": "", "color": "empty"}
                differences.append({
                    "row": r, "col": c, "type": dtype,
                    "before": original, "after": grid_b[r][c].copy(),
                })

        self.grid_a = grid_a
        self.grid_b = grid_b
        self.differences = differences
        return self

    def to_page_data(self, language: str = "uk") -> dict:
        return {
            "type": "find_differences",
            "rows": self.rows,
            "cols": self.cols,
            "num_to_find": len(self.differences),
            "grid_a": self.grid_a,
            "grid_b": self.grid_b,
            "differences": self.differences,
            "language": language,
        }

    def answer_text(self, language: str = "uk") -> str:
        if language in ("uk", "uk+en"):
            prefix = "Відмінності"
            types = {"color": "колір", "shape": "форма", "missing": "відсутній"}
        elif language == "en":
            prefix = "Differences"
            types = {"color": "color", "shape": "shape", "missing": "missing"}
        else:
            prefix = "Отличия"
            types = {"color": "цвет", "shape": "форма", "missing": "отсутствует"}
        parts = []
        for d in self.differences:
            r, c = d["row"] + 1, d["col"] + 1
            parts.append(f"({r},{c}) {types.get(d['type'], d['type'])}")
        return f"{prefix}: " + "; ".join(parts)
