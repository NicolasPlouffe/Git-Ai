from __future__ import annotations

"""
Utilitaires de résolution de chemins dans le dépôt Git.

Mandat :
- retrouver la racine du dépôt ;
- convertir un chemin utilisateur en chemin relatif au repo ;
- empêcher qu'un chemin sorte du dépôt.

Ce module reste technique : il ne contient pas de logique métier liée à --files.
"""

from pathlib import Path

from git_ai.git._common import run_git_command


def get_repo_root(repo_path: str | Path | None = None) -> Path:
    """
    Retourne la racine absolue du dépôt Git courant.
    """
    result = run_git_command(
        ["rev-parse", "--show-toplevel"],
        repo_path=repo_path,
    )
    return Path(result.stdout.strip()).resolve()


def _resolve_candidate(path: str | Path, repo_path: str | Path | None = None) -> Path:
    """
    Résout un chemin utilisateur en chemin absolu normalisé.

    Règle :
    - un chemin absolu reste absolu ;
    - un chemin relatif est interprété relativement au répertoire d'exécution
      si repo_path n'est pas fourni ;
    - si repo_path est fourni et désigne un dossier, il sert de base explicite.
    """
    candidate = Path(path)

    if candidate.is_absolute():
        return candidate.resolve()

    if repo_path is not None:
        base = Path(repo_path)
        if base.is_file():
            base = base.parent
        return (base.resolve() / candidate).resolve()

    return (Path.cwd() / candidate).resolve()


def to_repo_relative(path: str | Path, repo_path: str | Path | None = None) -> str:
    """
    Convertit un chemin absolu ou relatif en chemin relatif à la racine du dépôt.

    Lève ValueError si le chemin sort de la racine du dépôt.
    """
    repo_root = get_repo_root(repo_path)
    candidate = _resolve_candidate(path, repo_path=repo_path)

    return str(candidate.relative_to(repo_root)).replace("\\", "/")


def is_outside_repo(path: str | Path, repo_path: str | Path | None = None) -> bool:
    """
    Retourne True si le chemin fourni sort de la racine du dépôt.
    """
    repo_root = get_repo_root(repo_path)
    candidate = _resolve_candidate(path, repo_path=repo_path)

    try:
        candidate.relative_to(repo_root)
        return False
    except ValueError:
        return True