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


def generate_math_examples(count: int, difficulty: str, age: int, topic: str = "") -> list:
    import random
    examples = []

    max_val = {4: 5, 5: 10, 6: 20, 7: 30, 8: 50, 9: 100, 10: 100}.get(age, 20)
    if difficulty == "easy":
        max_val = min(max_val, 10)
    elif difficulty == "hard":
        max_val = min(max_val * 2, 200)

    ops_descriptions = []

    if age <= 5:
        ops = [("+", "сложение")]
    elif age <= 7:
        ops = [("+", "сложение"), ("-", "вычитание")]
    else:
        ops = [("+", "сложение"), ("-", "вычитание"), ("×", "умножение")]

    for i in range(count):
        op, op_name = random.choice(ops)
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
        if topic:
            theme_items = ["яблок", "конфет", "звёзд", "машинок", "динозавров",
                           "мячей", "книг", "карандашей", "кубиков", "монет"]
            item = random.choice(theme_items)
            full_q = f"Было {a} {item}, {op_name} {b}. Сколько стало? {question} = ?"

        examples.append({
            "question": full_q,
            "answer": answer,
            "type": "math",
            "answer_space": True
        })

    return examples
