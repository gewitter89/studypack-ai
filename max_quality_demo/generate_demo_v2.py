# -*- coding: utf-8 -*-
import sys, io, os, json, logging, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.card_generator import generate_from_preset
from core.preset_loader import find_best_preset, preset_to_request
from core.postprocess import postprocess
from core.paths import output_dir, ensure_dirs
from pdf.renderer import render_pdf

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger("demo")

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "max_quality_demo_v2")
os.makedirs(OUT, exist_ok=True)

SCENARIOS = [
    {"name": "01_preschool_animals_bw", "age": 6, "lang": "uk", "pack_type": "preschool", "topic": "animals", "diff": "easy", "style": "print_bw", "pages": 10},
    {"name": "02_preschool_space_fun", "age": 6, "lang": "uk", "pack_type": "preschool", "topic": "space", "diff": "easy", "style": "fun", "pages": 10},
    {"name": "03_math_dino_fun", "age": 7, "lang": "uk", "pack_type": "mixed_week", "topic": "dinosaurs", "diff": "medium", "style": "fun", "pages": 12},
    {"name": "04_reading_underwater_minimal", "age": 8, "lang": "uk", "pack_type": "reading", "topic": "underwater", "diff": "medium", "style": "minimal", "pages": 10},
    {"name": "05_english_farm_fun", "age": 7, "lang": "uk+en", "pack_type": "english", "topic": "farm", "diff": "easy", "style": "fun", "pages": 10},
    {"name": "06_logic_space_minimal", "age": 6, "lang": "ru", "pack_type": "logic", "topic": "space", "diff": "easy", "style": "minimal", "pages": 10},
    {"name": "07_math_soccer_academic", "age": 8, "lang": "ru", "pack_type": "math", "topic": "football", "diff": "medium", "style": "academic", "pages": 10},
    {"name": "08_preschool_cats_bw", "age": 5, "lang": "uk", "pack_type": "preschool", "topic": "cats", "diff": "easy", "style": "print_bw", "pages": 8},
    {"name": "09_english_travel_minimal", "age": 9, "lang": "uk", "pack_type": "english", "topic": "travel", "diff": "medium", "style": "minimal", "pages": 10},
    {"name": "10_math_pixel_fun", "age": 7, "lang": "uk", "pack_type": "math", "topic": "pixel_world", "diff": "medium", "style": "fun", "pages": 10},
    {"name": "11_logic_robots_fun", "age": 6, "lang": "ru", "pack_type": "logic", "topic": "robots", "diff": "easy", "style": "fun", "pages": 10},
    {"name": "12_custom_reading_academic", "age": 8, "lang": "uk", "pack_type": "reading", "topic": "magic_forest", "diff": "medium", "style": "academic", "pages": 10},
]

def generate_one(scenario):
    name = scenario["name"]
    dir_path = os.path.join(OUT, name)
    os.makedirs(dir_path, exist_ok=True)

    preset = find_best_preset(age=scenario["age"], pack_type=scenario["pack_type"], difficulty=scenario["diff"])
    if not preset:
        print(f"  {name}: NO PRESET")
        return

    pdata = preset_to_request(preset)
    pdata["age"] = scenario["age"]
    pdata["language"] = scenario["lang"]
    pdata["topic"] = scenario["topic"]
    pdata["pages_count"] = scenario["pages"]
    pdata["include_answers"] = True
    pdata["include_parent_instruction"] = True
    pdata["style"] = scenario["style"]

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
        render_pdf(data, pdf_path, watermark="", theme=scenario["style"])
        print(f"  {name}: PDF created ({os.path.getsize(pdf_path)} bytes), quality={'PASS' if quality_passed else 'FAIL'}, errors={quality_errors}, warnings={len(quality_warnings)}")
    except Exception as e:
        print(f"  {name}: PDF FAILED: {e}")
        return

    import fitz
    doc = fitz.open(pdf_path)
    targets = {"page_01_cover": 0, "page_02_task": min(3, len(doc)-3), "page_03_answers": max(0, len(doc)-2)}
    for label, pn in targets.items():
        if pn < len(doc):
            doc[pn].get_pixmap(dpi=150).save(os.path.join(dir_path, f"{label}.png"))
    doc.close()

    return {"name": name, "quality_passed": quality_passed, "quality_errors": quality_errors, "quality_warnings": quality_warnings, "pdf_path": pdf_path}

def inspect_pdf(name, data):
    pages = data.get("pages", [])
    insts = [p.get("instruction","") for p in pages]
    unique_insts = len(set(insts))
    
    topic = data.get("topic", "")
    lang = data.get("language", "ru")
    topic_pages = 0
    if topic and topic not in ("general", "custom"):
        from core.topic_lexicon import get_words
        words = get_words(topic, lang)
        if words:
            for p in pages:
                pt = str(p).lower()
                if any(w.lower() in pt for w in words):
                    topic_pages += 1
    
    ru_in_uk = 0
    if lang == "uk":
        ru_words = ["посчитай", "найди", "соедини", "реши", "ответь", "нарисуй", "раскрась"]
        pt_str = str(pages).lower()
        ru_in_uk = sum(1 for w in ru_words if re.search(r'\b' + re.escape(w) + r'\b', pt_str))

    return {"inst_repetition": len(insts) - unique_insts, "unique_insts": unique_insts, "topic_pages": topic_pages, "total_pages": len(pages), "ru_in_uk": ru_in_uk}

def main():
    print("=" * 60)
    print("StudyPack AI Max V2 — Quality Demo Generator")
    print("=" * 60)

    results = []
    for s in SCENARIOS:
        print(f"\n[{s['name']}]")
        r = generate_one(s)
        if r:
            results.append(r)

    print("\n" + "=" * 60)
    print(f"Generated {len(results)}/{len(SCENARIOS)} PDFs")
    passed = sum(1 for r in results if r["quality_passed"])
    print(f"Quality gate passed: {passed}/{len(results)}")
    
    for r in results:
        jpath = os.path.join(OUT, r["name"], f"{r['name']}.json")
        insp = {}
        if os.path.exists(jpath):
            with open(jpath, "r", encoding="utf-8") as f:
                insp = inspect_pdf(r["name"], json.load(f))
        status = "PASS" if r["quality_passed"] else "FAIL"
        print(f"  {r['name']}: {status} | inst_rep={insp.get('inst_repetition','?')} unique_inst={insp.get('unique_insts','?')} topic_pages={insp.get('topic_pages','?')}/{insp.get('total_pages','?')} ru_in_uk={insp.get('ru_in_uk','?')}")

    summary = [{"name": r["name"], "quality_passed": r["quality_passed"], "quality_errors": r["quality_errors"]} for r in results]
    with open(os.path.join(OUT, "generation_summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
