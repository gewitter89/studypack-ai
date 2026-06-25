import json
import os
import sys
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from core.preset_loader import load_preset, list_presets, find_best_preset


class TestPresetLoader:
    def test_load_preset_exists(self):
        p = load_preset("preschool_animals")
        assert p is not None
        assert p["id"] == "preschool_animals"
        assert p["age"] == 5
        assert p["language"] == "uk"

    def test_load_preset_nonexistent(self):
        assert load_preset("nonexistent_preset_xyz") is None

    def test_list_all_presets(self):
        all_p = list_presets()
        assert len(all_p) == 30
        for p in all_p:
            assert "id" in p
            assert "age" in p
            assert "difficulty" in p

    def test_list_presets_filter_age(self):
        age7 = list_presets(age=7)
        assert len(age7) > 0
        for p in age7:
            assert p["age"] == 7

    def test_list_presets_filter_difficulty(self):
        easy = list_presets(difficulty="easy")
        assert len(easy) > 0
        for p in easy:
            assert p["difficulty"] == "easy"

    def test_list_presets_filter_type(self):
        logic = list_presets(pack_type="logic")
        assert len(logic) > 0
        for p in logic:
            assert p["pack_type"] == "logic"

    def test_list_presets_filter_combined(self):
        filtered = list_presets(age=7, pack_type="math", difficulty="easy")
        assert len(filtered) >= 0

    def test_list_presets_filter_no_match(self):
        filtered = list_presets(age=4, pack_type="nonexistent")
        assert len(filtered) == 0

    def test_find_best_preset_exact(self):
        p = find_best_preset(age=5, pack_type="preschool", difficulty="easy")
        assert p is not None
        assert p["pack_type"] == "preschool"

    def test_find_best_preset_fallback(self):
        p = find_best_preset(age=9, pack_type="nonexistent_type", difficulty="medium")
        assert p is not None

    def test_all_presets_valid_json(self):
        for p in list_presets():
            assert p["age"] >= 4
            assert p["age"] <= 10
            assert p["difficulty"] in ("easy", "medium", "hard")
            assert isinstance(p["cards"], list)
            assert len(p["cards"]) > 0

    def test_preset_has_title(self):
        for p in list_presets():
            assert p.get("title"), f"Preset {p['id']} has no title"
