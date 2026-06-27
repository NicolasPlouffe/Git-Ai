from __future__ import annotations

import json
from unittest.mock import patch

import pytest

from git_ai.config import DEFAULT_MODEL
from git_ai.exceptions import ProviderConnectionError, ProviderResponseError
from git_ai.models import LLMRequest
from git_ai.providers.ollama import OllamaProvider


class DummyHTTPResponse:
    def __init__(self, payload: dict):
        self._payload = json.dumps(payload).encode("utf-8")

    def read(self) -> bytes:
        return self._payload

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


def test_generate_returns_normalized_text() -> None:
    provider = OllamaProvider(model=DEFAULT_MODEL)
    request = LLMRequest(
        system_prompt="Return only a commit message.",
        prompt="Add --dry-run option to CLI.",
        temperature=0.1,
        max_tokens=60,
    )

    payload = {
        "model": DEFAULT_MODEL,
        "choices": [
            {
                "message": {
                    "content": "  feat(cli): add dry-run option \n"
                }
            }
        ],
    }

    with patch(
        "git_ai.providers.ollama.urllib_request.urlopen",
        return_value=DummyHTTPResponse(payload),
    ):
        result = provider.generate(request)

    assert result.text == "feat(cli): add dry-run option"
    assert result.model_name == DEFAULT_MODEL
    assert not result.is_empty


def test_generate_raises_response_error_on_missing_content() -> None:
    provider = OllamaProvider(model=DEFAULT_MODEL)
    request = LLMRequest(prompt="Generate a commit message")

    payload = {"choices": []}

    with patch(
        "git_ai.providers.ollama.urllib_request.urlopen",
        return_value=DummyHTTPResponse(payload),
    ):
        with pytest.raises(ProviderResponseError):
            provider.generate(request)


def test_generate_raises_connection_error_on_url_error() -> None:
    provider = OllamaProvider(model=DEFAULT_MODEL)
    request = LLMRequest(prompt="Generate a commit message")

    from urllib import error as urllib_error

    with patch(
        "git_ai.providers.ollama.urllib_request.urlopen",
        side_effect=urllib_error.URLError("boom"),
    ):
        with pytest.raises(ProviderConnectionError):
            provider.generate(request)