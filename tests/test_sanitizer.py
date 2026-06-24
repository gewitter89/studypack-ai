import json
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.sanitizer import sanitize_pack_data, check_topic_and_replace, normalize_whitespace


def test_brand_replaced():
    data = {
        "title": "Minecraft Adventure",
        "pages": [
            {
                "page_number": 1,
                "page_type": "exercise",
                "title": "Minecraft world",
                "instruction": "Build like in Minecraft",
                "tasks": []
            }
        ],
        "answers": []
    }
    result = sanitize_pack_data(data)
    json_str = json.dumps(result, ensure_ascii=False)
    assert "Minecraft" not in json_str
    assert "пиксельный" in json_str


def test_unsafe_topic_blocked():
    data = {
        "title": "оружие game",
        "pages": [],
        "answers": []
    }
    result = sanitize_pack_data(data)
    json_str = json.dumps(result, ensure_ascii=False)
    assert "оружие" not in json_str


def test_medical_claim_removed():
    data = {
        "title": "This лечит your child",
        "pages": [],
        "answers": []
    }
    result = sanitize_pack_data(data)
    json_str = json.dumps(result, ensure_ascii=False)
    assert "лечит" not in json_str


def test_topic_replacement():
    assert "пиксельный блочный мир" in check_topic_and_replace("Minecraft")
    assert "пиксельный блочный мир" in check_topic_and_replace("minecraft adventures")
    assert check_topic_and_replace("dinosaurs") == "dinosaurs"


def test_normalize_whitespace():
    assert normalize_whitespace("  hello   world  ") == "hello world"
    assert normalize_whitespace("normal") == "normal"
