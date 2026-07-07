import random
from typing import List

from core.cards.base import BaseCardGenerator, CardResult, CardTemplate
from core.deterministic_generators.color_by_number_generator import ColorByNumberGenerator
from core.deterministic_generators.sudoku_generator import SudokuGenerator
from core.deterministic_generators.connect_dots_generator import ConnectDotsGenerator
from core.deterministic_generators.graphic_dictation_generator import GraphicDictationGenerator
from core.deterministic_generators.find_differences_generator import FindDifferencesGenerator
from core.deterministic_generators.crossword_generator import CrosswordGenerator
from core.deterministic_generators.maze_generator import MazeGenerator


class ColorByNumberCard(BaseCardGenerator):
    def generate(self, count: int = 1, theme: str = "") -> List[CardResult]:
        rng = random.Random(id(self))
        results = []
        for i in range(count):
            gen = ColorByNumberGenerator(
                size=rng.choice([5, 6]),
                num_colors=rng.randint(4, 6),
                seed=rng.randint(0, 999999),
            )
            gen.generate()
            data = gen.to_page_data(language=self.template.language[0] if self.template.language else "uk")
            lang = self.template.language[0] if self.template.language else "uk"
            instr = {
                "ru": "Раскрась клеточки по схеме: номер = цвет из легенды.",
                "uk": "Розфарбуй клітинки за схемою: номер = колір із легенди.",
                "en": "Color the cells according to the legend: number = color.",
            }.get(lang, "Розфарбуй клітинки за схемою: номер = колір із легенди.")
            results.append(CardResult(
                card_type="color_by_number",
                question="",
                answer="",
                has_answer_space=False,
                instruction=instr,
                visual_aid=str(data),
                difficulty=self.template.difficulty,
            ))
        return results

    def validate_answer(self, question: str, answer: str) -> bool:
        return True


class SudokuCard(BaseCardGenerator):
    def generate(self, count: int = 1, theme: str = "") -> List[CardResult]:
        rng = random.Random(id(self))
        results = []
        for _ in range(count):
            gen = SudokuGenerator(
                size=rng.choice([4, 4, 6]),
                difficulty=self.template.difficulty,
                seed=rng.randint(0, 999999),
            )
            gen.generate()
            data = gen.to_page_data()
            lang = self.template.language[0] if self.template.language else "uk"
            instr = {
                "ru": f"Заполни клетки числами 1–{gen.size} так, чтобы в строке, столбце и блоке не было повторов.",
                "uk": f"Заповни клітини числами 1–{gen.size} так, щоб у рядку, стовпці та блоці не було повторів.",
                "en": f"Fill cells with numbers 1–{gen.size} so that no number repeats in any row, column, or box.",
            }.get(lang, f"Заповни клітини числами 1–{gen.size} без повторів.")
            results.append(CardResult(
                card_type="sudoku",
                question="",
                answer="",
                has_answer_space=False,
                instruction=instr,
                visual_aid=str(data),
                difficulty=self.template.difficulty,
            ))
        return results

    def validate_answer(self, question: str, answer: str) -> bool:
        return True


class ConnectDotsCard(BaseCardGenerator):
    def generate(self, count: int = 1, theme: str = "") -> List[CardResult]:
        rng = random.Random(id(self))
        shapes = ["star", "heart", "fish", "house", "rocket"]
        results = []
        for _ in range(count):
            gen = ConnectDotsGenerator(
                shape=rng.choice(shapes),
                seed=rng.randint(0, 999999),
            )
            gen.generate()
            lang = self.template.language[0] if self.template.language else "uk"
            data = gen.to_page_data(language=lang)
            instr = {
                "ru": "Соедини точки по порядку номеров, чтобы получилась фигура.",
                "uk": "З'єднай крапки за порядком номерів, щоб вийшла фігура.",
                "en": "Connect the dots in number order to reveal the shape.",
            }.get(lang, "З'єднай крапки за порядком номерів.")
            results.append(CardResult(
                card_type="connect_dots",
                question="",
                answer="",
                has_answer_space=False,
                instruction=instr,
                visual_aid=str(data),
                difficulty=self.template.difficulty,
            ))
        return results

    def validate_answer(self, question: str, answer: str) -> bool:
        return True


class GraphicDictationCard(BaseCardGenerator):
    def generate(self, count: int = 1, theme: str = "") -> List[CardResult]:
        rng = random.Random(id(self))
        figures = list(FIGURES_KEYS)
        results = []
        for _ in range(count):
            gen = GraphicDictationGenerator(
                figure=rng.choice(figures),
                difficulty=self.template.difficulty,
                seed=rng.randint(0, 999999),
            )
            gen.generate()
            lang = self.template.language[0] if self.template.language else "uk"
            data = gen.to_page_data(language=lang)
            instr = {
                "ru": "Начни с точки и следуй указаниям — рисуй по одной клеточке за шаг.",
                "uk": "Почни з крапки та йди за вказівками — малюй по одній клітинці за крок.",
                "en": "Start from the dot and follow the steps — draw one cell at a time.",
            }.get(lang, "Почни з крапки та малюй по одній клітинці за крок.")
            results.append(CardResult(
                card_type="graphic_dictation",
                question="",
                answer="",
                has_answer_space=False,
                instruction=instr,
                visual_aid=str(data),
                difficulty=self.template.difficulty,
            ))
        return results

    def validate_answer(self, question: str, answer: str) -> bool:
        return True


FIGURES_KEYS = ["house", "robot", "dog", "cat", "tree", "car", "rabbit", "fish"]


class FindDiffCard(BaseCardGenerator):
    def generate(self, count: int = 1, theme: str = "") -> List[CardResult]:
        rng = random.Random(id(self))
        lang = self.template.language[0] if self.template.language else "uk"
        diff_by_level = {"easy": 4, "medium": 5, "hard": 6}
        n = diff_by_level.get(self.template.difficulty, 5)
        results = []
        for _ in range(count):
            gen = FindDifferencesGenerator(
                rows=4, cols=4, num_diffs=n,
                difficulty=self.template.difficulty,
                seed=rng.randint(0, 999999),
            )
            gen.generate()
            data = gen.to_page_data(language=lang)
            instr = {
                "ru": f"Два рисунка почти одинаковые. Найди {n} отличий и обведи их.",
                "uk": f"Два малюнки майже однакові. Знайди {n} відмінностей і обведи їх.",
                "en": f"Two drawings are almost the same. Find {n} differences and circle them.",
            }.get(lang, f"Два малюнки майже однакові. Знайди {n} відмінностей.")
            results.append(CardResult(
                card_type="find_differences",
                question="",
                answer=gen.answer_text(lang),
                has_answer_space=False,
                instruction=instr,
                visual_aid=str(data),
                difficulty=self.template.difficulty,
            ))
        return results

    def validate_answer(self, question: str, answer: str) -> bool:
        return True


class MazeCard(BaseCardGenerator):
    def generate(self, count: int = 1, theme: str = "") -> List[CardResult]:
        rng = random.Random(id(self))
        lang = self.template.language[0] if self.template.language else "uk"
        size_by_level = {"easy": 5, "medium": 7, "hard": 9}
        sz = size_by_level.get(self.template.difficulty, 6)
        results = []
        for _ in range(count):
            gen = MazeGenerator(rows=sz, cols=sz)
            random.seed(rng.randint(0, 999999))
            gen.generate()
            data = gen.to_page_data()
            data["type"] = "maze"
            solution = gen.solve()
            instr = {
                "ru": "Проведи линию от входа (слева) до выхода (справа).",
                "uk": "Проведи лінію від входу (зліва) до виходу (справа).",
                "en": "Draw a line from the entrance on the left to the exit on the right.",
            }.get(lang, "Проведи лінію від входу до виходу.")
            results.append(CardResult(
                card_type="maze",
                question="",
                answer=f"Шлях: {len(solution)} кроків",
                has_answer_space=False,
                instruction=instr,
                visual_aid=str(data),
                difficulty=self.template.difficulty,
            ))
        return results

    def validate_answer(self, question: str, answer: str) -> bool:
        return True


class CrosswordCard(BaseCardGenerator):
    def generate(self, count: int = 1, theme: str = "") -> List[CardResult]:
        rng = random.Random(id(self))
        lang = self.template.language[0] if self.template.language else "uk"
        results = []
        for _ in range(count):
            gen = CrosswordGenerator(
                theme=theme or "general",
                language=lang,
                max_words=6,
                seed=rng.randint(0, 999999),
            )
            gen.generate()
            data = gen.to_page_data()
            instr = {
                "ru": "Заполни кроссворд по подсказкам — по горизонтали и вертикали.",
                "uk": "Заповни кросворд за підказками — по горизонталі та вертикалі.",
                "en": "Fill in the crossword using the across and down clues.",
            }.get(lang, "Заповни кросворд за підказками.")
            results.append(CardResult(
                card_type="crossword",
                question="",
                answer=gen.answer_text(),
                has_answer_space=False,
                instruction=instr,
                visual_aid=str(data),
                difficulty=self.template.difficulty,
            ))
        return results

    def validate_answer(self, question: str, answer: str) -> bool:
        return True
