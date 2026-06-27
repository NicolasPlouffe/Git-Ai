from pathlib import Path

import pytest

from git_ai.git._common import GitRepositoryError, run_git_command


def test_run_git_command_raises_repository_error_outside_git_repo(tmp_path: Path) -> None:
    non_repo = tmp_path / "not-a-repo"
    non_repo.mkdir()

    with pytest.raises(GitRepositoryError):
        run_git_command(["status"], repo_path=non_repo)