import os
import sys
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from core.quality_gate import run_quality_gate

def test_theme_mismatch_fails_quality_gate():
    # If the topic is dinosaurs, but the cover title has nothing to do with it, it's a fail
    data = {
        "title": "Смешной набор на тему Природа",
        "topic": "dinosaurs",
        "language": "ru",
        "pages": [{
            "page_number": 1,
            "tasks": [{
                "type": "math",
                "question": "Посчитай динозавров",
                "answer": "3 динозавра"
            }]
        }],
        "answers": [{"page_number": 1, "answers": ["3 динозавра"]}]
    }
    passed, errors, warnings, comm_fails, score = run_quality_gate(data)
    assert any("does not match topic" in cf.lower() or "may not match topic" in cf.lower() for cf in comm_fails), f"Expected theme mismatch fail: {comm_fails}"

def test_theme_match_passes():
    data = {
        "title": "Набор про динозавров",
        "topic": "dinosaurs",
        "language": "ru",
        "pages": [{
            "page_number": 1,
            "tasks": [{
                "type": "math",
                "question": "Посчитай динозавров",
                "answer": "3 динозавра"
            }]
        }],
        "answers": [{"page_number": 1, "answers": ["3 динозавра"]}]
    }
    passed, errors, warnings, comm_fails, score = run_quality_gate(data)
    assert not any("does not match topic" in cf.lower() for cf in comm_fails), f"Valid theme match was flagged: {comm_fails}"
