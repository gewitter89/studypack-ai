import random
from typing import List, Tuple


class DeterministicMathGenerator:
    def __init__(self, seed: int = 42):
        self.seed = seed
        random.seed(seed)

    def addition(self, count: int = 10, min_n: int = 1, max_n: int = 20) -> List[Tuple[str, int]]:
        tasks = []
        for _ in range(count):
            a = random.randint(min_n, max_n - 1)
            b = random.randint(1, max_n - a)
            tasks.append((f"{a} + {b}", a + b))
        return tasks

    def subtraction(self, count: int = 10, min_n: int = 1, max_n: int = 20) -> List[Tuple[str, int]]:
        tasks = []
        for _ in range(count):
            a = random.randint(min_n + 1, max_n)
            b = random.randint(1, a - 1)
            tasks.append((f"{a} - {b}", a - b))
        return tasks

    def multiplication(self, count: int = 10, min_n: int = 2, max_n: int = 9) -> List[Tuple[str, int]]:
        tasks = []
        for _ in range(count):
            a = random.randint(min_n, max_n)
            b = random.randint(min_n, max_n)
            tasks.append((f"{a} × {b}", a * b))
        return tasks

    def division(self, count: int = 10, max_n: int = 9) -> List[Tuple[str, int]]:
        tasks = []
        for _ in range(count):
            b = random.randint(2, max_n)
            result = random.randint(2, max_n)
            a = b * result
            tasks.append((f"{a} ÷ {b}", result))
        return tasks

    def missing_number(self, count: int = 10, min_n: int = 1, max_n: int = 20) -> List[Tuple[str, int]]:
        tasks = []
        for _ in range(count):
            a = random.randint(min_n, max_n - 1)
            b = random.randint(1, max_n - a)
            result = a + b
            patterns = [
                (f"{a} + __ = {result}", b),
                (f"__ + {b} = {result}", a),
                (f"{result} - __ = {a}", b),
                (f"{result} - {a} = __", b),
            ]
            tasks.append(random.choice(patterns))
        return tasks

    def compare(self, count: int = 8, min_n: int = 1, max_n: int = 20) -> List[Tuple[str, str]]:
        tasks = []
        for _ in range(count):
            a = random.randint(min_n, max_n)
            b = random.randint(min_n, max_n)
            sign = ">" if a > b else "<" if a < b else "="
            tasks.append((f"{a} _ {b}", sign))
        return tasks

    def word_problem(self, count: int = 4, age: int = 7) -> List[Tuple[str, int]]:
        tasks = []
        objects = ["яблук", "груш", "цукерок", "олівців", "книжок", "звірят"]
        for _ in range(count):
            obj = random.choice(objects)
            a = random.randint(3, 10)
            b = random.randint(2, 8)
            ops = random.choice(["add", "sub"])
            if ops == "add":
                tasks.append((f"В кошику було {a} {obj}. Поклали ще {b}. Скільки стало?", a + b))
            else:
                b = min(b, a - 1)
                if b < 1:
                    b = 1
                tasks.append((f"Було {a} {obj}. Віддали {b}. Скільки залишилося?", a - b))
        return tasks
