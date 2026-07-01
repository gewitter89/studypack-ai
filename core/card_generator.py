import logging
import os
import random
from typing import Dict, Any, List

from core.cards.card_registry import registry
from core.cards.base import CardTemplate, CardResult
from core.deterministic_generators.math_generator import DeterministicMathGenerator
from core.deterministic_generators.word_search_generator import SimpleWordSearch
from core.deterministic_generators.maze_generator import MazeGenerator
from core.difficulty import get_params

logger = logging.getLogger(__name__)


GENERATOR_CLASSES = {}
try:
    from core.cards.math_cards import MathAdditionGenerator, MathSubtractionGenerator, MathCompareGenerator
    GENERATOR_CLASSES = {
        "math_addition": MathAdditionGenerator,
        "math_subtraction": MathSubtractionGenerator,
        "math_compare": MathCompareGenerator,
    }
except ImportError:
    logger.warning("Card generator classes not available")


def _make_template_for_id(cid: str, difficulty: str, age: int, language: str = "ru") -> CardTemplate:
    from core.cards.base import CardTemplate
    defaults = {
        "math_addition": ("Сложение", "math", 5, 10, "easy"),
        "math_subtraction": ("Вычитание", "math", 5, 10, "easy"),
        "math_compare": ("Сравнение", "math", 5, 10, "easy"),
        "math_multiplication": ("Умножение", "math", 7, 10, "medium"),
        "math_division": ("Деление", "math", 7, 10, "hard"),
        "missing_number": ("Пропущенное число", "math", 5, 10, "easy"),
        "math_word": ("Задачи", "math", 6, 10, "medium"),
        "maze": ("Лабиринт", "logic", 4, 10, "easy"),
        "labyrinth": ("Лабиринт", "logic", 4, 10, "easy"),
        "find_path": ("Найди путь", "logic", 4, 10, "easy"),
        "puzzle_lines": ("Головоломка", "logic", 5, 10, "easy"),
        "pattern": ("Закономерности", "logic", 5, 10, "easy"),
        "odd_one_out": ("Лишнее", "logic", 4, 10, "easy"),
        "sequence": ("Последовательность", "logic", 5, 10, "medium"),
        "story_read": ("Чтение", "reading", 5, 10, "easy"),
        "question_answer": ("Вопросы", "reading", 5, 10, "easy"),
        "find_word": ("Найди слово", "reading", 5, 10, "easy"),
        "count_trace": ("Счёт", "preschool", 4, 6, "easy"),
        "shape_find": ("Фигуры", "preschool", 4, 6, "easy"),
        "letter_trace": ("Буквы", "preschool", 4, 6, "easy"),
        "same_shape": ("Найди такую же", "preschool", 4, 6, "easy"),
        "coloring": ("Раскрась", "preschool", 4, 6, "easy"),
        "color_find": ("Цвета", "preschool", 4, 6, "easy"),
        "analogy": ("Аналогии", "logic", 6, 10, "medium"),
        "sudoku": ("Судоку", "logic", 7, 10, "hard"),
        "table_fill": ("Таблицы", "logic", 7, 10, "medium"),
        "crossword": ("Кроссворд", "logic", 6, 10, "medium"),
        "detective": ("Детектив", "logic", 8, 10, "hard"),
        "deduction": ("Дедукция", "logic", 8, 10, "hard"),
    }
    _TITLES_UK = {
        "math_addition": "Додавання",
        "math_subtraction": "Віднімання",
        "math_compare": "Порівняння",
        "math_multiplication": "Множення",
        "math_division": "Ділення",
        "missing_number": "Пропущене число",
        "math_word": "Задачі",
        "maze": "Лабіринт",
        "labyrinth": "Лабіринт",
        "find_path": "Знайди шлях",
        "puzzle_lines": "Головоломка",
        "pattern": "Закономірності",
        "odd_one_out": "Зайве",
        "sequence": "Послідовність",
        "story_read": "Читання",
        "question_answer": "Запитання",
        "find_word": "Знайди слово",
        "count_trace": "Лічба",
        "shape_find": "Фігури",
        "letter_trace": "Букви",
        "same_shape": "Знайди таку ж",
        "coloring": "Розфарбуй",
        "color_find": "Кольори",
        "analogy": "Аналогії",
        "sudoku": "Судоку",
        "table_fill": "Таблиці",
        "crossword": "Кросворд",
        "detective": "Детектив",
        "deduction": "Дедукція",
    }
    title, subject, amin, amax, default_diff = defaults.get(cid, (cid, "math", 5, 10, "easy"))
    if language.startswith("uk"):
        title = _TITLES_UK.get(cid, title)
    return CardTemplate(
        id=cid, title=title, subject=subject,
        age_min=amin, age_max=amax,
        grade=[], difficulty=difficulty or default_diff,
        language=["ru", "uk"], card_type=cid,
        theme_tags=[], layout="basic",
        requires_ai=(cid not in GENERATOR_CLASSES),
        has_answer_key=True,
        params={"min_number": 1, "max_number": 100},
    )


try:
    from core.card_text_gen import GENERATORS as TEXT_GENERATORS
except ImportError:
    logger.warning("card_text_gen not available, using math fallback")
    TEXT_GENERATORS = {}


def _generate_cards(tmpl: CardTemplate, count: int, topic: str,
                     seed: int, language: str = "ru") -> List[CardResult]:
    from core.topic_injector import inject_topic
    cls = GENERATOR_CLASSES.get(tmpl.id)
    if cls:
        try:
            gen = cls(tmpl)
            results = gen.generate(count, topic)
            if results:
                for cr in results:
                    q, a = inject_topic(cr.question, cr.answer, topic, language, tmpl.id, seed)
                    cr.question = q
                    cr.answer = a
            return results
        except Exception as e:
            logger.warning(f"Generator {tmpl.id} failed: {e}")
            return []
    text_gen = TEXT_GENERATORS.get(tmpl.id)
    if text_gen:
        try:
            results = text_gen(tmpl, count, topic, seed, language)
            if results:
                for cr in results:
                    q, a = inject_topic(cr.question, cr.answer, topic, language, tmpl.id, seed)
                    cr.question = q
                    cr.answer = a
                return results
        except Exception as e:
            logger.warning(f"Text generator {tmpl.id} failed: {e}")
    # Fallback: language-aware math
    from core.language_layer import instruction as lli
    gen = DeterministicMathGenerator(seed)
    tasks = _math_tasks_from_generator(gen, tmpl.id, count, tmpl.difficulty)
    return [
        CardResult(card_type=tmpl.id, question=t["question"], answer=t.get("answer", ""))
        for t in tasks
    ]


def generate_from_preset(preset_data: Dict[str, Any]) -> Dict[str, Any]:
    age = preset_data.get("age", 7)
    difficulty = preset_data.get("difficulty", "easy")
    language = preset_data.get("language", "ru")
    topic = preset_data.get("topic", "general")
    pages_count = preset_data.get("pages_count", 10)
    card_ids = preset_data.get("cards", [])
    include_answers = preset_data.get("include_answers", True)
    include_instruction = preset_data.get("include_parent_instruction", True)

    if not card_ids:
        logger.warning("No cards in preset, using default")
        card_ids = ["math_addition", "math_subtraction", "math_compare"]

    diff_params = get_params(difficulty)
    seed = random.randint(0, 999999)

    templates = [_make_template_for_id(cid, difficulty, age, language) for cid in card_ids]
    templates = [t for t in templates if t is not None]

    if not templates:
        logger.error("No card templates resolved, using fallback")
        return _fallback_generate(preset_data)

    pages = []
    answers = []
    tasks_per_page = diff_params["tasks_per_page"]

    card_index = 0
    
    from core.instruction_variety import InstructionProvider
    providers = {}
    
    for page_num in range(1, pages_count + 1):
        tmpl = templates[card_index % len(templates)]
        card_index += 1

        count = min(tasks_per_page, 5)
        cards = _generate_cards(tmpl, count, topic, seed + page_num, language)
        if not cards:
            cards = [
                CardResult(card_type="fallback", question=f"{page_num * 2} + {page_num} = ?", answer=str(page_num * 3))
                for _ in range(count)
            ]

        tasks = []
        for c in cards:
            tasks.append({
                "type": tmpl.card_type,
                "question": c.question,
                "options": c.options or [],
                "answer_space": True,
                "answer": str(c.answer) if c.answer is not None else "",
            })

        page_title = f"{tmpl.title} - {page_num}"
        
        if tmpl.card_type not in providers:
            providers[tmpl.card_type] = InstructionProvider(language, tmpl.card_type, age, topic)
        instruction = providers[tmpl.card_type].get()

        pages.append({
            "page_number": page_num,
            "page_type": tmpl.card_type,
            "title": page_title,
            "instruction": instruction,
            "tasks": tasks,
        })
        answers.append({
            "page_number": page_num,
            "answers": [t.get("answer", "") for t in tasks],
        })

    ru = language in ("ru", "ru+en")
    
    title = preset_data.get("title", "StudyPack") if preset_data.get("title") else "StudyPack"
    if ":" in title and topic and topic not in ("general", "custom", ""):
        try:
            from core.topic_lexicon import get_display_name
            dt = get_display_name(topic, language).lower()
            if dt:
                prefix = title.split(":")[0]
                title = f"{prefix}: {dt}"
        except:
            pass

    return {
        "title": title,
        "subtitle": f"Задания для детей {age} лет" if ru else f"Завдання для дітей {age} років",
        "language": language,
        "age": age,
        "grade": preset_data.get("grade", ""),
        "topic": topic,
        "pack_type": preset_data.get("pack_type", "mixed_week"),
        "difficulty": difficulty,
        "parent_instruction": _parent_instruction(language) if include_instruction else "",
        "pages": pages,
        "answers": answers if include_answers else [],
    }


def _math_tasks_from_generator(gen: DeterministicMathGenerator, card_type: str,
                                count: int, difficulty: str) -> List[Dict]:
    mapping = {
        "math_addition": gen.addition,
        "math_subtraction": gen.subtraction,
        "math_multiplication": gen.multiplication,
        "math_division": gen.division,
        "math_compare": gen.compare,
        "missing_number": gen.missing_number,
        "math_word": gen.word_problem,
    }
    func = mapping.get(card_type, gen.addition)
    try:
        pairs = func(count)
    except Exception:
        return []
    tasks = []
    for question, answer in pairs:
        tasks.append({
            "type": "math",
            "question": str(question),
            "options": [],
            "answer_space": True,
            "answer": str(answer) if answer is not None else "",
        })
    return tasks


def _parent_instruction(language: str) -> str:
    if language in ("ru", "ru+en"):
        return ("Занимайтесь 10-20 минут в день. Хвалите ребёнка за старание. "
                "Ответы - только для проверки взрослым.")
    return ("Займайтеся 10-20 хвилин на день. Хваліть дитину за старання. "
            "Відповіді - тільки для перевірки дорослим.")


def _make_fallback_tasks(page_num: int, count: int) -> List[Dict]:
    tasks = []
    for i in range(count):
        tasks.append({
            "type": "math",
            "question": f"{i + page_num * 2} + {i + 1} = ?",
            "options": [],
            "answer_space": True,
            "answer": str((i + page_num * 2) + (i + 1)),
        })
    return tasks


def _fallback_generate(preset_data: Dict[str, Any]) -> Dict[str, Any]:
    age = preset_data.get("age", 7)
    lang = preset_data.get("language", "ru")
    topic = preset_data.get("topic", "general")
    pages_count = min(preset_data.get("pages_count", 10), 20)
    ru = lang in ("ru", "ru+en")

    gen = DeterministicMathGenerator(42)
    pages = []
    answers = []
    for i in range(pages_count):
        pn = i + 1
        pairs = gen.addition(3)
        tasks = [{"type": "math", "question": str(q), "options": [], "answer_space": True, "answer": str(a)} for q, a in pairs]
        pages.append({"page_number": pn, "page_type": "math", "title": f"Примеры {pn}", "instruction": "Реши примеры" if ru else "Розв'яжи приклади", "tasks": tasks})
        answers.append({"page_number": pn, "answers": [str(a) for _, a in pairs]})

    return {
        "title": f"StudyPack: {topic}",
        "subtitle": f"Задания для детей {age} лет" if ru else f"Завдання для дітей {age} років",
        "language": lang, "age": age, "grade": preset_data.get("grade", ""),
        "topic": topic, "pack_type": preset_data.get("pack_type", "mixed_week"),
        "difficulty": preset_data.get("difficulty", "easy"),
        "parent_instruction": _parent_instruction(lang),
        "pages": pages, "answers": answers,
    }
