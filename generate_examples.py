#!/usr/bin/env python3
"""Generate 3 demo PDFs for the examples/ folder using offline templates."""

import os
import sys
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.models import PackRequest
from core.templates import generate_offline
from pdf.renderer import render_pdf
from core.paths import output_dir

EXAMPLES_DIR = os.path.join(os.path.dirname(__file__), "examples")


def make_example(name, request_data):
    print(f"Generating: {name}...")
    req = PackRequest(**request_data)
    data = generate_offline(req)
    if data is None:
        print(f"  FAILED: no template for {req.pack_type}")
        return

    json_path = os.path.join(EXAMPLES_DIR, f"{name}.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    pdf_path = os.path.join(EXAMPLES_DIR, f"{name}.pdf")
    render_pdf(data, pdf_path)
    size = os.path.getsize(pdf_path)
    print(f"  PDF: {pdf_path} ({size} bytes)")
    print(f"  JSON: {json_path}")


def main():
    os.makedirs(EXAMPLES_DIR, exist_ok=True)

    examples = [
        {
            "name": "7_uk_dinosaurs_mixed",
            "request": {
                "age": 7,
                "grade": "1 класс",
                "language": "uk",
                "pack_type": "mixed_week",
                "topic": "dinosaurs",
                "pages_count": 8,
                "difficulty": "easy",
                "include_answers": True,
                "include_parent_instruction": True,
                "style": "print_bw",
                "output_dir": EXAMPLES_DIR,
            }
        },
        {
            "name": "6_ru_space_logic",
            "request": {
                "age": 6,
                "grade": "Дошкольник",
                "language": "ru",
                "pack_type": "logic",
                "topic": "space",
                "pages_count": 8,
                "difficulty": "easy",
                "include_answers": True,
                "include_parent_instruction": True,
                "style": "print_bw",
                "output_dir": EXAMPLES_DIR,
            }
        },
        {
            "name": "8_uk_animals_math",
            "request": {
                "age": 8,
                "grade": "2 класс",
                "language": "uk",
                "pack_type": "math",
                "topic": "animals",
                "pages_count": 12,
                "difficulty": "medium",
                "include_answers": True,
                "include_parent_instruction": True,
                "style": "print_bw",
                "output_dir": EXAMPLES_DIR,
            }
        },
    ]

    for ex in examples:
        make_example(ex["name"], ex["request"])

    print(f"\nAll examples in: {EXAMPLES_DIR}")


if __name__ == "__main__":
    main()
