import os
import sys
import json
import fitz

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.models import PackRequest
from core.templates import generate_offline
from pdf.renderer import render_pdf
from core.quality_gate import run_quality_gate

def main():
    demo_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "commercial_fix_demo")
    os.makedirs(demo_dir, exist_ok=True)
    print(f"Created demo directory: {demo_dir}")

    configs = [
        {
            "id": 1,
            "lang": "uk",
            "age": 6,
            "pack_type": "preschool",
            "topic": "fairy_tales",
            "style": "fun",
            "pages_count": 8,
            "name": "preschool_fairy_tales"
        },
        {
            "id": 2,
            "lang": "uk",
            "age": 7,
            "pack_type": "mixed_week",
            "topic": "dinosaurs",
            "style": "fun",
            "pages_count": 8,
            "name": "math_logic_dinosaurs"
        },
        {
            "id": 3,
            "lang": "uk",
            "age": 6,
            "pack_type": "preschool",
            "topic": "animals",
            "style": "print_bw",
            "pages_count": 8,
            "name": "preschool_animals"
        },
        {
            "id": 4,
            "lang": "ru",
            "age": 6,
            "pack_type": "logic",
            "topic": "space",
            "style": "minimal",
            "pages_count": 8,
            "name": "logic_space"
        },
        {
            "id": 5,
            "lang": "uk",
            "age": 8,
            "pack_type": "reading",
            "topic": "underwater",
            "style": "minimal",
            "pages_count": 8,
            "name": "reading_underwater"
        }
    ]

    for cfg in configs:
        print(f"\n--- Generating Demo {cfg['id']}: {cfg['name']} ---")
        req = PackRequest(
            age=cfg["age"],
            grade="Дошкольник" if cfg["age"] <= 6 else "1 класс",
            language=cfg["lang"],
            pack_type=cfg["pack_type"],
            topic=cfg["topic"],
            pages_count=cfg["pages_count"],
            difficulty="easy",
            include_answers=True,
            include_parent_instruction=True,
            style=cfg["style"],
            child_name="Данило" if cfg["lang"] == "uk" else "Даня",
            output_dir=demo_dir
        )

        # Generate data
        data = generate_offline(req)
        if not data:
            print(f"Error: Failed to generate template data for Demo {cfg['id']}")
            continue

        base_name = f"demo_0{cfg['id']}_{cfg['name']}"
        pdf_path = os.path.join(demo_dir, f"{base_name}.pdf")
        json_path = os.path.join(demo_dir, f"{base_name}.json")
        report_path = os.path.join(demo_dir, f"{base_name}_quality_report.json")

        # Save JSON
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"Saved JSON to {json_path}")

        # Quality Gate
        passed, hard_fails, warnings, comm_fails, score = run_quality_gate(data)
        report = {
            "passed": passed,
            "hard_fails": hard_fails,
            "warnings": warnings,
            "commercial_fails": comm_fails,
            "commercial_score": score
        }
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        print(f"Saved Quality Report (Score: {score}) to {report_path}")

        # Render PDF (is_commercial=False with watermark="Демо-версія" to show the small footer)
        render_pdf(
            data,
            pdf_path,
            watermark="Демо-версія",
            is_commercial=False,
            brand="StudyPack AI"
        )
        print(f"Saved PDF to {pdf_path}")

        # Render PDF pages to PNG using PyMuPDF
        try:
            doc = fitz.open(pdf_path)
            
            # Cover page (1st)
            p1 = doc[0]
            pix1 = p1.get_pixmap(dpi=150)
            cover_img = os.path.join(demo_dir, f"{base_name}_cover.png")
            pix1.save(cover_img)
            print(f"Saved Cover Page Image to {cover_img}")

            # Task page (2nd page, first exercise)
            p2 = doc[1]
            pix2 = p2.get_pixmap(dpi=150)
            task_img = os.path.join(demo_dir, f"{base_name}_task_page.png")
            pix2.save(task_img)
            print(f"Saved Task Page Image to {task_img}")

            # Answers page (last page)
            p_last = doc[-1]
            pix_last = p_last.get_pixmap(dpi=150)
            answers_img = os.path.join(demo_dir, f"{base_name}_answers_page.png")
            pix_last.save(answers_img)
            print(f"Saved Answers Page Image to {answers_img}")
            
            doc.close()
        except Exception as e:
            print(f"Failed to generate PNGs: {e}")

if __name__ == "__main__":
    main()
