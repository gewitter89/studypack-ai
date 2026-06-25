import os
import sys
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from core.difficulty import get_params, adjust_tasks_per_page, adjust_max_number, difficulty_suffix


class TestDifficulty:
    def test_easy_params(self):
        p = get_params("easy")
        assert p["max_number"] == 20
        assert p["tasks_per_page"] == 3
        assert p["grid_size"] == 6

    def test_medium_params(self):
        p = get_params("medium")
        assert p["max_number"] == 100
        assert p["tasks_per_page"] == 5
        assert p["grid_size"] == 8

    def test_hard_params(self):
        p = get_params("hard")
        assert p["max_number"] == 1000
        assert p["tasks_per_page"] == 7
        assert p["grid_size"] == 10

    def test_unknown_difficulty_defaults_to_medium(self):
        p = get_params("unknown")
        assert p == get_params("medium")

    def test_adjust_tasks_per_page_easy(self):
        assert adjust_tasks_per_page(10, "easy") == 3

    def test_adjust_tasks_per_page_medium(self):
        assert adjust_tasks_per_page(10, "medium") == 5

    def test_adjust_tasks_per_page_hard(self):
        assert adjust_tasks_per_page(10, "hard") == 7

    def test_adjust_max_number_easy(self):
        assert adjust_max_number(50, "easy") == 20

    def test_adjust_max_number_medium(self):
        assert adjust_max_number(50, "medium") == 50

    def test_adjust_max_number_hard(self):
        assert adjust_max_number(50, "hard") == 50

    def test_difficulty_suffix_ru(self):
        assert difficulty_suffix("easy", "ru") == "Базовый уровень"
        assert difficulty_suffix("medium", "ru") == "Средний уровень"
        assert difficulty_suffix("hard", "ru") == "Продвинутый уровень"

    def test_difficulty_suffix_uk(self):
        assert difficulty_suffix("easy", "uk") == "Базовий рівень"
        assert difficulty_suffix("hard", "uk") == "Поглиблений рівень"

    def test_difficulty_suffix_en(self):
        assert difficulty_suffix("easy", "en") == "Easy level"
        assert difficulty_suffix("hard", "en") == "Advanced level"

    def test_difficulty_suffix_unknown_lang(self):
        assert difficulty_suffix("easy", "fr") == "easy"

    def test_age_shift_easy(self):
        assert get_params("easy")["age_shift"] == 0

    def test_age_shift_hard(self):
        assert get_params("hard")["age_shift"] == 2

    def test_maze_size_variation(self):
        assert get_params("easy")["maze_size"] == (5, 7)
        assert get_params("hard")["maze_size"] == (12, 14)
