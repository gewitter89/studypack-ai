#!/usr/bin/env python3
"""Demo: generate 3 sample packs using mock AI data (no API key required)."""

import os
import sys
import json
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.models import PackRequest
from core.generator import StudyPackGenerator
from pdf.renderer import render_pdf


SAMPLE_JSON = {
    "title": "Динозаврова пригода",
    "subtitle": "Завдання для дитини 7 років",
    "language": "uk",
    "age": 7,
    "grade": "1 класс",
    "topic": "dinosaurs",
    "pack_type": "mixed_week",
    "difficulty": "easy",
    "parent_instruction": (
        "Занимайтесь 10–20 минут в день. Хвалите ребёнка за старание. "
        "Ответы в конце набора — только для проверки взрослым."
    ),
    "pages": [
        {
            "page_number": 1,
            "page_type": "exercise",
            "title": "Порахуй динозаврів",
            "instruction": "Розв'яжи приклади та допоможи динозаврам знайти яйця.",
            "tasks": [
                {"type": "math", "question": "У гнізді було 5 яєць, динозавр приніс ще 3. Скільки яєць стало?", "answer_space": True, "answer": "8"},
                {"type": "math", "question": "Тиранозавр з'їв 4 листочки, а трицератопс з'їв 6. Скільки всього листочків вони з'їли?", "answer_space": True, "answer": "10"}
            ]
        },
        {
            "page_number": 2,
            "page_type": "exercise",
            "title": "Знайди тінь",
            "instruction": "З'єднай кожного динозавра з його тінню.",
            "tasks": [
                {"type": "logic", "question": "Подивись на малюнки динозаврів. Знайди для кожного його тінь.", "options": ["Тиранозавр", "Трицератопс", "Стегозавр", "Птеродактиль"], "answer_space": True, "answer": "1-А, 2-Б, 3-В, 4-Г"}
            ]
        },
        {
            "page_number": 3,
            "page_type": "exercise",
            "title": "Прочитай та обери",
            "instruction": "Прочитай слово та обери правильний малюнок.",
            "tasks": [
                {"type": "reading", "question": "Яка буква перша в слові ДИНОЗАВР?", "options": ["А", "Д", "Р", "Н"], "answer_space": True, "answer": "Д"}
            ]
        },
        {
            "page_number": 4,
            "page_type": "exercise",
            "title": "Лабіринт",
            "instruction": "Допоможи маленькому динозаврику дістатися до мами.",
            "tasks": [
                {"type": "logic", "question": "Проведи лінію через лабіринт від старту до фінішу.", "answer_space": True, "answer": ""}
            ]
        },
        {
            "page_number": 5,
            "page_type": "exercise",
            "title": "Англійські динозаври",
            "instruction": "Вивчи назви динозаврів англійською.",
            "tasks": [
                {"type": "english", "question": "Як буде 'динозавр' англійською?", "options": ["Dog", "Dinosaur", "Cat", "Bird"], "answer_space": True, "answer": "Dinosaur"},
                {"type": "english", "question": "Як буде 'яйце' англійською?", "options": ["Egg", "Apple", "Tree", "Stone"], "answer_space": True, "answer": "Egg"}
            ]
        },
        {
            "page_number": 6,
            "page_type": "exercise",
            "title": "Розфарбуй динозавра",
            "instruction": "Розфарбуй малюнок динозавра.",
            "tasks": [
                {"type": "creative", "question": "Розфарбуй динозавра в зелений колір. Намалюй йому плямки.", "answer_space": True, "answer": ""}
            ]
        },
        {
            "page_number": 7,
            "page_type": "exercise",
            "title": "Знайди зайве",
            "instruction": "Знайди зайвий предмет у кожному рядку.",
            "tasks": [
                {"type": "logic", "question": "Що зайве: тиранозавр, трицератопс, кішка, стегозавр?", "options": ["Тиранозавр", "Трицератопс", "Кішка", "Стегозавр"], "answer_space": True, "answer": "Кішка"},
                {"type": "logic", "question": "Що зайве: яйце, гніздо, дерево, літак?", "options": ["Яйце", "Гніздо", "Дерево", "Літак"], "answer_space": True, "answer": "Літак"}
            ]
        },
        {
            "page_number": 8,
            "page_type": "exercise",
            "title": "Повторення",
            "instruction": "Повтори те, що вивчив.",
            "tasks": [
                {"type": "quiz", "question": "Скільки ніг у динозавра?", "options": ["2", "4", "6", "8"], "answer_space": True, "answer": "4"},
                {"type": "quiz", "question": "Хто з динозаврів літав?", "options": ["Тиранозавр", "Птеродактиль", "Стегозавр", "Трицератопс"], "answer_space": True, "answer": "Птеродактиль"}
            ]
        }
    ],
    "answers": [
        {"page_number": 1, "answers": ["8", "10"]},
        {"page_number": 2, "answers": ["1-А, 2-Б, 3-В, 4-Г"]},
        {"page_number": 3, "answers": ["Д"]},
        {"page_number": 4, "answers": [""]},
        {"page_number": 5, "answers": ["Dinosaur", "Egg"]},
        {"page_number": 6, "answers": [""]},
        {"page_number": 7, "answers": ["Кішка", "Літак"]},
        {"page_number": 8, "answers": ["4", "Птеродактиль"]}
    ]
}


def main():
    print("StudyPack AI - Demo Generation\n")

    output_dir = os.path.join(os.path.dirname(__file__), "output")
    os.makedirs(output_dir, exist_ok=True)

    demos = [
        ("7_uk_dinosaurs.pdf", SAMPLE_JSON),
    ]

    for fname, data in demos:
        path = os.path.join(output_dir, fname)
        print(f"Generating: {fname}...")
        render_pdf(data, path)
        print(f"  Created: {path} ({os.path.getsize(path)} bytes)")

    json_path = os.path.join(output_dir, "demo_dinosaurs.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(SAMPLE_JSON, f, ensure_ascii=False, indent=2)
    print(f"  JSON: {json_path}")

    print("\nDemo complete! Check the output/ folder.")


if __name__ == "__main__":
    main()
