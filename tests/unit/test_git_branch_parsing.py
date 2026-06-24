import pytest

from git_ai.git.status import BranchStatus, _parse_branch_line


@pytest.mark.parametrize(
    ("line", "expected"),
    [
        (
            "## main",
            BranchStatus(
                name="main",
                upstream=None,
                ahead=0,
                behind=0,
                is_detached=False,
            ),
        ),
        (
            "## main...origin/main",
            BranchStatus(
                name="main",
                upstream="origin/main",
                ahead=0,
                behind=0,
                is_detached=False,
            ),
        ),
        (
            "## main...origin/main [ahead 2]",
            BranchStatus(
                name="main",
                upstream="origin/main",
                ahead=2,
                behind=0,
                is_detached=False,
            ),
        ),
        (
            "## main...origin/main [behind 3]",
            BranchStatus(
                name="main",
                upstream="origin/main",
                ahead=0,
                behind=3,
                is_detached=False,
            ),
        ),
        (
            "## main...origin/main [ahead 2, behind 1]",
            BranchStatus(
                name="main",
                upstream="origin/main",
                ahead=2,
                behind=1,
                is_detached=False,
            ),
        ),
    ],
)
def test_parse_branch_line_variants(line: str, expected: BranchStatus) -> None:
    assert _parse_branch_line(line) == expected