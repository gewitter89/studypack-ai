"""Tests for core.series_generator module."""
import pytest
from core.series_generator import (
    SeriesConfig, build_series_presets, get_difficulty_for_pack,
    generate_series, DIFFICULTY_LEVELS,
)


class TestDifficultyProgression:
    def test_single_pack_no_change(self):
        d = get_difficulty_for_pack(0, 1, "easy")
        assert d == "easy"

    def test_first_pack_start_level(self):
        d = get_difficulty_for_pack(0, 4, "easy")
        assert d == "easy"

    def test_last_pack_easy_to_hard(self):
        d = get_difficulty_for_pack(3, 4, "easy")
        assert d == "hard"

    def test_middle_pack_medium(self):
        d = get_difficulty_for_pack(2, 5, "easy")
        assert d in ("easy", "medium")

    def test_start_medium_stays_above(self):
        d = get_difficulty_for_pack(3, 4, "medium")
        assert d in ("medium", "hard")

    def test_never_below_min(self):
        for i in range(10):
            d = get_difficulty_for_pack(i, 10, "easy")
            assert d in DIFFICULTY_LEVELS


class TestBuildSeriesPresets:
    def test_returns_correct_count(self):
        cfg = SeriesConfig(
            name="animals", theme_chain=["animals", "dinosaurs", "ocean"],
            total_packs=3, pages_per_pack=8, age=7, language="uk",
        )
        presets = build_series_presets(cfg)
        assert len(presets) == 3

    def test_topics_from_chain(self):
        cfg = SeriesConfig(
            name="animals", theme_chain=["animals", "dinosaurs"],
            total_packs=2, pages_per_pack=6, age=7, language="uk",
        )
        presets = build_series_presets(cfg)
        assert presets[0]["topic"] == "animals"
        assert presets[1]["topic"] == "dinosaurs"

    def test_cycling_chain(self):
        cfg = SeriesConfig(
            name="animals", theme_chain=["animals", "ocean"],
            total_packs=4, pages_per_pack=6, age=7, language="uk",
        )
        presets = build_series_presets(cfg)
        assert presets[2]["topic"] == "animals"  # cycles back
        assert presets[3]["topic"] == "ocean"

    def test_presets_have_required_fields(self):
        cfg = SeriesConfig(
            name="animals", theme_chain=["animals"],
            total_packs=1, pages_per_pack=6, age=7, language="uk",
        )
        presets = build_series_presets(cfg)
        p = presets[0]
        assert "age" in p
        assert "difficulty" in p
        assert "language" in p
        assert "topic" in p
        assert "pages_count" in p
        assert "cards" in p

    def test_difficulty_progresses(self):
        cfg = SeriesConfig(
            name="animals", theme_chain=["animals", "ocean", "space"],
            total_packs=3, pages_per_pack=6, age=7, language="uk",
            difficulty_progress=True,
        )
        presets = build_series_presets(cfg)
        diffs = [p["difficulty"] for p in presets]
        assert diffs[0] == "easy"
        assert diffs[-1] in ("medium", "hard")

    def test_no_progress_same(self):
        cfg = SeriesConfig(
            name="animals", theme_chain=["animals", "ocean"],
            total_packs=2, pages_per_pack=6, age=7, language="uk",
            difficulty_progress=False,
        )
        presets = build_series_presets(cfg)
        assert presets[0]["difficulty"] == presets[1]["difficulty"]

    def test_unknown_name_uses_chain(self):
        cfg = SeriesConfig(
            name="unknown", theme_chain=["animals", "ocean"],
            total_packs=2, pages_per_pack=6, age=7, language="uk",
        )
        presets = build_series_presets(cfg)
        assert len(presets) == 2


class TestGenerateSeries:
    def test_generates_multiple_packs(self):
        cfg = SeriesConfig(
            name="animals", theme_chain=["animals", "ocean"],
            total_packs=2, pages_per_pack=4, age=7, language="uk",
        )
        results = generate_series(cfg)
        assert len(results) == 2

    def test_series_metadata_attached(self):
        cfg = SeriesConfig(
            name="animals", theme_chain=["animals", "ocean"],
            total_packs=2, pages_per_pack=4, age=7, language="uk",
        )
        results = generate_series(cfg)
        for i, data in enumerate(results):
            assert "_series" in data
            assert data["_series"]["name"] == "animals"
            assert data["_series"]["pack_index"] == i + 1
            assert data["_series"]["total_packs"] == 2

    def test_pages_generated(self):
        cfg = SeriesConfig(
            name="animals", theme_chain=["animals"],
            total_packs=1, pages_per_pack=4, age=7, language="uk",
        )
        results = generate_series(cfg)
        assert len(results[0]["pages"]) == 4

    def test_difficulty_varies(self):
        cfg = SeriesConfig(
            name="animals", theme_chain=["a", "b", "c"],
            total_packs=3, pages_per_pack=3, age=7, language="uk",
            difficulty_progress=True,
        )
        results = generate_series(cfg)
        diffs = [d["difficulty"] for d in results]
        assert diffs[0] == "easy"
        assert diffs[-1] != "easy"
