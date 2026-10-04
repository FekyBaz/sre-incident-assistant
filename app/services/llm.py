from abc import ABC, abstractmethod
from typing import TypeVar

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
    raise LLMError(f"Unsupported LLM provider: {settings.llm_provider}")
