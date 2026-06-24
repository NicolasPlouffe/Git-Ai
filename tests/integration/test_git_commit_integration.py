import subprocess
from pathlib import Path

from git_ai.git.commit import create_commit
from git_ai.git.stage import stage_files


def test_create_commit_creates_a_new_commit(temp_git_repo: Path) -> None:
    file_path = temp_git_repo / "app.py"
    file_path.write_text("print('commit test')\n", encoding="utf-8")

    stage_files(["app.py"], repo_path=temp_git_repo)
    create_commit("Add app entry point", repo_path=temp_git_repo)

    result = subprocess.run(
        ["git", "log", "-1", "--pretty=%s"],
        cwd=temp_git_repo,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=True,
    )

    assert result.stdout.strip() == "Add app entry point"