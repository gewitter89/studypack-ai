import random
from typing import List, Dict

COLORS_RU = ["красный", "синий", "жёлтый", "зелёный", "оранжевый", "фиолетовый",
             "розовый", "коричневый", "голубой", "серый"]
COLORS_UK = ["червоний", "синій", "жовтий", "зелений", "помаранчевий", "фіолетовий",
             "рожевий", "коричневий", "блакитний", "сірий"]
COLORS_EN = ["red", "blue", "yellow", "green", "orange", "purple",
             "pink", "brown", "light blue", "grey"]

PALETTES = {
    "animals":  [1, 2, 3, 4, 5],
    "space":    [1, 2, 6, 9, 10],
    "ocean":    [2, 3, 4, 9, 10],
    "forest":   [1, 3, 4, 7, 8],
    "default":  [1, 2, 3, 4, 5, 6],
}


class ColorByNumberGenerator:
    """Color-by-number / color-by-math-answer generator."""

    def __init__(self, size: int = 6, num_colors: int = 5, seed: int = 0):
        self.size = size
        self.num_colors = min(num_colors, 10)
        self.rng = random.Random(seed)
        self.grid: List[List[int]] = []
        self.palette: List[int] = []

    def generate(self) -> "ColorByNumberGenerator":
        self.palette = PALETTES["default"][:self.num_colors]
        self.grid = [[self.rng.choice(self.palette) for _ in range(self.size)]
                     for _ in range(self.size)]
        return self

    def generate_math_mode(self, difficulty: str = "easy") -> "ColorByNumberGenerator":
        """Each cell contains a math expression whose answer maps to a color index."""
        self.palette = PALETTES["default"][:self.num_colors]
        self.grid = []
        max_n = {"easy": 5, "medium": 10, "hard": 20}.get(difficulty, 5)
        for _ in range(self.size):
            row = []
            for _ in range(self.size):
                target = self.rng.choice(self.palette)
                a = self.rng.randint(1, max_n)
                b = self.rng.randint(1, max_n)
                if self.rng.random() < 0.5:
                    row.append((target, f"{a}+{b-(a-target) if b >= a - target else target}"))
                else:
                    row.append((target, str(target)))
            self.grid.append(row)
        return self

    def _get_legend(self, language: str = "uk") -> List[Dict]:
        color_list = {"ru": COLORS_RU, "uk": COLORS_UK, "en": COLORS_EN}.get(language, COLORS_UK)
        return [{"number": i + 1, "color": color_list[i]} for i in range(self.num_colors)]

    def to_page_data(self, title: str = "", language: str = "uk") -> dict:
        return {
            "type": "color_by_number",
            "title": title or ("Розфарбуй за номерами" if language == "uk" else "Color by Number"),
            "grid": self.grid,
            "size": self.size,
            "palette": self.palette,
            "legend": self._get_legend(language),
            "num_colors": self.num_colors,
        }
