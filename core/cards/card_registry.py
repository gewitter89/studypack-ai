from typing import Dict, Optional, Type
from core.cards.base import BaseCardGenerator, CardTemplate


class CardRegistry:
    def __init__(self):
        self._generators: Dict[str, BaseCardGenerator] = {}
        self._templates: Dict[str, CardTemplate] = {}

    def register(self, card_type: str, generator: BaseCardGenerator, template: Optional[CardTemplate] = None):
        self._generators[card_type] = generator
        if template:
            self._templates[card_type] = template

    def get_generator(self, card_type: str) -> Optional[BaseCardGenerator]:
        return self._generators.get(card_type)

    def get_template(self, card_type: str) -> Optional[CardTemplate]:
        return self._templates.get(card_type)

    def list_types(self) -> list:
        return list(self._generators.keys())

    def list_by_subject(self, subject: str) -> list:
        return [k for k, v in self._generators.items()
                if hasattr(v, 'template') and v.template.subject == subject]

    def list_by_age(self, age: int) -> list:
        return [k for k, v in self._generators.items()
                if hasattr(v, 'template') and v.template.age_min <= age <= v.template.age_max]


registry = CardRegistry()
