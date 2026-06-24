import json
import os
import logging
from datetime import datetime
from typing import Dict, Any, Optional

from core.models import PackRequest
from ai.openrouter_client import OpenRouterClient
from ai.prompt_builder import build_prompt, build_repair_prompt
from core.validator import full_validation
from core.sanitizer import sanitize_pack_data, check_topic_and_replace
from pdf.renderer import render_pdf
from config.settings_loader import load_settings

logger = logging.getLogger(__name__)


class GenerationResult:
    def __init__(self):
        self.success: bool = False
        self.pdf_path: Optional[str] = None
        self.json_path: Optional[str] = None
        self.error: Optional[str] = None
        self.warnings: list = []


class StudyPackGenerator:
    def __init__(self):
        self.settings = load_settings()
        self.client = OpenRouterClient(
            model=self.settings.get("default_model", "openrouter/free"),
            temperature=self.settings.get("temperature", 0.7),
            max_tokens=self.settings.get("max_tokens", 8000),
        )
        self.fallback_models = self.settings.get("fallback_models", [])
        self.max_retries = self.settings.get("max_retries", 2)

    def generate(self, request: PackRequest) -> GenerationResult:
        result = GenerationResult()

        if not self.client.is_configured():
            result.error = "API ключ не настроен. Создайте файл .env и укажите OPENROUTER_API_KEY."
            return result

        request.topic = check_topic_and_replace(request.topic)

        params = {
            "age": request.age,
            "grade": request.grade,
            "language": request.language,
            "pack_type": request.pack_type,
            "topic": request.topic,
            "pages_count": request.pages_count,
            "difficulty": request.difficulty,
            "include_answers": "да" if request.include_answers else "нет",
            "include_parent_instruction": "да" if request.include_parent_instruction else "нет",
        }

        prompt = build_prompt(params)
        logger.info(f"Generating pack: age={request.age}, topic={request.topic}, type={request.pack_type}")

        raw_json = None
        models_to_try = [self.client.model] + self.fallback_models

        for attempt, model in enumerate(models_to_try):
            if attempt > self.max_retries:
                break
            try:
                if model != self.client.model:
                    self.client.model = model
                    logger.info(f"Trying fallback model: {model}")

                raw_json = self.client.send_request(prompt)
                if raw_json:
                    break
            except Exception as e:
                logger.error(f"Attempt {attempt + 1} with {model} failed: {e}")
                if attempt == len(models_to_try) - 1:
                    result.error = f"Все попытки генерации не удались. Последняя ошибка: {e}"
                    return result
                continue

        if not raw_json:
            result.error = "AI не вернул ответ."
            return result

        raw_json = raw_json.strip()
        if raw_json.startswith("```"):
            raw_json = raw_json.strip("`").strip()
            if raw_json.startswith("json"):
                raw_json = raw_json[4:].strip()

        validation_result = full_validation(raw_json, request.pages_count, request.include_answers)

        if not validation_result.is_valid:
            logger.warning(f"Validation failed: {validation_result.errors}")
            repair_prompt = build_repair_prompt(raw_json)
            try:
                repaired = self.client.send_repair_request(repair_prompt)
                if repaired:
                    repaired = repaired.strip()
                    if repaired.startswith("```"):
                        repaired = repaired.strip("`").strip()
                        if repaired.startswith("json"):
                            repaired = repaired[4:].strip()
                    raw_json = repaired
                    validation_result = full_validation(raw_json, request.pages_count, request.include_answers)
            except Exception as e:
                logger.error(f"Repair attempt failed: {e}")

        if not validation_result.is_valid:
            result.error = "Не удалось получить корректный JSON от AI.\n"
            result.error += "\n".join(validation_result.errors)
            result.warnings = validation_result.warnings
            return result

        result.warnings = validation_result.warnings

        try:
            pack_data = json.loads(raw_json)
        except json.JSONDecodeError as e:
            result.error = f"Ошибка парсинга JSON: {e}"
            return result

        pack_data = sanitize_pack_data(pack_data)

        output_dir = request.output_dir
        os.makedirs(output_dir, exist_ok=True)

        date_str = datetime.now().strftime("%Y-%m-%d")
        base_name = f"StudyPack_{request.age}_{request.topic}_{date_str}"
        base_name = "".join(c if c.isalnum() or c in "-_" else "_" for c in base_name)

        json_path = os.path.join(output_dir, f"{base_name}.json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(pack_data, f, ensure_ascii=False, indent=2)
        logger.info(f"JSON saved: {json_path}")
        result.json_path = json_path

        try:
            pdf_path = os.path.join(output_dir, f"{base_name}.pdf")
            render_pdf(pack_data, pdf_path)
            result.pdf_path = pdf_path
            result.success = True
        except Exception as e:
            logger.error(f"PDF generation failed: {e}")
            result.error = f"Ошибка создания PDF: {e}"

        return result
