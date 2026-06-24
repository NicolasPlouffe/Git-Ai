from __future__ import annotations

"""
Infrastructure commune de la couche Git.

Ce module centralise l'exécution des commandes Git et la conversion des erreurs
bas niveau (codes de retour, stderr) en exceptions applicatives plus explicites.

Pourquoi ce module existe :
- éviter de dupliquer subprocess.run(...) dans chaque sous-module Git ;
- normaliser la gestion du repo_path / cwd ;
- offrir un contrat de retour stable pour les autres modules ;
- faciliter les tests unitaires en mockant un seul point d'entrée.
"""

from dataclasses import dataclass
from pathlib import Path
import subprocess
from typing import Sequence


class GitError(RuntimeError):
    """Erreur générique liée à la couche Git."""


class GitRepositoryError(GitError):
    """Le répertoire cible n'est pas un dépôt Git valide."""


class GitCommandError(GitError):
    """
    Une commande Git a échoué.

    Cette exception conserve le détail de la commande exécutée ainsi que
    stdout/stderr, ce qui facilite le diagnostic côté CLI, logs ou tests.
    """

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
    """
    Résultat standardisé d'une commande Git.
    """

    args: list[str]
    returncode: int
    stdout: str
    stderr: str


def _normalize_repo_path(repo_path: str | Path | None) -> Path:
    """
    Normalise le chemin du dépôt.

    - None => répertoire courant
    - supporte str et Path
    - expanduser/resolve pour obtenir un chemin absolu stable
    """
    return Path(repo_path or ".").expanduser().resolve()


def run_git_command(
    args: Sequence[str],
    repo_path: str | Path | None = None,
    check: bool = True,
) -> GitCommandResult:
    """
    Exécute une commande Git dans le dépôt ciblé.

    Parameters
    ----------
    args:
        Arguments Git sans le binaire `git` lui-même.
        Exemple: ["status", "--porcelain=v1"]
    repo_path:
        Répertoire de travail dans lequel exécuter la commande.
    check:
        Si True, lève une exception applicative si la commande échoue.

    Returns
    -------
    GitCommandResult
        Résultat standardisé avec stdout/stderr capturés.

    Notes
    -----
    On utilise subprocess.run(..., check=False) puis on convertit nous-mêmes
    les erreurs en exceptions métier, afin d'avoir un meilleur contrôle sur
    les messages et les types d'erreurs remontés.
    """
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