import os
import sys
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from core.quality_gate import run_quality_gate

def test_empty_answers_fail_quality_gate():
    # If tasks are standard (e.g. math), empty answers should be a commercial fail
    data = {
        "title": "Тест Математика",
        "language": "uk",
        "pages": [{
            "page_number": 1,
            "tasks": [{
                "type": "math",
                "question": "2 + 2 = ?",
                "answer": ""
            }]
        }],
        "answers": [{"page_number": 1, "answers": [""]}]
    }
    passed, errors, warnings, comm_fails, score = run_quality_gate(data)
    assert any("empty answer" in cf.lower() for cf in comm_fails), f"Expected commercial fail for empty answers. Fails: {comm_fails}"

def test_creative_empty_answers_allowed():
    # Creative tasks are allowed to have creative placeholder answers like "Перевіряється дорослим"
    data = {
        "title": "Тест Малювання",
        "language": "uk",
        "pages": [{
            "page_number": 1,
            "tasks": [{
                "type": "creative",
                "question": "Розфарбуй кошеня",
                "answer": "Перевіряється дорослим"
            }]
        }],
        "answers": [{"page_number": 1, "answers": ["Перевіряється дорослим"]}]
    }
    passed, errors, warnings, comm_fails, score = run_quality_gate(data)
    assert not any("empty answer" in cf.lower() for cf in comm_fails), f"Creative answer was flagged as fail: {comm_fails}"
