from pathlib import Path
import pytest
from git_ai.models import CommitLanguage, DiffSource, GitDiff, PromptRequest
from git_ai.services.prompt_service import PromptService


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
    tmp_path,
    language,
    template_name,
) -> None:
    for name in ("commit_fr.txt", "commit_en.txt", "commit_es.txt", "commit_pt.txt"):
        (tmp_path / name).write_text(f"{name}\n{{diff_text}}", encoding="utf-8")

    service = PromptService(prompts_dir=tmp_path)
    request = PromptRequest(
        diff=GitDiff(
            text="diff --git a/app.py b/app.py",
            files=("app.py",),
            source=DiffSource.STAGED,
        ),
        language=language,
        max_subject_length=72,
    )

    payload = service.build_commit_prompt(request)

    assert template_name in payload.user_prompt


def test_build_commit_prompt_returns_payload(tmp_path: Path) -> None:
    (tmp_path / "commit_en.txt").write_text(
        "Diff source: {diff_source}\nFiles:\n{files_block}\nDiff:\n{diff_text}",
        encoding="utf-8",
    )

    service = PromptService(prompts_dir=tmp_path)
    request = PromptRequest(
        diff=GitDiff(
            text="diff --git a/app.py b/app.py",
            files=("app.py",),
            source=DiffSource.FILES,
        ),
        language=CommitLanguage.ENGLISH,
        max_subject_length=72,
    )

    payload = service.build_commit_prompt(request)

    assert payload.system_prompt
    assert "diff --git a/app.py b/app.py" in payload.user_prompt
    assert "- app.py" in payload.user_prompt
    assert payload.metadata["language"] == "en"


def test_build_commit_prompt_replaces_all_placeholders(tmp_path: Path) -> None:
    (tmp_path / "commit_fr.txt").write_text(
        "Len={max_subject_length}\nSource={diff_source}\nFiles:\n{files_block}\nDiff:\n{diff_text}",
        encoding="utf-8",
    )

    service = PromptService(prompts_dir=tmp_path)
    request = PromptRequest(
        diff=GitDiff(
            text="diff --git a/app.py b/app.py",
            files=("app.py",),
            source=DiffSource.STAGED,
        ),
        language=CommitLanguage.FRENCH,
        max_subject_length=50,
    )

    payload = service.build_commit_prompt(request)

    assert "{max_subject_length}" not in payload.user_prompt
    assert "{diff_text}" not in payload.user_prompt
    assert "Len=50" in payload.user_prompt
    assert "Source=staged" in payload.user_prompt


def test_build_commit_prompt_handles_empty_files_list(tmp_path: Path) -> None:
    (tmp_path / "commit_en.txt").write_text(
        "Files:\n{files_block}\nDiff:\n{diff_text}",
        encoding="utf-8",
    )

    service = PromptService(prompts_dir=tmp_path)
    request = PromptRequest(
        diff=GitDiff(
            text="diff --git a/app.py b/app.py",
            files=(),
            source=DiffSource.STAGED,
        ),
        language=CommitLanguage.ENGLISH,
        max_subject_length=72,
    )

    payload = service.build_commit_prompt(request)

    assert "- (none)" in payload.user_prompt

def test_build_commit_prompt_raises_if_template_is_missing(tmp_path) -> None:
    service = PromptService(prompts_dir=tmp_path)

    request = PromptRequest(
        diff=GitDiff(
            text="diff --git a/app.py b/app.py",
            files=("app.py",),
            source=DiffSource.STAGED,
        ),
        language=CommitLanguage.FRENCH,
        max_subject_length=72,
    )

    with pytest.raises(FileNotFoundError):
        service.build_commit_prompt(request)