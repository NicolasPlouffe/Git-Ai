import pytest

from git_ai.models import (
    CommitLanguage,
    DiffSource,
    GitDiff,
    LLMResponse,
    PromptPayload,
    PromptRequest,
    ProviderInfo,
)
from git_ai.exceptions import ProviderResponseError
from git_ai.services.commit_message_service import CommitMessageService

class FakeProvider:
    @property
    def info(self) -> ProviderInfo:
        return ProviderInfo(name="fake")

    def generate(self, request):
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

        def generate(self, request):
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

        def generate(self, request):
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

        def generate(self, request):
            return LLMResponse(
                text="feat: add prompt builder\n\nAdd prompt loading service.\nNormalize commit output."
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

        def generate(self, request):
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

        def generate(self, request):
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

        def generate(self, request):
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

        def generate(self, request):
            return LLMResponse(
                text="feat: add prompt builder\n\n\nAdd prompt loading service.\n\nNormalize commit output.\n"
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
        "Add prompt loading service.\n"
        "Normalize commit output."
    )


def test_generate_raises_when_sanitization_removes_all_content() -> None:
    class PrefixOnlyProvider:
        @property
        def info(self) -> ProviderInfo:
            return ProviderInfo(name="fake")

        def generate(self, request):
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