from pathlib import Path

from git_ai.git.diff import get_staged_diff, has_staged_changes
from git_ai.git.stage import stage_files


def test_get_staged_diff_returns_patch_for_staged_file(temp_git_repo: Path) -> None:
    file_path = temp_git_repo / "feature.py"
    file_path.write_text("value = 1\n", encoding="utf-8")

    stage_files(["feature.py"], repo_path=temp_git_repo)

    diff = get_staged_diff(repo_path=temp_git_repo)

    assert "diff --git" in diff
    assert "feature.py" in diff
    assert "+value = 1" in diff


def test_has_staged_changes_is_true_after_staging(temp_git_repo: Path) -> None:
    file_path = temp_git_repo / "feature.py"
    file_path.write_text("value = 1\n", encoding="utf-8")

    stage_files(["feature.py"], repo_path=temp_git_repo)

    assert has_staged_changes(repo_path=temp_git_repo) is True


def test_has_staged_changes_is_false_when_nothing_is_staged(temp_git_repo: Path) -> None:
    assert has_staged_changes(repo_path=temp_git_repo) is False