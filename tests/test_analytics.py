"""Tests for core.analytics module."""
import pytest
from core.analytics import (
    generate_report, format_report_text,
    ParentReport, CATEGORY_MAP, TYPE_LABELS, TYPE_DETAIL_LABELS,
)


def _make_pages(task_specs):
    pages = []
    for i, spec in enumerate(task_specs, 1):
        tasks = []
        for t, count in spec.items():
            tasks.extend([{"type": t, "question": f"q{j}"} for j in range(count)])
        pages.append({"page_number": i, "page_type": list(spec.keys())[0] if spec else "", "tasks": tasks})
    return pages


class TestGenerateReport:
    def test_empty_pages(self):
        r = generate_report([], "uk")
        assert r.total_pages == 0
        assert r.total_tasks == 0

    def test_basic_math(self):
        pages = _make_pages([{"math_addition": 3}, {"math_subtraction": 2}])
        r = generate_report(pages, "uk")
        assert r.total_pages == 2
        assert r.total_tasks == 5
        assert r.category_breakdown["math"] == 5

    def test_mixed_categories(self):
        pages = _make_pages([
            {"math_addition": 2},
            {"sudoku": 2},
            {"color_by_number": 3},
            {"story_read": 2},
        ])
        r = generate_report(pages, "uk")
        assert r.category_breakdown["math"] == 2
        assert r.category_breakdown["logic"] == 2
        assert r.category_breakdown["creative"] == 3
        assert r.category_breakdown["reading"] == 2

    def test_identifies_strength(self):
        pages = _make_pages([{"math_addition": 10}, {"sudoku": 2}])
        r = generate_report(pages, "uk")
        assert "Математика" in r.strengths

    def test_identifies_area_to_work(self):
        pages = _make_pages([{"math_addition": 10}, {"sudoku": 2}])
        r = generate_report(pages, "uk")
        assert "Логіка" in r.areas_to_work

    def test_recommends_missing_category(self):
        pages = _make_pages([{"math_addition": 5}])
        r = generate_report(pages, "uk")
        rec_ids = [rid for rid, _ in r.recommendations]
        assert any("add_" in rid for rid in rec_ids)

    def test_type_breakdown(self):
        pages = _make_pages([{"math_addition": 3}, {"math_addition": 2}])
        r = generate_report(pages, "uk")
        assert r.type_breakdown["math_addition"] == 5

    def test_ru_labels(self):
        pages = _make_pages([{"math_addition": 5}])
        r = generate_report(pages, "ru")
        assert "Математика" in r.strengths

    def test_en_labels(self):
        pages = _make_pages([{"math_addition": 5}])
        r = generate_report(pages, "en")
        assert "Mathematics" in r.strengths


class TestFormatReportText:
    def test_uk_lines(self):
        r = ParentReport(total_pages=5, total_tasks=20,
                        category_breakdown={"math": 15, "logic": 5},
                        strengths=["Математика"], areas_to_work=["Логіка"])
        lines = format_report_text(r, "uk")
        assert any("Сторінок" in l for l in lines)
        assert any("Математика" in l for l in lines)

    def test_ru_lines(self):
        r = ParentReport(total_pages=5, total_tasks=20,
                        category_breakdown={"math": 20}, strengths=["Математика"])
        lines = format_report_text(r, "ru")
        assert any("Страниц" in l for l in lines)

    def test_includes_percentages(self):
        r = ParentReport(total_pages=2, total_tasks=10,
                        category_breakdown={"math": 8, "logic": 2})
        lines = format_report_text(r, "uk")
        assert any("80%" in l for l in lines)

    def test_recommendations_in_text(self):
        r = ParentReport(total_pages=3, total_tasks=10,
                        category_breakdown={"math": 10},
                        recommendations=[("add_logic", "Логіка")])
        lines = format_report_text(r, "uk")
        assert any("Логіка" in l for l in lines)

    def test_diversify_recommendation(self):
        r = ParentReport(total_pages=10, total_tasks=30,
                        category_breakdown={"math": 30},
                        recommendations=[("diversify", "")])
        lines = format_report_text(r, "uk")
        assert any("Урізноманітнити" in l or "Разнообразить" in l for l in lines)


class TestCategoryMap:
    def test_all_common_types_mapped(self):
        common = ["math_addition", "math_subtraction", "sudoku", "maze",
                  "color_by_number", "story_read", "coloring"]
        for t in common:
            assert t in CATEGORY_MAP, f"{t} not in CATEGORY_MAP"

    def test_categories_valid(self):
        valid_cats = {"math", "logic", "creative", "reading"}
        for t, cat in CATEGORY_MAP.items():
            assert cat in valid_cats, f"{t} mapped to unknown category {cat}"


class TestLabels:
    def test_all_langs_present(self):
        for lang in ["uk", "ru", "en"]:
            assert lang in TYPE_LABELS
            assert "math" in TYPE_LABELS[lang]
            assert "logic" in TYPE_LABELS[lang]
            assert "creative" in TYPE_LABELS[lang]
            assert "reading" in TYPE_LABELS[lang]
