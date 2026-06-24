import os
from typing import Dict, Any

from core.paths import prompts_dir


def load_prompt_template(path: str = None) -> str:
    if path is None:
        path = os.path.join(prompts_dir(), "generate_pack.md")
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def load_repair_template(path: str = None) -> str:
    if path is None:
        path = os.path.join(prompts_dir(), "repair_json.md")
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def build_prompt(params: Dict[str, Any]) -> str:
    template = load_prompt_template()
    return _fill_template(template, params)


def build_repair_prompt(raw_json: str) -> str:
    template = load_repair_template()
    return template.replace("{{raw_json}}", raw_json)


def _fill_template(template: str, params: Dict[str, Any]) -> str:
    result = template
    for key, value in params.items():
        placeholder = "{{" + key + "}}"
        str_value = str(value).lower() if isinstance(value, bool) else str(value)
        result = result.replace(placeholder, str_value)
    return result
