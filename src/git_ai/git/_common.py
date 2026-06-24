from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import subprocess
from typing import Sequence


class GitError(RuntimeError):
    """Erreur générique lors d'un appel Git."""


class GitRepositoryError(GitError):
    """Le répertoire cible n'est pas un dépôt Git valide."""


class GitCommandError(GitError):
    """Une commande Git a échoué."""

    def __init__(
        self,
        command: Sequence[str],
        returncode: int,
        stdout: str = "",
        stderr: str = "",
    ) -> None:
        self.command = list(command)
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr

        message = (
            f"Git command failed (exit={returncode}): {' '.join(command)}"
            f"\nstdout: {stdout.strip()}"
            f"\nstderr: {stderr.strip()}"
        )
        super().__init__(message)


@dataclass(frozen=True)
class GitCommandResult:
    args: list[str]
    returncode: int
    stdout: str
    stderr: str


def _normalize_repo_path(repo_path: str | Path | None) -> Path:
    path = Path(repo_path or ".").expanduser().resolve()
    return path


def run_git_command(
    args: Sequence[str],
    repo_path: str | Path | None = None,
    check: bool = True,
) -> GitCommandResult:
    cwd = _normalize_repo_path(repo_path)
    command = ["git", *args]

    completed = subprocess.run(
        command,
        cwd=cwd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )

    result = GitCommandResult(
        args=command,
        returncode=completed.returncode,
        stdout=completed.stdout,
        stderr=completed.stderr,
    )

    if check and completed.returncode != 0:
        stderr = completed.stderr.lower()

        if "not a git repository" in stderr:
            raise GitRepositoryError(completed.stderr.strip())

        raise GitCommandError(
            command=command,
            returncode=completed.returncode,
            stdout=completed.stdout,
            stderr=completed.stderr,
        )

    return result