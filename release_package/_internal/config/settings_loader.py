import json
import os
from typing import Dict, Any


def load_settings(path: str = None) -> Dict[str, Any]:
    if path is None:
        path = os.path.join(os.path.dirname(__file__), "settings.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)
