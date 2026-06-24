from git_ai.models import LLMRequest, LLMResponse, ProviderInfo


class FakeProvider:
    def __init__(self, response_text: str = "feat: default fake commit message") -> None:
        self._response_text = response_text
        self.requests: list[LLMRequest] = []

    @property
    def info(self) -> ProviderInfo:
        return ProviderInfo(name="fake", model="test-double")

    def generate(self, request: LLMRequest) -> LLMResponse:
        self.requests.append(request)
        return LLMResponse(
            text=self._response_text,
            model_name="test-double",
            raw_response={"ok": True},
        )