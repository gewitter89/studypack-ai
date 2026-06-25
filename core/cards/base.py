import random
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class CardTemplate:
    id: str
    title: str
    subject: str
    age_min: int
    age_max: int
    grade: List[str]
    difficulty: str
    language: List[str]
    card_type: str
    theme_tags: List[str]
    layout: str
    requires_ai: bool
    has_answer_key: bool
    params: dict = field(default_factory=dict)


@dataclass
class CardResult:
    card_type: str
    question: str
    answer: Optional[str] = None
    options: Optional[List[str]] = None
    has_answer_space: bool = True
    instruction: str = ""
    visual_aid: Optional[str] = None
    difficulty: str = "medium"


class BaseCardGenerator:
    def __init__(self, template: CardTemplate):
        self.template = template

    def generate(self, count: int = 1, theme: str = "") -> List[CardResult]:
        raise NotImplementedError

    def validate_answer(self, question: str, answer: str) -> bool:
        raise NotImplementedError

    def _age_appropriate_instruction(self, age: int, base: str) -> str:
        if age <= 5:
            return f"👇 {base}"
        elif age <= 7:
            return f"{base}"
        else:
            return f"📝 {base}"
