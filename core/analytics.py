"""Analytics engine — generates parent report from pack data."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple


@dataclass
class TypeStats:
    card_type: str
    count: int
    category: str


@dataclass
class ParentReport:
    total_pages: int
    total_tasks: int
    type_breakdown: Dict[str, int] = field(default_factory=dict)
    category_breakdown: Dict[str, int] = field(default_factory=dict)
    recommendations: List[Tuple[str, str]] = field(default_factory=list)
    strengths: List[str] = field(default_factory=list)
    areas_to_work: List[str] = field(default_factory=list)


CATEGORY_MAP = {
    "math_addition": "math", "math_subtraction": "math",
    "math_multiplication": "math", "math_division": "math",
    "math_compare": "math", "missing_number": "math", "math_word": "math",
    "sudoku": "logic", "maze": "logic", "find_differences": "logic",
    "crossword": "logic", "sequence": "logic", "pattern": "logic",
    "odd_one_out": "logic", "analogy": "logic",
    "color_by_number": "creative", "connect_dots": "creative",
    "coloring": "creative", "graphic_dictation": "creative",
    "story_read": "reading", "find_word": "reading",
    "question_answer": "reading", "word_search": "reading",
    "text_question": "reading",
}

TYPE_LABELS = {
    "uk": {
        "math": "Математика", "logic": "Логіка",
        "creative": "Творчість", "reading": "Читання",
    },
    "ru": {
        "math": "Математика", "logic": "Логика",
        "creative": "Творчество", "reading": "Чтение",
    },
    "en": {
        "math": "Mathematics", "logic": "Logic",
        "creative": "Creativity", "reading": "Reading",
    },
}

TYPE_DETAIL_LABELS = {
    "uk": {
        "math_addition": "Додавання", "math_subtraction": "Віднімання",
        "math_multiplication": "Множення", "math_division": "Ділення",
        "math_compare": "Порівняння", "sudoku": "Судоку",
        "maze": "Лабіринти", "find_differences": "Знайди відмінності",
        "crossword": "Кросворди", "color_by_number": "Розфарбовки за номерами",
        "connect_dots": "З'єднати точки", "graphic_dictation": "Графічний диктант",
        "coloring": "Розфарбовки", "story_read": "Читання текстів",
        "text_question": "Текстові питання", "word_search": "Пошук слів",
    },
    "ru": {
        "math_addition": "Сложение", "math_subtraction": "Вычитание",
        "math_multiplication": "Умножение", "math_division": "Деление",
        "math_compare": "Сравнение", "sudoku": "Судоку",
        "maze": "Лабиринты", "find_differences": "Найди отличия",
        "crossword": "Кроссворды", "color_by_number": "Раскраски по номерам",
        "connect_dots": "Соединить точки", "graphic_dictation": "Графический диктант",
        "coloring": "Раскраски", "story_read": "Чтение текстов",
        "text_question": "Текстовые вопросы", "word_search": "Поиск слов",
    },
    "en": {
        "math_addition": "Addition", "math_subtraction": "Subtraction",
        "math_multiplication": "Multiplication", "math_division": "Division",
        "math_compare": "Comparison", "sudoku": "Sudoku",
        "maze": "Mazes", "find_differences": "Find differences",
        "crossword": "Crosswords", "color_by_number": "Color by number",
        "connect_dots": "Connect dots", "graphic_dictation": "Graphic dictation",
        "coloring": "Coloring", "story_read": "Reading texts",
        "text_question": "Text questions", "word_search": "Word search",
    },
}


def generate_report(pages_data: List[Dict], lang: str = "uk") -> ParentReport:
    total_pages = len(pages_data)
    total_tasks = 0
    type_breakdown: Dict[str, int] = {}
    category_breakdown: Dict[str, int] = {}

    for page in pages_data:
        p_type = page.get("page_type", "")
        task_count = len(page.get("tasks", []))
        total_tasks += task_count
        type_breakdown[p_type] = type_breakdown.get(p_type, 0) + task_count
        cat = CATEGORY_MAP.get(p_type, "other")
        category_breakdown[cat] = category_breakdown.get(cat, 0) + task_count

    report = ParentReport(
        total_pages=total_pages,
        total_tasks=total_tasks,
        type_breakdown=type_breakdown,
        category_breakdown=category_breakdown,
    )

    labels = TYPE_LABELS.get(lang, TYPE_LABELS["uk"])

    max_cat = max(category_breakdown, key=category_breakdown.get) if category_breakdown else ""
    min_cat = min(category_breakdown, key=category_breakdown.get) if category_breakdown else ""

    if max_cat:
        report.strengths.append(labels.get(max_cat, max_cat))
    if min_cat and min_cat != max_cat:
        report.areas_to_work.append(labels.get(min_cat, min_cat))

    if category_breakdown.get("math", 0) == 0:
        report.recommendations.append(("add_math", labels.get("math", "math")))
    if category_breakdown.get("logic", 0) == 0:
        report.recommendations.append(("add_logic", labels.get("logic", "logic")))
    if category_breakdown.get("creative", 0) == 0:
        report.recommendations.append(("add_creative", labels.get("creative", "creative")))
    if category_breakdown.get("reading", 0) == 0:
        report.recommendations.append(("add_reading", labels.get("reading", "reading")))

    if len(category_breakdown) < 3 and total_pages >= 5:
        report.recommendations.append(("diversify", ""))

    return report


def format_report_text(report: ParentReport, lang: str = "uk") -> List[str]:
    labels = TYPE_LABELS.get(lang, TYPE_LABELS["uk"])
    uk = lang in ("uk", "uk+en")
    lines = []

    if uk:
        lines.append(f"Сторінок: {report.total_pages}")
        lines.append(f"Завдань: {report.total_tasks}")
    else:
        lines.append(f"Страниц: {report.total_pages}")
        lines.append(f"Заданий: {report.total_tasks}")

    lines.append("")
    if uk:
        lines.append("Розподіл за категоріями:")
    else:
        lines.append("Распределение по категориям:")
    for cat, count in sorted(report.category_breakdown.items(), key=lambda x: -x[1]):
        label = labels.get(cat, cat)
        pct = int(count / max(report.total_tasks, 1) * 100)
        lines.append(f"  {label}: {count} ({pct}%)")

    if report.strengths:
        lines.append("")
        if uk:
            lines.append(f"Сильні сторони: {', '.join(report.strengths)}")
        else:
            lines.append(f"Сильные стороны: {', '.join(report.strengths)}")

    if report.areas_to_work:
        if uk:
            lines.append(f"Підтягнути: {', '.join(report.areas_to_work)}")
        else:
            lines.append(f"Подтянуть: {', '.join(report.areas_to_work)}")

    if report.recommendations:
        lines.append("")
        if uk:
            lines.append("Рекомендації для наступного пакунку:")
        else:
            lines.append("Рекомендации для следующего пакунка:")
        for rec_id, rec_label in report.recommendations:
            if rec_id == "diversify":
                if uk:
                    lines.append("  - Урізноманітнити типи завдань")
                else:
                    lines.append("  - Разнообразить типы заданий")
            else:
                if uk:
                    lines.append(f"  - Додати більше: {rec_label}")
                else:
                    lines.append(f"  - Добавить больше: {rec_label}")

    return lines
