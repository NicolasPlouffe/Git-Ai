from __future__ import annotations

from pathlib import Path

from git_ai.git.diff import get_staged_diff
from git_ai.git.stage import stage_files


def test_get_staged_diff_can_be_scoped_to_specific_paths(temp_git_repo: Path) -> None:
    file_a = temp_git_repo / "a.py"
    file_b = temp_git_repo / "b.py"

    file_a.write_text("value_a = 1\n", encoding="utf-8")
    file_b.write_text("value_b = 2\n", encoding="utf-8")

    stage_files(["a.py", "b.py"], repo_path=temp_git_repo)

    diff = get_staged_diff(paths=["a.py"], repo_path=temp_git_repo)

    assert diff.strip()
    assert "a.py" in diff
    assert "+value_a = 1" in diff
    assert "b.py" not in diff
    assert "+value_b = 2" not in diff