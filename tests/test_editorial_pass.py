import json
import os
import sys
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from core.editorial_pass import (
    editorial_pass, remove_template_phrases, humanize_instructions,
    shorten_for_age, diversify_beginnings, remove_ads_tone, TEMPLATE_PHRASES,
)


class TestEditorialPass:
    def test_remove_template_phrases_basic(self):
        text = "Это задание поможет развить когнитивные навыки. Реши пример."
        result = remove_template_phrases(text)
        assert "поможет" not in result
        assert "когнитивные" not in result
        assert "Реши пример" in result

    def test_remove_template_phrases_no_change(self):
        text = "Напиши букву А"
        assert remove_template_phrases(text) == "Напиши букву А"

    def test_remove_ai_phrases(self):
        text = "Сгенерировано через openrouter модель"
        result = remove_template_phrases(text)
        assert "openrouter" not in result
        assert "Сгенерировано" not in result
        assert "модель" in result

    def test_remove_ads_tone(self):
        text = "Это отличный способ развивать навыки"
        result = remove_ads_tone(text)
        assert "отличный способ" not in result

    def test_remove_ads_tone_uk(self):
        text = "Найкращий спосіб вивчити літери"
        result = remove_ads_tone(text)
        assert "найкращий" not in result.lower()

    def test_humanize_instructions_ru(self):
        text = "Выполни задание и ответь на вопросы"
        result = humanize_instructions(text, "ru")
        assert "Выполни" not in result
        assert "Подумай" in result or "подумай" in result.lower()

    def test_humanize_instructions_uk(self):
        text = "Виконай завдання та дай відповіді на питання"
        result = humanize_instructions(text, "uk")
        assert "Виконай" not in result

    def test_humanize_no_change_for_en(self):
        text = "Do the task"
        result = humanize_instructions(text, "en")
        assert result == "Do the task"

    def test_shorten_for_age_young(self):
        text = "Прочитай внимательно текст и ответь на все вопросы после него"
        result = shorten_for_age(text, 4)
        assert len(result) <= 30

    def test_shorten_for_age_older(self):
        text = "Прочитай текст и ответь на вопросы. Подумай хорошо."
        result = shorten_for_age(text, 10)
        assert len(result) >= len(text) - 5

    def test_shorten_for_age_does_not_empty(self):
        text = "Напиши букву А"
        result = shorten_for_age(text, 4)
        assert len(result) > 0

    def test_diversify_beginnings(self):
        texts = ["Прочитай текст", "Прочитай ещё раз", "Напиши ответ"]
        result = diversify_beginnings(texts)
        assert result[0] != result[1] or "Прочитай" not in result[1]

    def test_editorial_pass_full(self):
        import copy
        original_pi = "Отличный способ развить навыки и сгенерировано через"
        data = {
            "language": "ru", "age": 5,
            "title": "Test",
            "pages": [{"page_number": 1, "title": "T", "instruction": "", "tasks": [
                {"question": "Это задание поможет развить навыки. Выполни задание: 2+2",
                 "instruction": "Выполни задание сюда", "answer": "4"},
            ]}],
            "answers": [{"page_number": 1, "answers": ["4"]}],
            "parent_instruction": original_pi,
        }
        result = editorial_pass(copy.deepcopy(data))
        assert "поможет" not in result["pages"][0]["tasks"][0]["question"]
        assert "Выполни" not in result["pages"][0]["tasks"][0]["question"]
        assert result["parent_instruction"] != original_pi

    def test_editorial_pass_uk(self):
        data = {
            "language": "uk", "age": 6,
            "title": "Test",
            "pages": [{"page_number": 1, "title": "T", "instruction": "", "tasks": [
                {"question": "Виконай завдання: 2+2",
                 "instruction": "Виконай завдання", "answer": "4"},
            ]}],
            "answers": [{"page_number": 1, "answers": ["4"]}],
        }
        result = editorial_pass(data)
        assert "Виконай" not in result["pages"][0]["tasks"][0]["instruction"]

    def test_editorial_pass_age_shortening(self):
        data = {
            "language": "ru", "age": 4,
            "title": "Test",
            "pages": [{"page_number": 1, "title": "T", "instruction": "", "tasks": [
                {"question": "Прочитай внимательно длинный текст и ответь на все вопросы после него",
                 "instruction": "Прочитай внимательно длинный текст", "answer": "4"},
            ]}],
            "answers": [{"page_number": 1, "answers": ["4"]}],
        }
        result = editorial_pass(data)
        inst = result["pages"][0]["tasks"][0]["instruction"]
        assert len(inst) <= 22

    def test_templates_phrases_no_ai_false_positive(self):
        text = json.dumps({"card": "main_idea", "pairs": "match"})
        for phrase in TEMPLATE_PHRASES:
            if phrase in text.lower():
                assert phrase == "промпт" or phrase == "prompt"
