import json
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.validator import validate_json_structure, validate_study_pack, check_safety


def test_valid_json_passes():
    data = {
        "title": "Test",
        "subtitle": "Sub",
        "language": "ru",
        "age": 7,
        "grade": "1 класс",
        "topic": "dinosaurs",
        "pack_type": "math",
        "difficulty": "easy",
        "parent_instruction": "Inst",
        "pages": [
            {
                "page_number": 1,
                "page_type": "exercise",
                "title": "Page 1",
                "instruction": "Do it",
                "tasks": [
                    {"type": "math", "question": "2+2?", "answer_space": True, "answer": "4"}
                ]
            }
        ],
        "answers": [{"page_number": 1, "answers": ["4"]}]
    }
    raw = json.dumps(data)
    valid, parsed, error = validate_json_structure(raw)
    assert valid
    assert parsed is not None
    assert error == ""


def test_invalid_json_fails():
    raw = "{invalid json}"
    valid, parsed, error = validate_json_structure(raw)
    assert not valid
    assert parsed is None
    assert "Невалидный JSON" in error


def test_validation_no_pages_fails():
    data = {
        "title": "Test",
        "subtitle": "Sub",
        "language": "ru",
        "age": 7,
        "grade": "1",
        "topic": "test",
        "pack_type": "math",
        "difficulty": "easy",
        "parent_instruction": "",
        "pages": [],
        "answers": []
    }
    result = validate_study_pack(data, 8, False)
    assert not result.is_valid
    assert any("Нет страниц" in e for e in result.errors)


def test_validation_no_title_fails():
    data = {
        "title": "",
        "subtitle": "Sub",
        "language": "ru",
        "age": 7,
        "grade": "1",
        "topic": "test",
        "pack_type": "math",
        "difficulty": "easy",
        "parent_instruction": "",
        "pages": [
            {
                "page_number": 1,
                "page_type": "exercise",
                "title": "Page 1",
                "instruction": "Do it",
                "tasks": []
            }
        ],
        "answers": []
    }
    result = validate_study_pack(data, 8, False)
    assert not result.is_valid
    assert any("Отсутствует название" in e for e in result.errors)


def test_safety_check_finds_brand():
    issues = check_safety("Play with Minecraft characters")
    assert len(issues) > 0
    assert any("Minecraft" in i for i in issues)


def test_safety_check_finds_medical_claim():
    issues = check_safety("This exercise лечит дислексию")
    assert len(issues) > 0


def test_safety_clean_text_passes():
    issues = check_safety("Solve the math problem")
    assert len(issues) == 0
