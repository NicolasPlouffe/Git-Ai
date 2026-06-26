from __future__ import annotations

import pytest

from git_ai.exceptions import ProviderResponseError
from git_ai.models import (
    CommitLanguage,
    DiffSource,
    GitDiff,
    LLMRequest,
    LLMResponse,
    PromptPayload,
    PromptRequest,
    ProviderInfo,
)
from git_ai.services.commit_message_service import CommitMessageService
from tests.conftest import make_prompt_request
from tests.unit.fakes import DummyProvider, DummyPromptService


class FakeProvider:
    @property
    def info(self) -> ProviderInfo:
        return ProviderInfo(name="fake")

    def generate(self, request: LLMRequest) -> LLMResponse:
        return LLMResponse(text="Commit message:\nfeat: add prompt builder")


class FakePromptService:
    def build_commit_prompt(self, request: PromptRequest) -> PromptPayload:
        return PromptPayload(
            system_prompt="SYSTEM",
            user_prompt="USER",
            metadata={"language": request.language.value},
        )


def test_generate_returns_commit_message() -> None:
    service = CommitMessageService(
        provider=FakeProvider(),
        prompt_service=FakePromptService(),
    )

    request = PromptRequest(
        diff=GitDiff(
            text="diff --git a/a.py b/a.py",
            files=("a.py",),
            source=DiffSource.STAGED,
        ),
        language=CommitLanguage.FRENCH,
        max_subject_length=72,
    )

    result = service.generate(request)

    assert result.text == "feat: add prompt builder"
    assert result.language is CommitLanguage.FRENCH


def test_generate_raises_on_empty_diff() -> None:
    service = CommitMessageService(
        provider=FakeProvider(),
        prompt_service=FakePromptService(),
    )

    request = PromptRequest(
        diff=GitDiff(text="   ", files=(), source=DiffSource.STAGED),
        language=CommitLanguage.FRENCH,
        max_subject_length=72,
    )

    with pytest.raises(ValueError):
        service.generate(request)


def test_generate_strips_markdown_fences() -> None:
    class FencedProvider:
        @property
        def info(self) -> ProviderInfo:
            return ProviderInfo(name="fake")

        def generate(self, request: LLMRequest) -> LLMResponse:
            return LLMResponse(text="```text\nfeat: add prompt builder\n```")

    service = CommitMessageService(
        provider=FencedProvider(),
        prompt_service=FakePromptService(),
    )

    request = PromptRequest(
        diff=GitDiff(
            text="diff --git a/a.py b/a.py",
            files=("a.py",),
            source=DiffSource.STAGED,
        ),
        language=CommitLanguage.ENGLISH,
        max_subject_length=72,
    )

    result = service.generate(request)

    assert result.text == "feat: add prompt builder"


def test_generate_truncates_long_subject() -> None:
    long_subject = "feat: " + "a" * 100

    class LongProvider:
        @property
        def info(self) -> ProviderInfo:
            return ProviderInfo(name="fake")

        def generate(self, request: LLMRequest) -> LLMResponse:
            return LLMResponse(text=long_subject)

    service = CommitMessageService(
        provider=LongProvider(),
        prompt_service=FakePromptService(),
    )

    request = PromptRequest(
        diff=GitDiff(
            text="diff --git a/a.py b/a.py",
            files=("a.py",),
            source=DiffSource.STAGED,
        ),
        language=CommitLanguage.ENGLISH,
        max_subject_length=20,
    )

    result = service.generate(request)

    assert len(result.subject) <= 20


def test_generate_keeps_clean_body() -> None:
    class BodyProvider:
        @property
        def info(self) -> ProviderInfo:
            return ProviderInfo(name="fake")

        def generate(self, request: LLMRequest) -> LLMResponse:
            return LLMResponse(
                text=(
                    "feat: add prompt builder\n\n"
                    "Add prompt loading service.\n"
                    "Normalize commit output."
                )
            )

    service = CommitMessageService(
        provider=BodyProvider(),
        prompt_service=FakePromptService(),
    )

    request = PromptRequest(
        diff=GitDiff(
            text="diff --git a/a.py b/a.py",
            files=("a.py",),
            source=DiffSource.STAGED,
        ),
        language=CommitLanguage.ENGLISH,
        max_subject_length=72,
    )

    result = service.generate(request)

    assert result.text == (
        "feat: add prompt builder\n\n"
        "Add prompt loading service.\n"
        "Normalize commit output."
    )


def test_generate_raises_on_empty_provider_response() -> None:
    class EmptyProvider:
        @property
        def info(self) -> ProviderInfo:
            return ProviderInfo(name="fake")

        def generate(self, request: LLMRequest) -> LLMResponse:
            return LLMResponse(text="   ")

    service = CommitMessageService(
        provider=EmptyProvider(),
        prompt_service=FakePromptService(),
    )

    request = PromptRequest(
        diff=GitDiff(
            text="diff --git a/a.py b/a.py",
            files=("a.py",),
            source=DiffSource.STAGED,
        ),
        language=CommitLanguage.ENGLISH,
        max_subject_length=72,
    )

    with pytest.raises(ProviderResponseError):
        service.generate(request)


def test_generate_strips_leading_empty_lines() -> None:
    class EmptyLinesProvider:
        @property
        def info(self) -> ProviderInfo:
            return ProviderInfo(name="fake")

        def generate(self, request: LLMRequest) -> LLMResponse:
            return LLMResponse(text="\n\nfeat: add prompt builder")

    service = CommitMessageService(
        provider=EmptyLinesProvider(),
        prompt_service=FakePromptService(),
    )

    request = PromptRequest(
        diff=GitDiff(
            text="diff --git a/a.py b/a.py",
            files=("a.py",),
            source=DiffSource.STAGED,
        ),
        language=CommitLanguage.ENGLISH,
        max_subject_length=72,
    )

    result = service.generate(request)

    assert result.text == "feat: add prompt builder"


def test_generate_strips_quotes_from_subject() -> None:
    class QuotesProvider:
        @property
        def info(self) -> ProviderInfo:
            return ProviderInfo(name="fake")

        def generate(self, request: LLMRequest) -> LLMResponse:
            return LLMResponse(text='"feat: add prompt builder"')

    service = CommitMessageService(
        provider=QuotesProvider(),
        prompt_service=FakePromptService(),
    )

    request = PromptRequest(
        diff=GitDiff(
            text="diff --git a/a.py b/a.py",
            files=("a.py",),
            source=DiffSource.STAGED,
        ),
        language=CommitLanguage.ENGLISH,
        max_subject_length=72,
    )

    result = service.generate(request)

    assert result.text == "feat: add prompt builder"


def test_generate_normalizes_body_by_removing_extra_blank_lines() -> None:
    class NoisyBodyProvider:
        @property
        def info(self) -> ProviderInfo:
            return ProviderInfo(name="fake")

        def generate(self, request: LLMRequest) -> LLMResponse:
            return LLMResponse(
                text=(
                    "feat: add prompt builder\n\n\n"
                    "Add prompt loading service.\n\n"
                    "Normalize commit output.\n"
                )
            )

    service = CommitMessageService(
        provider=NoisyBodyProvider(),
        prompt_service=FakePromptService(),
    )

    request = PromptRequest(
        diff=GitDiff(
            text="diff --git a/a.py b/a.py",
            files=("a.py",),
            source=DiffSource.STAGED,
        ),
        language=CommitLanguage.ENGLISH,
        max_subject_length=72,
    )

    result = service.generate(request)

    assert result.text == (
        "feat: add prompt builder\n\n"
        "Add prompt loading service.\n\n"
        "Normalize commit output."
    )


def test_generate_raises_when_sanitization_removes_all_content() -> None:
    class PrefixOnlyProvider:
        @property
        def info(self) -> ProviderInfo:
            return ProviderInfo(name="fake")

        def generate(self, request: LLMRequest) -> LLMResponse:
            return LLMResponse(text="Commit message:")

    service = CommitMessageService(
        provider=PrefixOnlyProvider(),
        prompt_service=FakePromptService(),
    )

    request = PromptRequest(
        diff=GitDiff(
            text="diff --git a/a.py b/a.py",
            files=("a.py",),
            source=DiffSource.STAGED,
        ),
        language=CommitLanguage.ENGLISH,
        max_subject_length=72,
    )

    with pytest.raises(ProviderResponseError):
        service.generate(request)


# --- Partie utilisant DummyProvider/DummyPromptService + make_prompt_request ---


def test_generate_raises_when_diff_is_empty() -> None:
    provider = DummyProvider("feat(cli): ajouter la commande")
    prompt_service = DummyPromptService()
    service = CommitMessageService(provider=provider, prompt_service=prompt_service)

    request = PromptRequest(
        diff=GitDiff(
            text="",
            files=(),
            source=DiffSource.STAGED,
        ),
        language=CommitLanguage.FRENCH,
        max_subject_length=50,
    )

    with pytest.raises(ValueError, match="empty diff"):
        service.generate(request)


def test_generate_raises_when_provider_returns_empty_message() -> None:
    provider = DummyProvider("")
    prompt_service = DummyPromptService()
    service = CommitMessageService(provider=provider, prompt_service=prompt_service)

    with pytest.raises(ProviderResponseError, match="empty commit message"):
        service.generate(make_prompt_request())


def test_generate_removes_code_fences_and_known_prefix() -> None:
    provider = DummyProvider(
        "```text\n"
        "Commit message:\n"
        "feat(cli): ajouter la commande de commit\n"
        "```"
    )
    prompt_service = DummyPromptService()
    service = CommitMessageService(provider=provider, prompt_service=prompt_service)

    result = service.generate(make_prompt_request())

    assert result.text == "feat(cli): ajouter la commande de commit"


def test_generate_removes_backticks_from_subject() -> None:
    provider = DummyProvider("feat(cli): ajouter la commande `commit`")
    prompt_service = DummyPromptService()
    service = CommitMessageService(provider=provider, prompt_service=prompt_service)

    result = service.generate(make_prompt_request())

    assert result.text == "feat(cli): ajouter la commande commit"


def test_generate_truncates_subject_and_removes_incomplete_ending_dummy() -> None:
    provider = DummyProvider(
        "feat(cli): ajouter la commande de commit avec interface utilisateur complete"
    )
    prompt_service = DummyPromptService()
    service = CommitMessageService(provider=provider, prompt_service=prompt_service)

    request = make_prompt_request(
        max_subject_length=49,  # attention: adapter au nom exact de ton champ
    )

    result = service.generate(request)

    assert result.text == "feat(cli): ajouter la commande de commit"
    assert len(result.text) <= 49


def test_generate_keeps_clean_body_when_present_dummy() -> None:
    provider = DummyProvider(
        "feat(cli): ajouter la commande de commit\n\n"
        "- ajoute le flux principal\n"
        "\n"
        "  nettoie la sortie du provider  \n"
    )
    prompt_service = DummyPromptService()
    service = CommitMessageService(provider=provider, prompt_service=prompt_service)

    result = service.generate(make_prompt_request())

    assert result.text == (
        "feat(cli): ajouter la commande de commit\n\n"
        "- ajoute le flux principal\n\n"
        "nettoie la sortie du provider"
    )


def test_generate_passes_prompt_to_provider() -> None:
    provider = DummyProvider("feat(cli): ajouter la commande de commit")
    prompt_service = DummyPromptService()
    service = CommitMessageService(
        provider=provider,
        prompt_service=prompt_service,
        temperature=0.3,
        max_tokens=80,
    )

    service.generate(make_prompt_request())

    assert len(provider.calls) == 1
    llm_request = provider.calls[0]
    assert llm_request.prompt == "user"
    assert llm_request.system_prompt == "system"
    assert llm_request.temperature == 0.3
    assert llm_request.max_tokens == 80


def test_generate_removes_backticks_in_body() -> None:
    class BacktickBodyProvider:
        @property
        def info(self) -> ProviderInfo:
            return ProviderInfo(name="fake")

        def generate(self, request: LLMRequest) -> LLMResponse:
            return LLMResponse(
                text=(
                    "feat: add prompt builder\n\n"
                    "Use `PromptService` to build prompts.\n"
                    "Normalize `CommitMessageService` output.\n"
                )
            )

    service = CommitMessageService(
        provider=BacktickBodyProvider(),
        prompt_service=FakePromptService(),
    )

    request = PromptRequest(
        diff=GitDiff(
            text="diff --git a/a.py b/a.py",
            files=("a.py",),
            source=DiffSource.STAGED,
        ),
        language=CommitLanguage.ENGLISH,
        max_subject_length=72,
    )

    result = service.generate(request)

    assert result.text == (
        "feat: add prompt builder\n\n"
        "Use PromptService to build prompts.\n"
        "Normalize CommitMessageService output."
    )


def test_truncate_subject_never_returns_empty() -> None:
    class ShortLimitProvider:
        @property
        def info(self) -> ProviderInfo:
            return ProviderInfo(name="fake")

        def generate(self, request: LLMRequest) -> LLMResponse:
            return LLMResponse(text="feat: add prompt builder")

    service = CommitMessageService(
        provider=ShortLimitProvider(),
        prompt_service=FakePromptService(),
    )

    request = PromptRequest(
        diff=GitDiff(
            text="diff --git a/a.py b/a.py",
            files=("a.py",),
            source=DiffSource.STAGED,
        ),
        language=CommitLanguage.ENGLISH,
        max_subject_length=5,
    )

    result = service.generate(request)

    assert result.text  # non vide
    assert len(result.text) <= 5


def test_generate_truncates_subject_and_removes_incomplete_ending_weak() -> None:
    class WeakEndingProvider:
        @property
        def info(self) -> ProviderInfo:
            return ProviderInfo(name="fake")

        def generate(self, request: LLMRequest) -> LLMResponse:
            return LLMResponse(
                text=(
                    "feat(cli): ajouter la commande de commit avec interface "
                    "utilisateur complete"
                )
            )

    service = CommitMessageService(
        provider=WeakEndingProvider(),
        prompt_service=FakePromptService(),
    )

    request = PromptRequest(
        diff=GitDiff(
            text="diff --git a/a.py b/a.py",
            files=("a.py",),
            source=DiffSource.STAGED,
        ),
        language=CommitLanguage.FRENCH,
        max_subject_length=47,
    )

    result = service.generate(request)

    assert result.text == "feat(cli): ajouter la commande de commit"


def test_generate_removes_prompt_echo_from_response() -> None:
    class PromptEchoProvider:
        @property
        def info(self) -> ProviderInfo:
            return ProviderInfo(name="fake")

        def generate(self, request: LLMRequest) -> LLMResponse:
            return LLMResponse(
                text=(
                    "refactor(cli): nettoyer la sortie du provider\n"
                    "Rédige un message de commit Git à partir du diff fourni.\n"
                    "Contraintes :\n"
                    "- Langue de sortie : français\n"
                )
            )

    service = CommitMessageService(
        provider=PromptEchoProvider(),
        prompt_service=FakePromptService(),
    )

    request = PromptRequest(
        diff=GitDiff(
            text="diff --git a/a.py b/a.py",
            files=("a.py",),
            source=DiffSource.STAGED,
        ),
        language=CommitLanguage.FRENCH,
        max_subject_length=72,
    )

    result = service.generate(request)

    assert result.text == "refactor(cli): nettoyer la sortie du provider"