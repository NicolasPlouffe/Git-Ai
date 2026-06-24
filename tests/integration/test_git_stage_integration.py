from pathlib import Path

from git_ai.git.stage import stage_files, unstage_files
from git_ai.git.status import get_repo_status


def test_stage_files_marks_file_as_staged(temp_git_repo: Path) -> None:
    file_path = temp_git_repo / "module.py"
    file_path.write_text("value = 1\n", encoding="utf-8")

    stage_files(["module.py"], repo_path=temp_git_repo)

    status = get_repo_status(repo_path=temp_git_repo)

    assert len(status.staged_files) == 1
    assert status.staged_files[0].path == "module.py"
    assert status.staged_files[0].is_staged is True


def test_unstage_files_removes_file_from_index(temp_git_repo: Path) -> None:
    file_path = temp_git_repo / "module.py"
    file_path.write_text("value = 1\n", encoding="utf-8")

    stage_files(["module.py"], repo_path=temp_git_repo)
    unstage_files(["module.py"], repo_path=temp_git_repo)

    status = get_repo_status(repo_path=temp_git_repo)

    assert len(status.staged_files) == 0
    assert len(status.files) == 1
    assert status.files[0].path == "module.py"