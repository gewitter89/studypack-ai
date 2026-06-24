import json
import os
from typing import Dict, Any


def load_topics(path: str = None) -> Dict[str, Any]:
    if path is None:
        path = os.path.join(os.path.dirname(__file__), "topics.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)
