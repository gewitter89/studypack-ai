import random
from typing import Dict, Optional, Tuple

MASCOTS: Dict[str, dict] = {
    "bear": {
        "id": "bear",
        "name_uk": "Ведмедик Михась",
        "name_ru": "Медвежонок Михася",
        "emoji": "🐻",
        "subject": "narrator",
        "greeting_uk": [
            "Привіт, {name}! Я — Ведмедик Михась! Сьогодні ми разом {action}!",
            "Вітаю, {name}! Давай разом {action}. Буде весело!",
            "Привіт-привіт, {name}! Я так радий тебе бачити! {action_let}!",
        ],
        "greeting_ru": [
            "Привет, {name}! Я — Медвежонок Михася! Сегодня мы вместе {action}!",
            "Здравствуй, {name}! Давай вместе {action}. Будет весело!",
            "Привет-привет, {name}! Я так рад тебя видеть! {action_let}!",
        ],
        "praise_uk": [
            "Чудово, {name}! Ти справжній геній!",
            "Браво! Ведмедик пишається тобою!",
            "Ого, як гарно! {name} — молодчина!",
            "Так тримати! Ти на правильному шляху!",
        ],
        "praise_ru": [
            "Здорово, {name}! Ты настоящий гений!",
            "Браво! Медвежонок гордится тобой!",
            "Ого, как здорово! {name} — молодец!",
            "Так держать! Ты на правильном пути!",
        ],
        "encourage_uk": [
            "Нічого, {name}, спробуй ще раз!",
            "Не здавайся! У тебе обов'язково вийде!",
            "Це складно, але ти впораєшся!",
        ],
        "encourage_ru": [
            "Ничего, {name}, попробуй ещё раз!",
            "Не сдавайся! У тебя обязательно получится!",
            "Это сложно, но ты справишься!",
        ],
    },
    "panda": {
        "id": "panda",
        "name_uk": "Панда Бамбук",
        "name_ru": "Панда Бамбук",
        "emoji": "🐼",
        "subject": "creative",
        "greeting_uk": [
            "Привіт, {name}! Я — Панда Бамбук! Люблю малювати і {action}!",
            "Хей, {name}! Давай пок{action_ending} разом! Буде яскраво!",
        ],
        "greeting_ru": [
            "Привет, {name}! Я — Панда Бамбук! Люблю рисовать и {action}!",
            "Хей, {name}! Давай по{action_ending} вместе! Будет ярко!",
        ],
        "praise_uk": [
            "Вау, {name}! Це справжній шедевр!",
            "Як красиво! Панда Бамбук аплодує!",
            "Ти — справжній художник!",
        ],
        "praise_ru": [
            "Вау, {name}! Это настоящий шедевр!",
            "Как красиво! Панда Бамбук аплодирует!",
            "Ты — настоящий художник!",
        ],
        "encourage_uk": [
            "Уяви ще раз — і спробуй!",
            "Твоя фантазія — твоя суперсила!",
        ],
        "encourage_ru": [
            "Представь ещё раз — и попробуй!",
            "Твоя фантазия — твоя суперсила!",
        ],
    },
    "hedgehog": {
        "id": "hedgehog",
        "name_uk": "Їжачок Цифрик",
        "name_ru": "Ёжик Цифрик",
        "emoji": "🦔",
        "subject": "math",
        "greeting_uk": [
            "Привіт, {name}! Я — Їжачок Цифрик! Давай рахувати разом!",
            "Вітаю, {name}! Сьогодні ми {action} і будемо розумнішими!",
        ],
        "greeting_ru": [
            "Привет, {name}! Я — Ёжик Цифрик! Давай считать вместе!",
            "Здравствуй, {name}! Сегодня мы {action} и станем умнее!",
        ],
        "praise_uk": [
            "Браво, {name}! Правильна відповідь!",
            "Ти — математичний геній!",
            "Цифрик пишається! Все правильно!",
        ],
        "praise_ru": [
            "Браво, {name}! Правильный ответ!",
            "Ты — математический гений!",
            "Цифрик гордится! Всё правильно!",
        ],
        "encourage_uk": [
            "Порахуй ще раз — вийде!",
            "Поміркуй уважніше, {name}!",
        ],
        "encourage_ru": [
            "Посчитай ещё раз — выйдет!",
            "Подумай внимательнее, {name}!",
        ],
    },
    "elephant": {
        "id": "elephant",
        "name_uk": "Слоненко Читалко",
        "name_ru": "Слонёнок Читалка",
        "emoji": "🐘",
        "subject": "reading",
        "greeting_uk": [
            "Привіт, {name}! Я — Слоненко Читалко! Люблю читати і тобі покажу!",
            "Вітаю, {name}! Сьогодні ми разом {action}!",
        ],
        "greeting_ru": [
            "Привет, {name}! Я — Слонёнок Читалка! Люблю читать и тебе покажу!",
            "Здравствуй, {name}! Сегодня мы вместе {action}!",
        ],
        "praise_uk": [
            "Чудово, {name}! Ти прекрасно читаєш!",
            "Слоненко Читалко вражений!",
            "Ти зрозумів текст! Молодець!",
        ],
        "praise_ru": [
            "Отлично, {name}! Ты прекрасно читаешь!",
            "Слонёнок Читалка впечатлён!",
            "Ты понял текст! Молодец!",
        ],
        "encourage_uk": [
            "Прочитай ще раз уважніше!",
            "Слоненко вірить у тебе!",
        ],
        "encourage_ru": [
            "Прочитай ещё раз внимательнее!",
            "Слонёнок верит в тебя!",
        ],
    },
    "bird": {
        "id": "bird",
        "name_uk": "Пташка Логіка",
        "name_ru": "Пташка Логика",
        "emoji": "🐦",
        "subject": "logic",
        "greeting_uk": [
            "Привіт, {name}! Я — Пташка Логіка! Давай разом {action}!",
            "Тві-тві, {name}! Сьогодні в нас цікаві загадки!",
        ],
        "greeting_ru": [
            "Привет, {name}! Я — Пташка Логика! Давай вместе {action}!",
            "Тви-тви, {name}! Сегодня у нас интересные загадки!",
        ],
        "praise_uk": [
            "Браво, {name}! Ти розгадав загадку!",
            "Пташка Логіка щаслива! Правильно!",
            "Ти — справжній детектив!",
        ],
        "praise_ru": [
            "Браво, {name}! Ты разгадал загадку!",
            "Пташка Логика счастлива! Правильно!",
            "Ты — настоящий детектив!",
        ],
        "encourage_uk": [
            "Подумай ще трішечки!",
            "Пташка підказує: спробуй з іншого боку!",
        ],
        "encourage_ru": [
            "Подумай ещё немножко!",
            "Пташка подсказывает: попробуй с другой стороны!",
        ],
    },
}

_SUBJECT_TO_MASCOT = {
    "math": "hedgehog",
    "reading": "elephant",
    "logic": "bird",
    "preschool": "bear",
    "creative": "panda",
    "english": "panda",
    "narrator": "bear",
}

_TOPIC_TO_MASCOT = {
    "dinosaurs": "bear",
    "space": "bird",
    "underwater": "panda",
    "ocean": "panda",
    "pirates": "bear",
    "robots": "bird",
    "magic_forest": "panda",
    "princesses": "elephant",
    "superheroes": "bear",
    "cats": "panda",
    "dogs": "bear",
    "farm": "elephant",
    "animals": "bear",
}


def get_mascot(subject: str = "", topic: str = "") -> dict:
    mascot_id = _TOPIC_TO_MASCOT.get(topic)
    if not mascot_id:
        mascot_id = _SUBJECT_TO_MASCOT.get(subject, "bear")
    return MASCOTS.get(mascot_id, MASCOTS["bear"])


def get_greeting(mascot: dict, child_name: str, language: str, subject: str = "") -> str:
    uk = language in ("uk", "uk+en")
    key = "greeting_uk" if uk else "greeting_ru"
    templates = mascot.get(key, [])
    if not templates:
        key_fallback = "greeting_ru" if uk else "greeting_uk"
        templates = mascot.get(key_fallback, ["Привіт, {name}!"])
    name = child_name if child_name else ("друг" if uk else "друг")

    if subject == "math" or "math" in str(mascot.get("subject", "")):
        action = "розв'язувати задачки" if uk else "решать задачки"
        action_let = "Давай рахувати" if uk else "Давай считать"
        action_ending = "рахувати" if uk else "считать"
    elif subject == "reading":
        action = "читати цікаві історії" if uk else "читать интересные истории"
        action_let = "Давай читати" if uk else "Давай читать"
        action_ending = "читати" if uk else "читать"
    elif subject == "logic":
        action = "розгадувати загадки" if uk else "разгадывать загадки"
        action_let = "Давай думати разом" if uk else "Давай думать вместе"
        action_ending = "думати" if uk else "думать"
    else:
        action = "вчитися і грати" if uk else "учиться и играть"
        action_let = "Давай вчитися разом" if uk else "Давай учиться вместе"
        action_ending = "вчитися" if uk else "учиться"

    template = random.choice(templates)
    return template.format(name=name, action=action, action_let=action_let, action_ending=action_ending)


def get_praise(mascot: dict, child_name: str, language: str) -> str:
    uk = language in ("uk", "uk+en")
    key = "praise_uk" if uk else "praise_ru"
    templates = mascot.get(key, [])
    if not templates:
        key_fallback = "praise_ru" if uk else "praise_uk"
        templates = mascot.get(key_fallback, ["Молодець!"])
    name = child_name if child_name else ("друг" if uk else "друг")
    return random.choice(templates).format(name=name)


def get_encouragement(mascot: dict, child_name: str, language: str) -> str:
    uk = language in ("uk", "uk+en")
    key = "encourage_uk" if uk else "encourage_ru"
    templates = mascot.get(key, [])
    if not templates:
        key_fallback = "encourage_ru" if uk else "encourage_uk"
        templates = mascot.get(key_fallback, ["Спробуй ще раз!"])
    name = child_name if child_name else ("друг" if uk else "друг")
    return random.choice(templates).format(name=name)


def format_cover_greeting(child_name: str, topic: str, subject: str, language: str) -> str:
    uk = language in ("uk", "uk+en")
    mascot = get_mascot(subject, topic)
    return get_greeting(mascot, child_name, language, subject)


def get_answers_heading(mascot: dict, child_name: str, language: str) -> str:
    uk = language in ("uk", "uk+en")
    if uk:
        return f"{mascot['emoji']} {get_praise(mascot, child_name, language)} Ось правильні відповіді для перевірки."
    return f"{mascot['emoji']} {get_praise(mascot, child_name, language)} Вот правильные ответы для проверки."
