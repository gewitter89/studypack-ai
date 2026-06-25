import logging
import re
from typing import Dict, Any, List, Tuple

logger = logging.getLogger(__name__)

BANNED_BRANDS = [
    "minecraft", "roblox", "marvel", "disney", "pokemon",
    "barbie", "lego", "nintendo", "sonic", "hello kitty",
    "star wars", "harry potter", "peppa pig", "paw patrol",
    "frozen", "spider-man", "batman", "superman",
]

MEDICAL_CLAIMS = [
    "дислекси", "аутизм", "аутист",
    "сдвг", "adhd", "задержк", "затримк",
    "логопедическ", "логопедичн", "дефект",
    "диагноз", "діагноз", "лечени", "лікуван",
]

TECHNICAL_WORDS = [
    "json", "prompt", "openrouter", "api key",
    "нейросеть", "нейромережа", "model=",
    "generator", "templates_library",
]

AI_TONE_PHRASES = [
    "это задание поможет", "це завдання допоможе",
    "развивает навыки", "розвиває навички",
    "способствует", "сприяє",
    "стимулирует", "стимулює",
]

_TOPIC_THRESHOLDS: Dict[str, float] = {
    "mixed_week": 0.7,
    "preschool": 0.7,
    "reading": 0.6,
    "logic": 0.6,
    "math": 0.5,
    "english": 0.55,
    "teacher": 0.4,
}


def _get_pack_type(data: Dict[str, Any]) -> str:
    pt = data.get("pack_type", "mixed_week")
    if pt in _TOPIC_THRESHOLDS:
        return pt
    if "english" in pt:
        return "english"
    if "math" in pt:
        return "math"
    return "mixed_week"


def _get_topic_threshold(data: Dict[str, Any]) -> float:
    pack_type = _get_pack_type(data)
    return _TOPIC_THRESHOLDS.get(pack_type, 0.6)


def check_technical_words(data: Dict[str, Any]) -> List[str]:
    issues = []
    text = str(data).lower()
    for word in TECHNICAL_WORDS:
        if word in text:
            issues.append(f"Technical word found: '{word}'")
    return issues


def check_brands(data: Dict[str, Any]) -> List[str]:
    issues = []
    text = str(data).lower()
    for brand in BANNED_BRANDS:
        if brand in text:
            pos = text.index(brand)
            context = text[max(0, pos - 20):pos + len(brand) + 20]
            issues.append(f"Brand '{brand}' found: ...{context}...")
    return issues


def check_medical_claims(data: Dict[str, Any]) -> List[str]:
    issues = []
    text = str(data).lower()
    for claim in MEDICAL_CLAIMS:
        if claim in text:
            issues.append(f"Medical claim found: '{claim}'")
    return issues


def check_ai_tone(data: Dict[str, Any]) -> List[str]:
    issues = []
    text = str(data).lower()
    for phrase in AI_TONE_PHRASES:
        if phrase in text:
            issues.append(f"AI tone phrase: '{phrase}'")
    return issues


def check_structure(data: Dict[str, Any]) -> List[str]:
    issues = []
    if not data.get("title"):
        issues.append("Missing title")
    pages = data.get("pages", [])
    if not pages:
        issues.append("No pages")
    for i, page in enumerate(pages):
        if not page.get("tasks"):
            issues.append(f"Page {i + 1} has no tasks")
        for j, task in enumerate(page.get("tasks", [])):
            if not task.get("question"):
                issues.append(f"Page {i + 1}, task {j + 1} has no question")
    return issues


def check_empty_pages(data: Dict[str, Any]) -> List[str]:
    issues = []
    for i, page in enumerate(data.get("pages", [])):
        tasks = page.get("tasks", [])
        if not tasks:
            issues.append(f"Page {i + 1} is empty")
    return issues


def check_answer_count(data: Dict[str, Any]) -> List[str]:
    issues = []
    total_tasks = sum(len(p.get("tasks", [])) for p in data.get("pages", []))
    total_answers = sum(len(a.get("answers", [])) for a in data.get("answers", []))
    if total_tasks > 0 and total_answers == 0:
        if data.get("include_answers", True):
            issues.append(f"No answers but {total_tasks} tasks exist")
    return issues


def check_repetitive_instructions(data: Dict[str, Any]) -> List[str]:
    issues = []
    seen = {}
    for page in data.get("pages", []):
        inst = page.get("instruction", "")
        if not inst:
            continue
        if inst in seen:
            seen[inst].append(page.get("page_number", "?"))
        else:
            seen[inst] = [page.get("page_number", "?")]
    for inst, pages in seen.items():
        if len(pages) >= 5:
            issues.append(f"HARD FAIL: Same instruction on {len(pages)} pages")
        elif len(pages) >= 3:
            issues.append(f"WARNING: Same instruction on {len(pages)} pages")
    return issues


def check_language_mismatch(data: Dict[str, Any]) -> List[str]:
    issues = []
    lang = data.get("language", "")
    if not lang:
        return ["HARD FAIL: No language specified"]
    if lang in ("ru+en", "uk+en", "en"):
        return issues
    text_lower = str(data).lower()
    ru_words = ["посчитай", "найди", "соедини", "реши", "ответь",
                "нарисуй", "раскрась", "пожалуйста", "какой", "какая"]
    uk_words = ["порахуй", "знайди", "з'єднай", "розв'яжи", "дай відповіді",
                "намалюй", "розфарбуй", "будь ласка", "який", "яка"]
    if lang == "uk":
        for w in ru_words:
            if re.search(r'\b' + re.escape(w) + r'\b', text_lower):
                issues.append(f"HARD FAIL: Russian word '{w}' in Ukrainian PDF")
    elif lang == "ru":
        for w in uk_words:
            if re.search(r'\b' + re.escape(w) + r'\b', text_lower):
                issues.append(f"HARD FAIL: Ukrainian word '{w}' in Russian PDF")
    return issues


def _count_topic_pages(pages, words):
    import re
    matched = 0
    for page in pages:
        page_text = str(page).lower()
        page_words = re.findall(r'\w+', page_text)
        found = False
        for w in words:
            wl = w.lower()
            if wl in page_text:
                found = True
                break
            if len(wl) >= 4:
                for pw in page_words:
                    if len(pw) >= 4 and (pw.startswith(wl) or wl.startswith(pw)):
                        found = True
                        break
                if found:
                    break
        if found:
            matched += 1
    return matched


def check_topic_usage(data: Dict[str, Any]) -> List[str]:
    issues = []
    topic = data.get("topic", "")
    if not topic or topic in ("general", "custom"):
        return issues
    try:
        from core.topic_lexicon import get_words
        lang = data.get("language", "ru")
        words = get_words(topic, lang)
        if not words:
            # For bilingual packs, prefer the component languages in order
            if "+" in lang:
                langs = lang.split("+")
            elif lang == "en":
                langs = ["en", "ru"]
            elif lang == "uk":
                langs = ["uk", "ru", "en"]
            else:
                langs = ["ru", "uk", "en"]
            for check_lang in langs:
                words = get_words(topic, check_lang)
                if words:
                    break
    except ImportError:
        return issues
    if not words:
        return issues

    pages = data.get("pages", [])
    if not pages:
        return issues

    matched_pages = _count_topic_pages(pages, words)
    ratio = matched_pages / len(pages)
    threshold = _get_topic_threshold(data)
    half_threshold = threshold / 2

    if ratio < half_threshold:
        issues.append(f"COMMERCIAL FAIL: Topic '{topic}' on only {matched_pages}/{len(pages)} pages ({ratio:.0%}), need >= {threshold:.0%}")
    elif ratio < threshold:
        issues.append(f"WARNING: Topic '{topic}' on only {matched_pages}/{len(pages)} pages ({ratio:.0%}), target >= {threshold:.0%}")
    return issues


def compute_commercial_score(data: Dict[str, Any]) -> int:
    score = 0
    lang = data.get("language", "ru")
    topic = data.get("topic", "general")

    # 1. Language correct: 25 points
    if lang in ("ru+en", "uk+en", "en"):
        score += 25
    elif lang == "uk" or lang == "ru":
        text_lower = str(data).lower()
        ru_words = ["посчитай", "найди", "соедини", "реши", "ответь",
                    "нарисуй", "раскрась"]
        uk_words = ["порахуй", "знайди", "з'єднай", "розв'яжи",
                    "намалюй", "розфарбуй"]
        has_mismatch = False
        if lang == "uk":
            for w in ru_words:
                if re.search(r'\b' + re.escape(w) + r'\b', text_lower):
                    has_mismatch = True
                    break
        else:
            for w in uk_words:
                if re.search(r'\b' + re.escape(w) + r'\b', text_lower):
                    has_mismatch = True
                    break
        score += 25 if not has_mismatch else 5
    else:
        score += 15

    # 2. Topic presence: 20 points
    try:
        from core.topic_lexicon import get_words
        if topic and topic not in ("general", "custom", ""):
            words = get_words(topic, lang)
            if not words:
                if "+" in lang:
                    langs = lang.split("+")
                elif lang == "en":
                    langs = ["en", "ru"]
                elif lang == "uk":
                    langs = ["uk", "ru", "en"]
                else:
                    langs = ["ru", "uk", "en"]
                for cl in langs:
                    words = get_words(topic, cl)
                    if words:
                        break
            if words:
                pages = data.get("pages", [])
                if pages:
                    matched = _count_topic_pages(pages, words)
                    ratio = matched / len(pages)
                    score += min(20, int(20 * ratio / 0.7))
                else:
                    score += 5
            else:
                score += 10
        else:
            score += 10
    except ImportError:
        score += 10

    # 3. Instruction variety: 15 points
    instructions = [p.get("instruction", "") for p in data.get("pages", [])]
    unique_insts = len(set(instructions))
    total_pages = len(instructions)
    if total_pages > 0:
        variety_ratio = unique_insts / total_pages
        score += min(15, int(15 * variety_ratio / 0.8))
    else:
        score += 5

    # 4. Age appropriateness: 15 points
    age = data.get("age", 7)
    score += 12

    # 5. Answers present: 10 points
    answers = data.get("answers", [])
    pages = data.get("pages", [])
    total_tasks = sum(len(p.get("tasks", [])) for p in pages)
    total_answers = sum(len(a.get("answers", [])) for a in answers)
    if answers and total_answers >= total_tasks:
        score += 10
    elif answers:
        score += 5
    else:
        score += 0

    # 6. No empty/overload: 10 points
    overloaded = False
    empty = False
    for p in pages:
        tasks = p.get("tasks", [])
        if len(tasks) > 7:
            overloaded = True
        if len(tasks) == 0:
            empty = True
    if not overloaded and not empty:
        score += 10
    elif not empty:
        score += 5
    else:
        score += 0

    # 7. Natural text: 5 points
    text = str(data).lower()
    has_ai_phrases = any(phrase in text for phrase in AI_TONE_PHRASES)
    score += 5 if not has_ai_phrases else 1

    return min(100, max(0, score))


def run_quality_gate(data: Dict[str, Any]) -> Tuple[bool, List[str], List[str], List[str], int]:
    hard_fails = []
    warnings = []
    commercial_fails = []

    # HARD FAIL checks
    hard_fails.extend(check_structure(data))
    hard_fails.extend(check_medical_claims(data))
    hard_fails.extend(check_brands(data))
    hard_fails.extend(check_technical_words(data))

    lang_issues = check_language_mismatch(data)
    for li in lang_issues:
        hard_fails.append(li)

    inst_issues = check_repetitive_instructions(data)
    for ii in inst_issues:
        if ii.startswith("HARD FAIL"):
            hard_fails.append(ii)
        else:
            warnings.append(ii)

    hard_fails.extend(check_empty_pages(data))
    hard_fails.extend(check_answer_count(data))

    # WARNING checks
    warnings.extend(check_ai_tone(data))

    topic_issues = check_topic_usage(data)
    for ti in topic_issues:
        if ti.startswith("COMMERCIAL FAIL"):
            commercial_fails.append(ti)
        elif ti.startswith("HARD FAIL"):
            hard_fails.append(ti[10:])
        elif ti.startswith("WARNING"):
            warnings.append(ti[9:])
        else:
            warnings.append(ti)

    # Commercial score
    commercial_score = compute_commercial_score(data)
    if commercial_score < 80:
        commercial_fails.append(f"COMMERCIAL FAIL: score={commercial_score}/100")

    passed = len(hard_fails) == 0

    if hard_fails:
        logger.warning(f"Quality gate HARD FAIL: {hard_fails}")
    if commercial_fails:
        logger.info(f"Quality gate COMMERCIAL: {commercial_fails}")
    if warnings:
        logger.info(f"Quality gate WARNINGS: {warnings}")

    return passed, hard_fails, warnings, commercial_fails, commercial_score


def run_quality_gate_legacy(data: Dict[str, Any]) -> Tuple[bool, List[str], List[str]]:
    passed, errors, warnings, _, _ = run_quality_gate(data)
    return passed, errors, warnings
