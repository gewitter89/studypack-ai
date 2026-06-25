import re
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

TEMPLATE_PHRASES = [
    "это задание поможет развить", "ето задание поможет развить",
    "в рамках данного упражнения", "учащийся должен",
    "когнитивные навыки", "данный материал", "данный матеріал",
    "сгенерировано", "згенеровано", "нейросеть", "нейромережа",
    "openai", "ИИ", "ШІ", "prompt", "openrouter",
    "данное упражнение", "направлено на развитие",
    "данное задание способствует",
    "мета даного завдання", "мета данного задания",
]

LIVING_INSTRUCTIONS_RU = {
    "Выполни задание": "Подумай и запиши ответ",
    "Соедини элементы": "Соедини стрелочкой",
    "Ответь на вопросы": "Прочитай и ответь",
    "Реши примеры": "Посчитай и запиши",
    "Напиши": "Запиши красиво",
    "Вставь пропущенные буквы": "Какая буква спряталась?",
    "Прочитай текст": "Читай внимательно",
    "Сделай": "Попробуй сделать",
}

LIVING_INSTRUCTIONS_UK = {
    "Виконай завдання": "Подумай і запиши відповідь",
    "З'єднай елементи": "З'єднай стрілочкою",
    "Дай відповіді на питання": "Прочитай і дай відповідь",
    "Розв'яжи приклади": "Порахуй і запиши",
    "Напиши": "Запиши гарно",
    "Встав пропущені букви": "Яка буква сховалася?",
    "Прочитай текст": "Читай уважно",
    "Зроби": "Спробуй зробити",
}

AGE_INSTRUCTION_MAX_LENGTH = {
    4: 20, 5: 30, 6: 50, 7: 70, 8: 90, 9: 110, 10: 130,
}

REPETITIVE_BEGINNINGS = [
    "Прочитай", "Реши", "Напиши", "Знайди", "Порахуй",
    "Розв'яжи", "Запиши", "Накресли", "Подумай",
]


def remove_template_phrases(text: str) -> str:
    for phrase in TEMPLATE_PHRASES:
        pattern = re.compile(re.escape(phrase), re.IGNORECASE)
        text = pattern.sub("", text)
    return text


def humanize_instructions(text: str, language: str = "ru") -> str:
    mapping = LIVING_INSTRUCTIONS_UK if language.startswith("uk") else LIVING_INSTRUCTIONS_RU
    for formal, living in mapping.items():
        text = text.replace(formal, living)
    return text


def shorten_for_age(text: str, age: int) -> str:
    max_len = AGE_INSTRUCTION_MAX_LENGTH.get(age, 100)
    if len(text) > max_len:
        sentences = re.split(r'[.!?]+', text)
        shortened = []
        current_len = 0
        for s in sentences:
            s = s.strip()
            if not s:
                continue
            if current_len + len(s) + 1 <= max_len:
                shortened.append(s)
                current_len += len(s) + 1
            else:
                break
        if not shortened:
            return text[:max_len].rsplit(" ", 1)[0] + "..."
        return ". ".join(shortened) + "."
    return text


def diversify_beginnings(texts: List[str], language: str = "ru") -> List[str]:
    result = []
    used = set()
    for text in texts:
        for beginning in REPETITIVE_BEGINNINGS:
            if text.startswith(beginning) and beginning in used:
                alt = _alternative_for(beginning, language)
                text = text.replace(beginning, alt, 1)
                break
        for beginning in REPETITIVE_BEGINNINGS:
            if text.startswith(beginning):
                used.add(beginning)
                break
        result.append(text)
    return result


def remove_ads_tone(text: str) -> str:
    ad_patterns = [
        r"чудово підходить для", r"ідеально для",
        r"отличн(ый|ая|ое|ого|ому|ым|ом) способ", r"прекрасн(ый|ая|ое|ого|ому|ым|ом) вариант",
        r"найкращ(ий|а|е|ого|ому|им|ому)", r"сам(ый|ая|ое|ого|ому|ым|ом) лучш(ий|ая|ее|его|ему|им)",
        r"незаменим(ый|ая|ое|ого|ому|ым|ом) помощник",
        r"незамінн(ий|а|е|ого|ому|им) помічник",
    ]
    for p in ad_patterns:
        text = re.sub(p, "", text, flags=re.IGNORECASE)
    return text


def _alternative_for(beginning: str, language: str = "ru") -> str:
    ru_alts = {
        "Прочитай": "Ознакомься с",
        "Реши": "Попробуй решить",
        "Напиши": "Аккуратно запиши",
        "Знайди": "Попробуй найти",
        "Порахуй": "Посчитай",
        "Розв'яжи": "Найди відповідь",
        "Запиши": "Впиши",
        "Накресли": "Нарисуй",
        "Подумай": "Поміркуй",
    }
    uk_alts = {
        "Прочитай": "Ознайомся з",
        "Реши": "Спробуй розв'язати",
        "Напиши": "Акуратно запиши",
        "Знайди": "Спробуй знайти",
        "Порахуй": "Полічи",
        "Розв'яжи": "Знайди відповідь",
        "Запиши": "Впиши",
        "Накресли": "Намалюй",
        "Подумай": "Поміркуй",
    }
    if language.startswith("uk"):
        return uk_alts.get(beginning, beginning)
    return ru_alts.get(beginning, beginning)


def editorial_pass(pack_data: Dict[str, Any]) -> Dict[str, Any]:
    lang = pack_data.get("language", "ru")
    age = pack_data.get("age", 7)
    pages = pack_data.get("pages", [])

    for page in pages:
        for task in page.get("tasks", []):
            q = task.get("question", "")
            q = remove_template_phrases(q)
            q = humanize_instructions(q, lang)
            q = remove_ads_tone(q)
            q = shorten_for_age(q, age)
            task["question"] = q.strip()

            inst = task.get("instruction", "")
            if inst:
                inst = remove_template_phrases(inst)
                inst = humanize_instructions(inst, lang)
                inst = remove_ads_tone(inst)
                inst = shorten_for_age(inst, age)
                task["instruction"] = inst.strip()

        instructions = [t.get("instruction", "") or t.get("question", "")[:40]
                        for t in page.get("tasks", [])]
        diversified = diversify_beginnings(instructions, lang)
        for idx, task in enumerate(page.get("tasks", [])):
            if idx < len(diversified) and task.get("instruction"):
                task["instruction"] = diversified[idx]

    if pack_data.get("parent_instruction"):
        pi = pack_data["parent_instruction"]
        pi = remove_template_phrases(pi)
        pi = remove_ads_tone(pi)
        pi = humanize_instructions(pi, lang)
        pi = shorten_for_age(pi, age + 10)
        pack_data["parent_instruction"] = pi.strip()

    return pack_data
