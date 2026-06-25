import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from core.instruction_variety import InstructionProvider, get_pool_for_card


class TestInstructionVariety:
    def test_uk_provider_returns_uk_instruction(self):
        ip = InstructionProvider(language="uk", card_type="shape_find", age=6, topic="general")
        inst = ip.get()
        pool = get_pool_for_card("shape_find", "uk")
        assert inst in pool, f"UK instruction not from UK pool. Got: {inst}, pool: {pool}"

    def test_ru_provider_returns_ru_instruction(self):
        ip = InstructionProvider(language="ru", card_type="shape_find", age=6, topic="general")
        inst = ip.get()
        assert "Найди" in inst or "Где" in inst or "фигура" in inst or "найди" in inst, f"Expected RU instruction, got: {inst}"

    def test_en_provider_returns_en_instruction(self):
        ip = InstructionProvider(language="en", card_type="color_find_en", age=7, topic="general")
        inst = ip.get()
        assert any(w in inst.lower() for w in ["find", "colour", "what"]), f"Expected EN instruction, got: {inst}"

    def test_uk_no_ru_words_in_instruction(self):
        ru_words = ["посчитай", "найди", "соедини", "реши", "раскрась"]
        for card_type in ["shape_find", "coloring", "same_shape", "count_trace", "math_addition"]:
            ip = InstructionProvider(language="uk", card_type=card_type, age=6, topic="general")
            for _ in range(10):
                inst = ip.get().lower()
                for ru in ru_words:
                    if ru in inst:
                        # Allow 'знайди' which contains 'найди' as substring
                        if ru == "найди" and "знайди" in inst:
                            continue
                        assert False, f"RU word '{ru}' in UK instruction: {inst} (card={card_type})"

    def test_unique_instructions_across_calls(self):
        ip = InstructionProvider(language="ru", card_type="math_addition", age=7, topic="general")
        seen = set()
        for _ in range(20):
            inst = ip.get()
            seen.add(inst)
        assert len(seen) >= 3, f"Expected at least 3 unique instructions, got {len(seen)}"

    def test_pool_has_uk_entries(self):
        pool = get_pool_for_card("shape_find", "uk")
        assert len(pool) >= 2
        assert any("Знайди" in p for p in pool)

    def test_pool_has_en_entries(self):
        pool = get_pool_for_card("correct_form_en", "en")
        assert len(pool) >= 3
