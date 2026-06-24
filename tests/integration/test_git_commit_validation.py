from pathlib import Path

import pytest

from git_ai.git.commit import create_commit
from git_ai.git.stage import stage_files


def test_create_commit_rejects_empty_message(temp_git_repo: Path) -> None:
    file_path = temp_git_repo / "empty_message.py"
    file_path.write_text("print('x')\n", encoding="utf-8")

    stage_files(["empty_message.py"], repo_path=temp_git_repo)

    with pytest.raises(ValueError, match="Commit message cannot be empty."):
        create_commit("   ", repo_path=temp_git_repo)