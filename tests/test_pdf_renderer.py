import json
import os
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from pdf.renderer import render_pdf


SAMPLE_PACK = {
    "title": "Тестовый набор",
    "subtitle": "Для проверки",
    "language": "ru",
    "age": 7,
    "grade": "1 класс",
    "topic": "dinosaurs",
    "pack_type": "math",
    "difficulty": "easy",
    "parent_instruction": "Занимайтесь 10-20 минут.",
    "pages": [
        {
            "page_number": 1,
            "page_type": "exercise",
            "title": "Сложение",
            "instruction": "Реши примеры",
            "tasks": [
                {"type": "math", "question": "2 + 2 = ?", "answer_space": True, "answer": "4"},
                {"type": "math", "question": "3 + 5 = ?", "answer_space": True, "answer": "8"}
            ]
        },
        {
            "page_number": 2,
            "page_type": "exercise",
            "title": "Вычитание",
            "instruction": "Реши примеры на вычитание",
            "tasks": [
                {"type": "math", "question": "7 - 3 = ?", "answer_space": True, "answer": "4"}
            ]
        }
    ],
    "answers": [
        {"page_number": 1, "answers": ["4", "8"]},
        {"page_number": 2, "answers": ["4"]}
    ]
}


def test_pdf_created():
    with tempfile.TemporaryDirectory() as tmpdir:
        output = os.path.join(tmpdir, "test.pdf")
        result = render_pdf(SAMPLE_PACK, output)
        assert os.path.exists(result)
        assert os.path.getsize(result) > 0


def test_pdf_not_empty():
    with tempfile.TemporaryDirectory() as tmpdir:
        output = os.path.join(tmpdir, "test.pdf")
        render_pdf(SAMPLE_PACK, output)
        size = os.path.getsize(output)
        assert size > 1000


def test_pdf_contains_title():
    with tempfile.TemporaryDirectory() as tmpdir:
        output = os.path.join(tmpdir, "test.pdf")
        render_pdf(SAMPLE_PACK, output)
        with open(output, "rb") as f:
            content = f.read()
        assert b"PDF" in content
        assert content.startswith(b"%PDF-")
