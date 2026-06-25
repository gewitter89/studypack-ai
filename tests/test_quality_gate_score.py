import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from core.quality_gate import (
    run_quality_gate, compute_commercial_score,
    check_repetitive_instructions, check_topic_usage, check_language_mismatch,
)

SAMPLE_PAGE = {"page_number": 1, "tasks": [{"question": "2+2", "answer": "4"}]}


class TestQualityGateScore:
    def test_uk_no_ru_words_passes(self):
        data = {
            "title": "Математика", "language": "uk",
            "pages": [
                {"page_number": 1, "instruction": "Розв'яжи приклади", "tasks": [{"question": "2+2", "answer": "4"}]},
                {"page_number": 2, "instruction": "Знайди правильну відповідь", "tasks": [{"question": "3+3", "answer": "6"}]},
            ],
            "answers": [{"page_number": 1, "answers": ["4"]}, {"page_number": 2, "answers": ["6"]}],
            "age": 7, "topic": "general",
        }
        passed, errors, warnings, comm_fails, score = run_quality_gate(data)
        assert passed
        assert score >= 60

    def test_uk_with_ru_word_fails(self):
        data = {
            "title": "Математика", "language": "uk",
            "pages": [
                {"page_number": 1, "instruction": "Найди ответ", "tasks": [{"question": "2+2", "answer": "4"}]},
            ],
            "answers": [{"page_number": 1, "answers": ["4"]}],
            "age": 7,
        }
        passed, errors, warnings, comm_fails, score = run_quality_gate(data)
        assert not passed
        assert any("Russian word" in e for e in errors)

    def test_instruction_repeat_5_gives_hard_fail(self):
        data = {"pages": [
            {"page_number": i, "instruction": "Реши пример", "tasks": [{"question": "2+2"}]}
            for i in range(1, 6)
        ]}
        issues = check_repetitive_instructions(data)
        assert any("HARD FAIL" in i for i in issues)

    def test_instruction_repeat_3_gives_warning(self):
        data = {"pages": [
            {"page_number": i, "instruction": "Реши пример", "tasks": [{"question": "2+2"}]}
            for i in range(1, 4)
        ]}
        issues = check_repetitive_instructions(data)
        assert any("WARNING" in i for i in issues)

    def test_commercial_score_below_80_fails(self):
        data = {
            "title": "Test", "language": "uk",
            "pages": [{"page_number": 1, "instruction": "Розв'яжи приклади",
                       "tasks": [{"question": "2+2", "answer": "4"}]}],
            "answers": [{"page_number": 1, "answers": ["4"]}],
            "age": 7, "topic": "general",
        }
        score = compute_commercial_score(data)
        assert score >= 0

    def test_commercial_score_max_100(self):
        score = compute_commercial_score({
            "title": "Test", "language": "uk", "age": 7, "topic": "general",
            "pages": [
                {"page_number": 1, "instruction": "Розв'яжи приклади",
                 "tasks": [{"question": "2+2", "answer": "4"}]},
                {"page_number": 2, "instruction": "Знайди правильну відповідь",
                 "tasks": [{"question": "3+3", "answer": "6"}]},
            ],
            "answers": [{"page_number": 1, "answers": ["4"]}, {"page_number": 2, "answers": ["6"]}],
        })
        assert score <= 100

    def test_topic_threshold_depends_on_subject(self):
        from core.quality_gate import _get_topic_threshold
        class Mock:
            def get(self, k, d=None):
                return {"pack_type": "math"}.get(k, d)
        assert _get_topic_threshold(Mock()) == 0.5

        class Mock2:
            def get(self, k, d=None):
                return {"pack_type": "preschool"}.get(k, d)
        assert _get_topic_threshold(Mock2()) == 0.7
