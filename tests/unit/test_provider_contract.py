from git_ai.models import LLMRequest
from git_ai.providers.base import LLMProvider
from tests.unit.fakes import FakeProvider


def test_fake_provider_satisfies_llm_provider_protocol():
    provider = FakeProvider()

    assert isinstance(provider, LLMProvider)


def test_fake_provider_returns_configured_response():
    provider = FakeProvider(response_text="fix: normalize empty provider output")

    response = provider.generate(
        LLMRequest(
            prompt="Generate a commit message",
            system_prompt="You generate git commit messages.",
        )
    )

    assert response.text == "fix: normalize empty provider output"
    assert response.model_name == "test-double"


def test_fake_provider_keeps_received_requests():
    provider = FakeProvider()

    request = LLMRequest(
        prompt="Summarize this diff",
        system_prompt="Return one commit message only.",
    )
    provider.generate(request)

    assert len(provider.requests) == 1
    assert provider.requests[0] == request