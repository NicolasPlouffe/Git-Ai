from __future__ import annotations

from git_ai.models import LLMRequest, LLMResponse, PromptPayload, PromptRequest, ProviderInfo


class FakeProvider:
    def __init__(self, response_text: str = "feat: default fake commit message") -> None:
        self.response_text = response_text
        self.requests: list[LLMRequest] = []

    @property
    def info(self) -> ProviderInfo:
        return ProviderInfo(name="fake", model_name="test-double")

    def generate(self, request: LLMRequest) -> LLMResponse:
        self.requests.append(request)
        return LLMResponse(
            text=self.response_text,
            model_name="test-double",
            raw_response={"ok": True},
        )


class DummyProvider:
    def __init__(self, response_text: str) -> None:
        self.response_text = response_text
        self.calls: list[LLMRequest] = []

    @property
    def info(self) -> ProviderInfo:
        return ProviderInfo(name="fake", model_name="dummy-provider")

    def generate(self, request: LLMRequest) -> LLMResponse:
        self.calls.append(request)
        return LLMResponse(text=self.response_text, model_name="dummy-provider")


class DummyPromptService:
    def build_commit_prompt(self, request: PromptRequest) -> PromptPayload:
        return PromptPayload(
            system_prompt="system",
            user_prompt="user",
            metadata={"language": request.language.value},
        )


class StaticResponseProvider:
    def __init__(self, text: str) -> None:
        self.text = text

    @property
    def info(self) -> ProviderInfo:
        return ProviderInfo(name="fake", model_name="static-response")

    def generate(self, request: LLMRequest) -> LLMResponse:
        return LLMResponse(text=self.text, model_name="static-response")