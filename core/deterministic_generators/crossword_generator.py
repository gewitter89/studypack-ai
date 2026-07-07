from __future__ import annotations

import random
from typing import List, Dict, Tuple, Optional


WORD_POOLS = {
    "uk": {
        "general": ["кіт", "пес", "ліс", "дом", "море", "зірка", "квітка", "хмара", "сонце", "пташка"],
        "animals": ["кіт", "пес", "лиса", "вовк", "заєць", "слон", "тигр", "зебра", "ведмідь", "риба"],
        "nature": [
            "ліс", "гора", "море", "озеро", "река", "хмара", "сонце", "дощ", "сніг", "вітер",
        ],
        "food": ["хліб", "яблуко", "сир", "молоко", "чай", "кава", "цукор", "сіль", "рис", "суп"],
    },
    "ru": {
        "general": ["кот", "пёс", "лес", "дом", "море", "звезда", "цветок", "облако", "солнце", "птица"],
        "animals": [
            "кот", "пёс", "лиса", "волк", "заяц", "слон", "тигр", "зебра", "медведь", "рыба",
        ],
        "nature": [
            "лес", "гора", "море", "озеро", "река", "облако", "солнце", "дождь", "снег", "ветер",
        ],
        "food": [
            "хлеб", "яблоко", "сыр", "молоко", "чай", "кофе", "сахар", "соль", "рис", "суп",
        ],
    },
    "en": {
        "general": ["cat", "dog", "fox", "bee", "ant", "owl", "sun", "moon", "rain", "snow"],
        "animals": ["cat", "dog", "fox", "bear", "wolf", "lion", "deer", "frog", "duck", "fish"],
        "nature": ["tree", "leaf", "rock", "hill", "lake", "pond", "rain", "snow", "wind", "sun"],
        "food": ["bread", "cheese", "milk", "egg", "rice", "soup", "fish", "pie", "tea", "jam"],
    },
}


def _hints() -> dict:
    return {
        "кит": "М'який пухнастий звір, мурликає",
        "пес": "Гав-гав, найкращий друг людини",
        "кіт-ru": "cat (русская форма не используется)",
        "кот": "Мягкий пушистый зверь, мурлычет",
        "пёс": "Гав-гав, лучший друг человека",
        "кот-uk": "cat (uk форма не используется)",
        "cat": "Soft, purring pet",
        "dog": "Barking pet, man's best friend",
        "fox": "Small, clever wild animal",
    }


class CrosswordGenerator:
    def __init__(self, theme: str = "general", language: str = "uk",
                 max_words: int = 6, seed: int = 0):
        self.theme = theme
        self.language = language
        self.max_words = max_words
        self.seed = seed
        self.rows = 11
        self.cols = 13
        self.grid: List[List[str]] = [["" for _ in range(self.cols)] for _ in range(self.rows)]
        self.placed_words: List[Dict] = []
        self.across: List[Dict] = []
        self.down: List[Dict] = []

    def generate(self) -> "CrosswordGenerator":
        rng = random.Random(self.seed)
        pool_key = self.language if self.language in WORD_POOLS else "uk"
        sub_pool = WORD_POOLS[pool_key]
        word_list_by_theme = sub_pool.get(self.theme, sub_pool.get("general", []))
        words = [w.upper() for w in word_list_by_theme if len(w) >= 2 and len(w) <= 8]
        rng.shuffle(words)
        words = words[: self.max_words + 4]
        words.sort(key=len, reverse=True)

        for w in words:
            if len(self.placed_words) >= self.max_words:
                break
            if not self.placed_words:
                self._place_first(w)
                continue
            self._try_place(w)

        self._compact_and_number()
        return self

    def _place_first(self, word: str) -> None:
        c_start = (self.cols - len(word)) // 2
        r = self.rows // 2
        for i, ch in enumerate(word):
            self.grid[r][c_start + i] = ch
        self.placed_words.append({"word": word, "row": r, "col": c_start, "dir": "across"})
        self._rebuild_clue_lists()

    def _can_place(self, word: str, r: int, c: int, direction: str) -> bool:
        if direction == "across":
            if c < 0 or c + len(word) > self.cols:
                return False
            before = self.grid[r][c - 1] if c > 0 else ""
            if before:
                return False
            after = self.grid[r][c + len(word)] if c + len(word) < self.cols else ""
            if after:
                return False
            touches = 0
            for i, ch in enumerate(word):
                gc = c + i
                cur = self.grid[r][gc]
                if cur == "":
                    if r > 0 and self.grid[r - 1][gc]:
                        return False
                    if r < self.rows - 1 and self.grid[r + 1][gc]:
                        return False
                elif cur == ch:
                    touches += 1
                else:
                    return False
            return touches > 0
        else:
            if r < 0 or r + len(word) > self.rows:
                return False
            before = self.grid[r - 1][c] if r > 0 else ""
            if before:
                return False
            after = self.grid[r + len(word)][c] if r + len(word) < self.rows else ""
            if after:
                return False
            touches = 0
            for i, ch in enumerate(word):
                gr = r + i
                cur = self.grid[gr][c]
                if cur == "":
                    if c > 0 and self.grid[gr][c - 1]:
                        return False
                    if c < self.cols - 1 and self.grid[gr][c + 1]:
                        return False
                elif cur == ch:
                    touches += 1
                else:
                    return False
            return touches > 0

    def _place_word(self, word: str, r: int, c: int, direction: str) -> None:
        if direction == "across":
            for i, ch in enumerate(word):
                self.grid[r][c + i] = ch
        else:
            for i, ch in enumerate(word):
                self.grid[r + i][c] = ch
        self.placed_words.append({"word": word, "row": r, "col": c, "dir": direction})
        self._rebuild_clue_lists()

    def _try_place(self, word: str) -> None:
        rng = random.Random(self.seed + hash(word))
        for pw in self.placed_words:
            for i in range(len(pw["word"])):
                for j in range(len(word)):
                    if pw["word"][i] != word[j]:
                        continue
                    if pw["dir"] == "across":
                        r = pw["row"] - j
                        c = pw["col"] + i
                        if self._can_place(word, r, c, "down"):
                            self._place_word(word, r, c, "down")
                            return
                    else:
                        r = pw["row"] + i
                        c = pw["col"] - j
                        if self._can_place(word, r, c, "across"):
                            self._place_word(word, r, c, "across")
                            return
        for _ in range(80):
            r = rng.randint(0, self.rows - len(word))
            c = rng.randint(0, self.cols - 1)
            for d in ("across", "down"):
                if self._can_place(word, r, c, d):
                    self._place_word(word, r, c, d)
                    return

    def _rebuild_clue_lists(self) -> None:
        self.across = [p for p in self.placed_words if p["dir"] == "across"]
        self.down = [p for p in self.placed_words if p["dir"] == "down"]
        self.across.sort(key=lambda p: (p["row"], p["col"]))
        self.down.sort(key=lambda p: (p["row"], p["col"]))

    def _compact_and_number(self) -> None:
        min_r, max_r = 0, self.rows - 1
        min_c, max_c = 0, self.cols - 1
        non_empty = [(r, c) for r in range(self.rows) for c in range(self.cols) if self.grid[r][c]]
        if non_empty:
            min_r = min(r for r, _ in non_empty)
            max_r = max(r for r, _ in non_empty)
            min_c = min(c for _, c in non_empty)
            max_c = max(c for _, c in non_empty)
        self.bounds = (min_r, max_r, min_c, max_c)

        self.numbers: Dict[Tuple[int, int], int] = {}
        n = 1
        for r in range(self.rows):
            for c in range(self.cols):
                if not self.grid[r][c]:
                    continue
                is_across_start = (
                    (c == 0 or not self.grid[r][c - 1])
                    and c + 1 < self.cols and self.grid[r][c + 1]
                )
                is_down_start = (
                    (r == 0 or not self.grid[r - 1][c])
                    and r + 1 < self.rows and self.grid[r + 1][c]
                )
                if is_across_start or is_down_start:
                    self.numbers[(r, c)] = n
                    for p in self.placed_words:
                        if p["row"] == r and p["col"] == c:
                            p["number"] = n
                    n += 1
        self._rebuild_clue_lists()

    def to_page_data(self) -> dict:
        min_r, max_r, min_c, max_c = self.bounds
        compact_grid = [row[min_c: max_c + 1] for row in self.grid[min_r: max_r + 1]]
        offsets = {
            "row_offset": min_r,
            "col_offset": min_c,
        }
        clue_numbers = {
            "across": [
                {"number": p["number"], "word": p["word"], "hint": _hints().get(
                    p["word"].lower(), p["word"])} for p in self.across
            ],
            "down": [
                {"number": p["number"], "word": p["word"], "hint": _hints().get(
                    p["word"].lower(), p["word"])} for p in self.down
            ],
        }
        numbers_dict = {f"{k[0]},{k[1]}": v for k, v in self.numbers.items()}
        return {
            "type": "crossword",
            "grid": compact_grid,
            "numbers": numbers_dict,
            "clues": clue_numbers,
            "rows": len(compact_grid),
            "cols": len(compact_grid[0]) if compact_grid else 0,
            **offsets,
        }

    def answer_text(self) -> str:
        if not self.placed_words:
            return ""
        return " | ".join(f"{p['word']}" for p in self.placed_words)
