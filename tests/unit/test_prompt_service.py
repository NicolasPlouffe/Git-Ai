from __future__ import annotations

from pathlib import Path

import pytest

from git_ai.models import CommitLanguage, DiffSource
from git_ai.services.prompt_service import PromptService
from tests.conftest import make_prompt_request


@pytest.mark.parametrize(
    ("language", "template_name"),
    [
        (CommitLanguage.FRENCH, "commit_fr.txt"),
        (CommitLanguage.ENGLISH, "commit_en.txt"),
        (CommitLanguage.SPANISH, "commit_es.txt"),
        (CommitLanguage.PORTUGUESE, "commit_pt.txt"),
    ],
)
def test_build_commit_prompt_loads_template_for_each_language(
    tmp_path: Path,
    language: CommitLanguage,
    template_name: str,
) -> None:
    for name in ("commit_fr.txt", "commit_en.txt", "commit_es.txt", "commit_pt.txt"):
        (tmp_path / name).write_text(f"{name}\n{{diff_text}}", encoding="utf-8")

    service = PromptService(prompts_dir=tmp_path)
    request = make_prompt_request(
        diff_text="diff --git a/app.py b/app.py",
        files=("app.py",),
        source=DiffSource.STAGED,
        language=language,
        max_subject_length=72,
    )

    payload = service.build_commit_prompt(request)

    assert template_name in payload.user_prompt
    assert "diff --git a/app.py b/app.py" in payload.user_prompt


def test_build_commit_prompt_sets_language_metadata_for_portuguese(
    tmp_path: Path,
) -> None:
    (tmp_path / "commit_pt.txt").write_text(
        "Origem: {diff_source}\nDiff:\n{diff_text}",
        encoding="utf-8",
    )

    service = PromptService(prompts_dir=tmp_path)
    request = make_prompt_request(
        diff_text="diff --git a/app.py b/app.py",
        files=("app.py",),
        source=DiffSource.FILES,
        language=CommitLanguage.PORTUGUESE,
        max_subject_length=60,
    )

    payload = service.build_commit_prompt(request)

    assert payload.metadata["language"] == "pt"
    assert payload.metadata["diff_source"] == "files"
    assert payload.metadata["max_subject_length"] == "60"


def test_build_commit_prompt_raises_if_template_is_missing(tmp_path: Path) -> None:
    service = PromptService(prompts_dir=tmp_path)

    request = make_prompt_request(
        diff_text="diff --git a/app.py b/app.py",
        files=("app.py",),
        source=DiffSource.STAGED,
        language=CommitLanguage.FRENCH,
        max_subject_length=72,
    )

    with pytest.raises(FileNotFoundError):
        service.build_commit_prompt(request)