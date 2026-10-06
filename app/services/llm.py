import json
from abc import ABC, abstractmethod
from typing import TypeVar

import httpx
from pydantic import BaseModel

from app.core.config import settings

T = TypeVar("T", bound=BaseModel)


class LLMError(RuntimeError):
    """Raised when the configured LLM provider cannot complete a request."""


class LLMService(ABC):
    @abstractmethod
    def generate_structured(
        self,
        prompt: str,
        response_model: type[T],
    ) -> T:
        raise NotImplementedError


class OpenAICompatibleLLMService(LLMService):
    def __init__(self) -> None:
        if not settings.llm_api_key:
            raise LLMError("LLM_API_KEY is not configured.")
        self._api_key = settings.llm_api_key
        self._base_url = settings.llm_base_url.rstrip("/")
        self._model = settings.llm_model
        if not self._model:
            raise LLMError("LLM_MODEL is required for an OpenAI-compatible provider.")

    def generate_structured(self, prompt: str, response_model: type[T]) -> T:
        schema = response_model.model_json_schema()
        payload = {
            "model": self._model,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "Return ONLY valid JSON matching the supplied JSON schema. "
                        "Do not wrap the JSON in markdown fences."
                    ),
                },
                {
                    "role": "user",
                    "content": f"{prompt}\n\nJSON schema:\n{json.dumps(schema)}",
                },
            ],
            "temperature": 0,
            "response_format": {"type": "json_object"},
        }
        try:
            response = httpx.post(
                f"{self._base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self._api_key}",
                    "Content-Type": "application/json",
                },
                json=payload,
                timeout=60,
            )
            response.raise_for_status()
            data = response.json()
            content = data["choices"][0]["message"]["content"]
            if isinstance(content, list):
                content = "".join(
                    part.get("text", "") for part in content if isinstance(part, dict)
                )
            if not content:
                raise LLMError("LLM returned an empty response.")
            return response_model.model_validate_json(content)
        except LLMError:
            raise
        except Exception as exc:
            raise LLMError("OpenAI-compatible LLM request failed.") from exc


class GeminiLLMService(LLMService):
    def __init__(self) -> None:
        if not settings.llm_api_key:
            raise LLMError("LLM_API_KEY is not configured.")

        from google import genai

        self._client = genai.Client(api_key=settings.llm_api_key)
        self._model = settings.llm_model or "gemini-2.5-flash"

    def generate_structured(
        self,
        prompt: str,
        response_model: type[T],
    ) -> T:
        try:
            response = self._client.models.generate_content(
                model=self._model,
                contents=prompt,
                config={
                    "response_mime_type": "application/json",
                    "response_schema": response_model,
                },
            )
            if not response.text:
                raise LLMError("LLM returned an empty response.")
            return response_model.model_validate_json(response.text)
        except LLMError:
            raise
        except Exception as exc:
            raise LLMError("Gemini request failed.") from exc


def get_llm_service() -> LLMService:
    provider = settings.llm_provider.lower()
    if provider == "gemini":
        return GeminiLLMService()
    if provider in {"openai", "openai_compatible"}:
        return OpenAICompatibleLLMService()
    raise LLMError(f"Unsupported LLM provider: {settings.llm_provider}")
