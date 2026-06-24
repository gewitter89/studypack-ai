import json
import os
from typing import Dict


def load_blacklist(path: str = None) -> Dict:
    if path is None:
        path = os.path.join(os.path.dirname(__file__), "blacklist.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)
