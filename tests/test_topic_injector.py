import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from core.topic_injector import inject_topic, subject_for
from core.topic_lexicon import get_words


class TestTopicInjector:
    def test_inject_into_math_dino(self):
        q, a = inject_topic("5 + 3 = ?", "8", "dinosaurs", "ru", "math_addition", seed=42)
        assert any(w in q.lower() for w in ["динозавр", "яйцо", "след", "вулкан", "кость"]), f"No dino word in: {q}"

    def test_inject_into_math_uk(self):
        q, a = inject_topic("5 + 3 = ?", "8", "dinosaurs", "uk", "math_addition", seed=42)
        assert any(w in q.lower() for w in ["динозавр", "яйце", "слід", "вулкан", "кістка"]), f"No dino word in: {q}"

    def test_inject_into_math_pixel(self):
        q, a = inject_topic("5 + 3 = ?", "8", "pixel_world", "uk", "math_addition", seed=7)
        assert any(w in q.lower() for w in ["блок", "піксель", "куб", "світ", "інвентар"]), f"No pixel word in: {q}"

    def test_inject_into_preschool(self):
        q, a = inject_topic("Count the stars ★★★", "3", "space", "en", "count_trace", seed=1)
        assert any(w in q.lower() for w in ["ракет", "планет", "звезд", "star", "astronaut", "космонавт", "alien"]), f"No space word in: {q}"

    def test_inject_into_english_farm(self):
        q, a = inject_topic("Fill in: The ___ is in the barn.", "cow", "farm", "en", "fill_gap_en", seed=5)
        words = get_words("farm", "en")
        assert any(w in q.lower() for w in words), f"No farm word in: {q}"

    def test_inject_into_uk_travel(self):
        q, a = inject_topic("I ___ a student.", "am", "travel", "en", "fill_gap_en", seed=3)
        words = get_words("travel", "en")
        assert any(w in q.lower() for w in words), f"No travel word in: {q}"

    def test_general_topic_skipped(self):
        q_orig, a_orig = "2+2=?", "4"
        q, a = inject_topic(q_orig, a_orig, "general", "ru", "math_addition", seed=42)
        assert q == q_orig, f"General topic should not modify question: {q}"

    def test_custom_topic_skipped(self):
        q_orig, a_orig = "Count the stars", "5"
        q, a = inject_topic(q_orig, a_orig, "custom", "en", "count_en", seed=0)
        assert q == q_orig

    def test_subject_for_preschool(self):
        assert subject_for("count_trace") == "preschool"
        assert subject_for("coloring") == "preschool"
        assert subject_for("shape_find") == "preschool"

    def test_subject_for_english(self):
        assert subject_for("fill_gap_en") == "english"
        assert subject_for("correct_form_en") == "english"
        assert subject_for("sentence_build") == "english"

    def test_subject_for_math(self):
        assert subject_for("math_addition") == "math"
        assert subject_for("math_multiplication") == "math"
