import argparse
import sys
import os

from core.models import PackRequest
from core.generator import StudyPackGenerator


def setup_argparser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="StudyPack AI - генератор PDF-наборов заданий для детей"
    )
    parser.add_argument("--cli", action="store_true", help="Запуск в режиме CLI")

    parser.add_argument("--age", type=int, choices=range(4, 11), help="Возраст ребёнка (4-10)")
    parser.add_argument("--grade", type=str, help="Класс/уровень: дошкольник, 1 класс, ...")
    parser.add_argument("--language", type=str, choices=["uk", "ru", "en", "uk+en", "ru+en"],
                        help="Язык набора")
    parser.add_argument("--pack", type=str, help="Тип набора: math, reading, logic, mixed_week, ...")
    parser.add_argument("--topic", type=str, help="Тема: dinosaurs, space, animals, ...")
    parser.add_argument("--pages", type=int, choices=[8, 12, 20, 30, 40], default=12,
                        help="Количество страниц")
    parser.add_argument("--difficulty", type=str, choices=["easy", "medium", "hard", "auto"],
                        default="auto", help="Сложность")
    parser.add_argument("--answers", type=str, choices=["yes", "no"], default="yes",
                        help="Добавить ответы")
    parser.add_argument("--instruction", type=str, choices=["yes", "no"], default="yes",
                        help="Добавить инструкцию для родителя")
    parser.add_argument("--style", type=str, choices=["print_bw", "fun", "minimal"],
                        default="print_bw", help="Стиль оформления")
    parser.add_argument("--name", type=str, default="", help="Имя ребёнка (необязательно)")
    parser.add_argument("--output", type=str, default="output", help="Папка сохранения")

    return parser


def run_cli(args: argparse.Namespace):
    if not args.age:
        print("Укажите --age (4-10)")
        sys.exit(1)
    if not args.language:
        print("Укажите --language (uk/ru/en/uk+en/ru+en)")
        sys.exit(1)
    if not args.pack:
        print("Укажите --pack (math/reading/logic/mixed_week/...)")
        sys.exit(1)
    if not args.topic:
        print("Укажите --topic (dinosaurs/space/animals/...)")
        sys.exit(1)

    grade_map = {
        "preschool": "Дошкольник",
        "1": "1 класс",
        "2": "2 класс",
        "3": "3 класс",
        "4": "4 класс",
    }
    grade = grade_map.get(args.grade, args.grade)

    pack_type_map = {
        "preschool": "preschool",
        "math": "math",
        "reading": "reading",
        "ukrainian": "ukrainian",
        "english": "english",
        "logic": "logic",
        "mixed_week": "mixed_week",
    }
    pack_type = pack_type_map.get(args.pack, args.pack)

    request = PackRequest(
        age=args.age,
        grade=grade,
        language=args.language,
        pack_type=pack_type,
        topic=args.topic,
        pages_count=args.pages,
        difficulty=args.difficulty,
        include_answers=args.answers == "yes",
        include_parent_instruction=args.instruction == "yes",
        style=args.style,
        child_name=args.name,
        output_dir=args.output,
    )

    print(f"Генерация набора: возраст {request.age}, тема {request.topic}, тип {request.pack_type}")
    print(f"Язык: {request.language}, страниц: {request.pages_count}")
    print("Запуск генерации...")

    generator = StudyPackGenerator()
    result = generator.generate(request)

    if result.success:
        print(f"\nPDF успешно создан:\n{os.path.abspath(result.pdf_path)}")
        print(f"\nJSON успешно создан:\n{os.path.abspath(result.json_path)}")
    else:
        print(f"\nОшибка: {result.error}")
        if result.warnings:
            print("Предупреждения:")
            for w in result.warnings:
                print(f"  - {w}")
        sys.exit(1)
