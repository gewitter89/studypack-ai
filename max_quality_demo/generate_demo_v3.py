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
logger = logging.getLogger("demo_v3")

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "max_quality_demo_v3")
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
    commercial_score = qc.get("commercial_score", 0)
    hard_fails = qc.get("hard_fails", [])
    commercial_fails = qc.get("commercial_fails", [])

    json_path = os.path.join(dir_path, f"{name}.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    quality_report_path = os.path.join(dir_path, "quality_report.json")
    with open(quality_report_path, "w", encoding="utf-8") as f:
        json.dump({
            "passed": quality_passed,
            "errors": quality_errors,
            "warnings": quality_warnings,
            "commercial_score": commercial_score,
            "hard_fails": hard_fails,
            "commercial_fails": commercial_fails,
        }, f, ensure_ascii=False, indent=2)

    pdf_path = os.path.join(dir_path, f"{name}.pdf")
    try:
        render_pdf(data, pdf_path, watermark="", theme=scenario["style"])
        print(f"  {name}: PDF created ({os.path.getsize(pdf_path)} bytes), score={commercial_score}, passed={quality_passed}, errors={len(quality_errors)}")
    except Exception as e:
        print(f"  {name}: PDF FAILED: {e}")
        return

    try:
        import fitz
        doc = fitz.open(pdf_path)
        targets = {"page_01_cover": 0, "page_02_task": min(3, len(doc)-3), "page_03_answers": max(0, len(doc)-2)}
        for label, pn in targets.items():
            if pn < len(doc):
                doc[pn].get_pixmap(dpi=150).save(os.path.join(dir_path, f"{label}.png"))
        doc.close()
    except ImportError:
        print(f"  {name}: fitz not available, skipping screenshots")

    return {
        "name": name,
        "quality_passed": quality_passed,
        "quality_errors": quality_errors,
        "quality_warnings": quality_warnings,
        "commercial_score": commercial_score,
        "hard_fails": hard_fails,
        "commercial_fails": commercial_fails,
        "pdf_path": pdf_path,
    }

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
        if not words:
            for cl in ["ru", "uk", "en"]:
                words = get_words(topic, cl)
                if words:
                    break
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

    inst_rep = len(insts) - unique_insts
    return {"inst_repetition": inst_rep, "unique_insts": unique_insts, "topic_pages": topic_pages, "total_pages": len(pages), "ru_in_uk": ru_in_uk}


def make_short_review(name, data, qc):
    pages = data.get("pages", [])
    topic = data.get("topic", "general")
    lang = data.get("language", "ru")

    strengths = []
    weaknesses = []

    insts = [p.get("instruction","") for p in pages]
    unique_insts = len(set(insts))
    if unique_insts >= len(insts) * 0.7:
        strengths.append("good instruction variety")
    elif unique_insts < len(insts) * 0.5:
        weaknesses.append("low instruction variety")

    topic_words_ok = True
    try:
        from core.topic_lexicon import get_words
        words = get_words(topic, lang)
        if not words:
            for cl in ["ru", "uk", "en"]:
                words = get_words(topic, cl)
                if words:
                    break
        if words:
            topic_pages = sum(1 for p in pages if any(w.lower() in str(p).lower() for w in words))
            ratio = topic_pages / len(pages) if pages else 0
            if ratio >= 0.5:
                strengths.append(f"topic '{topic}' on {topic_pages}/{len(pages)} pages")
            else:
                weaknesses.append(f"topic '{topic}' only on {topic_pages}/{len(pages)} pages")
    except:
        pass

    if not qc.get("hard_fails"):
        strengths.append("no hard fails")
    if qc.get("commercial_score", 0) >= 80:
        strengths.append(f"commercial ready ({qc.get('commercial_score')}/100)")

    review = f"=== {name} ===\n"
    review += f"score: {qc.get('commercial_score')}/100 | passed: {qc.get('passed')}\n"
    review += f"strengths: {', '.join(strengths) if strengths else 'none'}\n"
    review += f"weaknesses: {', '.join(weaknesses) if weaknesses else 'none'}\n"
    if qc.get("errors"):
        review += f"errors: {qc['errors'][:3]}\n"
    return review


def main():
    print("=" * 60)
    print("StudyPack AI Max V3 — Content Relevance Demo")
    print("=" * 60)
    print()

    results = []
    for s in SCENARIOS:
        print(f"[{s['name']}]")
        r = generate_one(s)
        if r:
            results.append(r)
        print()

    print("=" * 60)
    print(f"Generated {len(results)}/{len(SCENARIOS)} PDFs")

    hard_fail_count = sum(1 for r in results if r["hard_fails"])
    comm_fail_count = sum(1 for r in results if r["commercial_fails"])
    passed_count = sum(1 for r in results if r["quality_passed"])
    avg_score = sum(r["commercial_score"] for r in results) / len(results) if results else 0

    print(f"Hard fails: {hard_fail_count}")
    print(f"Quality gate passed: {passed_count}/{len(results)}")
    print(f"Commercial ready (score>=80): {sum(1 for r in results if r['commercial_score'] >= 80)}/{len(results)}")
    print(f"Average commercial score: {avg_score:.0f}")
    print()

    ru_in_uk_total = 0
    topic_ok_total = 0
    lang_ok_total = 0

    for r in results:
        jpath = os.path.join(OUT, r["name"], f"{r['name']}.json")
        insp = {}
        if os.path.exists(jpath):
            with open(jpath, "r", encoding="utf-8") as f:
                insp = inspect_pdf(r["name"], json.load(f))

        status = "PASS" if r["quality_passed"] else "FAIL"
        score_str = f"score={r['commercial_score']}" if r["commercial_score"] else "score=?"
        fails = []
        if r["hard_fails"]:
            fails.append(f"hard={len(r['hard_fails'])}")
        if r["commercial_fails"]:
            fails.append(f"comm={len(r['commercial_fails'])}")
        fail_str = f" [{','.join(fails)}]" if fails else ""

        riu = insp.get("ru_in_uk", "?")
        tp = f"{insp.get('topic_pages','?')}/{insp.get('total_pages','?')}"
        print(f"  {r['name']}: {status} | {score_str}{fail_str} | topic={tp} ru_in_uk={riu}")

        if riu == 0:
            lang_ok_total += 1
        if isinstance(tp, str) and "/" in tp:
            tpn, tpt = tp.split("/")
            topic_ok_total += 1 if int(tpn) > 0 else 0

    print()
    print(f"Language mismatch = 0: {lang_ok_total}/{len(results)}")
    print(f"Has topic words: {topic_ok_total}/{len(results)}")

    # Sales pack candidates
    sales_candidates = sorted(
        [r for r in results if r["quality_passed"] and r["commercial_score"] >= 80],
        key=lambda r: r["commercial_score"],
        reverse=True
    )
    print(f"\nTop sales candidates: {len(sales_candidates)}")
    for r in sales_candidates[:5]:
        print(f"  {r['name']}: score={r['commercial_score']}")

    if results:
        weak = sorted(results, key=lambda r: r["commercial_score"])[:3]
        print(f"\nNeeds manual fix:")
        for r in weak:
            print(f"  {r['name']}: score={r['commercial_score']} errors={r['quality_errors'][:2]}")

    # Save summary
    summary = []
    for r in results:
        summary.append({
            "name": r["name"],
            "quality_passed": r["quality_passed"],
            "commercial_score": r["commercial_score"],
            "hard_fails": r["hard_fails"],
            "commercial_fails": r["commercial_fails"],
        })
    summary.append({
        "_meta": {
            "total": len(results),
            "hard_fail": hard_fail_count,
            "commerce_fail": comm_fail_count,
            "quality_pass": passed_count,
            "average_score": round(avg_score, 0),
            "commercial_ready": sum(1 for r in results if r["commercial_score"] >= 80),
            "language_ok": lang_ok_total,
        }
    })
    with open(os.path.join(OUT, "generation_summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    print(f"\nSummary saved to {os.path.join(OUT, 'generation_summary.json')}")

if __name__ == "__main__":
    main()
