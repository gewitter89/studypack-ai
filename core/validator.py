import json
import logging
from typing import Dict, List, Optional, Tuple

from core.models import StudyPack
from config.blacklist_loader import load_blacklist

logger = logging.getLogger(__name__)


class ValidationResult:
    def __init__(self):
        self.is_valid: bool = True
        self.errors: List[str] = []
        self.warnings: List[str] = []

    def add_error(self, msg: str):
        self.is_valid = False
        self.errors.append(msg)

    def add_warning(self, msg: str):
        self.warnings.append(msg)


def validate_json_structure(raw: str) -> Tuple[bool, Optional[Dict], str]:
    try:
        data = json.loads(raw)
        return True, data, ""
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error: {e}")
        return False, None, f"Невалидный JSON: {e}"


def validate_study_pack(data: Dict, expected_pages: int, include_answers: bool) -> ValidationResult:
    result = ValidationResult()

    if not isinstance(data, dict):
        result.add_error("Ответ AI не является объектом JSON.")
        return result

    if not data.get("title"):
        result.add_error("Отсутствует название (title).")

    if not data.get("subtitle"):
        result.add_warning("Отсутствует подзаголовок (subtitle).")

    if not isinstance(data.get("age"), (int, float)):
        result.add_error("Возраст (age) должен быть числом.")

    pages = data.get("pages", [])
    if not pages:
        result.add_error("Нет страниц с заданиями (pages).")
        return result

    exercise_pages = [p for p in pages if p.get("page_type") in ("exercise", "story", "quiz")]
    if len(exercise_pages) < expected_pages:
        result.add_warning(
            f"Ожидалось {expected_pages} страниц заданий, получено {len(exercise_pages)}."
        )

    for i, page in enumerate(pages):
        if not page.get("title"):
            result.add_warning(f"Страница {page.get('page_number', i + 1)} без заголовка.")
        tasks = page.get("tasks", [])
        for j, task in enumerate(tasks):
            if not task.get("question"):
                result.add_warning(
                    f"Задание {j + 1} на странице {page.get('page_number', i + 1)} без вопроса."
                )

    if include_answers:
        answers = data.get("answers", [])
        if not answers:
            result.add_warning("Ответы включены, но блок answers пуст.")
        else:
            answer_pages = {a["page_number"] for a in answers}
            for page in exercise_pages:
                pn = page.get("page_number")
                if pn and pn not in answer_pages:
                    result.add_warning(f"Нет ответов для страницы {pn}.")

    return result


def check_safety(text: str) -> List[str]:
    blacklist = load_blacklist()
    issues = []

    text_lower = text.lower()

    for brand in blacklist.get("brands", []):
        if brand.lower() in text_lower:
            issues.append(f"Найден бренд: {brand}")

    for unsafe in blacklist.get("unsafe_topics", []):
        if unsafe.lower() in text_lower:
            issues.append(f"Найдена опасная тема: {unsafe}")

    for claim in blacklist.get("medical_claims", []):
        if claim.lower() in text_lower:
            issues.append(f"Найдено медицинское утверждение: {claim}")

    return issues


def full_validation(raw: str, expected_pages: int, include_answers: bool) -> ValidationResult:
    result = ValidationResult()

    valid, data, error = validate_json_structure(raw)
    if not valid:
        result.add_error(error)
        return result

    pack_result = validate_study_pack(data, expected_pages, include_answers)
    if not pack_result.is_valid:
        result.errors.extend(pack_result.errors)
    result.warnings.extend(pack_result.warnings)

    json_str = json.dumps(data)
    safety_issues = check_safety(json_str)
    for issue in safety_issues:
        result.add_error(f"Безопасность: {issue}")

    return result
