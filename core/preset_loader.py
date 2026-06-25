import json
import os
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


def load_preset(preset_id: str) -> Optional[Dict[str, Any]]:
    presets_dir = _presets_dir()
    if not presets_dir:
        return None
    for fname in sorted(os.listdir(presets_dir)):
        if not fname.endswith(".json"):
            continue
        fpath = os.path.join(presets_dir, fname)
        try:
            with open(fpath, "r", encoding="utf-8") as f:
                data = json.load(f)
            if data.get("id") == preset_id:
                return data
        except (json.JSONDecodeError, IOError) as e:
            logger.warning(f"Failed to load preset {fname}: {e}")
    return None


def list_presets(age: Optional[int] = None, difficulty: Optional[str] = None,
                 pack_type: Optional[str] = None) -> List[Dict[str, Any]]:
    presets_dir = _presets_dir()
    if not presets_dir:
        return []
    result = []
    for fname in sorted(os.listdir(presets_dir)):
        if not fname.endswith(".json"):
            continue
        fpath = os.path.join(presets_dir, fname)
        try:
            with open(fpath, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (json.JSONDecodeError, IOError):
            continue
        if age is not None and data.get("age", 0) != age:
            continue
        if difficulty is not None and data.get("difficulty") != difficulty:
            continue
        if pack_type is not None and data.get("pack_type") != pack_type:
            continue
        result.append(data)
    return result


def find_best_preset(age: int, pack_type: str, difficulty: str = "medium") -> Optional[Dict[str, Any]]:
    exact = list_presets(age=age, pack_type=pack_type, difficulty=difficulty)
    if exact:
        return exact[0]
    relaxed = list_presets(pack_type=pack_type, difficulty=difficulty)
    if relaxed:
        return relaxed[0]
    any_type = list_presets(age=age, difficulty=difficulty)
    if any_type:
        return any_type[0]
    fallback = list_presets()
    if fallback:
        return fallback[0]
    return None


def preset_to_request(preset: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "pack_type": preset.get("pack_type", "mixed_week"),
        "age": preset.get("age", 7),
        "grade": preset.get("grade", ""),
        "language": preset.get("language", "ru"),
        "topic": preset.get("topic", "general"),
        "pages_count": preset.get("pages_count", 10),
        "difficulty": preset.get("difficulty", "easy"),
        "style": preset.get("style", "print_bw"),
        "include_answers": preset.get("with_answers", True),
        "include_parent_instruction": preset.get("with_instruction", True),
        "cards": preset.get("cards", []),
        "mode": preset.get("mode", "class"),
        "description": preset.get("description", ""),
        "title": preset.get("title", ""),
    }


def _presets_dir() -> Optional[str]:
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    path = os.path.join(base, "templates_library", "presets")
    if os.path.isdir(path):
        return path
    logger.warning(f"Presets directory not found: {path}")
    return None
