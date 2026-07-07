import random
from typing import List, Dict, Any, Tuple


def _uk(lang: str) -> bool:
    return lang in ("uk", "uk+en")


def sticker_reward_page(pack_data: Dict[str, Any]) -> Dict[str, Any]:
    lang = pack_data.get("language", "uk")
    is_uk = _uk(lang)

    pages_data = [p for p in pack_data.get("pages", []) if p.get("page_type") != "answers"]
    num_stickers = min(len(pages_data), 12)

    tasks = []
    for i in range(num_stickers):
        tasks.append({
            "type": "sticker",
            "question": f"{'Завдання' if is_uk else 'Задание'} {i + 1}: [наклейка]",
            "options": [],
            "answer_space": False,
            "answer": "",
        })

    title = "🌟 Твої нагороди 🌟" if is_uk else "🌟 Твои награды 🌟"
    instruction = (
        "За кожне виконане завдання наклей сюди зірочку або смішну наліпку!"
        if is_uk
        else "За каждое выполненное задание наклей сюда звёздочку или смешную наклейку!"
    )

    return {
        "page_number": 9990,
        "page_type": "sticker_rewards",
        "title": title,
        "instruction": instruction,
        "tasks": tasks,
    }


def surprise_bonus_page(pack_data: Dict[str, Any], page_type: str = "random") -> Dict[str, Any]:
    lang = pack_data.get("language", "uk")
    is_uk = _uk(lang)

    if page_type == "random":
        page_type = random.choice(["coloring", "maze", "find_differences", "connect_dots"])

    if page_type == "coloring":
        return _bonus_coloring(lang, is_uk)
    elif page_type == "maze":
        return _bonus_maze(lang, is_uk)
    elif page_type == "find_differences":
        return _bonus_find_differences(lang, is_uk)
    elif page_type == "connect_dots":
        return _bonus_connect_dots(lang, is_uk)
    else:
        return _bonus_coloring(lang, is_uk)


def _bonus_coloring(lang: str, is_uk: bool) -> Dict[str, Any]:
    tasks = [{
        "type": "creative",
        "question": (
            "Розфарбуй цей малюнок своїми улюбленими кольорами!"
            if is_uk
            else "Раскрась этот рисунок своими любимыми цветами!"
        ),
        "options": [],
        "answer_space": False,
        "answer": "Перевіряється дорослим" if is_uk else "Проверяется взрослым",
    }]
    return {
        "page_number": 9991,
        "page_type": "bonus_coloring",
        "title": "🎨 Бонус: Розмальовка! 🎨" if is_uk else "🎨 Бонус: Раскраска! 🎨",
        "instruction": (
            "Це бонусна сторінка! Розфарбуй та покажи батькам."
            if is_uk
            else "Это бонусная страница! Раскрась и покажи родителям."
        ),
        "tasks": tasks,
    }


def _bonus_maze(lang: str, is_uk: bool) -> Dict[str, Any]:
    tasks = [{
        "type": "logic",
        "question": (
            "Проведи героя через лабіринт до фінішу!"
            if is_uk
            else "Проведи героя через лабиринт к финишу!"
        ),
        "options": [],
        "answer_space": False,
        "answer": "",
    }]
    return {
        "page_number": 9992,
        "page_type": "bonus_maze",
        "title": "🧩 Бонус: Лабіринт! 🧩" if is_uk else "🧩 Бонус: Лабиринт! 🧩",
        "instruction": (
            "Знайди шлях від старту до фінішу! Не заходь у глухі кути."
            if is_uk
            else "Найди путь от старта до финиша! Не заходи в тупики."
        ),
        "tasks": tasks,
    }


def _bonus_find_differences(lang: str, is_uk: bool) -> Dict[str, Any]:
    tasks = [{
        "type": "logic",
        "question": (
            "Знайди 5 відмінностей між двома картинками!"
            if is_uk
            else "Найди 5 отличий между двумя картинками!"
        ),
        "options": [],
        "answer_space": False,
        "answer": "",
    }]
    return {
        "page_number": 9993,
        "page_type": "bonus_find_differences",
        "title": "🔍 Бонус: Знайди відмінності! 🔍" if is_uk else "🔍 Бонус: Найди отличия! 🔍",
        "instruction": (
            "Уважно подивись на дві картинки і знайди всі відмінності."
            if is_uk
            else "Внимательно посмотри на две картинки и найди все отличия."
        ),
        "tasks": tasks,
    }


def _bonus_connect_dots(lang: str, is_uk: bool) -> Dict[str, Any]:
    tasks = [{
        "type": "creative",
        "question": (
            "З'єднай точки по номерах і дізнайся, хто це!"
            if is_uk
            else "Соедини точки по номерам и узнай, кто это!"
        ),
        "options": [],
        "answer_space": False,
        "answer": "",
    }]
    return {
        "page_number": 9994,
        "page_type": "bonus_connect_dots",
        "title": "✏️ Бонус: З'єднай точки! ✏️" if is_uk else "✏️ Бонус: Соедини точки! ✏️",
        "instruction": (
            "Проведи лінію від 1 до останнього числа і розфарбуй малюнок."
            if is_uk
            else "Проведи линию от 1 до последнего числа и раскрась рисунок."
        ),
        "tasks": tasks,
    }


def secret_code_page(pack_data: Dict[str, Any]) -> Dict[str, Any]:
    lang = pack_data.get("language", "uk")
    is_uk = _uk(lang)

    if is_uk:
        code_map = {"А": "1", "Б": "2", "В": "3", "Г": "4", "Д": "5", "Е": "6", "Є": "7", "Ж": "8", "З": "9"}
        secret_word = "МОЛОДЕЦЬ"
        encoded = " ".join(code_map.get(c, c) for c in secret_word)
        tasks = [{
            "type": "logic",
            "question": f"Розшифруй секретний код! Кожна цифра = буква алфавіту.\n{encoded}\nПідказка: 1=А, 2=Б, 3=В ...",
            "options": [],
            "answer_space": True,
            "answer": secret_word,
        }]
    else:
        code_map = {"А": "1", "Б": "2", "В": "3", "Г": "4", "Д": "5", "Е": "6", "Ё": "7", "Ж": "8", "З": "9"}
        secret_word = "МОЛОДЕЦ"
        encoded = " ".join(code_map.get(c, c) for c in secret_word)
        tasks = [{
            "type": "logic",
            "question": f"Расшифруй секретный код! Каждая цифра = буква алфавита.\n{encoded}\nПодсказка: 1=А, 2=Б, 3=В ...",
            "options": [],
            "answer_space": True,
            "answer": secret_word,
        }]

    return {
        "page_number": 9999,
        "page_type": "secret_code",
        "title": "🔐 Секретний код!" if is_uk else "🔐 Секретный код!",
        "instruction": (
            "Розгадай послання і покажи батькам!"
            if is_uk
            else "Разгадай послание и покажи родителям!"
        ),
        "tasks": tasks,
    }
