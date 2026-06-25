import os, sys, json, logging
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.card_generator import generate_from_preset
from core.preset_loader import find_best_preset, preset_to_request, list_presets
from core.postprocess import postprocess
from core.paths import output_dir, ensure_dirs
from pdf.renderer import render_pdf

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger("demo")

OUT = os.path.dirname(os.path.abspath(__file__))
ensure_dirs()

SCENARIOS = [
    {"name": "01_preschool_animals_bw", "age": 6, "lang": "uk", "pack_type": "preschool", "topic": "animals", "diff": "easy", "style": "print_bw", "pages": 10},
    {"name": "02_preschool_space_fun", "age": 6, "lang": "uk", "pack_type": "preschool", "topic": "space", "diff": "easy", "style": "fun", "pages": 10},
    {"name": "03_math_dino_fun", "age": 7, "lang": "uk", "pack_type": "mixed_week", "topic": "dinosaurs", "diff": "medium", "style": "fun", "pages": 12},
    {"name": "04_reading_underwater_minimal", "age": 8, "lang": "uk", "pack_type": "reading", "topic": "underwater", "diff": "medium", "style": "minimal", "pages": 10},
    {"name": "05_english_farm_fun", "age": 7, "lang": "uk+en", "pack_type": "english", "topic": "farm", "diff": "easy", "style": "fun", "pages": 10},
    {"name": "06_logic_space_minimal", "age": 6, "lang": "ru", "pack_type": "logic", "topic": "space", "diff": "easy", "style": "minimal", "pages": 10},
    {"name": "07_math_soccer_academic", "age": 8, "lang": "ru", "pack_type": "math", "topic": "soccer", "diff": "medium", "style": "academic", "pages": 10},
    {"name": "08_preschool_cats_bw", "age": 5, "lang": "uk", "pack_type": "preschool", "topic": "cats", "diff": "easy", "style": "print_bw", "pages": 8},
    {"name": "09_english_travel_minimal", "age": 9, "lang": "uk", "pack_type": "english", "topic": "travel", "diff": "medium", "style": "minimal", "pages": 10},
    {"name": "10_math_pixel_fun", "age": 7, "lang": "uk", "pack_type": "math", "topic": "pixel_world", "diff": "medium", "style": "fun", "pages": 10},
    {"name": "11_logic_robots_fun", "age": 6, "lang": "ru", "pack_type": "logic", "topic": "robots", "diff": "easy", "style": "fun", "pages": 10},
]

def generate_one(scenario):
    name = scenario["name"]
    age = scenario["age"]
    lang = scenario["lang"]
    pack_type = scenario["pack_type"]
    topic = scenario["topic"]
    diff = scenario["diff"]
    style = scenario["style"]
    pages = scenario["pages"]

    dir_path = os.path.join(OUT, name)
    os.makedirs(dir_path, exist_ok=True)

    preset = find_best_preset(age=age, pack_type=pack_type, difficulty=diff)
    if not preset:
        print(f"  {name}: NO PRESET FOUND, skipping")
        return

    pdata = preset_to_request(preset)
    pdata["age"] = age
    pdata["language"] = lang
    pdata["topic"] = topic
    pdata["pages_count"] = pages
    pdata["include_answers"] = True
    pdata["include_parent_instruction"] = True
    pdata["style"] = style

    data = generate_from_preset(pdata)
    data = postprocess(data)

    qc = data.get("_quality", {})
    quality_passed = qc.get("passed", False)
    quality_errors = qc.get("errors", [])
    quality_warnings = qc.get("warnings", [])

    json_path = os.path.join(dir_path, f"{name}.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    quality_report_path = os.path.join(dir_path, "quality_report.json")
    with open(quality_report_path, "w", encoding="utf-8") as f:
        json.dump({"passed": quality_passed, "errors": quality_errors, "warnings": quality_warnings}, f, ensure_ascii=False, indent=2)

    pdf_path = os.path.join(dir_path, f"{name}.pdf")
    try:
        render_pdf(data, pdf_path, watermark="", theme=style)
        print(f"  {name}: PDF created ({os.path.getsize(pdf_path)} bytes), quality={'PASS' if quality_passed else 'FAIL'}")
    except Exception as e:
        print(f"  {name}: PDF FAILED: {e}")
        return

    return {
        "name": name,
        "age": age, "lang": lang, "type": pack_type,
        "topic": topic, "diff": diff, "style": style,
        "pages": len(data.get("pages", [])),
        "quality_passed": quality_passed,
        "quality_errors": quality_errors,
        "quality_warnings": quality_warnings,
        "pdf_path": pdf_path,
        "json_path": json_path,
        "data": data,
    }

def screenshot_pdf(pdf_path, dir_path, name):
    try:
        import fitz
        doc = fitz.open(pdf_path)
        targets = {
            "page_01_cover": 0,
            "page_02_task": min(3, len(doc) - 3),
            "page_03_answers": max(0, len(doc) - 2),
        }
        for label, pageno in targets.items():
            if pageno < len(doc):
                page = doc[pageno]
                pix = page.get_pixmap(dpi=150)
                img_path = os.path.join(dir_path, f"{label}.png")
                pix.save(img_path)
        doc.close()
        return True
    except Exception as e:
        print(f"  {name}: screenshot failed: {e}")
        return False

def main():
    print("=" * 60)
    print("StudyPack AI Max — Quality Demo Generator")
    print("=" * 60)
    print(f"\nGenerating {len(SCENARIOS)} scenarios...\n")

    results = []
    for s in SCENARIOS:
        print(f"[{s['name']}]")
        r = generate_one(s)
        if r and os.path.exists(r["pdf_path"]):
            screenshot_pdf(r["pdf_path"], os.path.join(OUT, r["name"]), r["name"])
            results.append(r)
        print()

    print("=" * 60)
    print(f"Generated {len(results)}/{len(SCENARIOS)} PDFs")
    passed = sum(1 for r in results if r["quality_passed"])
    print(f"Quality gate passed: {passed}/{len(results)}")
    for r in results:
        status = "PASS" if r["quality_passed"] else "FAIL"
        errs = r["quality_errors"]
        warns = r["quality_warnings"]
        print(f"  {r['name']}: {status} (errors={errs}, warnings={len(warns)})")

    summary_path = os.path.join(OUT, "generation_summary.json")
    summary = [{
        "name": r["name"], "age": r["age"], "lang": r["lang"],
        "type": r["type"], "topic": r["topic"], "diff": r["diff"],
        "style": r["style"], "pages": r["pages"],
        "quality_passed": r["quality_passed"],
        "quality_errors": r["quality_errors"],
        "quality_warnings_count": len(r["quality_warnings"]),
    } for r in results]
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    print(f"\nSummary saved to {summary_path}")

if __name__ == "__main__":
    main()
