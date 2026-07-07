"""Tests for core.adaptive_difficulty module."""
import pytest
from core.adaptive_difficulty import (
    get_age_bracket, get_profile, adaptive_math_range,
    adaptive_card_params, recommended_card_mix, next_theme_in_chain,
    generate_story_opening, AGE_PROFILES, THEME_CHAINS,
)


class TestAgeBrackets:
    def test_bracket_3(self):
        assert get_age_bracket(3) == "3-4"

    def test_bracket_4(self):
        assert get_age_bracket(4) == "3-4"

    def test_bracket_5(self):
        assert get_age_bracket(5) == "5-6"

    def test_bracket_7(self):
        assert get_age_bracket(7) == "7-8"

    def test_bracket_10(self):
        assert get_age_bracket(10) == "9-10"

    def test_bracket_12(self):
        assert get_age_bracket(12) == "11-12"

    def test_bracket_2(self):
        assert get_age_bracket(2) == "3-4"


class TestProfiles:
    def test_all_brackets_have_profiles(self):
        for bracket in ["3-4", "5-6", "7-8", "9-10", "11-12"]:
            assert bracket in AGE_PROFILES

    def test_younger_simpler_math(self):
        young = get_profile(4)
        old = get_profile(10)
        assert young.math_add_range[1] < old.math_add_range[1]

    def test_younger_no_multiplication(self):
        young = get_profile(4)
        assert young.math_mult_range == (0, 0)

    def test_older_has_multiplication(self):
        old = get_profile(10)
        assert old.math_mult_range[1] > 0

    def test_younger_smaller_maze(self):
        young = get_profile(4)
        old = get_profile(10)
        assert young.maze_size[0] < old.maze_size[0]

    def test_younger_fewer_differences(self):
        young = get_profile(5)
        old = get_profile(10)
        assert young.find_diffs_count < old.find_diffs_count


class TestAdaptiveMathRange:
    def test_add_young(self):
        r = adaptive_math_range(4, "add")
        assert r == (1, 5)

    def test_add_older(self):
        r = adaptive_math_range(10, "add")
        assert r == (10, 50)

    def test_subtract(self):
        r = adaptive_math_range(8, "subtract")
        assert r[0] >= 5

    def test_multiply_young(self):
        r = adaptive_math_range(4, "multiply")
        assert r == (0, 0)

    def test_multiply_old(self):
        r = adaptive_math_range(10, "multiply")
        assert r[1] > 0

    def test_unknown_op_fallback(self):
        r = adaptive_math_range(7, "unknown")
        assert r == (1, 10)


class TestAdaptiveCardParams:
    def test_sudoku(self):
        p = adaptive_card_params(7, "sudoku")
        assert "size" in p

    def test_maze(self):
        p = adaptive_card_params(7, "maze")
        assert "width" in p
        assert "height" in p

    def test_find_differences(self):
        p = adaptive_card_params(7, "find_differences")
        assert "diff_count" in p

    def test_crossword(self):
        p = adaptive_card_params(8, "crossword")
        assert "min_words" in p
        assert "max_words" in p

    def test_unknown_type(self):
        p = adaptive_card_params(7, "unknown")
        assert p == {}


class TestRecommendedCardMix:
    def test_young_no_crossword(self):
        cards = recommended_card_mix(3, 4)
        assert "crossword" not in cards

    def test_young_has_color(self):
        cards = recommended_card_mix(3, 4)
        visual = [c for c in cards if c in ("color_by_number", "coloring", "connect_dots")]
        assert len(visual) > 0

    def test_older_has_sudoku(self):
        cards = recommended_card_mix(10, 8)
        assert "sudoku" in cards

    def test_older_has_crossword(self):
        cards = recommended_card_mix(9, 8)
        assert "crossword" in cards

    def test_respects_count(self):
        cards = recommended_card_mix(7, 6)
        assert len(cards) == 6


class TestThemeChains:
    def test_animals_chain(self):
        assert "animals" in THEME_CHAINS

    def test_next_in_chain(self):
        nxt = next_theme_in_chain("animals", 0)
        assert nxt in THEME_CHAINS["animals"]
        assert nxt != "animals"

    def test_cycle_back(self):
        chain = THEME_CHAINS["animals"]
        last = chain[-1]
        nxt = next_theme_in_chain(last, 0)
        assert nxt == chain[0]

    def test_unknown_topic_returns_self(self):
        assert next_theme_in_chain("xyz_unknown", 0) == "xyz_unknown"


class TestStoryOpening:
    def test_uk(self):
        s = generate_story_opening("Мія", "animals", "uk")
        assert "Мія" in s
        assert "animals" in s or "тварин" in s.lower() or len(s) > 10

    def test_ru(self):
        s = generate_story_opening("Саша", "space", "ru")
        assert "Саша" in s

    def test_en(self):
        s = generate_story_opening("Lily", "ocean", "en")
        assert "Lily" in s

    def test_empty_name_uses_fallback(self):
        s = generate_story_opening("", "animals", "uk")
        assert len(s) > 10
