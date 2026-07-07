import json
import os
import sys
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from core.card_generator import (
    generate_from_preset, _generate_cards, _make_template_for_id,
    _math_tasks_from_generator, _make_fallback_tasks,
)
from core.cards.base import CardResult, CardTemplate
from core.deterministic_generators.math_generator import DeterministicMathGenerator
from core.card_text_gen import GENERATORS as TEXT_GENERATORS


class TestCardGenerator:
    def test_generate_from_preset_simple(self):
        preset = {"age": 7, "difficulty": "easy", "language": "ru", "topic": "general",
                   "pages_count": 6, "cards": ["math_addition"], "title": "Test"}
        from core.postprocess import postprocess
        data = postprocess(generate_from_preset(preset))
        assert data is not None
        assert len(data["pages"]) == 6
        assert len(data["answers"]) == 6
        assert data["_quality"]["passed"] is True

    def test_generate_from_preset_no_cards(self):
        preset = {"age": 7, "difficulty": "easy", "language": "ru", "topic": "test",
                   "pages_count": 4, "cards": [], "title": "Test"}
        data = generate_from_preset(preset)
        assert data is not None
        assert len(data["pages"]) == 4

    def test_generate_from_preset_uk(self):
        preset = {"age": 6, "difficulty": "easy", "language": "uk", "topic": "tварини",
                   "pages_count": 8, "cards": ["letter_trace", "count_trace"], "title": "Test"}
        data = generate_from_preset(preset)
        assert data is not None
        assert data["language"] == "uk"

    def test_generate_from_preset_en(self):
        preset = {"age": 7, "difficulty": "easy", "language": "en", "topic": "farm",
                   "pages_count": 6, "cards": ["abc_match", "word_picture"], "title": "English"}
        data = generate_from_preset(preset)
        assert data is not None
        assert data["language"] == "en"
        assert len(data["pages"]) > 0

    def test_generate_math_cards(self):
        tmpl = _make_template_for_id("math_addition", "easy", 7)
        cards = _generate_cards(tmpl, 5, "dinosaurs", 42)
        assert len(cards) == 5
        for c in cards:
            assert "+" in c.question or "?" in c.question or "додали" in c.question

    def test_generate_compare_cards(self):
        tmpl = _make_template_for_id("math_compare", "medium", 8)
        cards = _generate_cards(tmpl, 4, "space", 42)
        assert len(cards) == 4
        for c in cards:
            assert c.answer in (">", "<", "=")

    def test_generate_subtraction_cards(self):
        tmpl = _make_template_for_id("math_subtraction", "easy", 7)
        cards = _generate_cards(tmpl, 3, "toys", 42)
        assert len(cards) == 3
        for c in cards:
            assert "-" in c.question or "залишилося" in c.question

    def test_generate_reading_story(self):
        tmpl = _make_template_for_id("story_read", "medium", 8)
        cards = _generate_cards(tmpl, 2, "underwater", 42, "uk")
        assert len(cards) == 2
        assert all(c.question for c in cards)
        assert all(c.answer for c in cards)

    def test_generate_pattern(self):
        tmpl = _make_template_for_id("pattern", "easy", 6)
        cards = _generate_cards(tmpl, 3, "space", 42, "ru")
        assert len(cards) == 3
        for c in cards:
            assert "ряд" in c.question.lower() or "продолжи" in c.question.lower()

    def test_generate_odd_one_out(self):
        tmpl = _make_template_for_id("odd_one_out", "easy", 6)
        cards = _generate_cards(tmpl, 2, "animals", 42, "ru")
        assert len(cards) == 2
        assert all(c.answer for c in cards)

    def test_generate_character_guess(self):
        tmpl = _make_template_for_id("character_guess", "medium", 7)
        cards = _generate_cards(tmpl, 2, "fairytale", 42, "uk")
        assert len(cards) == 2
        assert all(c.answer for c in cards)

    def test_generate_letter_trace(self):
        tmpl = _make_template_for_id("letter_trace", "easy", 5)
        cards = _generate_cards(tmpl, 2, "animals", 42, "uk")
        assert len(cards) == 2
        assert all("букв" in c.question.lower() or "обведи" in c.question.lower() for c in cards)

    def test_generate_english_abc(self):
        tmpl = _make_template_for_id("abc_match", "easy", 7)
        cards = _generate_cards(tmpl, 2, "farm", 42, "en")
        assert len(cards) == 2
        assert all(c.answer for c in cards)
        assert all("match" in c.question.lower() for c in cards)

    def test_generate_english_fill_gap(self):
        tmpl = _make_template_for_id("fill_gap_en", "medium", 8)
        cards = _generate_cards(tmpl, 3, "school", 42, "en")
        assert len(cards) == 3
        for c in cards:
            assert c.answer in ("am", "is", "are")

    def test_text_generators_have_all_types(self):
        expected = ["story_read", "question_answer", "find_word", "pattern", "odd_one_out",
                     "analogy", "maze", "letter_trace", "count_trace", "shape_find",
                     "abc_match", "word_picture", "fill_gap_en", "sentence_build"]
        for name in expected:
            assert name in TEXT_GENERATORS, f"Missing text generator: {name}"

    def test_generate_with_answers_enabled(self):
        preset = {"age": 7, "difficulty": "easy", "language": "ru", "topic": "math",
                   "pages_count": 4, "cards": ["math_addition"], "title": "Test",
                   "include_answers": True}
        data = generate_from_preset(preset)
        assert len(data["answers"]) > 0

    def test_generate_with_answers_disabled(self):
        preset = {"age": 7, "difficulty": "easy", "language": "ru", "topic": "math",
                   "pages_count": 4, "cards": ["math_addition"], "title": "Test",
                   "include_answers": False}
        data = generate_from_preset(preset)
        assert len(data["answers"]) == 0

    def test_generate_no_empty_pages(self):
        for cards in [["math_addition"], ["pattern", "odd_one_out"], ["letter_trace", "count_trace"]]:
            preset = {"age": 7, "difficulty": "easy", "language": "ru", "topic": "test",
                       "pages_count": 8, "cards": cards, "title": "Test"}
            data = generate_from_preset(preset)
            for p in data["pages"]:
                assert len(p["tasks"]) > 0, f"Empty page {p['page_number']}"

    def test_generate_color_by_number(self):
        tmpl = _make_template_for_id("color_by_number", "easy", 6, "uk")
        results = _generate_cards(tmpl, 2, "animals", 42, "uk")
        assert len(results) == 2
        assert all(r.card_type == "color_by_number" for r in results)
        assert all(r.instruction for r in results)
        assert all(r.visual_aid for r in results)

    def test_generate_sudoku(self):
        tmpl = _make_template_for_id("sudoku", "easy", 7, "uk")
        results = _generate_cards(tmpl, 1, "general", 42, "uk")
        assert len(results) == 1
        assert results[0].card_type == "sudoku"
        assert "1–" in results[0].instruction

    def test_generate_connect_dots(self):
        tmpl = _make_template_for_id("connect_dots", "easy", 5, "uk")
        results = _generate_cards(tmpl, 2, "general", 42, "uk")
        assert len(results) == 2
        assert all(r.card_type == "connect_dots" for r in results)

    def test_generate_graphic_dictation(self):
        tmpl = _make_template_for_id("graphic_dictation", "easy", 6, "uk")
        results = _generate_cards(tmpl, 1, "general", 42, "uk")
        assert len(results) == 1
        assert results[0].card_type == "graphic_dictation"
        assert "клітинці" in results[0].instruction or "клеточке" in results[0].instruction

    def test_new_card_types_multilang(self):
        for lang in ["uk", "ru", "en"]:
            for cid in ["color_by_number", "sudoku", "connect_dots", "graphic_dictation"]:
                tmpl = _make_template_for_id(cid, "easy", 6, lang)
                results = _generate_cards(tmpl, 1, "test", 42, lang)
                assert len(results) >= 1, f"No results for {cid} in {lang}"
                assert len(results[0].instruction) > 5, f"Empty instruction for {cid} in {lang}"

    def test_generate_find_differences(self):
        tmpl = _make_template_for_id("find_differences", "easy", 6, "uk")
        results = _generate_cards(tmpl, 2, "general", 42, "uk")
        assert len(results) == 2
        assert all(r.card_type == "find_differences" for r in results)
        assert all(r.visual_aid for r in results)
        assert results[0].answer

    def test_generate_maze(self):
        tmpl = _make_template_for_id("maze", "easy", 6, "uk")
        results = _generate_cards(tmpl, 1, "general", 42, "uk")
        assert len(results) == 1
        assert results[0].card_type == "maze"
        assert results[0].visual_aid
        assert "кроків" in results[0].answer or "шаг" in results[0].answer

    def test_generate_crossword(self):
        tmpl = _make_template_for_id("crossword", "medium", 7, "uk")
        results = _generate_cards(tmpl, 1, "animals", 42, "uk")
        assert len(results) == 1
        assert results[0].card_type == "crossword"
        assert results[0].visual_aid
        assert len(results[0].answer) > 5

    def test_phase2_multilang(self):
        for lang in ["uk", "ru", "en"]:
            for cid in ["find_differences", "maze", "crossword"]:
                tmpl = _make_template_for_id(cid, "easy", 6, lang)
                results = _generate_cards(tmpl, 1, "general", 42, lang)
                assert len(results) >= 1, f"No results for {cid} in {lang}"
                assert len(results[0].instruction) > 5, f"Empty instruction for {cid} in {lang}"
