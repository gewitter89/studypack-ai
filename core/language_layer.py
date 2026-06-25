import logging
from typing import Optional

logger = logging.getLogger(__name__)

_INSTRUCTIONS = {
    "count": {"ru": "Посчитай", "uk": "Порахуй", "en": "Count"},
    "find": {"ru": "Найди", "uk": "Знайди", "en": "Find"},
    "match": {"ru": "Соедини", "uk": "З'єднай", "en": "Match"},
    "read": {"ru": "Прочитай", "uk": "Прочитай", "en": "Read"},
    "write": {"ru": "Запиши", "uk": "Запиши", "en": "Write"},
    "circle": {"ru": "Обведи", "uk": "Обведи", "en": "Circle"},
    "continue_pattern": {"ru": "Продолжи ряд", "uk": "Продовж ряд", "en": "Continue the pattern"},
    "answer": {"ru": "Ответь на вопросы", "uk": "Дай відповіді на запитання", "en": "Answer the questions"},
    "solve": {"ru": "Реши", "uk": "Розв'яжи", "en": "Solve"},
    "draw": {"ru": "Нарисуй", "uk": "Намалюй", "en": "Draw"},
    "color": {"ru": "Раскрась", "uk": "Розфарбуй", "en": "Colour"},
    "connect": {"ru": "Проведи линию", "uk": "Проведи лінію", "en": "Draw a line"},
    "choose": {"ru": "Выбери", "uk": "Обери", "en": "Choose"},
    "guess": {"ru": "Угадай", "uk": "Відгадай", "en": "Guess"},
    "think": {"ru": "Подумай", "uk": "Поміркуй", "en": "Think"},
    "repeat": {"ru": "Повтори", "uk": "Повтори", "en": "Repeat"},
    "listen": {"ru": "Послушай", "uk": "Послухай", "en": "Listen"},
    "look": {"ru": "Посмотри", "uk": "Подивись", "en": "Look"},
    "help": {"ru": "Помоги", "uk": "Допоможи", "en": "Help"},
    "check": {"ru": "Проверь", "uk": "Перевір", "en": "Check"},
}

_VERBS = {
    "has": {"ru": "есть", "uk": "є", "en": "has"},
    "likes": {"ru": "любит", "uk": "любить", "en": "likes"},
    "found": {"ru": "нашёл", "uk": "знайшов", "en": "found"},
    "went": {"ru": "пошёл", "uk": "пішов", "en": "went"},
    "flew": {"ru": "полетел", "uk": "полетів", "en": "flew"},
    "swam": {"ru": "поплыл", "uk": "поплив", "en": "swam"},
    "saw": {"ru": "увидел", "uk": "побачив", "en": "saw"},
    "ran": {"ru": "побежал", "uk": "побіг", "en": "ran"},
    "jumped": {"ru": "прыгнул", "uk": "стрибнув", "en": "jumped"},
    "said": {"ru": "сказал", "uk": "сказав", "en": "said"},
}

_GRAMMAR_MARKERS = {
    "in": {"ru": "в", "uk": "у", "en": "in"},
    "on": {"ru": "на", "uk": "на", "en": "on"},
    "under": {"ru": "под", "uk": "під", "en": "under"},
    "above": {"ru": "над", "uk": "над", "en": "above"},
    "left": {"ru": "слева", "uk": "зліва", "en": "on the left"},
    "right": {"ru": "справа", "uk": "справа", "en": "on the right"},
    "and": {"ru": "и", "uk": "і", "en": "and"},
    "or": {"ru": "или", "uk": "або", "en": "or"},
    "how_many": {"ru": "Сколько", "uk": "Скільки", "en": "How many"},
    "which": {"ru": "Какой", "uk": "Який", "en": "Which"},
    "who": {"ru": "Кто", "uk": "Хто", "en": "Who"},
    "what": {"ru": "Что", "uk": "Що", "en": "What"},
    "where": {"ru": "Где", "uk": "Де", "en": "Where"},
}

_GREETINGS = {
    "well_done": {"ru": "Молодец!", "uk": "Молодець!", "en": "Well done!"},
    "great_job": {"ru": "Отлично!", "uk": "Чудово!", "en": "Great job!"},
    "keep_going": {"ru": "Продолжай в том же духе!", "uk": "Продовжуй у тому ж дусі!", "en": "Keep it up!"},
}

_RU_WORDS_IN_UK = frozenset([
    "посчитай", "найди", "соедини", "реши", "ответь",
    "прочитай слова и соедини", "какой", "какая", "какие",
    "нарисуй", "раскрась", "пожалуйста", "угадай", "подумай",
])

_UK_WORDS_IN_RU = frozenset([
    "порахуй", "знайди", "з'єднай", "розв'яжи", "дай відповіді",
    "намалюй", "розфарбуй", "будь ласка", "відгадай", "поміркуй",
])

_TECH_WORDS = frozenset([
    "ai", "prompt", "model", "openrouter", "json",
    "generated", "нейросеть", "сгенерировано", "алгоритм",
    "neural", "dataset", "api", "gpt", "completion",
])


def get(key: str, language: str = "ru") -> str:
    if key in _INSTRUCTIONS:
        return _INSTRUCTIONS[key].get(language, _INSTRUCTIONS[key].get("ru", key))
    if key in _VERBS:
        return _VERBS[key].get(language, _VERBS[key].get("ru", key))
    if key in _GRAMMAR_MARKERS:
        return _GRAMMAR_MARKERS[key].get(language, _GRAMMAR_MARKERS[key].get("ru", key))
    if key in _GREETINGS:
        return _GREETINGS[key].get(language, _GREETINGS[key].get("ru", key))
    return key


def instruction(key: str, language: str = "ru") -> str:
    return get(key, language)


def verb(key: str, language: str = "ru") -> str:
    return get(key, language)


def grammar(key: str, language: str = "ru") -> str:
    return get(key, language)


def greeting(key: str, language: str = "ru") -> str:
    return get(key, language)


def make_question(question_template: str, topic_word: str, language: str = "ru") -> str:
    return question_template.replace("{topic}", topic_word)


def check_language_mismatch(text: str, language: str) -> list:
    import re
    text_lower = text.lower()
    issues = []
    if language == "uk":
        for word in _RU_WORDS_IN_UK:
            if re.search(r'\b' + re.escape(word) + r'\b', text_lower):
                issues.append(f"RU word '{word}' in UK text")
    elif language == "ru":
        for word in _UK_WORDS_IN_RU:
            if re.search(r'\b' + re.escape(word) + r'\b', text_lower):
                issues.append(f"UK word '{word}' in RU text")
    return issues


def check_tech_words(text: str) -> list:
    text_lower = text.lower()
    return [w for w in _TECH_WORDS if w in text_lower]


def list_instr_keys() -> list:
    return list(_INSTRUCTIONS.keys())
