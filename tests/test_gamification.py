"""Tests for core.gamification module — XP, achievements, stars, quotes."""
import pytest
from core.gamification import (
    compute_xp, compute_achievements, compute_stars,
    get_quote, XPProgress, StarReward, Achievement, ACHIEVEMENTS,
)


class TestXPProgress:
    def test_initial_state(self):
        xp = XPProgress()
        assert xp.level == 1
        assert xp.current_xp == 0
        assert xp.xp_to_next == 100

    def test_add_xp_no_levelup(self):
        xp = XPProgress()
        leveled = xp.add_xp(50)
        assert not leveled
        assert xp.current_xp == 50
        assert xp.level == 1

    def test_add_xp_levelup(self):
        xp = XPProgress()
        leveled = xp.add_xp(100)
        assert leveled
        assert xp.level == 2
        assert xp.current_xp == 0
        assert xp.xp_to_next == 130

    def test_add_xp_multiple_levelups(self):
        xp = XPProgress()
        leveled = xp.add_xp(300)
        assert leveled
        assert xp.level >= 3

    def test_add_xp_exact_boundary(self):
        xp = XPProgress()
        leveled = xp.add_xp(99)
        assert not leveled
        assert xp.level == 1
        leveled2 = xp.add_xp(1)
        assert leveled2
        assert xp.level == 2


class TestAchievements:
    def test_no_pages_no_achievements(self):
        ach = compute_achievements([], "uk")
        assert len(ach) == 0

    def test_first_pack_always_unlocked(self):
        ach = compute_achievements([{"page_type": "math_addition", "tasks": []}], "uk")
        ids = [a.id for a in ach]
        assert "first_pack" in ids

    def test_math_master_10_tasks(self):
        pages = []
        for i in range(6):
            pages.append({
                "page_type": "math_addition",
                "tasks": [{"type": "addition"} for _ in range(2)],
            })
        ach = compute_achievements(pages, "uk")
        ids = [a.id for a in ach]
        assert "math_master" in ids

    def test_explorer_4_types(self):
        pages = [
            {"page_type": "math_addition", "tasks": [{"type": "addition"}]},
            {"page_type": "sudoku", "tasks": [{"type": "sudoku"}]},
            {"page_type": "coloring", "tasks": [{"type": "coloring"}]},
            {"page_type": "maze", "tasks": [{"type": "maze"}]},
        ]
        ach = compute_achievements(pages, "uk")
        ids = [a.id for a in ach]
        assert "explorer" in ids

    def test_persistence_8_pages(self):
        pages = [{"page_type": f"type_{i}", "tasks": []} for i in range(8)]
        ach = compute_achievements(pages, "uk")
        ids = [a.id for a in ach]
        assert "persistence" in ids

    def test_achievements_are_unlocked(self):
        pages = [{"page_type": "math_addition", "tasks": [{"type": "addition"}]}]
        ach = compute_achievements(pages, "uk")
        assert all(a.unlocked for a in ach)

    def test_all_achievement_ids_exist(self):
        expected = {
            "first_pack", "math_master", "logic_king", "reader_star",
            "creative_soul", "full_completion", "speed_demon",
            "perfect_score", "explorer", "persistence",
        }
        assert set(ACHIEVEMENTS.keys()) == expected

    def test_achievement_titles_multilang(self):
        for ach_id, ach in ACHIEVEMENTS.items():
            for lang in ["uk", "ru", "en"]:
                assert lang in ach.title, f"{ach_id} missing title for {lang}"


class TestStars:
    def test_no_pages_no_stars(self):
        stars = compute_stars([])
        assert len(stars) == 0

    def test_visual_page_earns_star(self):
        pages = [{"page_type": "maze"}]
        stars = compute_stars(pages)
        assert len(stars) == 1
        assert stars[0].earned
        assert stars[0].page_number == 1

    def test_non_visual_page_no_star(self):
        pages = [{"page_type": "math_addition"}]
        stars = compute_stars(pages)
        assert len(stars) == 1
        assert not stars[0].earned

    def test_mixed_pages(self):
        pages = [
            {"page_type": "color_by_number"},
            {"page_type": "math_addition"},
            {"page_type": "sudoku"},
        ]
        stars = compute_stars(pages)
        assert len(stars) == 3
        assert stars[0].earned
        assert not stars[1].earned
        assert stars[2].earned


class TestMotivationalQuotes:
    def test_uk_quote(self):
        q = get_quote("uk", 0)
        assert len(q) > 5

    def test_ru_quote(self):
        q = get_quote("ru", 0)
        assert len(q) > 5

    def test_en_quote(self):
        q = get_quote("en", 0)
        assert len(q) > 5

    def test_quote_cycles(self):
        q1 = get_quote("uk", 0)
        q2 = get_quote("uk", 6)
        assert q1 == q2

    def test_unknown_lang_fallback_ru(self):
        q = get_quote("de", 0)
        assert len(q) > 5
