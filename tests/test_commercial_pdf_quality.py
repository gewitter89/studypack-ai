import os
import sys
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from core.quality_gate import run_quality_gate, compute_commercial_score

def test_commercial_quality_gate_score_boundaries():
    # A perfectly compliant pack
    good_data = {
        "title": "Сборник про динозавров",
        "topic": "dinosaurs",
        "language": "ru",
        "pack_type": "math",
        "pages": [
            {"page_number": 1, "tasks": [{"type": "math", "question": "Сколько тут тираннозавров?", "answer": "3 тираннозавра"}]},
            {"page_number": 2, "tasks": [{"type": "math", "question": "Реши задачу с яйцами динозавров", "answer": "5 яиц"}]}
        ],
        "answers": [
            {"page_number": 1, "answers": ["3 тираннозавра"]},
            {"page_number": 2, "answers": ["5 яиц"]}
        ]
    }
    passed, errors, warnings, comm_fails, score = run_quality_gate(good_data)
    assert score >= 80, f"Expected high commercial score, got {score}. Errors: {errors + comm_fails}"
    assert len(errors) == 0, f"Expected no hard errors, got: {errors}"
    assert len(comm_fails) == 0, f"Expected no commercial failures, got: {comm_fails}"

def test_commercial_quality_gate_fails_on_low_score():
    # Missing answers and mismatch languages should lower the score drastically
    bad_data = {
        "title": "Сборник про динозавров",
        "topic": "dinosaurs",
        "language": "uk",
        "pack_type": "math",
        "pages": [
            {"page_number": 1, "tasks": [{"type": "math", "question": "Реши задачу с динозавром", "answer": ""}]}  # Russian word in UK, empty answer
        ],
        "answers": []
    }
    passed, errors, warnings, comm_fails, score = run_quality_gate(bad_data)
    assert score < 80, f"Expected low commercial score, got {score}"
    assert any("score=" in cf.lower() for cf in comm_fails), f"Expected low score failure in comm_fails: {comm_fails}"
