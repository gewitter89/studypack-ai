import random
from typing import List, Optional, Tuple
from core.cards.base import CardTemplate, CardResult, BaseCardGenerator


class MathAdditionGenerator(BaseCardGenerator):
    def generate(self, count: int = 8, theme: str = "") -> List[CardResult]:
        results = []
        min_n = self.template.params.get("min_number", 1)
        max_n = self.template.params.get("max_number", 10)
        with_story = self.template.params.get("with_story", False)

        for i in range(count):
            a = random.randint(min_n, max_n)
            b = random.randint(1, max_n - a) if a < max_n else 0
            b = max(1, b)
            answer = a + b

            if with_story and i < count // 2:
                obj = self._random_object(theme)
                question = f"{obj[0]} {a} {obj[1]}, а {obj[2]} додали ще {b}. Скільки всього?"
            else:
                question = f"{a} + {b} = ?"

            results.append(CardResult(
                card_type="math_addition",
                question=question,
                answer=str(answer),
                has_answer_space=True,
                instruction=self._age_appropriate_instruction(
                    self.template.age_min, "Порахуй і запиши відповідь"
                ),
                difficulty=self.template.difficulty,
            ))

        return results

    def validate_answer(self, question: str, answer: str) -> bool:
        try:
            parts = question.replace("= ?", "").replace("=", "").strip()
            if "+" in parts:
                nums = [int(x.strip()) for x in parts.split("+")]
                return str(sum(nums)) == answer.strip()
            return False
        except (ValueError, IndexError):
            return False

    def _random_object(self, theme: str) -> Tuple[str, str, str]:
        objects = {
            "dinosaurs": ("У джунглях гуляло", "динозаврів", "потім"),
            "space": ("На космічній станції було", "космонавтів", "прилетіло"),
            "animals": ("У зоопарку було", "звірів", "привезли"),
            "toys": ("У коробці лежало", "іграшок", "поклали"),
        }
        obj = objects.get(theme, ("Було", "яблук", "додали"))
        return obj


class MathSubtractionGenerator(BaseCardGenerator):
    def generate(self, count: int = 10, theme: str = "") -> List[CardResult]:
        results = []
        min_n = self.template.params.get("min_number", 1)
        max_n = self.template.params.get("max_number", 20)

        for i in range(count):
            a = random.randint(min_n + 1, max_n)
            b = random.randint(1, a - 1)
            answer = a - b

            if self.template.params.get("with_story", False) and i < count // 2:
                question = f"Було {a} цукерок. З'їли {b}. Скільки залишилося?"
            else:
                question = f"{a} - {b} = ?"

            results.append(CardResult(
                card_type="math_subtraction",
                question=question,
                answer=str(answer),
                has_answer_space=True,
                instruction="Відніми і запиши відповідь",
                difficulty=self.template.difficulty,
            ))

        return results

    def validate_answer(self, question: str, answer: str) -> bool:
        try:
            parts = question.replace("= ?", "").replace("=", "").strip()
            if "-" in parts:
                nums = [int(x.strip()) for x in parts.split("-")]
                return str(nums[0] - nums[1]) == answer.strip()
            return False
        except (ValueError, IndexError):
            return False


class MathCompareGenerator(BaseCardGenerator):
    def generate(self, count: int = 8, theme: str = "") -> List[CardResult]:
        results = []
        for i in range(count):
            a = random.randint(1, 20)
            b = random.randint(1, 20)
            answer = ">" if a > b else "<" if a < b else "="
            results.append(CardResult(
                card_type="math_compare",
                question=f"{a} ○ {b}",
                answer=answer,
                has_answer_space=True,
                options=[">", "<", "="],
                instruction="Постав знак >, < або =",
                difficulty=self.template.difficulty,
            ))
        return results

    def validate_answer(self, question: str, answer: str) -> bool:
        return answer.strip() in (">", "<", "=")
