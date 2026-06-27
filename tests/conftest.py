from __future__ import annotations

from types import SimpleNamespace

import pytest
from typer.testing import CliRunner

from git_ai.config import DEFAULT_MODEL
from git_ai.models import CommitLanguage, DiffSource, GitDiff, PromptRequest


@pytest.fixture
def cli_runner() -> CliRunner:
    return CliRunner()


def make_config(
    *,
    language: str = "fr",
    provider: str = "ollama",
    model: str = DEFAULT_MODEL,
    base_url: str = "http://localhost:11434",
    push_after_commit: bool = False,
    max_subject_length: int = 72,
):
    return SimpleNamespace(
        language=language,
        provider=provider,
        model=model,
        base_url=base_url,
        commit=SimpleNamespace(max_subject_length=max_subject_length),
        git=SimpleNamespace(push_after_commit=push_after_commit),
    )


def make_selected_files_result(
    *,
    files: list[str] | None = None,
    source: str = "staged",
    warnings: list[str] | None = None,
):
    return SimpleNamespace(
        files=files or [],
        source=source,
        warnings=warnings or [],
    )


def make_git_diff(
    *,
    text: str = "diff --git a/a.py b/a.py",
    files: tuple[str, ...] = ("a.py",),
    source: str = "staged",
    is_empty: bool = False,
):
    return SimpleNamespace(
        text=text,
        files=files,
        source=source,
        is_empty=is_empty,
    )


def make_commit_message(
    text: str = "feat(cli): ajouter la commande de commit",
    language: str = "fr",
):
    return SimpleNamespace(
        text=text,
        language=language,
    )


def make_prompt_request(
    *,
    diff_text: str = "diff --git a/file.py b/file.py",
    files: tuple[str, ...] = ("src/git_ai/cli.py",),
    source: DiffSource = DiffSource.STAGED,
    language: CommitLanguage = CommitLanguage.FRENCH,
    max_subject_length: int = 50,
) -> PromptRequest:
    return PromptRequest(
        diff=GitDiff(
            text=diff_text,
            files=files,
            source=source,
        ),
        language=language,
        max_subject_length=max_subject_length,
    )