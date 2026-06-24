from __future__ import annotations

from typing import Protocol, runtime_checkable

from git_ai.models import LLMRequest, LLMResponse, ProviderInfo


@runtime_checkable
class LLMProvider(Protocol):
    def generate(self, request: LLMRequest) -> LLMResponse:
        """Generate a text completion from a normalized request."""

    @property
    def info(self) -> ProviderInfo:
        """Return provider metadata useful for logging/debugging."""