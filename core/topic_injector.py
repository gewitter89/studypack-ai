import random
import re
from typing import Dict, List, Optional, Tuple
from core.topic_lexicon import get_words, random_word, resolve_topic


_INJECTION_TEMPLATES: Dict[str, Dict[str, List[str]]] = {
    "math": {
        "ru": [
            "{topic_word}: {a} + {b} = ?",
            "Сколько {topic_word}? {a} + {b} = ?",
            "У {topic_word} было {a}. Добавили {b}. Сколько стало?",
            "Найди сумму {topic_word}: {a} + {b}",
            "{topic_word} принёс {a}. Потом ещё {b}. Сколько всего?",
        ],
        "uk": [
            "{topic_word}: {a} + {b} = ?",
            "Скільки {topic_word}? {a} + {b} = ?",
            "У {topic_word} було {a}. Додали {b}. Скільки стало?",
            "Знайди суму {topic_word}: {a} + {b}",
            "{topic_word} приніс {a}. Потім ще {b}. Скільки всього?",
        ],
        "en": [
            "{topic_word}: {a} + {b} = ?",
            "How many {topic_word}? {a} + {b} = ?",
            "{topic_word} had {a}. Added {b}. How many now?",
            "Find the sum of {topic_word}: {a} + {b}",
        ],
    },
    "preschool": {
        "ru": [
            "Посчитай {topic_word}.",
            "Сколько {topic_word}?",
            "Найди {topic_word} среди картинок.",
            "Обведи {topic_word}.",
            "Покажи {topic_word}.",
        ],
        "uk": [
            "Порахуй {topic_word}.",
            "Скільки {topic_word}?",
            "Знайди {topic_word} серед картинок.",
            "Обведи {topic_word}.",
            "Покажи {topic_word}.",
        ],
        "en": [
            "Count the {topic_word}.",
            "How many {topic_word}?",
            "Find the {topic_word} among the pictures.",
            "Circle the {topic_word}.",
        ],
    },
    "logic": {
        "ru": [
            "Продолжи ряд {topic_word}.",
            "Найди закономерность для {topic_word}.",
            "Что лишнее среди {topic_word}?",
            "Сравни {topic_word}.",
        ],
        "uk": [
            "Продовж ряд {topic_word}.",
            "Знайди закономірність для {topic_word}.",
            "Що зайве серед {topic_word}?",
            "Порівняй {topic_word}.",
        ],
        "en": [
            "Continue the pattern of {topic_word}.",
            "Find the rule for {topic_word}.",
            "What is odd among {topic_word}?",
            "Compare the {topic_word}.",
        ],
    },
    "reading": {
        "ru": [
            "Прочитай про {topic_word}.",
            "Ответь на вопросы о {topic_word}.",
            "Что делает {topic_word}?",
            "Опиши {topic_word}.",
        ],
        "uk": [
            "Прочитай про {topic_word}.",
            "Дай відповіді на запитання про {topic_word}.",
            "Що робить {topic_word}?",
            "Опиши {topic_word}.",
        ],
        "en": [
            "Read about {topic_word}.",
            "Answer questions about {topic_word}.",
            "What does {topic_word} do?",
            "Describe {topic_word}.",
        ],
    },
}

_MATH_WORD_PROBLEMS: Dict[str, Dict[str, List[str]]] = {
    "dinosaurs": {
        "ru": [
            "У динозавра было {a} яиц. Вылупилось {b} детёнышей. Сколько яиц осталось?",
            "Тираннозавр пробежал {a} метров, а стегозавр — {b} метров. На сколько больше пробежал тираннозавр?",
            "В стаде было {a} динозавров. Пришло ещё {b}. Сколько стало?",
        ],
        "uk": [
            "У динозавра було {a} яєць. Вилупилося {b} дитинчат. Скільки яєць залишилося?",
            "Тиранозавр пробіг {a} метрів, а стегозавр — {b} метрів. На скільки більше пробіг тиранозавр?",
            "У стаді було {a} динозаврів. Прийшло ще {b}. Скільки стало?",
        ],
        "en": [
            "A dinosaur had {a} eggs. {b} babies hatched. How many eggs are left?",
            "A T-Rex ran {a} meters, a stegosaurus ran {b} meters. How much farther did the T-Rex run?",
            "There were {a} dinosaurs. {b} more came. How many now?",
        ],
    },
    "space": {
        "ru": [
            "На космодроме было {a} ракет. Улетело {b}. Сколько осталось?",
            "Космонавт нашёл {a} звёзд, а потом ещё {b}. Сколько всего?",
            "На планете было {a} инопланетян. Прилетело ещё {b}. Сколько стало?",
        ],
        "uk": [
            "На космодромі було {a} ракет. Полетіло {b}. Скільки залишилося?",
            "Космонавт знайшов {a} зірок, а потім ще {b}. Скільки всього?",
            "На планеті було {a} інопланетян. Прилетіло ще {b}. Скільки стало?",
        ],
        "en": [
            "There were {a} rockets at the spaceport. {b} launched. How many are left?",
            "An astronaut found {a} stars, then {b} more. How many total?",
            "There were {a} aliens on the planet. {b} more arrived. How many now?",
        ],
    },
    "farm": {
        "en": [
            "{a} cows are in the field. {b} more come. How many cows?",
            "The farmer has {a} sheep. He buys {b} more. How many sheep?",
            "There are {a} chickens in the barn. {b} go outside. How many inside?",
        ],
        "ru": [
            "{a} коров на поле. Пришло ещё {b}. Сколько стало?",
            "У фермера {a} овец. Он купил ещё {b}. Сколько овец?",
            "{a} кур в сарае. {b} вышли. Сколько внутри?",
        ],
        "uk": [
            "{a} корів на полі. Прийшло ще {b}. Скільки стало?",
            "У фермера {a} овець. Він купив ще {b}. Скільки овець?",
            "{a} курей у хліві. {b} вийшли. Скільки всередині?",
        ],
    },
    "cats": {
        "ru": [
            "{a} котят играют с клубком. Прибежало ещё {b}. Сколько котят?",
            "У кошки было {a} котят. {b} уснули. Сколько бодрствуют?",
            "В миске {a} рыбок. Кот съел {b}. Сколько осталось?",
        ],
        "uk": [
            "{a} кошенят грають з клубком. Прибігло ще {b}. Скільки кошенят?",
            "У кішки було {a} кошенят. {b} заснули. Скільки не сплять?",
            "У мисці {a} рибок. Кіт з'їв {b}. Скільки залишилося?",
        ],
        "en": [
            "{a} kittens play with yarn. {b} more come. How many kittens?",
            "A cat had {a} kittens. {b} fell asleep. How many are awake?",
            "There are {a} fish in the bowl. The cat eats {b}. How many left?",
        ],
    },
    "pixel_world": {
        "ru": [
            "У игрока {a} блоков. Он сломал {b}. Сколько осталось?",
            "В инвентаре {a} пикселей. Добавили {b}. Сколько всего?",
            "Построили {a} кубов, потом ещё {b}. Сколько стало?",
        ],
        "uk": [
            "У гравця {a} блоків. Він зламав {b}. Скільки залишилося?",
            "В інвентарі {a} пікселів. Додали {b}. Скільки всього?",
            "Побудували {a} кубів, потім ще {b}. Скільки стало?",
        ],
        "en": [
            "The player has {a} blocks. He breaks {b}. How many are left?",
            "There are {a} pixels in the inventory. Added {b}. How many total?",
            "Built {a} cubes, then {b} more. How many now?",
        ],
    },
    "animals": {
        "ru": [
            "В лесу {a} зайцев. Прибежало ещё {b}. Сколько стало?",
            "У медведя было {a} ягод. Он съел {b}. Сколько осталось?",
            "На поляне {a} белок. Убежали {b}. Сколько осталось?",
        ],
        "uk": [
            "У лісі {a} зайців. Прибігло ще {b}. Скільки стало?",
            "У ведмедя було {a} ягід. Він з'їв {b}. Скільки залишилося?",
            "На галявині {a} білок. Втекли {b}. Скільки залишилося?",
        ],
        "en": [
            "There are {a} hares in the forest. {b} more came. How many now?",
            "A bear had {a} berries. He ate {b}. How many left?",
            "There are {a} squirrels. {b} ran away. How many left?",
        ],
    },
    "pirates": {
        "ru": [
            "Пираты нашли {a} сокровищ. Потеряли {b}. Сколько осталось?",
            "На корабле {a} пиратов. Присоединились {b}. Сколько стало?",
            "В сундуке {a} золотых монет. Добавили {b}. Сколько всего?",
        ],
        "uk": [
            "Пірати знайшли {a} скарбів. Загубили {b}. Скільки залишилося?",
            "На кораблі {a} піратів. Приєдналися {b}. Скільки стало?",
            "У скрині {a} золотих монет. Додали {b}. Скільки всього?",
        ],
        "en": [
            "Pirates found {a} treasures. Lost {b}. How many left?",
            "There are {a} pirates on the ship. {b} more joined. How many now?",
            "In the chest {a} gold coins. Added {b}. How many total?",
        ],
    },
    "princesses": {
        "ru": [
            "У принцессы {a} платьев. Ей подарили ещё {b}. Сколько стало?",
            "В замке {a} комнат. Открыли ещё {b}. Сколько комнат?",
            "На балу танцевали {a} гостей. Ушли {b}. Сколько осталось?",
        ],
        "uk": [
            "У принцеси {a} суконь. Їй подарували ще {b}. Скільки стало?",
            "У замку {a} кімнат. Відкрили ще {b}. Скільки кімнат?",
            "На балу танцювали {a} гостей. Пішли {b}. Скільки залишилося?",
        ],
        "en": [
            "A princess has {a} dresses. She got {b} more. How many now?",
            "The castle has {a} rooms. {b} more opened. How many rooms?",
            "At the ball {a} guests danced. {b} left. How many stayed?",
        ],
    },
    "robots": {
        "ru": [
            "У робота {a} шестерёнок. Добавили {b}. Сколько стало?",
            "На заводе {a} роботов. Собрали ещё {b}. Сколько всего?",
            "Робот выполнил {a} заданий. Осталось {b}. Сколько было?",
        ],
        "uk": [
            "У робота {a} шестерень. Додали {b}. Скільки стало?",
            "На заводі {a} роботів. Зібрали ще {b}. Скільки всього?",
            "Робот виконав {a} завдань. Залишилося {b}. Скільки було?",
        ],
        "en": [
            "A robot has {a} gears. Added {b}. How many now?",
            "The factory has {a} robots. Built {b} more. How many total?",
            "A robot did {a} tasks. {b} remain. How many total?",
        ],
    },
    "underwater": {
        "ru": [
            "В море плавает {a} рыб. Приплыли ещё {b}. Сколько стало?",
            "Осьминог нашёл {a} ракушек. Потерял {b}. Сколько осталось?",
            "На дне {a} кораллов. Выросло ещё {b}. Сколько всего?",
        ],
        "uk": [
            "У морі плаває {a} риб. Припливли ще {b}. Скільки стало?",
            "Восьминіг знайшов {a} мушель. Загубив {b}. Скільки залишилося?",
            "На дні {a} коралів. Виросло ще {b}. Скільки всього?",
        ],
        "en": [
            "{a} fish swim in the sea. {b} more came. How many now?",
            "An octopus found {a} shells. Lost {b}. How many left?",
            "There are {a} corals. {b} more grew. How many total?",
        ],
    },
}


def _get_topic_word(topic: str, language: str = "ru") -> str:
    """Get a topic word. NEVER returns a generic placeholder — returns '' if nothing found."""
    if topic and topic not in ("general", "custom", ""):
        tw = random_word(topic, language)
        if tw:
            return tw
    # No fallback to 'предмет'/'object' — return empty string
    return ""


def _pluralize(word: str) -> str:
    if not word:
        return word
    return word + "и" if word[-1] in "ая" else word + "ы" if word[-1] == "ь" else word + "а"


def inject_into_math(
    question: str,
    answer: str,
    topic: str,
    language: str,
    card_type: str,
    seed: int,
) -> Tuple[str, str]:
    if topic in ("general", "custom", ""):
        return question, answer
    # Comparison cards (math_compare) have non-numeric answers (> < =)
    # — just append topic word suffix instead of replacing the question
    tw = _get_topic_word(topic, language)
    if card_type == "math_compare":
        if tw:
            question = f"{question} ({tw})"
        return question, answer
    if topic not in _MATH_WORD_PROBLEMS:
        if tw:
            question = f"{question} ({tw})"
        return question, answer
    topics_dict = _MATH_WORD_PROBLEMS[topic]
    lang_pool = topics_dict.get(language, topics_dict.get(list(topics_dict.keys())[0], []))
    if not lang_pool:
        return question, answer
    template = lang_pool[seed % len(lang_pool)]
    rng = random.Random(seed)
    a = rng.randint(2, 20)
    b = rng.randint(1, 9)
    if "+" in answer or " - " in question or "остал" in question or "залиши" in question:
        result = a - b
        if result < 0:
            result = abs(result)
    elif "больш" in question or "більш" in question or "more" in question.lower() or "farther" in question.lower():
        result = abs(a - b)
    else:
        result = a + b
    filled = template.format(a=a, b=b, topic_word=tw if tw else topic)
    return filled, str(result)


def inject_into_preschool(
    question: str,
    answer: str,
    topic: str,
    language: str,
    card_type: str,
    seed: int,
) -> Tuple[str, str]:
    if topic in ("general", "custom", ""):
        return question, answer
    tw = _get_topic_word(topic, language)
    if not tw:
        return question, answer
    if "{topic_word}" in question:
        question = question.replace("{topic_word}", tw)
    prefix_templates = _INJECTION_TEMPLATES.get("preschool", {})
    templates = prefix_templates.get(language, prefix_templates.get("ru", []))
    if templates:
        prefix = templates[seed % len(templates)]
        prefix = prefix.replace("{topic_word}", tw)
        return f"{prefix} {question}", answer
    return f"{question} ({tw})", answer


def inject_into_english(
    question: str,
    answer: str,
    topic: str,
    language: str,
    card_type: str,
    seed: int,
) -> Tuple[str, str]:
    if topic in ("general", "custom", ""):
        return question, answer
    tw = random_word(topic, "en") if topic else ""
    if not tw:
        return question, answer
    if "{topic_word}" in question:
        question = question.replace("{topic_word}", tw)
    else:
        separate = " " if question and not question.endswith(" ") else ""
        question = f"{question}{separate}({tw})"
    return question, answer


def inject_into_logic(
    question: str,
    answer: str,
    topic: str,
    language: str,
    card_type: str,
    seed: int,
) -> Tuple[str, str]:
    if topic in ("general", "custom", ""):
        return question, answer
    tw = _get_topic_word(topic, language)
    if not tw:
        return question, answer
    if "{topic_word}" in question:
        question = question.replace("{topic_word}", tw)
    separate = " " if question and not question.endswith(" ") else ""
    question = f"{question}{separate}({tw})"
    return question, answer


def inject_into_reading(
    question: str,
    answer: str,
    topic: str,
    language: str,
    card_type: str,
    seed: int,
) -> Tuple[str, str]:
    return question, answer


_SUBJECT_MAP = {
    "math_addition": "math",
    "math_subtraction": "math",
    "math_multiplication": "math",
    "math_division": "math",
    "math_compare": "math",
    "missing_number": "math",
    "math_word": "math",
    "math_scheme": "math",
    "pattern": "logic",
    "odd_one_out": "logic",
    "sequence": "logic",
    "analogy": "logic",
    "maze": "logic",
    "labyrinth": "logic",
    "find_path": "logic",
    "puzzle_lines": "logic",
    "table_fill": "logic",
    "detective": "logic",
    "deduction": "logic",
    "sudoku": "logic",
    "crossword": "logic",
    "story_read": "reading",
    "question_answer": "reading",
    "find_word": "reading",
    "main_idea": "reading",
    "character_guess": "reading",
    "retelling": "reading",
    "make_plan": "reading",
    "synonym_find": "reading",
    "discussion": "reading",
    "count_trace": "preschool",
    "shape_find": "preschool",
    "letter_trace": "preschool",
    "same_shape": "preschool",
    "coloring": "preschool",
    "color_find": "preschool",
    "find_shadow": "preschool",
    "sound_letter": "preschool",
    "letter_trace_en": "english",
    "abc_match": "english",
    "word_picture": "english",
    "color_find_en": "english",
    "count_en": "english",
    "match_pairs_en": "english",
    "read_short_en": "english",
    "question_answer_en": "english",
    "fill_gap_en": "english",
    "correct_form_en": "english",
    "sentence_build": "english",
    "true_false_en": "english",
    "vocab_match": "english",
}


def subject_for(card_type: str) -> str:
    return _SUBJECT_MAP.get(card_type, "math")


def inject_topic(
    question: str,
    answer: str,
    topic: str,
    language: str,
    card_type: str,
    seed: int = 0,
) -> Tuple[str, str]:
    if topic in ("general", "custom", ""):
        return question, answer
    subject = _SUBJECT_MAP.get(card_type, "math")
    if subject == "math":
        return inject_into_math(question, answer, topic, language, card_type, seed)
    elif subject == "preschool":
        return inject_into_preschool(question, answer, topic, language, card_type, seed)
    elif subject == "english":
        return inject_into_english(question, answer, topic, language, card_type, seed)
    elif subject == "logic":
        return inject_into_logic(question, answer, topic, language, card_type, seed)
    elif subject == "reading":
        return inject_into_reading(question, answer, topic, language, card_type, seed)
    return question, answer


INJECTABLE_TYPES = list(_SUBJECT_MAP.keys())
