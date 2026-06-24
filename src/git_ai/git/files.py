from __future__ import annotations

"""
Utilitaires Git orientés fichiers pour la sélection de périmètre.

Mandat :
- savoir si un chemin existe dans le working tree ou dans l'index ;
- savoir si un chemin est ignoré par Git ;
- savoir si un chemin est un dossier ;
- lister récursivement les fichiers suivis dans un dossier.

Ce module fournit des primitives techniques utilisées par FileSelectionService.
"""

from pathlib import Path

from git_ai.git._common import run_git_command
from git_ai.git.paths import get_repo_root


def is_directory(path: str, repo_path: str | Path | None = None) -> bool:
    """
    Retourne True si le chemin désigne un dossier existant dans le working tree.
    """
    repo_root = get_repo_root(repo_path)
    return (repo_root / path).is_dir()


def exists_in_worktree_or_index(path: str, repo_path: str | Path | None = None) -> bool:
    """
    Retourne True si le chemin existe dans le working tree ou est connu de l'index Git.
    """
    repo_root = get_repo_root(repo_path)
    absolute_path = repo_root / path

    if absolute_path.exists():
        return True

    result = run_git_command(
        ["ls-files", "--error-unmatch", path],
        repo_path=repo_path,
        check=False,
    )
    return result.returncode == 0


def is_ignored(path: str, repo_path: str | Path | None = None) -> bool:
    """
    Retourne True si le chemin est ignoré par Git (.gitignore, exclude, etc.).
    """
    result = run_git_command(
        ["check-ignore", path],
        repo_path=repo_path,
        check=False,
    )
    return result.returncode == 0


def list_tracked_files_in_path(path: str, repo_path: str | Path | None = None) -> list[str]:
    """
    Liste récursivement les fichiers suivis par Git sous un chemin donné.

    Si le chemin ne contient aucun fichier suivi, retourne une liste vide.
    """
    result = run_git_command(
        ["ls-files", path],
        repo_path=repo_path,
        check=False,
    )

    if result.returncode != 0:
        return []

    return [
        line.strip()
        for line in result.stdout.splitlines()
        if line.strip()
    ]


def get_staged_files(repo_path: str | Path | None = None) -> list[str]:
    """
    Retourne la liste des chemins ayant des changements présents dans l'index.
    """
    result = run_git_command(
        ["diff", "--cached", "--name-only"],
        repo_path=repo_path,
    )

    return [
        line.strip()
        for line in result.stdout.splitlines()
        if line.strip()
    ]