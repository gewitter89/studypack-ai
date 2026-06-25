import json
import os
import logging
import time
from datetime import datetime
from typing import Dict, Any, Optional

from core.models import PackRequest
import core.paths
from ai.cascade_client import CascadeClient
from ai.prompt_builder import build_prompt, build_repair_prompt
from core.validator import full_validation
from core.sanitizer import sanitize_pack_data, check_topic_and_replace
from core.math_checker import verify_math_in_pack
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
        self.math_issues: list = []


class StudyPackGenerator:
    def __init__(self):
        self.settings = load_settings()
        self.client = CascadeClient(
            model=self.settings.get("default_model", "llama3-70b-8192"),
            temperature=self.settings.get("temperature", 0.7),
            max_tokens=self.settings.get("max_tokens", 8000),
        )
        self.max_retries = self.settings.get("max_retries", 2)

    def _clean_raw_json(self, raw: str) -> str:
        raw = raw.strip()
        if raw.startswith("```"):
            raw = raw.strip("`").strip()
            if raw.startswith("json"):
                raw = raw[4:].strip()
        return raw

    def _request_json(self, prompt: str, label: str = "") -> Optional[str]:
        for attempt in range(self.max_retries + 1):
            try:
                raw = self.client.send_request(prompt)
                if raw:
                    return self._clean_raw_json(raw)
            except Exception as e:
                logger.error(f"Attempt {attempt + 1} {label} failed: {e}")
                if attempt == self.max_retries:
                    raise
                time.sleep(2)
                continue
        return None

    def _generate_single_block(self, params: dict, block_label: str) -> Optional[Dict]:
        prompt = build_prompt(params)
        raw = self._request_json(prompt, block_label)
        if not raw:
            return None

        from core.validator import validate_json_structure
        val_res = full_validation(raw, params["pages_count"], True)
        valid, data, err = validate_json_structure(raw)
        
        if (not val_res.is_valid or not valid) and val_res.errors:
            logger.warning(f"Validation failed for {block_label}, attempting repair: {val_res.errors}")
            repair_prompt = build_repair_prompt(raw)
            try:
                repaired = self._request_json(repair_prompt, f"repair-{block_label}")
                if repaired:
                    val_res2 = full_validation(repaired, params["pages_count"], True)
                    valid2, data2, err2 = validate_json_structure(repaired)
                    if val_res2.is_valid and valid2:
                        return data2
            except Exception as e:
                logger.error(f"Repair failed: {e}")

        if val_res.is_valid and valid:
            return data
        return None

    def generate(self, request: PackRequest) -> GenerationResult:
        result = GenerationResult()

        if not request.offline_mode and not self.client.is_configured():
            result.error = "API ключ не настроен. Создайте файл .env и укажите OPENROUTER_API_KEY, GROQ_API_KEY, DEEPSEEK_API_KEY или GEMINI_API_KEY."
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

        logger.info(f"Generating: age={request.age}, topic={request.topic}, type={request.pack_type}")

        if request.pages_count > 20:
            return self._generate_blocked(request, params, result)
        else:
            return self._generate_single(request, params, result)

    def _generate_single(self, request, params, result):
        try:
            raw = self._request_json(build_prompt(params), "main")
            if not raw:
                result.error = "AI не вернул ответ."
                return result
        except Exception as e:
            result.error = f"Ошибка генерации: {e}"
            return result

        validation_result = full_validation(raw, request.pages_count, request.include_answers)

        if not validation_result.is_valid:
            logger.warning(f"Validation failed: {validation_result.errors}")
            repair_prompt = build_repair_prompt(raw)
            try:
                repaired = self._request_json(repair_prompt, "repair")
                if repaired:
                    raw = repaired
                    validation_result = full_validation(raw, request.pages_count, request.include_answers)
            except Exception as e:
                logger.error(f"Repair failed: {e}")

        if not validation_result.is_valid:
            result.error = "Не удалось получить корректный JSON от AI.\n"
            result.error += "\n".join(validation_result.errors)
            result.warnings = validation_result.warnings
            return result

        result.warnings = validation_result.warnings

        try:
            pack_data = json.loads(raw)
        except json.JSONDecodeError as e:
            result.error = f"Ошибка парсинга JSON: {e}"
            return result

        return self._finalize(pack_data, request, result)

    def _generate_blocked(self, request, params, result):
        logger.info(f"Block generation for {request.pages_count} pages")
        all_pages = []
        all_answers = []
        parent_instruction = ""
        title = ""
        subtitle = ""

        block_size = 10
        num_blocks = (request.pages_count + block_size - 1) // block_size
        offset = 0

        for block_idx in range(num_blocks):
            block_pages = min(block_size, request.pages_count - offset)
            block_params = dict(params)
            block_params["pages_count"] = block_pages
            block_params["topic"] = f"{request.topic} (блок {block_idx + 1} из {num_blocks})"
            block_params["include_parent_instruction"] = "нет" if block_idx > 0 else params["include_parent_instruction"]

            try:
                data = self._generate_single_block(block_params, f"block-{block_idx + 1}")
                if data is None:
                    result.warnings.append(f"Блок {block_idx + 1} не удалось сгенерировать.")
                    continue

                if block_idx == 0:
                    title = data.get("title", "")
                    subtitle = data.get("subtitle", "")
                    parent_instruction = data.get("parent_instruction", "")

                for page in data.get("pages", []):
                    new_pn = offset + page["page_number"]
                    page["page_number"] = new_pn
                    all_pages.append(page)

                for ans in data.get("answers", []):
                    new_pn = offset + ans["page_number"]
                    ans["page_number"] = new_pn
                    all_answers.append(ans)

                offset += block_pages
            except Exception as e:
                logger.error(f"Block {block_idx + 1} error: {e}")
                result.warnings.append(f"Ошибка блока {block_idx + 1}: {e}")

        if not all_pages:
            result.error = "Не удалось сгенерировать ни одного блока."
            return result

        pack_data = {
            "title": title or "StudyPack",
            "subtitle": subtitle or "",
            "language": request.language,
            "age": request.age,
            "grade": request.grade,
            "topic": request.topic,
            "pack_type": request.pack_type,
            "difficulty": request.difficulty,
            "parent_instruction": parent_instruction,
            "pages": all_pages,
            "answers": all_answers,
        }

        return self._finalize(pack_data, request, result)

    def _finalize(self, pack_data: dict, request, result) -> GenerationResult:
        pack_data = sanitize_pack_data(pack_data)
        from core.postprocess import postprocess
        pack_data = postprocess(pack_data)

        # Quality Gate enforcement
        quality = pack_data.get("_quality", {})
        if not quality.get("passed", True) or quality.get("hard_fails"):
            result.success = False
            result.error = "Quality gate HARD FAIL:\n" + "\n".join(quality.get("hard_fails", []))
            return result

        if quality.get("commercial_fails"):
            result.warnings.extend(quality.get("commercial_fails", []))
            # In commercial mode, a commercial fail is a hard error
            if getattr(request, 'commercial_mode', False):
                result.success = False
                result.error = "Quality gate COMMERCIAL FAIL:\n" + "\n".join(quality.get("commercial_fails", []))
                return result

        math_issues = verify_math_in_pack(pack_data)
        result.math_issues = math_issues
        if math_issues:
            warnings = [f"Стр.{i['page']}: {i['question']}" for i in math_issues[:10]]
            result.warnings.append(f"Найдено {len(math_issues)} ошибок в математике:")
            result.warnings.extend(warnings)

        output_dir = request.output_dir or core.paths.output_dir()
        os.makedirs(output_dir, exist_ok=True)

        date_str = datetime.now().strftime("%Y-%m-%d")
        base_name = f"StudyPack_{request.age}_{request.topic}_{date_str}"
        base_name = "".join(c if c.isalnum() or c in "-_" else "_" for c in base_name)

        json_path = os.path.join(output_dir, f"{base_name}.json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(pack_data, f, ensure_ascii=False, indent=2)
        logger.info(f"JSON saved: {json_path}")
        result.json_path = json_path

        is_commercial = getattr(request, 'commercial_mode', False)
        brand_name = getattr(request, 'brand_name', "")

        try:
            pdf_path = os.path.join(output_dir, f"{base_name}.pdf")
            render_pdf(
                pack_data, pdf_path,
                watermark="" if is_commercial else "Демо-набір StudyPack AI",
                is_commercial=is_commercial,
                brand=brand_name,
            )
            result.pdf_path = pdf_path
            result.success = True
        except Exception as e:
            logger.error(f"PDF generation failed: {e}")
            result.error = f"Ошибка создания PDF: {e}"

        return result
