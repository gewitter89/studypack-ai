import argparse
import json
import sys
import os

from core.models import PackRequest
from core.generator import StudyPackGenerator
from core.math_checker import verify_math_in_pack
from core.templates import generate_offline
from pdf.renderer import render_pdf
from core.paths import output_dir


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
    parser.add_argument("--output", type=str, default="", help="Папка сохранения")
    parser.add_argument("--offline", action="store_true", help="Офлайн-режим (без AI, шаблоны)")
    parser.add_argument("--from-json", type=str, help="Собрать PDF из существующего JSON-файла")
    parser.add_argument("--check-math", type=str, help="Проверить математику в JSON-файле")
    return parser


def run_cli(args: argparse.Namespace):
    if args.from_json:
        _build_from_json(args.from_json, args.output)
        return

    if args.check_math:
        _check_math_file(args.check_math)
        return

    if args.offline:
        if not args.age or not args.pack:
            print("Для офлайн-режима укажите --age и --pack")
            sys.exit(1)
        _run_offline(args)
        return

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

    if args.pages > 20:
        print("[!] Предупреждение: большой набор (>20 стр) может быть нестабильным.")

    grade_map = {
        "preschool": "Дошкольник", "1": "1 класс", "2": "2 класс",
        "3": "3 класс", "4": "4 класс",
    }
    grade = grade_map.get(args.grade, args.grade)

    pack_type_map = {
        "preschool": "preschool", "math": "math", "reading": "reading",
        "ukrainian": "ukrainian", "english": "english", "logic": "logic",
        "mixed_week": "mixed_week",
    }
    pack_type = pack_type_map.get(args.pack, args.pack)

    request = PackRequest(
        age=args.age, grade=grade, language=args.language,
        pack_type=pack_type, topic=args.topic, pages_count=args.pages,
        difficulty=args.difficulty,
        include_answers=args.answers == "yes",
        include_parent_instruction=args.instruction == "yes",
        style=args.style, child_name=args.name,
        output_dir=args.output or output_dir(),
    )

    print(f"Генерация: возраст {request.age}, тема {request.topic}, тип {request.pack_type}")
    print(f"Язык: {request.language}, страниц: {request.pages_count}")
    print("Запуск генерации...")

    generator = StudyPackGenerator()
    result = generator.generate(request)

    if result.success:
        print(f"\nPDF: {os.path.abspath(result.pdf_path)}")
        print(f"JSON: {os.path.abspath(result.json_path)}")
        if result.json_path:
            _check_math_file(result.json_path)
    else:
        print(f"\nОшибка: {result.error}")
        if result.warnings:
            for w in result.warnings:
                print(f"  - {w}")
        sys.exit(1)


def _build_from_json(json_path: str, out_dir: str):
    if not os.path.exists(json_path):
        print(f"Файл не найден: {json_path}")
        sys.exit(1)
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    out = out_dir or output_dir()
    os.makedirs(out, exist_ok=True)

    age = data.get("age", 7)
    topic = data.get("topic", "custom")
    from datetime import datetime
    date_str = datetime.now().strftime("%Y-%m-%d")
    base = f"StudyPack_{age}_{topic}_{date_str}"
    base = "".join(c if c.isalnum() or c in "-_" else "_" for c in base)

    pdf_path = os.path.join(out, f"{base}.pdf")
    render_pdf(data, pdf_path)
    print(f"PDF создан: {os.path.abspath(pdf_path)}")
    _check_math_in_data(data)


def _check_math_file(path: str):
    if not os.path.exists(path):
        print(f"Файл не найден: {path}")
        return
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    _check_math_in_data(data)


def _check_math_in_data(data: dict):
    issues = verify_math_in_pack(data)
    if issues:
        print(f"\n[!] Найдено {len(issues)} проблем в математике:")
        for iss in issues:
            print(f"  Стр.{iss['page']}: {iss['question']} -> '{iss['given_answer']}'")
    else:
        print("[OK] Математика проверена, ошибок нет.")


def _run_offline(args: argparse.Namespace):
    request = PackRequest(
        age=args.age,
        grade=args.grade or "Дошкольник",
        language=args.language or "ru",
        pack_type=args.pack,
        topic=args.topic or "general",
        pages_count=args.pages,
        difficulty=args.difficulty,
        include_answers=args.answers == "yes",
        include_parent_instruction=args.instruction == "yes",
        style=args.style,
        child_name=args.name,
        output_dir=args.output or output_dir(),
    )
    print(f"Офлайн-режим: шаблон {args.pack} для возраста {args.age}")
    data = generate_offline(request)
    if data is None:
        print(f"Нет шаблона для типа: {args.pack}")
        sys.exit(1)

    out = args.output or output_dir()
    os.makedirs(out, exist_ok=True)
    from datetime import datetime
    date_str = datetime.now().strftime("%Y-%m-%d")
    base = f"StudyPack_{args.age}_{args.topic or 'general'}_{date_str}"
    base = "".join(c if c.isalnum() or c in "-_" else "_" for c in base)

    json_path = os.path.join(out, f"{base}.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"JSON: {os.path.abspath(json_path)}")

    pdf_path = os.path.join(out, f"{base}.pdf")
    render_pdf(data, pdf_path)
    print(f"PDF: {os.path.abspath(pdf_path)}")
