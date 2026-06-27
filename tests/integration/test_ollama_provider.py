from __future__ import annotations

import os

import pytest

from git_ai.models import LLMRequest
from git_ai.providers.ollama import OllamaProvider
from git_ai.config import DEFAULT_MODEL


OLLAMA_BASE_URL = os.getenv("GIT_AI_OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("GIT_AI_OLLAMA_MODEL", DEFAULT_MODEL)


@pytest.mark.integration
def test_ollama_provider_generate_returns_text():
    provider = OllamaProvider(
        model=OLLAMA_MODEL,
        base_url=OLLAMA_BASE_URL,
        timeout=30.0,
    )

    request = LLMRequest(
        system_prompt="Return only a short git commit message.",
        prompt="Add --dry-run option to CLI and update unit tests.",
        temperature=0.1,
        max_tokens=60,
    )

    response = provider.generate(request)

    assert response.text
    assert isinstance(response.text, str)
    assert not response.is_empty