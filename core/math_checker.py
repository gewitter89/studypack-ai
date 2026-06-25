import re
import logging
from typing import Optional

logger = logging.getLogger(__name__)


def _parse_number(s: str) -> Optional[int]:
    s = s.strip().lower()
    digits = {"ноль": 0, "один": 1, "два": 2, "три": 3, "четыре": 4, "пять": 5,
              "шесть": 6, "семь": 7, "восемь": 8, "девять": 9, "десять": 10}
    try:
        return int(s)
    except ValueError:
        return digits.get(s)


def check_math_answer(question: str, answer: str) -> bool:
    q = question.lower().strip()
    a = answer.strip()

    patterns = [
        (r'(\d+)\s*[\+\+\+]\s*(\d+)', lambda m: int(m.group(1)) + int(m.group(2))),
        (r'(\d+)\s*[\-–—−]\s*(\d+)', lambda m: int(m.group(1)) - int(m.group(2))),
        (r'(\d+)\s*[хx\*×]\s*(\d+)', lambda m: int(m.group(1)) * int(m.group(2))),
        (r'(\d+)\s*[:/÷]\s*(\d+)', lambda m: int(m.group(1)) // int(m.group(2))
         if int(m.group(2)) != 0 and int(m.group(1)) % int(m.group(2)) == 0 else None),
    ]

    for pattern, calc in patterns:
        m = re.search(pattern, q)
        if m:
            try:
                expected = calc(m)
                if expected is None:
                    return False
                given = _parse_number(a)
                if given is not None and given == expected:
                    return True
                else:
                    logger.warning(f"Math mismatch: {q} -> expected {expected}, got '{a}'")
                    return False
            except (ValueError, ZeroDivisionError):
                return False

    return True


def verify_math_in_pack(pack_data: dict) -> list:
    issues = []
    for page in pack_data.get("pages", []):
        for task in page.get("tasks", []):
            if task.get("type") == "math" and task.get("answer"):
                q = task["question"]
                a = task["answer"]
                if not check_math_answer(q, a):
                    issues.append({
                        "page": page.get("page_number", "?"),
                        "question": q,
                        "given_answer": a,
                        "issue": "Ответ не совпадает с вычислением"
                    })
    return issues


def generate_math_examples(count: int, difficulty: str, age: int, topic: str = "",
                            language: str = "uk") -> list:
    import random
    examples = []

    max_val = {4: 5, 5: 10, 6: 20, 7: 30, 8: 50, 9: 100, 10: 100}.get(age, 20)
    if difficulty == "easy":
        max_val = min(max_val, 10)
    elif difficulty == "hard":
        max_val = min(max_val * 2, 200)

    if age <= 5:
        ops = ["+"]
    elif age <= 7:
        ops = ["+", "-"]
    else:
        ops = ["+", "-", "×"]

    # Get topic words from lexicon (not hardcoded)
    topic_items = []
    if topic and topic not in ("general", "custom", ""):
        try:
            from core.topic_lexicon import get_words, get_generic
            simple_lang = language.split("+")[0]
            topic_items = get_words(topic, simple_lang)
            if not topic_items:
                topic_items = get_generic(simple_lang)
        except ImportError:
            pass

    for i in range(count):
        op = random.choice(ops)
        if op == "+":
            b = random.randint(1, max_val)
            a = random.randint(1, max_val)
            question = f"{a} + {b}"
            answer = str(a + b)
        elif op == "-":
            a = random.randint(1, max_val)
            b = random.randint(1, a)
            question = f"{a} - {b}"
            answer = str(a - b)
        elif op == "×":
            a = random.randint(2, min(9, max_val))
            b = random.randint(2, min(9, max_val))
            question = f"{a} × {b}"
            answer = str(a * b)

        full_q = f"{question} = ?"

        examples.append({
            "question": full_q,
            "answer": answer,
            "type": "math",
            "answer_space": True
        })

    return examples
