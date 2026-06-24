from __future__ import annotations

import json
from unittest.mock import patch

import pytest

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


def test_generate_returns_normalized_text():
    provider = OllamaProvider(model="qwen2.5-coder:7b")
    request = LLMRequest(
        system_prompt="Return only a commit message.",
        prompt="Add --dry-run option to CLI.",
        temperature=0.1,
        max_tokens=60,
    )

    payload = {
        "model": "qwen2.5-coder:7b",
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
    assert result.model_name == "qwen2.5-coder:7b"
    assert not result.is_empty


def test_generate_raises_response_error_on_missing_content():
    provider = OllamaProvider(model="qwen2.5-coder:7b")
    request = LLMRequest(prompt="Generate a commit message")

    payload = {"choices": []}

    with patch(
        "git_ai.providers.ollama.urllib_request.urlopen",
        return_value=DummyHTTPResponse(payload),
    ):
        with pytest.raises(ProviderResponseError):
            provider.generate(request)


def test_generate_raises_connection_error_on_url_error():
    provider = OllamaProvider(model="qwen2.5-coder:7b")
    request = LLMRequest(prompt="Generate a commit message")

    from urllib import error as urllib_error

    with patch(
        "git_ai.providers.ollama.urllib_request.urlopen",
        side_effect=urllib_error.URLError("boom"),
    ):
        with pytest.raises(ProviderConnectionError):
            provider.generate(request)