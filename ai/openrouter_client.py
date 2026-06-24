import os
import json
import logging
from typing import Optional

import requests
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


class OpenRouterClient:
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "openrouter/free",
        temperature: float = 0.7,
        max_tokens: int = 8000,
    ):
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY", "")
        self.model = model or os.getenv("OPENROUTER_MODEL", "openrouter/free")
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"

    def is_configured(self) -> bool:
        return bool(self.api_key) and self.api_key != "your_key_here"

    def send_request(self, prompt: str) -> Optional[str]:
        if not self.is_configured():
            logger.error("API key not configured")
            raise ValueError("API ключ не настроен. Проверьте .env файл.")

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://studypack-ai.local",
        }

        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
        }

        logger.info(f"Sending request to OpenRouter model: {self.model}")

        try:
            response = requests.post(
                self.base_url,
                headers=headers,
                json=payload,
                timeout=60,
            )
            response.raise_for_status()
            data = response.json()
            content = data["choices"][0]["message"]["content"]
            logger.info("OpenRouter request successful")
            return content
        except requests.exceptions.Timeout:
            logger.error("OpenRouter request timeout")
            raise ConnectionError("Таймаут запроса к OpenRouter. Проверьте интернет.")
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Connection error: {e}")
            raise ConnectionError("Нет подключения к OpenRouter. Проверьте интернет.")
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error: {e}, response: {e.response.text if hasattr(e, 'response') else ''}")
            status = e.response.status_code if hasattr(e, 'response') else 0
            if status == 402:
                raise RuntimeError("Недостаточно средств на аккаунте OpenRouter.")
            elif status == 429:
                raise RuntimeError("Превышен лимит запросов OpenRouter.")
            elif status == 401:
                raise RuntimeError("Неверный API ключ OpenRouter.")
            else:
                raise RuntimeError(f"Ошибка OpenRouter API (код {status}).")
        except (KeyError, IndexError, json.JSONDecodeError) as e:
            logger.error(f"Failed to parse OpenRouter response: {e}")
            raise RuntimeError("Ошибка обработки ответа от OpenRouter.")

    def send_repair_request(self, prompt: str) -> Optional[str]:
        return self.send_request(prompt)
