from __future__ import annotations

import json
from typing import Any
from urllib import error, request as urllib_request

from git_ai.exceptions import (
    ProviderConnectionError,
    ProviderError,
    ProviderResponseError,
)
from git_ai.models import LLMRequest, LLMResponse, ProviderInfo


class OllamaProvider:
    """Provider LLM pour Ollama via l'API OpenAI-compatible."""

    def __init__(
        self,
        model: str,
        base_url: str = "http://localhost:11434",
        timeout: float = 60.0,
    ) -> None:
        self._model = model
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout

    # --- Métadonnées pour logging/debugging ---------------------------------

    @property
    def info(self) -> ProviderInfo:
        return ProviderInfo(
            name="ollama",
            model=self._model,
            endpoint=self.chat_completions_url,
            extra={"transport": "openai-compatible"},
        )

    @property
    def chat_completions_url(self) -> str:
        if self._base_url.endswith("/v1"):
            return f"{self._base_url}/chat/completions"
        return f"{self._base_url}/v1/chat/completions"

    # --- API LLMProvider ----------------------------------------------------

    def generate(self, request: LLMRequest) -> LLMResponse:
        payload = self._build_payload(request)
        raw_data = self._post_json(payload)
        text = self._extract_text(raw_data)

        return LLMResponse(
            text=text,
            model_name=self._extract_model_name(raw_data),
            raw_response=raw_data,
        )

    # --- Construction du payload -------------------------------------------

    def _build_payload(self, request: LLMRequest) -> dict[str, Any]:
        messages: list[dict[str, str]] = []

        if request.system_prompt:
            messages.append(
                {
                    "role": "system",
                    "content": request.system_prompt,
                }
            )

        messages.append(
            {
                "role": "user",
                "content": request.prompt,
            }
        )

        payload: dict[str, Any] = {
            "model": self._model,
            "messages": messages,
            "temperature": request.temperature,
            "stream": False,
        }

        if request.max_tokens is not None:
            payload["max_tokens"] = request.max_tokens

        return payload

    # --- Appel HTTP (urllib, pas de dépendance externe) --------------------

    def _post_json(self, payload: dict[str, Any]) -> dict[str, Any]:
        body = json.dumps(payload).encode("utf-8")
        http_request = urllib_request.Request(
            url=self.chat_completions_url,
            data=body,
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
            method="POST",
        )

        try:
            with urllib_request.urlopen(http_request, timeout=self._timeout) as response:
                raw_body = response.read().decode("utf-8")
        except error.HTTPError as exc:
            error_body = exc.read().decode("utf-8", errors="replace")
            raise ProviderError(
                f"Ollama a renvoyé une erreur HTTP {exc.code}: {error_body}"
            ) from exc
        except error.URLError as exc:
            raise ProviderConnectionError(
                f"Impossible de joindre Ollama à {self.chat_completions_url}: {exc.reason}"
            ) from exc
        except TimeoutError as exc:
            raise ProviderConnectionError(
                f"Ollama n'a pas répondu dans le délai imparti ({self._timeout}s)"
            ) from exc
        except OSError as exc:
            raise ProviderConnectionError(
                f"Erreur réseau lors de l'appel à Ollama: {exc}"
            ) from exc

        try:
            data = json.loads(raw_body)
        except json.JSONDecodeError as exc:
            raise ProviderResponseError(
                "Réponse Ollama non JSON ou invalide"
            ) from exc

        if not isinstance(data, dict):
            raise ProviderResponseError(
                "Réponse Ollama invalide: objet JSON attendu"
            )

        return data

    # --- Normalisation de la réponse ---------------------------------------

    def _extract_text(self, data: dict[str, Any]) -> str:
        try:
            content = data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise ProviderResponseError(
                "Structure de réponse Ollama inattendue: champ texte introuvable"
            ) from exc

        normalized = self._normalize_text(content)

        if not normalized:
            raise ProviderResponseError("Ollama a renvoyé un contenu vide")

        return normalized

    def _extract_model_name(self, data: dict[str, Any]) -> str:
        model_name = data.get("model", self._model)
        return model_name if isinstance(model_name, str) else self._model

    @staticmethod
    def _normalize_text(content: Any) -> str:
        if content is None:
            return ""

        if not isinstance(content, str):
            content = str(content)

        return content.strip()