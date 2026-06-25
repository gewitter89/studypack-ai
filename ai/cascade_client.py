import os
import json
import logging
import time
from typing import Optional

import requests
from openai import OpenAI
from dotenv import load_dotenv
from core.paths import env_file_path

load_dotenv(env_file_path())

logger = logging.getLogger(__name__)


class CascadeClient:
    def __init__(
        self,
        model: str = "llama3-70b-8192",
        temperature: float = 0.7,
        max_tokens: int = 8000,
    ):
        self.temperature = temperature
        self.max_tokens = max_tokens
        self._model = model
        self._providers = self._init_providers()

    def _init_providers(self):
        return [
            _OpenRouterProvider(self.temperature, self.max_tokens),
            _GroqProvider(self.temperature, self.max_tokens),
            _DeepSeekProvider(self.temperature, self.max_tokens),
            _GeminiProvider(self.temperature, self.max_tokens),
        ]

    @property
    def model(self):
        return self._model

    @model.setter
    def model(self, value):
        self._model = value

    def is_configured(self) -> bool:
        for p in self._providers:
            if p.is_configured():
                return True
        return False

    def send_request(self, prompt: str) -> Optional[str]:
        last_error = None
        for provider in self._providers:
            if not provider.is_configured():
                logger.info(f"Skipping {provider.name}: not configured")
                continue
            try:
                logger.info(f"Trying {provider.name}...")
                result = provider.send_request(prompt)
                if result:
                    logger.info(f"{provider.name} succeeded")
                    return result
            except Exception as e:
                logger.warning(f"{provider.name} failed: {e}")
                last_error = e
                continue
        raise RuntimeError(
            f"All providers failed. Last error: {last_error}"
        )

    def send_repair_request(self, prompt: str) -> Optional[str]:
        return self.send_request(prompt)


class _GroqProvider:
    def __init__(self, temperature: float, max_tokens: int):
        self.name = "Groq"
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.api_key = os.getenv("GROQ_API_KEY", "")
        self.model = os.getenv("GROQ_MODEL", "llama3-70b-8192")
        self.base_url = "https://api.groq.com/openai/v1"

    def is_configured(self) -> bool:
        return bool(self.api_key) and self.api_key != "your_key_here"

    def send_request(self, prompt: str) -> Optional[str]:
        if not self.is_configured():
            raise ValueError("Groq API key not configured")

        client = OpenAI(api_key=self.api_key, base_url=self.base_url)
        response = client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            timeout=60,
        )
        return response.choices[0].message.content


class _DeepSeekProvider:
    def __init__(self, temperature: float, max_tokens: int):
        self.name = "DeepSeek"
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.api_key = os.getenv("DEEPSEEK_API_KEY", "")
        self.model = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
        self.base_url = "https://api.deepseek.com/v1"

    def is_configured(self) -> bool:
        return bool(self.api_key) and self.api_key != "your_key_here"

    def send_request(self, prompt: str) -> Optional[str]:
        if not self.is_configured():
            raise ValueError("DeepSeek API key not configured")

        client = OpenAI(api_key=self.api_key, base_url=self.base_url)
        response = client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            timeout=60,
        )
        return response.choices[0].message.content


class _GeminiProvider:
    def __init__(self, temperature: float, max_tokens: int):
        self.name = "Gemini"
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.api_key = os.getenv("GEMINI_API_KEY", "")
        self.model = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")

    def is_configured(self) -> bool:
        return bool(self.api_key) and self.api_key != "your_key_here"

    def send_request(self, prompt: str) -> Optional[str]:
        if not self.is_configured():
            raise ValueError("Gemini API key not configured")

        try:
            from google import genai
            client = genai.Client(api_key=self.api_key)
            response = client.models.generate_content(
                model=self.model,
                contents=prompt,
                config={
                    "temperature": self.temperature,
                    "max_output_tokens": self.max_tokens,
                },
            )
            return response.text
        except Exception:
            import google.generativeai as genai_old
            genai_old.configure(api_key=self.api_key)
            model = genai_old.GenerativeModel(self.model)
            response = model.generate_content(prompt)
            return response.text


class _OpenRouterProvider:
    def __init__(self, temperature: float, max_tokens: int):
        self.name = "OpenRouter"
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.api_key = os.getenv("OPENROUTER_API_KEY", "")
        self.model = os.getenv("OPENROUTER_MODEL", "meta-llama/llama-3.3-70b-instruct:free")

    def is_configured(self) -> bool:
        return bool(self.api_key) and self.api_key != "your_key_here"

    def send_request(self, prompt: str) -> Optional[str]:
        if not self.is_configured():
            raise ValueError("OpenRouter API key not configured")
        from ai.openrouter_client import OpenRouterClient
        client = OpenRouterClient(
            api_key=self.api_key,
            model=self.model,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
        )
        return client.send_request(prompt)

