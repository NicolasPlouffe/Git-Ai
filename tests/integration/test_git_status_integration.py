from pathlib import Path

from git_ai.git.stage import stage_files
from git_ai.git.status import get_repo_status


def test_get_repo_status_detects_unstaged_file(temp_git_repo: Path) -> None:
    file_path = temp_git_repo / "hello.py"
    file_path.write_text("print('hello')\n", encoding="utf-8")

    status = get_repo_status(repo_path=temp_git_repo)

    assert len(status.files) == 1
    assert status.files[0].path == "hello.py"
    assert status.files[0].is_untracked is True
    assert status.files[0].is_staged is False


def test_get_repo_status_detects_staged_file(temp_git_repo: Path) -> None:
    file_path = temp_git_repo / "hello.py"
    file_path.write_text("print('hello')\n", encoding="utf-8")

    stage_files(["hello.py"], repo_path=temp_git_repo)

    status = get_repo_status(repo_path=temp_git_repo)

    assert len(status.staged_files) == 1
    assert status.staged_files[0].path == "hello.py"
    assert status.staged_files[0].is_staged is True


def test_get_repo_status_returns_branch_information(temp_git_repo: Path) -> None:
    status = get_repo_status(repo_path=temp_git_repo)

    assert status.branch.is_detached is False
    assert status.branch.name in {"main", "master"}