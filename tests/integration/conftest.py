from __future__ import annotations

import subprocess
from pathlib import Path

import pytest


def _run(command: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=cwd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=True,
    )


@pytest.fixture
def temp_git_repo(tmp_path: Path) -> Path:
    """
    Crée un dépôt Git temporaire isolé pour les tests d'intégration.

    Notes importantes :
    - on configure user.name / user.email en local pour ne pas dépendre
      de la machine de dev ;
    - on crée un commit initial pour avoir un HEAD valide, ce qui simplifie
      les tests de diff et de commit.
    """
    repo_path = tmp_path / "repo"
    repo_path.mkdir()

    _run(["git", "init"], cwd=repo_path)
    _run(["git", "config", "--local", "user.name", "Test User"], cwd=repo_path)
    _run(["git", "config", "--local", "user.email", "test@example.com"], cwd=repo_path)

    readme = repo_path / "README.md"
    readme.write_text("# Test Repository\n", encoding="utf-8")

    _run(["git", "add", "README.md"], cwd=repo_path)
    _run(["git", "commit", "-m", "Initial commit"], cwd=repo_path)

    return repo_path