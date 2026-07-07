"""Adaptive difficulty engine — adjusts parameters based on child's age."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


@dataclass
class DifficultyProfile:
    age: int
    math_add_range: Tuple[int, int]
    math_sub_range: Tuple[int, int]
    math_mult_range: Tuple[int, int]
    sudoku_size: int
    maze_size: Tuple[int, int]
    connect_dots_count: int
    find_diffs_count: int
    crossword_min_words: int
    crossword_max_words: int
    graphic_dictation_steps: int
    word_search_grid_size: int
    text_max_chars: int
    reading_comprehension_q_count: int


AGE_PROFILES: Dict[str, DifficultyProfile] = {
    "3-4": DifficultyProfile(
        age=3,
        math_add_range=(1, 5),
        math_sub_range=(2, 5),
        math_mult_range=(0, 0),
        sudoku_size=0,
        maze_size=(5, 5),
        connect_dots_count=6,
        find_diffs_count=3,
        crossword_min_words=0,
        crossword_max_words=0,
        graphic_dictation_steps=3,
        word_search_grid_size=0,
        text_max_chars=50,
        reading_comprehension_q_count=1,
    ),
    "5-6": DifficultyProfile(
        age=5,
        math_add_range=(1, 10),
        math_sub_range=(2, 10),
        math_mult_range=(0, 0),
        sudoku_size=4,
        maze_size=(7, 7),
        connect_dots_count=10,
        find_diffs_count=4,
        crossword_min_words=3,
        crossword_max_words=5,
        graphic_dictation_steps=5,
        word_search_grid_size=6,
        text_max_chars=150,
        reading_comprehension_q_count=2,
    ),
    "7-8": DifficultyProfile(
        age=7,
        math_add_range=(5, 20),
        math_sub_range=(5, 20),
        math_mult_range=(2, 5),
        sudoku_size=4,
        maze_size=(9, 9),
        connect_dots_count=15,
        find_diffs_count=5,
        crossword_min_words=4,
        crossword_max_words=7,
        graphic_dictation_steps=7,
        word_search_grid_size=8,
        text_max_chars=300,
        reading_comprehension_q_count=3,
    ),
    "9-10": DifficultyProfile(
        age=9,
        math_add_range=(10, 50),
        math_sub_range=(10, 50),
        math_mult_range=(2, 9),
        sudoku_size=6,
        maze_size=(11, 11),
        connect_dots_count=20,
        find_diffs_count=6,
        crossword_min_words=5,
        crossword_max_words=9,
        graphic_dictation_steps=10,
        word_search_grid_size=10,
        text_max_chars=500,
        reading_comprehension_q_count=4,
    ),
    "11-12": DifficultyProfile(
        age=11,
        math_add_range=(20, 100),
        math_sub_range=(20, 100),
        math_mult_range=(2, 12),
        sudoku_size=6,
        maze_size=(13, 13),
        connect_dots_count=25,
        find_diffs_count=7,
        crossword_min_words=6,
        crossword_max_words=12,
        graphic_dictation_steps=12,
        word_search_grid_size=12,
        text_max_chars=800,
        reading_comprehension_q_count=5,
    ),
}


def get_age_bracket(age: int) -> str:
    if age <= 4:
        return "3-4"
    elif age <= 6:
        return "5-6"
    elif age <= 8:
        return "7-8"
    elif age <= 10:
        return "9-10"
    else:
        return "11-12"


def get_profile(age: int) -> DifficultyProfile:
    bracket = get_age_bracket(age)
    return AGE_PROFILES[bracket]


def adaptive_math_range(age: int, operation: str = "add") -> Tuple[int, int]:
    p = get_profile(age)
    if operation == "add":
        return p.math_add_range
    elif operation == "subtract":
        return p.math_sub_range
    elif operation == "multiply":
        return p.math_mult_range
    return (1, 10)


def adaptive_card_params(age: int, card_type: str) -> Dict:
    p = get_profile(age)
    if card_type == "sudoku":
        return {"size": p.sudoku_size}
    elif card_type == "maze":
        return {"width": p.maze_size[0], "height": p.maze_size[1]}
    elif card_type == "connect_dots":
        return {"count": p.connect_dots_count}
    elif card_type == "find_differences":
        return {"diff_count": p.find_diffs_count}
    elif card_type == "crossword":
        return {"min_words": p.crossword_min_words, "max_words": p.crossword_max_words}
    elif card_type == "graphic_dictation":
        return {"steps": p.graphic_dictation_steps}
    elif card_type == "word_search":
        return {"grid_size": p.word_search_grid_size}
    return {}


THEME_CHAINS: Dict[str, List[str]] = {
    "animals": ["animals", "dinosaurs", "ocean", "insects", "birds"],
    "nature": ["nature", "weather", "space", "seasons", "plants"],
    "everyday": ["food", "transport", "clothes", "home", "school"],
    "adventure": ["space", "dinosaurs", "ocean", "pirates", "castles"],
    "learning": ["math_practice", "reading", "writing", "science", "history"],
}


def next_theme_in_chain(current_theme: str, used_count: int = 0) -> str:
    for chain_name, chain in THEME_CHAINS.items():
        if current_theme in chain:
            idx = chain.index(current_theme)
            next_idx = (idx + 1 + used_count) % len(chain)
            return chain[next_idx]
    return current_theme


def recommended_card_mix(age: int, count: int = 8) -> List[str]:
    if age <= 4:
        base = ["color_by_number", "connect_dots", "coloring", "graphic_dictation"]
        base += ["math_addition"] * max(0, count - len(base))
    elif age <= 6:
        base = ["color_by_number", "sudoku", "maze", "connect_dots",
                "math_addition", "text_question"]
        base += ["find_differences"] * max(0, count - len(base))
    elif age <= 8:
        base = ["sudoku", "maze", "find_differences", "crossword",
                "color_by_number", "math_addition", "text_question", "connect_dots"]
    elif age <= 10:
        base = ["sudoku", "maze", "find_differences", "crossword",
                "math_addition", "math_subtraction", "text_question", "graphic_dictation"]
    else:
        base = ["sudoku", "maze", "find_differences", "crossword",
                "math_addition", "math_subtraction", "math_multiplication",
                "text_question"]
    return base[:count]


PERSONALIZED_STORY_TEMPLATES: Dict[str, Dict[str, List[str]]] = {
    "uk": [
        "Одного дня {name} вирішив/ла дослідити {topic}.",
        "{name} знайшов/ла книгу про {topic} і не міг/ла відірватися.",
        "«{name}, — сказав друг, — давай вивчимо {topic} разом!»",
        "{name} мріяв/ла стати експертом з {topic}.",
    ],
    "ru": [
        "Однажды {name} решил/а исследовать {topic}.",
        "{name} нашёл/ла книгу о {topic} и не мог/ла оторваться.",
        "«{name}, — сказал друг, — давай изучим {topic} вместе!»",
        "{name} мечтал/а стать экспертом по {topic}.",
    ],
    "en": [
        "One day, {name} decided to explore {topic}.",
        "{name} found a book about {topic} and couldn't put it down.",
        '"{name}," said a friend, "let\'s learn about {topic} together!"',
        "{name} dreamed of becoming an expert in {topic}.",
    ],
}


def generate_story_opening(name: str, topic: str, lang: str = "uk") -> str:
    import random
    lang_key = "uk" if lang in ("uk", "uk+en") else "en" if lang == "en" else "ru"
    templates = PERSONALIZED_STORY_TEMPLATES.get(lang_key, PERSONALIZED_STORY_TEMPLATES["uk"])
    template = random.choice(templates)
    return template.format(name=name or "Дитина", topic=topic or "нове")
