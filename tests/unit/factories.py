from __future__ import annotations

from types import SimpleNamespace

from git_ai.config import (
    DEFAULT_BASE_URL,
    DEFAULT_LANGUAGE,
    DEFAULT_MAX_SUBJECT_LENGTH,
    DEFAULT_MODEL,
    DEFAULT_PROVIDER,
    DEFAULT_PUSH_AFTER_COMMIT,
)
def make_config(
    *,
    language: str = DEFAULT_LANGUAGE,
    provider: str = DEFAULT_PROVIDER,
    model: str = DEFAULT_MODEL,
    base_url: str = DEFAULT_BASE_URL,
    push_after_commit: bool = DEFAULT_PUSH_AFTER_COMMIT,
    max_subject_length: int = DEFAULT_MAX_SUBJECT_LENGTH,
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