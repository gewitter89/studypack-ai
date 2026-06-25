"""
Offline template generators — produce complete pack_data dicts without AI.
All tasks use real thematic words; no placeholders permitted.
"""
import json
import os
import random
import logging
from typing import Dict, Any, Optional, List, Tuple

from core.models import PackRequest
from core.math_checker import generate_math_examples
from core.paths import output_dir
from core.topic_lexicon import (
    get_words, random_word, random_n_words, get_generic, resolve_topic, get_display_name
)

logger = logging.getLogger(__name__)

TEMPLATES = {}

# ─── Helpers ─────────────────────────────────────────────────────────────────

def _make_page(num, title, instruction, tasks, page_type="exercise"):
    return {
        "page_number": num,
        "page_type": page_type,
        "title": title,
        "instruction": instruction,
        "tasks": tasks
    }


def _make_task(ttype, question, answer="", opts=None):
    return {
        "type": ttype,
        "question": question,
        "options": opts or [],
        "answer_space": True,
        "answer": answer
    }


def _creative_answer(lang: str) -> str:
    """Placeholder-safe answer for creative/drawing tasks."""
    if lang in ("uk", "uk+en"):
        return "Перевіряється дорослим"
    return "Проверяется взрослым"


def _grade_label(grade: str, lang: str) -> str:
    """Translate grade label to target language."""
    if not grade:
        return ""
    g = grade.strip().lower()
    if lang in ("uk", "uk+en"):
        # Try to detect if it contains Russian "класс" and replace
        g = g.replace("класс", "клас").replace("дошкольник", "дошкільник")
        if "дошк" in g:
            return "Дошкільник"
        return grade.replace("класс", "клас").replace("Дошкольник", "Дошкільник")
    if lang in ("ru", "ru+en"):
        g2 = g.replace("клас", "класс").replace("дошкільник", "дошкольник")
        return g2.capitalize()
    return grade


def _topic_words_safe(topic: str, lang: str, n: int = 6) -> List[str]:
    """Return n topic words; fall back to generic (never placeholders)."""
    simple = lang.split("+")[0]
    words = get_words(topic, simple)
    if not words:
        words = get_generic(simple)
    if not words:
        words = ["зірка", "квітка", "книга", "м'яч"] if simple == "uk" else ["звезда", "цветок", "книга", "мяч"]
    return random.sample(words, min(n, len(words)))


def _parent_instruction(lang: str) -> str:
    if lang in ("uk", "uk+en"):
        return ("Займайтеся 10–20 хвилин на день. Хваліть дитину за старання. "
                "Відповіді — тільки для перевірки дорослим.")
    return ("Занимайтесь 10–20 минут в день. Хвалите ребёнка за старание. "
            "Ответы — только для проверки взрослым.")


# ─── Topical count items and pluralization helper ──────────────────────────────

_TOPIC_COUNT_ITEMS = {
    "dinosaurs": [
        {"ru": ("яйцо", "яйца", "яиц"), "uk": ("яйце", "яйця", "яєць"), "emoji": "🥚"},
        {"ru": ("вулкан", "вулкана", "вулканов"), "uk": ("вулкан", "вулкани", "вулканів"), "emoji": "🌋"},
        {"ru": ("кость", "кости", "костей"), "uk": ("кістка", "кістки", "кісток"), "emoji": "🦴"},
    ],
    "space": [
        {"ru": ("ракета", "ракеты", "ракет"), "uk": ("ракета", "ракети", "ракет"), "emoji": "🚀"},
        {"ru": ("планета", "планеты", "планет"), "uk": ("планета", "планети", "планет"), "emoji": "🪐"},
        {"ru": ("звезда", "звезды", "звезд"), "uk": ("зірка", "зірки", "зірок"), "emoji": "⭐"},
    ],
    "animals": [
        {"ru": ("заяц", "зайца", "зайцев"), "uk": ("заєць", "зайці", "зайців"), "emoji": "🐰"},
        {"ru": ("лиса", "лисы", "лис"), "uk": ("лисиця", "лисиці", "лисиць"), "emoji": "🦊"},
        {"ru": ("ёж", "ежа", "ежей"), "uk": ("їжак", "їжаки", "їжаків"), "emoji": "🦔"},
    ],
    "fairy_tales": [
        {"ru": ("замок", "замка", "замков"), "uk": ("замок", "замки", "замків"), "emoji": "🏰"},
        {"ru": ("книга", "книги", "книг"), "uk": ("книга", "книги", "книг"), "emoji": "📘"},
        {"ru": ("звезда", "звезды", "звезд"), "uk": ("зірка", "зірки", "зірок"), "emoji": "⭐"},
    ],
    "cartoon_heroes": [
        {"ru": ("маска", "маски", "масок"), "uk": ("маска", "маски", "масок"), "emoji": "🎭"},
        {"ru": ("плащ", "плаща", "плащей"), "uk": ("плащ", "плащі", "плащів"), "emoji": "🧣"},
        {"ru": ("звезда", "звезды", "звезд"), "uk": ("зірка", "зірки", "зірок"), "emoji": "⭐"},
    ],
    "cats": [
        {"ru": ("рыбка", "рыбки", "рыбок"), "uk": ("рибка", "рибки", "рибок"), "emoji": "🐟"},
        {"ru": ("мышка", "мышки", "мышек"), "uk": ("мишка", "мишки", "мишок"), "emoji": "🐭"},
        {"ru": ("клубок", "клубка", "клубочков"), "uk": ("клубок", "клубки", "клубочків"), "emoji": "🧶"},
    ],
    "dogs": [
        {"ru": ("кость", "кости", "костей"), "uk": ("кістка", "кістки", "кісток"), "emoji": "🦴"},
        {"ru": ("мяч", "мяча", "мячей"), "uk": ("м'яч", "м'ячі", "м'ячів"), "emoji": "⚽"},
        {"ru": ("миска", "миски", "мисок"), "uk": ("миска", "миски", "мисок"), "emoji": "🥣"},
    ],
    "cars": [
        {"ru": ("машина", "машины", "машин"), "uk": ("машина", "машини", "машин"), "emoji": "🚗"},
        {"ru": ("колесо", "колеса", "колес"), "uk": ("колесо", "колеса", "коліс"), "emoji": "🛞"},
        {"ru": ("ключ", "ключа", "ключей"), "uk": ("ключ", "ключі", "ключів"), "emoji": "🔑"},
    ],
    "football": [
        {"ru": ("мяч", "мяча", "мячей"), "uk": ("м'яч", "м'ячі", "м'ячів"), "emoji": "⚽"},
        {"ru": ("кубок", "кубка", "кубков"), "uk": ("кубок", "кубки", "кубків"), "emoji": "🏆"},
        {"ru": ("ворота", "ворота", "ворот"), "uk": ("ворота", "ворота", "воріт"), "emoji": "🥅"},
    ],
    "princesses": [
        {"ru": ("корона", "короны", "корон"), "uk": ("корона", "корони", "корон"), "emoji": "👑"},
        {"ru": ("замок", "замка", "замков"), "uk": ("замок", "замки", "замків"), "emoji": "🏰"},
        {"ru": ("туфелька", "туфельки", "туфелек"), "uk": ("туфелька", "туфельки", "туфельок"), "emoji": "👠"},
    ],
    "pirates": [
        {"ru": ("корабль", "корабля", "кораблей"), "uk": ("корабель", "кораблі", "кораблів"), "emoji": "🚢"},
        {"ru": ("карта", "карты", "карт"), "uk": ("карта", "карти", "карт"), "emoji": "🗺️"},
        {"ru": ("монета", "монеты", "монет"), "uk": ("монета", "монети", "монет"), "emoji": "🪙"},
    ],
    "superheroes_generic": [
        {"ru": ("маска", "маски", "масок"), "uk": ("маска", "маски", "масок"), "emoji": "🎭"},
        {"ru": ("молния", "молнии", "молний"), "uk": ("блискавка", "блискавки", "блискавок"), "emoji": "⚡"},
        {"ru": ("звезда", "звезды", "звезд"), "uk": ("зірка", "зірки", "зірок"), "emoji": "⭐"},
    ],
    "pixel_world": [
        {"ru": ("куб", "куба", "кубов"), "uk": ("куб", "куби", "кубів"), "emoji": "🧊"},
        {"ru": ("меч", "меча", "мечей"), "uk": ("меч", "мечі", "мечів"), "emoji": "⚔️"},
        {"ru": ("кирка", "кирки", "кирок"), "uk": ("кирка", "кирки", "кирок"), "emoji": "⛏️"},
    ],
    "underwater": [
        {"ru": ("рыбка", "рыбки", "рыбок"), "uk": ("рибка", "рибки", "рибок"), "emoji": "🐟"},
        {"ru": ("ракушка", "ракушки", "ракушек"), "uk": ("мушля", "мушлі", "мушель"), "emoji": "🐚"},
        {"ru": ("осьминог", "осьминога", "осьминогов"), "uk": ("восьминіг", "восьминоги", "восьминогів"), "emoji": "🐙"},
    ],
    "travel": [
        {"ru": ("чемодан", "чемодана", "чемоданов"), "uk": ("валіза", "валізи", "валіз"), "emoji": "💼"},
        {"ru": ("билет", "билета", "билетов"), "uk": ("квиток", "квитки", "квитків"), "emoji": "🎫"},
        {"ru": ("поезд", "поезда", "поездов"), "uk": ("поїзд", "поїзди", "поїздів"), "emoji": "🚂"},
    ],
    "robots": [
        {"ru": ("shesterenka", "shesterenki", "shesterenok"), "uk": ("шестерня", "шестерні", "шестерень"), "emoji": "⚙️"},
        {"ru": ("batareyka", "batareyki", "batareyek"), "uk": ("батарея", "батареї", "батарей"), "emoji": "🔋"},
        {"ru": ("ekran", "ekrana", "ekranov"), "uk": ("екран", "екрани", "екранів"), "emoji": "📱"},
    ],
    "magic_forest": [
        {"ru": ("гриб", "гриба", "грибов"), "uk": ("гриб", "гриби", "грибів"), "emoji": "🍄"},
        {"ru": ("цветок", "цветка", "цветов"), "uk": ("квітка", "квітки", "квіток"), "emoji": "🌸"},
        {"ru": ("ягода", "ягоды", "ягод"), "uk": ("ягода", "ягоди", "ягід"), "emoji": "🍓"},
    ],
    "sport": [
        {"ru": ("мяч", "мяча", "мячей"), "uk": ("м'яч", "м'ячі", "м'ячів"), "emoji": "⚽"},
        {"ru": ("медаль", "медали", "медалей"), "uk": ("медаль", "медалі", "медалей"), "emoji": "🥇"},
        {"ru": ("кубок", "кубка", "кубков"), "uk": ("кубок", "кубки", "кубків"), "emoji": "🏆"},
    ],
    "cooking": [
        {"ru": ("кастрюля", "кастрюли", "кастрюль"), "uk": ("каструля", "каструлі", "каструль"), "emoji": "🍲"},
        {"ru": ("пирог", "пирога", "пирогов"), "uk": ("пиріг", "пироги", "пирогів"), "emoji": "🍰"},
        {"ru": ("ложка", "ложки", "ложек"), "uk": ("ложка", "ложки", "ложок"), "emoji": "🥄"},
    ],
    "farm": [
        {"ru": ("корова", "коровы", "коров"), "uk": ("корова", "корови", "корів"), "emoji": "🐄"},
        {"ru": ("курица", "курицы", "куриц"), "uk": ("курка", "курки", "курей"), "emoji": "🐔"},
        {"ru": ("трактор", "трактора", "тракторов"), "uk": ("трактор", "трактори", "тракторів"), "emoji": "🚜"},
    ],
    "zoo": [
        {"ru": ("слон", "слона", "слонов"), "uk": ("слон", "слони", "слонів"), "emoji": "🐘"},
        {"ru": ("лев", "льва", "львов"), "uk": ("лев", "леви", "левів"), "emoji": "🦁"},
        {"ru": ("обезьяна", "обезьяны", "обезьян"), "uk": ("мавпа", "мавпи", "мавп"), "emoji": "🐒"},
    ],
    "nature": [
        {"ru": ("цветок", "цветка", "цветов"), "uk": ("квітка", "квітки", "квіток"), "emoji": "🌸"},
        {"ru": ("облако", "облака", "облаков"), "uk": ("хмара", "хмари", "хмар"), "emoji": "☁️"},
        {"ru": ("камень", "камня", "камней"), "uk": ("камінь", "камені", "каменів"), "emoji": "🪨"},
    ],
}

def _pluralize(count: int, forms: Tuple[str, str, str]) -> str:
    """Forms: (singular_1, plural_234, genitive_plural_5)"""
    if count % 100 in (11, 12, 13, 14):
        return forms[2]
    c10 = count % 10
    if c10 == 1:
        return forms[0]
    elif c10 in (2, 3, 4):
        return forms[1]
    else:
        return forms[2]

# ─── Preschool page generators ───────────────────────────────────────────────

def _page_lichba(page_num: int, topic: str, lang: str) -> Tuple[dict, dict]:
    """Лічба / Счёт — counting tasks with thematic items."""
    uk = lang in ("uk", "uk+en")
    canonical_topic = resolve_topic(topic, lang)
    
    items = _TOPIC_COUNT_ITEMS.get(canonical_topic)
    if not items:
        items = [
            {"ru": ("звезда", "звезды", "звезд"), "uk": ("зірка", "зірки", "зірок"), "emoji": "⭐"},
            {"ru": ("цветок", "цветка", "цветов"), "uk": ("квітка", "квітки", "квіток"), "emoji": "🌸"},
            {"ru": ("яблоко", "яблока", "яблок"), "uk": ("яблуко", "яблука", "яблук"), "emoji": "🍎"},
        ]
        
    title = "Лічба" if uk else "Счёт"
    instruction = "Порахуй та запиши кількість" if uk else "Посчитай и запиши количество"

    tasks = []
    answers_list = []
    for i, item in enumerate(items[:3]):
        count = random.randint(2, 7)
        emoji = item["emoji"]
        lang_key = "uk" if uk else "ru"
        forms = item[lang_key]
        noun = _pluralize(count, forms)
        
        icons_str = " ".join([emoji] * count)
        if uk:
            q = f"Порахуй {noun}: {icons_str}"
        else:
            q = f"Посчитай {noun}: {icons_str}"
        tasks.append(_make_task("math", q, f"{count} {noun}"))
        answers_list.append(f"{count} {noun}")

    page = _make_page(page_num, title, instruction, tasks)
    return page, {"page_number": page_num, "answers": answers_list}


def _page_figury(page_num: int, topic: str, lang: str) -> Tuple[dict, dict]:
    """Фігури / Фигуры — shape recognition."""
    uk = lang in ("uk", "uk+en")
    shapes = (
        [("квадрат", "○ □ △"), ("коло", "○ □ △"), ("трикутник", "○ □ △"), ("прямокутник", "□ ○ △ ▭")]
        if uk else
        [("квадрат", "○ □ △"), ("круг", "○ □ △"), ("треугольник", "○ □ △"), ("прямоугольник", "□ ○ △ ▭")]
    )

    title = "Фігури" if uk else "Фигуры"
    instruction = "Обведи правильну фігуру" if uk else "Обведи правильную фигуру"

    tasks = []
    answers_list = []
    for shape_name, shape_row in shapes:
        if uk:
            q = f"Обведи {shape_name}: {shape_row}"
        else:
            q = f"Обведи {shape_name}: {shape_row}"
        tasks.append(_make_task("logic", q, shape_name))
        answers_list.append(shape_name)

    page = _make_page(page_num, title, instruction, tasks)
    return page, {"page_number": page_num, "answers": answers_list}


def _page_bukvy(page_num: int, topic: str, lang: str) -> Tuple[dict, dict]:
    """Букви / Буквы — letter recognition using topic words."""
    uk = lang in ("uk", "uk+en")
    words = _topic_words_safe(topic, lang, 4)
    # Filter: use words with at least 2 chars
    words = [w for w in words if len(w) >= 2][:3]
    if not words:
        words = ["зірка", "книга", "лис"] if uk else ["звезда", "книга", "лиса"]

    title = "Букви" if uk else "Буквы"
    instruction = "Обведи першу букву кожного слова" if uk else "Обведи первую букву каждого слова"

    tasks = []
    answers_list = []
    for word in words:
        first_letter = word[0].upper()
        if uk:
            q = f"Обведи букву {first_letter} у слові «{word}»"
        else:
            q = f"Обведи букву {first_letter} в слове «{word}»"
        tasks.append(_make_task("writing", q, first_letter))
        answers_list.append(f"літера {first_letter}" if uk else f"буква {first_letter}")

    page = _make_page(page_num, title, instruction, tasks)
    return page, {"page_number": page_num, "answers": answers_list}


def _page_znajdy(page_num: int, topic: str, lang: str) -> Tuple[dict, dict]:
    """Знайди таку ж / Найди такую же — matching pairs."""
    uk = lang in ("uk", "uk+en")
    canonical_topic = resolve_topic(topic, lang)
    items = _TOPIC_COUNT_ITEMS.get(canonical_topic)
    if not items:
        items = [
            {"ru": ("звезда", "звезды", "звезд"), "uk": ("зірка", "зірки", "зірок"), "emoji": "⭐"},
            {"ru": ("цветок", "цветка", "цветов"), "uk": ("квітка", "квітки", "квіток"), "emoji": "🌸"},
            {"ru": ("шарик", "шарика", "шариков"), "uk": ("кулька", "кульки", "кульок"), "emoji": "🎈"},
        ]

    title = "Знайди таку ж" if uk else "Найди такую же"
    instruction = "З'єднай однакові предмети" if uk else "Соедини одинаковые предметы"

    tasks = []
    answers_list = []
    for i, item in enumerate(items[:3]):
        emoji = item["emoji"]
        lang_key = "uk" if uk else "ru"
        noun_singular = item[lang_key][0]
        noun_plural = item[lang_key][1]
        
        if uk:
            q = f"З'єднай однакові {noun_plural}: {emoji} — {emoji}"
        else:
            q = f"Соедини одинаковые {noun_plural}: {emoji} — {emoji}"
        tasks.append(_make_task("logic", q, noun_singular))
        answers_list.append(noun_singular)

    page = _make_page(page_num, title, instruction, tasks)
    return page, {"page_number": page_num, "answers": answers_list}


def _page_rozfarbuy(page_num: int, topic: str, lang: str) -> Tuple[dict, dict]:
    """Розфарбуй / Раскрась — coloring instructions."""
    uk = lang in ("uk", "uk+en")
    canonical_topic = resolve_topic(topic, lang)
    items = _TOPIC_COUNT_ITEMS.get(canonical_topic)
    if not items:
        items = [
            {"ru": ("звезда", "звезды", "звезд"), "uk": ("зірка", "зірки", "зірок"), "emoji": "⭐"},
            {"ru": ("цветок", "цветка", "цветов"), "uk": ("квітка", "квітки", "квіток"), "emoji": "🌸"},
            {"ru": ("шарик", "шарика", "шариков"), "uk": ("кулька", "кульки", "кульок"), "emoji": "🎈"},
        ]

    title = "Розфарбуй" if uk else "Раскрась"
    instruction = "Розфарбуй малюнки за вказівками" if uk else "Раскрась рисунки по указанию"

    tasks = []
    answers_list = []
    for i, item in enumerate(items[:3]):
        count = random.randint(2, 5)
        lang_key = "uk" if uk else "ru"
        forms = item[lang_key]
        noun = _pluralize(count, forms)
        if uk:
            q = f"Розфарбуй {count} {noun}"
        else:
            q = f"Раскрась {count} {noun}"
        tasks.append(_make_task("creative", q, _creative_answer(lang)))
        answers_list.append(_creative_answer(lang))

    page = _make_page(page_num, title, instruction, tasks)
    return page, {"page_number": page_num, "answers": answers_list}


def _page_znaidy_zaive(page_num: int, topic: str, lang: str) -> Tuple[dict, dict]:
    """Знайди зайве / Найди лишнее — odd one out."""
    uk = lang in ("uk", "uk+en")
    topic_words = _topic_words_safe(topic, lang, 3)
    generic_words = get_generic(lang.split("+")[0])
    intruder = random.choice(generic_words) if generic_words else ("стіл" if uk else "стол")

    # Build sets of 4: 3 topic + 1 generic intruder
    items = topic_words[:3] + [intruder]
    random.shuffle(items)
    items_str = ", ".join(items)

    title = "Знайди зайве" if uk else "Найди лишнее"
    instruction = "Знайди предмет, який не підходить до групи" if uk else "Найди предмет, не подходящий к группе"

    if uk:
        q = f"Що зайве? {items_str}"
    else:
        q = f"Что лишнее? {items_str}"

    tasks = [_make_task("logic", q, intruder, items)]
    page = _make_page(page_num, title, instruction, tasks)
    return page, {"page_number": page_num, "answers": [intruder]}


def _page_math_topical(page_num: int, topic: str, lang: str, age: int) -> Tuple[dict, dict]:
    """Тематична математика / Тематическая математика — word math problems."""
    uk = lang in ("uk", "uk+en")
    words = _topic_words_safe(topic, lang, 3)
    max_num = min(age + 2, 10)

    title = "Задачки" if uk else "Задачи"
    instruction = "Розв'яжи задачки" if uk else "Реши задачи"

    tasks = []
    answers_list = []
    for word in words:
        a = random.randint(1, max_num // 2)
        b = random.randint(1, max_num - a)
        operation = random.choice(["+", "-"]) if a > b else "+"
        if operation == "-":
            a, b = max(a, b), min(a, b)
        answer = a + b if operation == "+" else a - b
        if uk:
            if operation == "+":
                q = f"У кошика {a} {word}. Поклали ще {b}. Скільки всього?"
            else:
                q = f"Було {a} {word}. Взяли {b}. Скільки залишилося?"
        else:
            if operation == "+":
                q = f"В корзине {a} {word}. Положили ещё {b}. Сколько всего?"
            else:
                q = f"Было {a} {word}. Взяли {b}. Сколько осталось?"
        tasks.append(_make_task("math", q, str(answer)))
        answers_list.append(str(answer))

    page = _make_page(page_num, title, instruction, tasks)
    return page, {"page_number": page_num, "answers": answers_list}


def _page_reading_topic(page_num: int, topic: str, lang: str) -> Tuple[dict, dict]:
    """Short reading passage built from topic words."""
    uk = lang in ("uk", "uk+en")
    words = _topic_words_safe(topic, lang, 4)
    display = get_display_name(topic, lang)

    if uk:
        text = (
            f"Жив собі маленький {words[0]}. "
            f"Одного разу він знайшов {words[1] if len(words) > 1 else 'скарб'}. "
            f"Поряд стояв великий {words[2] if len(words) > 2 else 'замок'}. "
            f"Всі були дуже раді!"
        )
        q1 = f"Кого описується в тексті?"
        q2 = f"Що знайшов {words[0]}?"
        a1 = words[0]
        a2 = words[1] if len(words) > 1 else "скарб"
    else:
        text = (
            f"Жил-был маленький {words[0]}. "
            f"Однажды он нашёл {words[1] if len(words) > 1 else 'сокровище'}. "
            f"Рядом стоял большой {words[2] if len(words) > 2 else 'замок'}. "
            f"Все были очень рады!"
        )
        q1 = f"Кто описывается в тексте?"
        q2 = f"Что нашёл {words[0]}?"
        a1 = words[0]
        a2 = words[1] if len(words) > 1 else "сокровище"

    title = f"Читання: {display}" if uk else f"Чтение: {display}"
    instruction = "Прочитай текст та дай відповіді" if uk else "Прочитай текст и ответь на вопросы"

    tasks = [
        _make_task("reading", f"{text}\n\n{q1}", a1),
        _make_task("reading", q2, a2),
    ]
    page = _make_page(page_num, title, instruction, tasks)
    return page, {"page_number": page_num, "answers": [a1, a2]}


def _page_logic_pattern(page_num: int, topic: str, lang: str) -> Tuple[dict, dict]:
    """Pattern/sequence logic task."""
    uk = lang in ("uk", "uk+en")
    words = _topic_words_safe(topic, lang, 2)
    a, b = words[0], words[1] if len(words) > 1 else words[0]
    icons = ["★", "●", "★", "●", "★", "?"]
    pattern_str = " ".join(icons)

    title = "Закономірність" if uk else "Закономерность"
    instruction = "Знайди закономірність та продовж ряд" if uk else "Найди закономерность и продолжи ряд"

    if uk:
        q1 = f"Продовж ряд: {a}, {b}, {a}, {b}, ..."
    else:
        q1 = f"Продолжи ряд: {a}, {b}, {a}, {b}, ..."

    if uk:
        q2 = f"Що йде далі? ★ ● ★ ● ★ ..."
    else:
        q2 = f"Что дальше? ★ ● ★ ● ★ ..."

    tasks = [
        _make_task("logic", q1, a),
        _make_task("logic", q2, "●"),
    ]
    page = _make_page(page_num, title, instruction, tasks)
    return page, {"page_number": page_num, "answers": [a, "●"]}


# ─── Main template functions ──────────────────────────────────────────────────

def template_preschool(request: PackRequest) -> Dict[str, Any]:
    age = request.age
    topic = resolve_topic(request.topic, request.language)
    lang = request.language
    pages_count = min(request.pages_count, 12)
    uk = lang in ("uk", "uk+en")

    display_topic = get_display_name(topic, lang)
    title = f"Підготовка до школи: {display_topic}" if uk else f"Подготовка к школе: {display_topic}"
    subtitle = f"Завдання для дітей {age} років" if uk else f"Задания для детей {age} лет"
    grade_str = _grade_label(request.grade, lang)

    # Page generators pool — rotate through varied types
    # _page_math_topical needs age, so wrap it
    def _math_topical_wrapper(pn, tp, ln):
        return _page_math_topical(pn, tp, ln, age)

    _generators = [
        _page_lichba,
        _page_figury,
        _page_bukvy,
        _page_znajdy,
        _page_rozfarbuy,
        _page_znaidy_zaive,
        _math_topical_wrapper,
        _page_reading_topic,
        _page_logic_pattern,
    ]

    pages = []
    answers = []
    for i in range(pages_count):
        gen = _generators[i % len(_generators)]
        try:
            page, ans = gen(i + 1, topic, lang)
        except Exception as e:
            logger.warning(f"Generator {gen.__name__} failed: {e}")
            # Safe fallback
            page, ans = _page_lichba(i + 1, topic, lang)
        pages.append(page)
        answers.append(ans)

    return {
        "title": title,
        "subtitle": subtitle,
        "language": lang,
        "age": age,
        "grade": grade_str or ("Дошкільник" if uk else "Дошкольник"),
        "topic": topic,
        "pack_type": request.pack_type,
        "difficulty": "easy",
        "parent_instruction": _parent_instruction(lang),
        "pages": pages,
        "answers": answers,
    }


def template_math(request: PackRequest) -> Dict[str, Any]:
    age = request.age
    topic = resolve_topic(request.topic, request.language)
    lang = request.language
    pages_count = min(request.pages_count, 20)
    uk = lang in ("uk", "uk+en")

    pages = []
    answers = []

    # Diversified instructions to avoid repetition hard fail
    math_instructions_uk = [
        "Розв'яжи приклади", "Порахуй і запиши", "Знайди відповідь",
        "Обчисли", "Запиши правильну відповідь",
    ]
    math_instructions_ru = [
        "Реши примеры", "Посчитай и запиши", "Найди ответ",
        "Вычисли", "Запиши правильный ответ",
    ]
    math_insts = math_instructions_uk if uk else math_instructions_ru

    for i in range(pages_count):
        # Alternate: 2 standard examples + 1 word problem
        if i % 3 == 2 and topic not in ("general", ""):
            page, ans = _page_math_topical(i + 1, topic, lang, age)
        else:
            examples = generate_math_examples(3, request.difficulty, age, topic)
            tasks = [_make_task("math", e["question"], e["answer"]) for e in examples]
            ans_list = [e["answer"] for e in examples]
            page = _make_page(
                i + 1,
                f"Приклади {i + 1}" if uk else f"Примеры {i + 1}",
                math_insts[i % len(math_insts)],
                tasks
            )
            ans = {"page_number": i + 1, "answers": ans_list}
        pages.append(page)
        answers.append(ans)

    display_topic = get_display_name(topic, lang)
    return {
        "title": f"Математика: {display_topic}" if topic and topic not in ("general", "") else "Математика",
        "subtitle": f"Приклади для дітей {age} років" if uk else f"Примеры для детей {age} лет",
        "language": lang,
        "age": age,
        "grade": _grade_label(request.grade, lang),
        "topic": topic,
        "pack_type": request.pack_type,
        "difficulty": request.difficulty,
        "parent_instruction": _parent_instruction(lang),
        "pages": pages,
        "answers": answers,
    }


def template_logic(request: PackRequest) -> Dict[str, Any]:
    age = request.age
    topic = resolve_topic(request.topic, request.language)
    lang = request.language
    pages_count = min(request.pages_count, 12)
    uk = lang in ("uk", "uk+en")

    pages = []
    answers = []

    _logic_gens = [_page_logic_pattern, _page_znaidy_zaive, _page_znajdy]

    for i in range(pages_count):
        gen = _logic_gens[i % len(_logic_gens)]
        try:
            page, ans = gen(i + 1, topic, lang)
        except Exception as e:
            logger.warning(f"Logic gen failed: {e}")
            page, ans = _page_logic_pattern(i + 1, topic, lang)
        pages.append(page)
        answers.append(ans)

    display_topic = get_display_name(topic, lang)
    return {
        "title": (f"Логіка та увага: {display_topic}" if uk else f"Логика и внимание: {display_topic}") if topic and topic not in ("general", "") else ("Логіка та увага" if uk else "Логика и внимание"),
        "subtitle": f"Завдання для дітей {age} років" if uk else f"Задания для детей {age} лет",
        "language": lang,
        "age": age,
        "grade": _grade_label(request.grade, lang),
        "topic": topic,
        "pack_type": request.pack_type,
        "difficulty": request.difficulty,
        "parent_instruction": _parent_instruction(lang),
        "pages": pages,
        "answers": answers,
    }


def template_reading(request: PackRequest) -> Dict[str, Any]:
    age = request.age
    topic = resolve_topic(request.topic, request.language)
    lang = request.language
    pages_count = min(request.pages_count, 12)
    uk = lang in ("uk", "uk+en")

    texts_uk = [
        ("Кіт і миша",
         "Кіт побачив мишу. Миша втекла в нірку. Кіт залишився голодним.",
         ["Кого побачив кіт?", "Куди втекла миша?"], ["мишу", "в нірку"]),
        ("Сонячний день",
         "Сонце світить яскраво. Діти раді. Вони грають у дворі.",
         ["Що світить яскраво?", "Де грають діти?"], ["сонце", "у дворі"]),
        ("Весна прийшла",
         "Прийшла весна. Птахи повернулися. Квіти зацвіли в саду.",
         ["Що прийшло?", "Що зацвіло?"], ["весна", "квіти"]),
    ]
    texts_ru = [
        ("Кот и мышь",
         "Кот увидел мышь. Мышь убежала в норку. Кот остался голодным.",
         ["Кого увидел кот?", "Куда убежала мышь?"], ["мышь", "в норку"]),
        ("Солнечный день",
         "Солнце светит ярко. Дети рады. Они играют во дворе.",
         ["Что светит ярко?", "Где играют дети?"], ["солнце", "во дворе"]),
        ("Весна пришла",
         "Пришла весна. Птицы вернулись. Цветы расцвели в саду.",
         ["Что пришло?", "Что расцвело?"], ["весна", "цветы"]),
    ]

    pool = texts_uk if uk else texts_ru
    pages = []
    answers = []

    for i in range(pages_count):
        # Mix topic-based passages with fixed ones
        if i % 2 == 0 and topic not in ("general", ""):
            page, ans = _page_reading_topic(i + 1, topic, lang)
        else:
            entry = pool[i % len(pool)]
            instruction = "Прочитай та дай відповіді на запитання" if uk else "Прочитай и ответь на вопросы"
            tasks = [
                _make_task("reading", f"{entry[1]}\n\n{q}", entry[3][j])
                for j, q in enumerate(entry[2])
            ]
            page = _make_page(i + 1, entry[0], instruction, tasks)
            ans = {"page_number": i + 1, "answers": entry[3]}
        pages.append(page)
        answers.append(ans)

    display_topic = get_display_name(topic, lang)
    return {
        "title": (f"Читання: {display_topic}" if uk else f"Чтение: {display_topic}") if topic and topic not in ("general", "") else ("Читання" if uk else "Чтение"),
        "subtitle": f"Тексти для дітей {age} років" if uk else f"Тексты для детей {age} лет",
        "language": lang,
        "age": age,
        "grade": _grade_label(request.grade, lang),
        "topic": topic,
        "pack_type": request.pack_type,
        "difficulty": request.difficulty,
        "parent_instruction": _parent_instruction(lang),
        "pages": pages,
        "answers": answers,
    }


def template_mixed(request: PackRequest) -> Dict[str, Any]:
    age = request.age
    topic = resolve_topic(request.topic, request.language)
    lang = request.language
    pages_count = min(request.pages_count, 14)
    uk = lang in ("uk", "uk+en")

    _day_generators = [
        ("reading", "Читання" if uk else "Чтение", _page_reading_topic),
        ("math", "Математика", _page_math_topical),
        ("logic", "Логіка" if uk else "Логика", _page_logic_pattern),
        ("writing", "Букви" if uk else "Буквы", _page_bukvy),
        ("math", "Лічба" if uk else "Счёт", _page_lichba),
        ("logic", "Знайди зайве" if uk else "Найди лишнее", _page_znaidy_zaive),
        ("creative", "Розфарбуй" if uk else "Раскрась", _page_rozfarbuy),
    ]

    pages = []
    answers = []

    for i in range(min(pages_count, len(_day_generators))):
        ptype, ptitle, gen = _day_generators[i]
        try:
            if gen == _page_math_topical:
                page, ans = gen(i + 1, topic, lang, age)
            else:
                page, ans = gen(i + 1, topic, lang)
            # Override page title with day label
            page["title"] = f"День {i + 1}: {ptitle}"
        except Exception as e:
            logger.warning(f"Mixed gen day {i+1} failed: {e}")
            page, ans = _page_lichba(i + 1, topic, lang)
            page["title"] = f"День {i + 1}"
        pages.append(page)
        answers.append(ans)

    display_topic = get_display_name(topic, lang)
    return {
        "title": (f"Змішаний набір: {display_topic}" if uk else f"Смешанный набор: {display_topic}") if topic and topic not in ("general", "") else ("Змішаний набір на тиждень" if uk else "Смешанный набор на неделю"),
        "subtitle": f"Завдання для дітей {age} років" if uk else f"Задания для детей {age} лет",
        "language": lang,
        "age": age,
        "grade": _grade_label(request.grade, lang),
        "topic": topic,
        "pack_type": request.pack_type,
        "difficulty": request.difficulty,
        "parent_instruction": _parent_instruction(lang),
        "pages": pages,
        "answers": answers,
    }


TEMPLATES = {
    "preschool": template_preschool,
    "math": template_math,
    "logic": template_logic,
    "reading": template_reading,
    "mixed_week": template_mixed,
}


def generate_offline(request: PackRequest) -> Optional[Dict[str, Any]]:
    func = TEMPLATES.get(request.pack_type)
    if func is None:
        logger.warning(f"No template for pack type: {request.pack_type}")
        return None
    logger.info(f"Generating offline template: {request.pack_type}")
    data = func(request)
    if data:
        from core.postprocess import postprocess
        data = postprocess(data)
    return data
