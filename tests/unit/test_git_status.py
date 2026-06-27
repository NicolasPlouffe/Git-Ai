from git_ai.git.status import (
    BranchStatus,
    FileStatus,
    _parse_branch_line,
    _parse_file_status_line,
)


def test_parse_branch_line_with_upstream_and_ahead_behind() -> None:
    branch = _parse_branch_line("## main...origin/main [ahead 2, behind 1]")

    assert branch == BranchStatus(
        name="main",
        upstream="origin/main",
        ahead=2,
        behind=1,
        is_detached=False,
    )


def test_parse_branch_line_detached_head() -> None:
    branch = _parse_branch_line("## HEAD (no branch)")

    assert branch == BranchStatus(
        name=None,
        upstream=None,
        ahead=0,
        behind=0,
        is_detached=True,
    )


def test_parse_file_status_line_for_staged_file() -> None:
    file_status = _parse_file_status_line("M  src/git_ai/git/status.py")

    assert file_status == FileStatus(
        path="src/git_ai/git/status.py",
        index_status="M",
        worktree_status=" ",
    )
    assert file_status.is_staged is True
    assert file_status.is_untracked is False
    assert file_status.is_modified_in_worktree is False


def test_parse_file_status_line_for_untracked_file() -> None:
    file_status = _parse_file_status_line("?? notes.txt")

    assert file_status == FileStatus(
        path="notes.txt",
        index_status="?",
        worktree_status="?",
    )
    assert file_status.is_staged is False
    assert file_status.is_untracked is True
    assert file_status.is_modified_in_worktree is False