import random
from typing import List, Tuple

FIGURES = {
    "house": [(1, -2), (2, 0), (-4, 0), (0, -2)],
    "robot": [(2, 0), (0, 2), (-1, 0), (0, -1), (-2, 0), (0, -3), (2, 0), (1, 0), (0, 1), (1, 0), (0, 1)],
    "dog":   [(2, 1), (1, 0), (0, -1), (-1, 0), (0, 2), (-1, 0), (0, -2), (-2, 0), (0, 2), (1, 0)],
    "cat":   [(2, 0), (1, 1), (0, -1), (-1, 0), (0, 2), (-2, 0), (0, -2), (-1, 0), (0, 2), (1, -1)],
    "tree":  [(1, 1), (0, 2), (-1, 1), (0, -2), (1, 1), (0, 2), (-1, -1), (0, -2)],
    "car":   [(3, 0), (1, 1), (0, -1), (-1, 0), (0, 1), (-2, 0), (0, -1), (-1, 0), (0, 1)],
    "rabbit":[(1, 2), (0, 1), (1, 0), (0, -2), (1, 0), (0, -1), (-1, 0), (0, 1), (-1, 0), (0, 2)],
    "fish":  [(2, 1), (0, 2), (-2, 1), (0, -3), (2, 0), (1, -1), (0, 1)],
}

DIRECTIONS_RU = {
    (1, 0):  "→ вправо",
    (-1, 0): "← влево",
    (0, 1):  "↑ вверх",
    (0, -1): "↓ вниз",
    (1, 1):  "↗ вправо-вверх",
    (-1, 1): "↖ влево-вверх",
    (1, -1): "↘ вправо-вниз",
    (-1, -1): "↙ влево-вниз",
}
DIRECTIONS_UK = {
    (1, 0):  "→ праворуч",
    (-1, 0): "← ліворуч",
    (0, 1):  "↑ вгору",
    (0, -1): "↓ вниз",
    (1, 1):  "↗ праворуч-вгору",
    (-1, 1): "↖ ліворуч-вгору",
    (1, -1): "↘ праворуч-вниз",
    (-1, -1): "↙ ліворуч-вниз",
}
DIRECTIONS_EN = {
    (1, 0):  "→ right",
    (-1, 0): "← left",
    (0, 1):  "↑ up",
    (0, -1): "↓ down",
    (1, 1):  "↗ right-up",
    (-1, 1): "↖ left-up",
    (1, -1): "↘ right-down",
    (-1, -1): "↙ left-down",
}


class GraphicDictationGenerator:
    """Graph paper dictation: draw a figure following cell-by-cell steps."""

    def __init__(self, figure: str = "house", difficulty: str = "easy", seed: int = 0):
        self.rng = random.Random(seed)
        self.difficulty = difficulty
        if figure not in FIGURES:
            figure = "house"
        self.figure_name = figure
        self.raw_steps = FIGURES[figure]

    def generate(self) -> "GraphicDictationGenerator":
        return self

    def _expand_steps(self) -> List[Tuple[int, int]]:
        expanded = []
        for dx_total, dy_total in self.raw_steps:
            steps = max(abs(dx_total), abs(dy_total), 1)
            sx = (1 if dx_total > 0 else -1) if dx_total != 0 else 0
            sy = (1 if dy_total > 0 else -1) if dy_total != 0 else 0
            for _ in range(steps):
                expanded.append((sx, sy))
        return expanded

    def to_page_data(self, title: str = "", language: str = "uk") -> dict:
        expanded = self._expand_steps()
        dir_map = {"ru": DIRECTIONS_RU, "uk": DIRECTIONS_UK, "en": DIRECTIONS_EN}.get(language, DIRECTIONS_UK)

        steps_text = []
        for dx, dy in expanded:
            label = dir_map.get((dx, dy), f"({dx},{dy})")
            steps_text.append(label)

        title_map = {
            "house":  {"ru": "Домик",   "uk": "Будиночок", "en": "House"},
            "robot":  {"ru": "Робот",   "uk": "Робот",     "en": "Robot"},
            "dog":    {"ru": "Собачка", "uk": "Собачка",   "en": "Dog"},
            "cat":    {"ru": "Кошка",   "uk": "Кішка",     "en": "Cat"},
            "tree":   {"ru": "Ёлочка",  "uk": "Ялинка",    "en": "Tree"},
            "car":    {"ru": "Машина",  "uk": "Машина",    "en": "Car"},
            "rabbit": {"ru": "Зайчик",  "uk": "Зайчик",    "en": "Rabbit"},
            "fish":   {"ru": "Рыбка",   "uk": "Рибка",     "en": "Fish"},
        }
        return {
            "type": "graphic_dictation",
            "title": title or title_map.get(self.figure_name, {}).get(language, "Draw by Steps"),
            "figure": self.figure_name,
            "steps": expanded,
            "steps_text": steps_text,
            "total_steps": len(expanded),
            "difficulty": self.difficulty,
        }
