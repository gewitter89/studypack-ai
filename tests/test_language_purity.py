import os
import sys
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from core.quality_gate import run_quality_gate

def test_ukrainian_pdf_no_russian_words():
    # Russian words forbidden in Ukrainian PDF
    banned_ru = [
        "дошкольник", "подготовка к школе", "животные",
        "найди", "посчитай", "какая", "реши", "соедини"
    ]
    for w in banned_ru:
        data = {
            "title": "Тест",
            "language": "uk",
            "pages": [{
                "page_number": 1,
                "tasks": [{
                    "question": f"Спробуй {w} це завдання",
                    "answer": "кіт"
                }]
            }],
            "answers": [{"page_number": 1, "answers": ["кіт"]}]
        }
        passed, errors, warnings, comm_fails, score = run_quality_gate(data)
        assert not passed, f"Russian word '{w}' in Ukrainian PDF did not fail the quality gate!"
        assert any(w in err.lower() or "russian word" in err.lower() for err in errors)

def test_russian_pdf_no_ukrainian_words():
    # Ukrainian words forbidden in Russian PDF
    banned_uk = [
        "порахуй", "знайди", "з'єднай", "розв'яжи", "дай відповіді",
        "намалюй", "розфарбуй", "будь ласка", "який", "яка",
        "дошкільник", "підготовка до школи"
    ]
    for w in banned_uk:
        data = {
            "title": "Тест",
            "language": "ru",
            "pages": [{
                "page_number": 1,
                "tasks": [{
                    "question": f"Попробуй {w} это задание",
                    "answer": "кот"
                }]
            }],
            "answers": [{"page_number": 1, "answers": ["кот"]}]
        }
        passed, errors, warnings, comm_fails, score = run_quality_gate(data)
        assert not passed, f"Ukrainian word '{w}' in Russian PDF did not fail the quality gate!"
        assert any(w in err.lower() or "ukrainian word" in err.lower() for err in errors)
