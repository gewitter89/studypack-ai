DIFFICULTY_PARAMS = {
    "easy": {
        "max_number": 20,
        "min_number": 1,
        "grid_size": 6,
        "maze_size": (5, 7),
        "word_length_max": 4,
        "tasks_per_page": 3,
        "instruction_detail": "simple",
        "age_shift": 0,
    },
    "medium": {
        "max_number": 100,
        "min_number": 1,
        "grid_size": 8,
        "maze_size": (8, 10),
        "word_length_max": 6,
        "tasks_per_page": 5,
        "instruction_detail": "normal",
        "age_shift": 1,
    },
    "hard": {
        "max_number": 1000,
        "min_number": 1,
        "grid_size": 10,
        "maze_size": (12, 14),
        "word_length_max": 8,
        "tasks_per_page": 7,
        "instruction_detail": "minimal",
        "age_shift": 2,
    },
}


def get_params(difficulty: str) -> dict:
    return DIFFICULTY_PARAMS.get(difficulty, DIFFICULTY_PARAMS["medium"])


def adjust_tasks_per_page(base_count: int, difficulty: str) -> int:
    params = get_params(difficulty)
    return min(base_count, params["tasks_per_page"])


def adjust_max_number(base: int, difficulty: str) -> int:
    params = get_params(difficulty)
    return min(base, params["max_number"])


def difficulty_suffix(difficulty: str, language: str = "ru") -> str:
    suffixes = {
        "easy": {"ru": "Базовый уровень", "uk": "Базовий рівень", "en": "Easy level"},
        "medium": {"ru": "Средний уровень", "uk": "Середній рівень", "en": "Medium level"},
        "hard": {"ru": "Продвинутый уровень", "uk": "Поглиблений рівень", "en": "Advanced level"},
    }
    return suffixes.get(difficulty, {}).get(language, difficulty)
