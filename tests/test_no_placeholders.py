import os
import sys
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from core.quality_gate import run_quality_gate

def test_no_placeholders_hard_fail():
    placeholders = [
        "word", "line", "shape", "digit", "object", "picture", "number", "sign",
        "placeholder", "TODO", "{topic_word}", "{word}", "{object}", "ssss",
        "ccccc", "ddddd"
    ]
    for p in placeholders:
        data = {
            "title": "Test Title",
            "language": "ru",
            "pages": [{
                "page_number": 1,
                "tasks": [{
                    "question": f"Найди {p} на картинке",
                    "answer": "ответ"
                }]
            }],
            "answers": [{"page_number": 1, "answers": ["ответ"]}]
        }
        passed, errors, warnings, comm_fails, score = run_quality_gate(data)
        assert not passed, f"Placeholder '{p}' did not trigger a hard fail!"
        assert any(p in err.lower() or "placeholder" in err.lower() for err in errors), f"Error for '{p}' not found in: {errors}"
