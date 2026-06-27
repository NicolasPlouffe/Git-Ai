import subprocess
from pathlib import Path

from git_ai.git.branch import (
    get_branch_status,
    get_current_branch,
    get_upstream_branch,
    has_upstream,
)


def test_branch_helpers_return_current_branch_without_upstream(temp_git_repo: Path) -> None:
    branch_name = get_current_branch(repo_path=temp_git_repo)
    branch_status = get_branch_status(repo_path=temp_git_repo)

    assert branch_name in {"main", "master"}
    assert branch_status.name in {"main", "master"}
    assert branch_status.is_detached is False
    assert has_upstream(repo_path=temp_git_repo) is False
    assert get_upstream_branch(repo_path=temp_git_repo) is None


def test_branch_helpers_detect_detached_head(temp_git_repo: Path) -> None:
    head_sha = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=temp_git_repo,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=True,
    ).stdout.strip()

    subprocess.run(
        ["git", "checkout", head_sha],
        cwd=temp_git_repo,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=True,
    )

    branch_name = get_current_branch(repo_path=temp_git_repo)
    branch_status = get_branch_status(repo_path=temp_git_repo)

    assert branch_name is None
    assert branch_status.name is None
    assert branch_status.is_detached is True