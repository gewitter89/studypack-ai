import random
import math
from typing import List, Tuple


class ConnectDotsGenerator:
    """Connect-the-dots: numbered points forming a recognizable shape."""

    SHAPES = {
        "star": [(0, 4), (1.2, 1.5), (4, 1.5), (1.8, -0.3), (3, -3.5),
                 (0, -1.3), (-3, -3.5), (-1.8, -0.3), (-4, 1.5), (-1.2, 1.5)],
        "heart": [(0, 3), (2, 3.8), (3.5, 2.5), (3.5, 1), (2, -0.5),
                  (0, -2.5), (-2, -0.5), (-3.5, 1), (-3.5, 2.5), (-2, 3.8)],
        "fish":  [(0, 0), (2, 1.5), (4, 1), (5, 0), (4, -1), (2, -1.5),
                  (0, -1), (-2, -2), (-3.5, -1), (-3.5, 1), (-2, 2)],
        "house": [(0, 3), (2.5, 3), (3.5, 0), (2.5, -2.5), (2.5, 0),
                  (-2.5, 0), (-2.5, -2.5), (-3.5, 0), (-2.5, 3), (0, 3)],
        "rocket": [(0, 4), (1.5, 2), (1.5, -1), (2.5, -2.5), (1, -2),
                   (0, -4), (-1, -2), (-2.5, -2.5), (-1.5, -1), (-1.5, 2)],
    }

    def __init__(self, shape: str = "star", num_dots: int = 0, seed: int = 0):
        self.rng = random.Random(seed)
        if shape not in self.SHAPES:
            shape = "star"
        self.shape_name = shape
        base_points = self.SHAPES[shape]
        if num_dots and num_dots != len(base_points):
            base_points = self._interpolate_points(base_points, num_dots)
        self.points: List[Tuple[float, float]] = base_points
        self.start_x = 30.0
        self.start_y = 30.0
        self.scale = 18.0

    def _interpolate_points(self, pts: List, target: int) -> List:
        result = []
        step = max(1, len(pts) // target)
        for i in range(0, len(pts), step):
            result.append(pts[i])
        while len(result) < target:
            idx = self.rng.randint(0, len(result) - 1)
            nxt = (idx + 1) % len(pts)
            mid = ((result[idx][0] + pts[nxt][0]) / 2,
                   (result[idx][1] + pts[nxt][1]) / 2)
            result.insert(idx + 1, mid)
        return result[:target]

    def generate(self) -> "ConnectDotsGenerator":
        return self

    def to_page_data(self, title: str = "", language: str = "uk") -> dict:
        raw_points = [
            (self.start_x + p[0] * self.scale, self.start_y - p[1] * self.scale)
            for p in self.points
        ]
        min_x = min(x for x, _ in raw_points)
        min_y = min(y for _, y in raw_points)
        offset_x = max(0, 20 - min_x)
        offset_y = max(0, 50 - min_y)
        page_points = [
            {"num": i + 1,
             "x": round(x + offset_x, 2),
             "y": round(y + offset_y, 2)}
            for i, (x, y) in enumerate(raw_points)
        ]
        title_map = {
            "star":  {"ru": "Звезда", "uk": "Зірка",   "en": "Star"},
            "heart": {"ru": "Сердце", "uk": "Серце",   "en": "Heart"},
            "fish":  {"ru": "Рыбка",  "uk": "Рибка",   "en": "Fish"},
            "house": {"ru": "Домик",  "uk": "Будиночок","en": "House"},
            "rocket":{"ru": "Ракета", "uk": "Ракета",  "en": "Rocket"},
        }
        return {
            "type": "connect_dots",
            "title": title or title_map.get(self.shape_name, {}).get(language, "Connect Dots"),
            "points": page_points,
            "shape": self.shape_name,
            "total_dots": len(page_points),
        }
