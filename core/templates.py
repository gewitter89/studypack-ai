import json
import os
import random
import logging
from typing import Dict, Any, Optional

from core.models import PackRequest
from core.math_checker import generate_math_examples
from core.paths import output_dir

logger = logging.getLogger(__name__)

TEMPLATES = {}


def _make_page(num, title, instruction, tasks, page_type="exercise"):
    return {
        "page_number": num,
        "page_type": page_type,
        "title": title,
        "instruction": instruction,
        "tasks": tasks
    }


def _make_task(ttype, question, answer="", opts=None):
    return {
        "type": ttype,
        "question": question,
        "options": opts or [],
        "answer_space": True,
        "answer": answer
    }


def template_preschool(request: PackRequest) -> Dict[str, Any]:
    age = request.age
    topic = request.topic
    lang = request.language
    pages_count = min(request.pages_count, 12)
    ru = lang in ("ru", "ru+en")

    title = "Подготовка к школе" if ru else "Підготовка до школи"
    subtitle = f"Задания для детей {age} лет" if ru else f"Завдання для дітей {age} років"

    pages = []
    answers = []
    page_num = 1

    letters = ["А", "Б", "В", "Г", "Д"] if ru else ["А", "Б", "В", "Г", "Д"]
    letter = random.choice(letters)

    pages.append(_make_page(page_num,
        f"Буква {letter}" if ru else f"Буква {letter}",
        f"Найди букву {letter} среди других" if ru else f"Знайди букву {letter} серед інших",
        [_make_task("writing", f"Обведи букву {letter} по точкам" if ru else f"Обведи букву {letter} по крапках", ""),
         _make_task("writing", f"Напиши букву {letter} три раза" if ru else f"Напиши букву {letter} тричі", "")]))
    answers.append({"page_number": page_num, "answers": ["", ""]})

    page_num += 1
    count_to = min(age + 2, 10)
    math_examples = generate_math_examples(3, "easy", age, topic)
    pages.append(_make_page(page_num,
        "Счёт" if ru else "Лічба",
        f"Посчитай до {count_to}" if ru else f"Порахуй до {count_to}",
        [_make_task("math", e["question"], e["answer"]) for e in math_examples]))
    answers.append({"page_number": page_num, "answers": [e["answer"] for e in math_examples]})

    page_num += 1
    items = ["котик", "собачка", "мячик", "кубик"] if ru else ["котик", "собачка", "м'ячик", "кубик"]
    pages.append(_make_page(page_num,
        "Найди лишнее" if ru else "Знайди зайве",
        "Найди лишний предмет" if ru else "Знайди зайвий предмет",
        [_make_task("logic", f"Что лишнее? {', '.join(items)}", items[-1], items)]))
    answers.append({"page_number": page_num, "answers": [items[-1]]})

    page_num += 1
    pages.append(_make_page(page_num,
        "Проведи линию" if ru else "Проведи лінію",
        "Проведи линию от точки А до точки Б" if ru else "Проведи лінію від точки А до точки Б",
        [_make_task("writing", "Нарисуй линию по пунктиру" if ru else "Намалюй лінію по пунктиру", "")]))
    answers.append({"page_number": page_num, "answers": [""]})

    while len(pages) < pages_count:
        page_num += 1
        pages.append(_make_page(page_num,
            "Повторение" if ru else "Повторення",
            "Повтори то, что выучил" if ru else "Повтори те, що вивчив",
            [_make_task("quiz", f"Сколько будет 1 + 1?", "2"),
             _make_task("quiz", f"Какая буква первая в алфавите?", "А")]))
        answers.append({"page_number": page_num, "answers": ["2", "А"]})

    return {
        "title": title, "subtitle": subtitle, "language": lang,
        "age": age, "grade": request.grade, "topic": topic,
        "pack_type": request.pack_type, "difficulty": "easy",
        "parent_instruction": _parent_instruction(lang),
        "pages": pages, "answers": answers
    }


def template_math(request: PackRequest) -> Dict[str, Any]:
    age = request.age
    lang = request.language
    pages_count = min(request.pages_count, 20)
    ru = lang in ("ru", "ru+en")

    pages = []
    answers = []

    for i in range(pages_count):
        examples = generate_math_examples(3, request.difficulty, age, request.topic)
        pages.append(_make_page(i + 1,
            f"Примеры {i + 1}" if ru else f"Приклади {i + 1}",
            "Реши примеры" if ru else "Розв'яжи приклади",
            [_make_task("math", e["question"], e["answer"]) for e in examples]))
        answers.append({"page_number": i + 1, "answers": [e["answer"] for e in examples]})

    return {
        "title": "Математика" if ru else "Математика",
        "subtitle": f"Примеры для детей {age} лет" if ru else f"Приклади для дітей {age} років",
        "language": lang, "age": age, "grade": request.grade,
        "topic": request.topic, "pack_type": request.pack_type,
        "difficulty": request.difficulty,
        "parent_instruction": _parent_instruction(lang),
        "pages": pages, "answers": answers
    }


def template_logic(request: PackRequest) -> Dict[str, Any]:
    age = request.age
    lang = request.language
    pages_count = min(request.pages_count, 12)
    ru = lang in ("ru", "ru+en")

    pages = []
    answers = []
    puzzles = [
        ("Найди лишнее", "Что лишнее в ряду?", ["яблоко, груша, машина, банан"], "машина"),
        ("Продолжи ряд", "Какое число следующее? 2, 4, 6, ...", [], "8"),
        ("Сравнение", "Что больше: 10 или 5?", ["10", "5"], "10"),
        ("Логика", "У кота 4 лапы. Сколько лап у двух котов?", [], "8"),
    ]

    for i in range(pages_count):
        puzzle = puzzles[i % len(puzzles)]
        pn = i + 1
        pages.append(_make_page(pn, puzzle[0], puzzle[1],
            [_make_task("logic", puzzle[1], puzzle[3], puzzle[2] if puzzle[2] else [])]))
        answers.append({"page_number": pn, "answers": [puzzle[3]]})

    return {
        "title": "Логика и внимание" if ru else "Логіка та увага",
        "subtitle": f"Задания для детей {age} лет" if ru else f"Завдання для дітей {age} років",
        "language": lang, "age": age, "grade": request.grade,
        "topic": request.topic, "pack_type": request.pack_type,
        "difficulty": request.difficulty,
        "parent_instruction": _parent_instruction(lang),
        "pages": pages, "answers": answers
    }


def template_reading(request: PackRequest) -> Dict[str, Any]:
    age = request.age
    lang = request.language
    pages_count = min(request.pages_count, 12)
    ru = lang in ("ru", "ru+en")

    texts = {
        "ru": [
            ("Кот и мышь", "Кот увидел мышь. Мышь убежала в норку. Кот остался голодным.",
             ["Кого увидел кот?", "Куда убежала мышь?"], ["мышь", "в норку"]),
            ("Солнце", "Солнце светит ярко. Дети рады. Они играют во дворе.",
             ["Что светит ярко?", "Где играют дети?"], ["солнце", "во дворе"]),
        ],
        "uk": [
            ("Кіт і миша", "Кіт побачив мишу. Миша втекла в нірку. Кіт залишився голодним.",
             ["Кого побачив кіт?", "Куди втекла миша?"], ["мишу", "в нірку"]),
            ("Сонце", "Сонце світить яскраво. Діти раді. Вони грають у дворі.",
             ["Що світить яскраво?", "Де грають діти?"], ["сонце", "у дворі"]),
        ]
    }

    key = "ru" if ru else "uk"
    pair = texts[key][0]

    pages = []
    answers = []

    for i in range(pages_count):
        pair = texts[key][i % len(texts[key])]
        pn = i + 1
        questions_text = "Ответь на вопросы" if ru else "Дай відповіді на запитання"
        tasks = [_make_task("reading", f"{pair[1]}\n\n{q}", pair[3][j])
                 for j, q in enumerate(pair[2])]
        pages.append(_make_page(pn, pair[0], questions_text, tasks))
        answers.append({"page_number": pn, "answers": pair[3]})

    return {
        "title": "Чтение" if ru else "Читання",
        "subtitle": f"Тексты для детей {age} лет" if ru else f"Тексти для дітей {age} років",
        "language": lang, "age": age, "grade": request.grade,
        "topic": request.topic, "pack_type": request.pack_type,
        "difficulty": request.difficulty,
        "parent_instruction": _parent_instruction(lang),
        "pages": pages, "answers": answers
    }


def template_mixed(request: PackRequest) -> Dict[str, Any]:
    age = request.age
    lang = request.language
    pages_count = min(request.pages_count, 14)
    ru = lang in ("ru", "ru+en")

    days = [
        ("reading", "Чтение" if ru else "Читання"),
        ("math", "Математика" if ru else "Математика"),
        ("logic", "Логика" if ru else "Логіка"),
        ("writing", "Письмо" if ru else "Письмо"),
        ("math", "Математика" if ru else "Математика"),
        ("logic", "Мини-квест" if ru else "Міні-квест"),
        ("quiz", "Повторение" if ru else "Повторення"),
    ]

    pages = []
    answers = []

    for i in range(min(pages_count, len(days))):
        pn = i + 1
        ptype, ptitle = days[i]
        if ptype == "math":
            examples = generate_math_examples(2, request.difficulty, age, request.topic)
            tasks = [_make_task("math", e["question"], e["answer"]) for e in examples]
            ans = [e["answer"] for e in examples]
        elif ptype == "logic":
            tasks = [_make_task("logic", "Найди лишнее: кошка, собака, книга, птица", "книга",
                                ["кошка", "собака", "книга", "птица"])]
            ans = ["книга"]
        elif ptype == "reading":
            tasks = [_make_task("reading", "Прочитай слово 'МАМА'. Сколько в нём букв?", "4")]
            ans = ["4"]
        elif ptype == "writing":
            tasks = [_make_task("writing", "Напиши букву А три раза", "")]
            ans = [""]
        else:
            tasks = [_make_task("quiz", "Сколько будет 2 + 2?", "4")]
            ans = ["4"]

        pages.append(_make_page(pn, ptitle, f"День {i + 1}: {ptitle}", tasks))
        answers.append({"page_number": pn, "answers": ans})

    return {
        "title": "Смешанный набор на неделю" if ru else "Змішаний набір на тиждень",
        "subtitle": f"Задания для детей {age} лет" if ru else f"Завдання для дітей {age} років",
        "language": lang, "age": age, "grade": request.grade,
        "topic": request.topic, "pack_type": request.pack_type,
        "difficulty": request.difficulty,
        "parent_instruction": _parent_instruction(lang),
        "pages": pages, "answers": answers
    }


def _parent_instruction(lang: str) -> str:
    ru = lang in ("ru", "ru+en")
    if ru:
        return ("Занимайтесь 10–20 минут в день. Хвалите ребёнка за старание. "
                "Ответы — только для проверки взрослым.")
    return ("Займайтеся 10–20 хвилин на день. Хваліть дитину за старання. "
            "Відповіді — тільки для перевірки дорослим.")


TEMPLATES = {
    "preschool": template_preschool,
    "math": template_math,
    "logic": template_logic,
    "reading": template_reading,
    "mixed_week": template_mixed,
}


def generate_offline(request: PackRequest) -> Optional[Dict[str, Any]]:
    func = TEMPLATES.get(request.pack_type)
    if func is None:
        logger.warning(f"No template for pack type: {request.pack_type}")
        return None
    logger.info(f"Generating offline template: {request.pack_type}")
    return func(request)
