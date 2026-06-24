from pathlib import Path

from git_ai.git.stage import stage_files
from git_ai.git.status import get_repo_status


def test_get_repo_status_detects_file_staged_and_modified_in_worktree(temp_git_repo: Path) -> None:
    file_path = temp_git_repo / "mixed.py"
    file_path.write_text("value = 1\n", encoding="utf-8")

    stage_files(["mixed.py"], repo_path=temp_git_repo)

    file_path.write_text("value = 1\nvalue = 2\n", encoding="utf-8")

    status = get_repo_status(repo_path=temp_git_repo)

    assert len(status.files) == 1

    file_status = status.files[0]
    assert file_status.path == "mixed.py"
    assert file_status.is_staged is True
    assert file_status.is_modified_in_worktree is True