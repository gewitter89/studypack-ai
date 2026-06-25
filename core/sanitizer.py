import json
import re
import logging
from typing import Dict, Any

from config.blacklist_loader import load_blacklist

logger = logging.getLogger(__name__)


def remove_unsupported_pdf_glyphs(text: str) -> str:
    if not isinstance(text, str):
        return text

    replacements = {
        '🦕': 'динозавр',
        '🚀': 'ракета',
        '📚': 'книги',
        '🏰': 'замок',
        '🐱': 'котик',
        '🐶': 'песик',
        '🐟': 'рибка',
        '⭐': 'зірка',
        '🧩': 'пазл',
        '🍓': 'полуниця',
        '🦊': 'лисичка',
        '🧚': 'фея',
        '🦸': 'супергерой',
        '🚗': 'машина',
        '⚽': 'м’яч',
        '👑': 'корона',
        '🏴\u200d☠️': 'пірат',
        '⚡': 'блискавка',
        '🎮': 'гра',
        '🐠': 'рибка',
        '✈️': 'літак',
        '🤖': 'робот',
        '🌲': 'дерево',
        '🏅': 'медаль',
        '🍳': 'їжа',
        '🐄': 'корова',
        '🦁': 'лев',
        '🌻': 'соняшник',
        '👍': 'добре',
        '👏': 'молодець',
        '🔥': 'супер',
    }
    
    for emoji, word in replacements.items():
        text = text.replace(emoji, word)

    emoji_pattern = re.compile(
        "["
        "\U0001f600-\U0001f64f"
        "\U0001f300-\U0001f5ff"
        "\U0001f680-\U0001f6ff"
        "\U0001f1e0-\U0001f1ff"
        "\U0001f900-\U0001f9ff"
        "\U0001fa70-\U0001faff"
        "]+", flags=re.UNICODE)
    
    text = emoji_pattern.sub(r'', text)
    text = text.replace('⚙️', '').replace('☁️', '').replace('❤️', '').replace('✔️', '').replace('\uFE0F', '')
    
    return text


def sanitize_pack_data(data: Dict[str, Any]) -> Dict[str, Any]:
    blacklist = load_blacklist()
    brands = blacklist.get("brands", [])
    replacements = blacklist.get("brand_replacements", {})
    unsafe = blacklist.get("unsafe_topics", [])
    medical = blacklist.get("medical_claims", [])

    json_str = json.dumps(data, ensure_ascii=False)

    for brand in brands:
        replacement = replacements.get(brand.lower(), "[ТЕМА]")
        json_str = re.sub(re.escape(brand), replacement, json_str, flags=re.IGNORECASE)

    for term in unsafe:
        json_str = re.sub(re.escape(term), "[ДОПУСТИМАЯ ТЕМА]", json_str, flags=re.IGNORECASE)

    for term in medical:
        json_str = re.sub(re.escape(term), "", json_str, flags=re.IGNORECASE)

    json_str = remove_unsupported_pdf_glyphs(json_str)

    sanitized = json.loads(json_str)
    logger.info("Sanitization complete")
    return sanitized


def normalize_whitespace(text: str) -> str:
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def check_topic_and_replace(topic: str) -> str:
    blacklist = load_blacklist()
    replacements = blacklist.get("brand_replacements", {})

    topic_lower = topic.lower().strip()

    for brand, replacement in replacements.items():
        if brand in topic_lower:
            logger.info(f"Topic '{topic}' replaced with '{replacement}'")
            return replacement

    return topic
