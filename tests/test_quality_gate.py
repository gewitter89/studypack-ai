import json
import os
import sys
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from core.quality_gate import (
    run_quality_gate, check_brands, check_medical_claims,
    check_structure, check_empty_pages, check_answer_count,
    check_repetitive_instructions, check_ai_tone, check_technical_words,
)


class TestQualityGate:
    def test_good_data_passes(self):
        data = {"title": "Test", "language": "ru",
                "pages": [{"page_number": 1, "tasks": [
                    {"question": "2+2", "answer": "4"},
                    {"question": "2+2", "answer": "4"},
                    {"question": "2+2", "answer": "4"},
                    {"question": "2+2", "answer": "4"}
                ]}],
                "answers": [{"page_number": 1, "answers": ["4", "4", "4", "4"]}]}
        passed, errors, warnings, comm_fails, score = run_quality_gate(data)
        assert passed
        assert len(errors) == 0

    def test_no_title_fails(self):
        data = {"title": "", "language": "ru", "pages": [],
                "answers": []}
        passed, errors, warnings, comm_fails, score = run_quality_gate(data)
        assert not passed
        assert any("title" in e.lower() for e in errors)

    def test_no_pages_fails(self):
        data = {"title": "Test", "language": "ru", "pages": []}
        passed, errors, warnings, comm_fails, score = run_quality_gate(data)
        assert not passed
        assert any("no pages" in e.lower() or "pages" in e.lower() for e in errors)

    def test_empty_pages_detected(self):
        data = {"title": "Test", "language": "ru",
                "pages": [{"page_number": 1, "tasks": []}]}
        passed, errors, warnings, comm_fails, score = run_quality_gate(data)
        assert any("empty" in str(e).lower() or "no tasks" in str(e).lower() for e in errors)

    def test_brand_minecraft_detected(self):
        issues = check_brands({"title": "Minecraft adventure"})
        assert len(issues) > 0
        assert "minecraft" in issues[0].lower()

    def test_brand_disney_detected(self):
        issues = check_brands({"content": "Disney princess"})
        assert len(issues) > 0

    def test_brand_lego_detected(self):
        issues = check_brands({"text": "Lego blocks"})
        assert len(issues) > 0

    def test_brand_clean_passes(self):
        issues = check_brands({"title": "Математика для детей"})
        assert len(issues) == 0

    def test_medical_claim_dyslexia_detected(self):
        issues = check_medical_claims({"text": "для детей с дислексией"})
        assert len(issues) > 0

    def test_medical_claim_autism_detected(self):
        issues = check_medical_claims({"text": "аутизм и развитие"})
        assert len(issues) > 0

    def test_medical_claim_clean_passes(self):
        issues = check_medical_claims({"text": "обычные задания"})
        assert len(issues) == 0

    def test_technical_words_detected(self):
        issues = check_technical_words({"text": "this is a prompt for generation"})
        assert len(issues) > 0

    def test_technical_words_openrouter(self):
        issues = check_technical_words({"text": "openrouter api"})
        assert len(issues) > 0

    def test_ai_tone_detected(self):
        issues = check_ai_tone({"text": "это задание поможет развить"})
        assert len(issues) > 0

    def test_ai_tone_uk(self):
        issues = check_ai_tone({"text": "це завдання допоможе"})
        assert len(issues) > 0

    def test_repetitive_instructions_detected(self):
        data = {"pages": [
            {"page_number": 1, "instruction": "Реши пример", "tasks": [{"question": "2+2"}]},
            {"page_number": 2, "instruction": "Реши пример", "tasks": [{"question": "3+3"}]},
            {"page_number": 3, "instruction": "Реши пример", "tasks": [{"question": "4+4"}]},
        ]}
        issues = check_repetitive_instructions(data)
        assert len(issues) > 0

    def test_repetitive_instructions_clean(self):
        data = {"pages": [
            {"page_number": 1, "instruction": "Реши пример", "tasks": [{"question": "2+2"}]},
            {"page_number": 2, "instruction": "Напиши ответ", "tasks": [{"question": "3+3"}]},
        ]}
        issues = check_repetitive_instructions(data)
        assert len(issues) == 0

    def test_answer_count_missing(self):
        data = {"pages": [{"page_number": 1, "tasks": [{"question": "2+2"}]}],
                "answers": [], "include_answers": True}
        issues = check_answer_count(data)
        assert len(issues) > 0

    def test_answer_count_ok(self):
        data = {"pages": [{"page_number": 1, "tasks": [{"question": "2+2"}]}],
                "answers": [{"page_number": 1, "answers": ["4"]}], "include_answers": True}
        issues = check_answer_count(data)
        assert len(issues) == 0

    def test_language_consistency_missing(self):
        data = {"language": ""}
        _, errors, _, _, _ = run_quality_gate(data)
        assert any("No language" in str(e) for e in errors)

    def test_full_pipeline_good(self):
        data = {"title": "Math", "language": "ru",
                "pages": [{"page_number": 1, "tasks": [
                    {"question": "2+2", "answer": "4"},
                    {"question": "2+2", "answer": "4"},
                    {"question": "2+2", "answer": "4"},
                    {"question": "2+2", "answer": "4"}
                ]},
                          {"page_number": 2, "tasks": [
                    {"question": "3+3", "answer": "6"},
                    {"question": "3+3", "answer": "6"},
                    {"question": "3+3", "answer": "6"},
                    {"question": "3+3", "answer": "6"}
                ]}],
                "answers": [{"page_number": 1, "answers": ["4", "4", "4", "4"]},
                            {"page_number": 2, "answers": ["6", "6", "6", "6"]}]}
        passed, errors, warnings, comm_fails, score = run_quality_gate(data)
        assert passed
