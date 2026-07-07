"""Series generator — creates a sequence of related packs with progressive difficulty."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Any, Optional


@dataclass
class SeriesConfig:
    name: str
    theme_chain: List[str]
    total_packs: int
    pages_per_pack: int
    age: int
    language: str
    difficulty_start: str = "easy"
    difficulty_progress: bool = True


DIFFICULTY_LEVELS = ["easy", "medium", "hard"]


def get_difficulty_for_pack(pack_index: int, total: int, start: str = "easy") -> str:
    """Progressively increase difficulty across packs in a series."""
    if total <= 1:
        return start
    start_idx = DIFFICULTY_LEVELS.index(start) if start in DIFFICULTY_LEVELS else 0
    step = (pack_index / max(total - 1, 1)) * (len(DIFFICULTY_LEVELS) - start_idx - 1)
    idx = start_idx + int(step)
    return DIFFICULTY_LEVELS[min(idx, len(DIFFICULTY_LEVELS) - 1)]


def build_series_presets(config: SeriesConfig) -> List[Dict[str, Any]]:
    """Generate preset dicts for each pack in a series."""
    from core.adaptive_difficulty import THEME_CHAINS, recommended_card_mix

    chain = config.theme_chain
    if not chain:
        for chain_name, chain_list in THEME_CHAINS.items():
            if config.name.lower() in chain_name:
                chain = chain_list
                break
    if not chain:
        chain = ["general"]

    presets = []
    for i in range(config.total_packs):
        topic_idx = i % len(chain)
        topic = chain[topic_idx]

        difficulty = (
            get_difficulty_for_pack(i, config.total_packs, config.difficulty_start)
            if config.difficulty_progress else config.difficulty_start
        )

        cards = recommended_card_mix(config.age, config.pages_per_pack)

        preset = {
            "age": config.age,
            "difficulty": difficulty,
            "language": config.language,
            "topic": topic,
            "pages_count": config.pages_per_pack,
            "cards": cards,
            "title": f"{config.name} #{i + 1}",
        }
        presets.append(preset)
    return presets


def generate_series(config: SeriesConfig, generator_func=None) -> List[Dict[str, Any]]:
    """Generate a series of pack_data dicts. generator_func should accept a preset dict."""
    from core.card_generator import generate_from_preset
    from core.postprocess import postprocess

    gen = generator_func or (lambda p: postprocess(generate_from_preset(p)))

    presets = build_series_presets(config)
    results = []
    for i, preset in enumerate(presets):
        preset.setdefault("cards", [])
        data = gen(preset)
        data["_series"] = {
            "name": config.name,
            "pack_index": i + 1,
            "total_packs": config.total_packs,
            "topic": preset["topic"],
        }
        results.append(data)
    return results
