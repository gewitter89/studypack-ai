from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Dict


@dataclass
class Achievement:
    id: str
    title: Dict[str, str]
    icon: str
    description: Dict[str, str] = field(default_factory=dict)
    unlocked: bool = False


@dataclass
class StarReward:
    page_number: int
    earned: bool = False
    max_stars: int = 3


@dataclass
class XPProgress:
    current_xp: int = 0
    level: int = 1
    xp_to_next: int = 100

    def add_xp(self, amount: int) -> bool:
        self.current_xp += amount
        leveled = False
        while self.current_xp >= self.xp_to_next:
            self.current_xp -= self.xp_to_next
            self.level += 1
            self.xp_to_next = int(self.xp_to_next * 1.3)
            leveled = True
        return leveled


ACHIEVEMENTS = {
    "first_pack": Achievement(
        id="first_pack",
        title={"uk": "Перший пакунок", "ru": "Первый пакунок", "en": "First Pack"},
        icon="🏅",
        description={
            "uk": "Розпочав свій перший StudyPack!",
            "ru": "Начал свой первый StudyPack!",
            "en": "Started your first StudyPack!",
        },
    ),
    "math_master": Achievement(
        id="math_master",
        title={"uk": "Мат-геній", "ru": "Мат-гений", "en": "Math Genius"},
        icon="🧮",
        description={
            "uk": "Вирішив 10+ математичних завдань",
            "ru": "Решил 10+ математических заданий",
            "en": "Solved 10+ math problems",
        },
    ),
    "logic_king": Achievement(
        id="logic_king",
        title={"uk": "Логік-мастер", "ru": "Логик-мастер", "en": "Logic Master"},
        icon="🧩",
        description={
            "uk": "Проходив лабіринти та судоку",
            "ru": "Проходил лабиринты и судоку",
            "en": "Completed mazes and sudoku",
        },
    ),
    "reader_star": Achievement(
        id="reader_star",
        title={"uk": "Зірка читання", "ru": "Звезда чтения", "en": "Reading Star"},
        icon="📚",
        description={
            "uk": "Прочитав 5+ текстів",
            "ru": "Прочитал 5+ текстов",
            "en": "Read 5+ texts",
        },
    ),
    "creative_soul": Achievement(
        id="creative_soul",
        title={"uk": "Креативна душа", "ru": "Креативная душа", "en": "Creative Soul"},
        icon="🎨",
        description={
            "uk": "Розфарбував 5+ картинок",
            "ru": "Раскрасил 5+ картинок",
            "en": "Colored 5+ pictures",
        },
    ),
    "full_completion": Achievement(
        id="full_completion",
        title={"uk": "Абсолют", "ru": "Абсолют", "en": "Absolute"},
        icon="💎",
        description={
            "uk": "Завершив увесь пакунок до кінця",
            "ru": "Завершил весь пакунок до конца",
            "en": "Finished the entire pack",
        },
    ),
    "speed_demon": Achievement(
        id="speed_demon",
        title={"uk": "Блискавка", "ru": "Молния", "en": "Lightning"},
        icon="⚡",
        description={
            "uk": "Все завдання на сторінці за менше 3 хвилин",
            "ru": "Все задания на странице за менее 3 минуты",
            "en": "Finished all page tasks in under 3 minutes",
        },
    ),
    "perfect_score": Achievement(
        id="perfect_score",
        title={"uk": "Ідеально!", "ru": "Идеально!", "en": "Perfect!"},
        icon="🌟",
        description={
            "uk": "100% правильних на сторінці",
            "ru": "100% правильных на странице",
            "en": "100% correct on a page",
        },
    ),
    "explorer": Achievement(
        id="explorer",
        title={"uk": "Дослідник", "ru": "Исследователь", "en": "Explorer"},
        icon="🔍",
        description={
            "uk": "Спробував 4+ різних типів завдань",
            "ru": "Попробовал 4+ разных типов заданий",
            "en": "Tried 4+ different task types",
        },
    ),
    "persistence": Achievement(
        id="persistence",
        title={"uk": "Наполегливий", "ru": "Настойчивый", "en": "Persistent"},
        icon="💪",
        description={
            "uk": "Пройшов 8+ сторінок",
            "ru": "Прошёл 8+ страниц",
            "en": "Completed 8+ pages",
        },
    ),
}


def compute_achievements(pages_data: List[Dict], lang: str = "uk") -> List[Achievement]:
    unlocked = []
    if pages_data:
        a = Achievement(**ACHIEVEMENTS["first_pack"].__dict__)
        a.unlocked = True
        unlocked.append(a)

    types_done = set()
    math_tasks = 0
    logic_tasks = 0
    reading_tasks = 0
    creative_tasks = 0
    for page in pages_data:
        p_type = page.get("page_type", "")
        types_done.add(p_type)
        for t in page.get("tasks", []):
            tt = t.get("type", "")
            if "math" in tt or p_type in ("math_addition", "math_subtraction", "math_compare"):
                math_tasks += 1
            elif tt in ("logic", "maze", "sudoku", "find_differences", "crossword"):
                logic_tasks += 1
            elif "reading" in tt or p_type in ("story_read", "find_word", "word_search"):
                reading_tasks += 1
            elif tt in ("creative", "coloring", "drawing", "color_by_number"):
                creative_tasks += 1

    if math_tasks >= 10:
        a = Achievement(**ACHIEVEMENTS["math_master"].__dict__)
        a.unlocked = True
        unlocked.append(a)
    if logic_tasks >= 5:
        a = Achievement(**ACHIEVEMENTS["logic_king"].__dict__)
        a.unlocked = True
        unlocked.append(a)
    if reading_tasks >= 5:
        a = Achievement(**ACHIEVEMENTS["reader_star"].__dict__)
        a.unlocked = True
        unlocked.append(a)
    if creative_tasks >= 5:
        a = Achievement(**ACHIEVEMENTS["creative_soul"].__dict__)
        a.unlocked = True
        unlocked.append(a)
    if len(types_done) >= 4:
        a = Achievement(**ACHIEVEMENTS["explorer"].__dict__)
        a.unlocked = True
        unlocked.append(a)
    if len(pages_data) >= 8:
        a = Achievement(**ACHIEVEMENTS["persistence"].__dict__)
        a.unlocked = True
        unlocked.append(a)

    total = len(pages_data)
    if total >= 3:
        a = Achievement(**ACHIEVEMENTS["full_completion"].__dict__)
        a.unlocked = True
        unlocked.append(a)
    return unlocked


def compute_stars(pages_data: List[Dict]) -> List[StarReward]:
    stars = []
    for i, page in enumerate(pages_data, start=1):
        p_type = page.get("page_type", "")
        is_visual = p_type in ("color_by_number", "maze", "find_differences", "sudoku", "crossword")
        is_creative = p_type in ("coloring", "creative")
        sr = StarReward(page_number=i)
        if is_visual or is_creative:
            sr.earned = True
        stars.append(sr)
    return stars


def compute_xp(pages_data: List[Dict]) -> XPProgress:
    xp = XPProgress()
    for page in pages_data:
        task_xp = len(page.get("tasks", [])) * 10
        xp.add_xp(task_xp)
    return xp


MOTIVATIONAL_QUOTES = {
    "uk": [
        "Ти молодець! Так тримати!",
        "Кожне завдання — крок до успіху!",
        "Вірю в тебе! У тебе все вийде!",
        "Твоя праця дає плоди!",
        "Ти вчишся швидше, ніж здається!",
        "Супер! Ще трішки — і наступний рівень!",
    ],
    "ru": [
        "Ты молодец! Так держать!",
        "Каждое задание — шаг к успеху!",
        "Верю в тебя! У тебя всё получится!",
        "Твой труд даёт плоды!",
        "Ты учишься быстрее, чем кажется!",
        "Супер! Ещё чуть-чуть — и следующий уровень!",
    ],
    "en": [
        "Great job! Keep going!",
        "Each task is a step toward success!",
        "I believe in you! You can do it!",
        "Your hard work is paying off!",
        "You learn faster than you think!",
        "Awesome! Almost at the next level!",
    ],
}


def get_quote(lang: str, index: int) -> str:
    if lang in ("uk", "uk+en"):
        pool = MOTIVATIONAL_QUOTES["uk"]
    elif lang == "en":
        pool = MOTIVATIONAL_QUOTES["en"]
    else:
        pool = MOTIVATIONAL_QUOTES["ru"]
    return pool[index % len(pool)]
