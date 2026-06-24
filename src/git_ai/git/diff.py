from __future__ import annotations

"""
Accès aux diffs Git.

Ce module encapsule les variantes de `git diff` utiles à la V1.

Rôle dans l'architecture :
- fournir la matière première textuelle qui sera ensuite analysée par les
  services de sélection, de prompt et de génération du message de commit ;
- éviter que les couches supérieures manipulent directement les commandes Git.
"""

from pathlib import Path
from typing import Sequence

from git_ai.git._common import run_git_command


def get_staged_diff(
    paths: Sequence[str] | None = None,
    repo_path: str | Path | None = None,
) -> str:
    """
    Retourne le diff des changements stagés.

    Git accepte `--staged` comme synonyme de `--cached`. On utilise `--cached`
    pour rester explicite vis-à-vis de l'index.
    """
    args = ["diff", "--cached"]

    if paths:
        args.append("--")
        args.extend(paths)

    result = run_git_command(args, repo_path=repo_path)
    return result.stdout


def get_unstaged_diff(
    paths: Sequence[str] | None = None,
    repo_path: str | Path | None = None,
) -> str:
    """
    Retourne le diff des changements non stagés.

    Ce mode n'est pas central dans la V1, mais il est utile pour tests, debug
    ou évolutions futures.
    """
    args = ["diff"]

    if paths:
        args.append("--")
        args.extend(paths)

    result = run_git_command(args, repo_path=repo_path)
    return result.stdout


def has_staged_changes(
    paths: Sequence[str] | None = None,
    repo_path: str | Path | None = None,
) -> bool:
    """
    Vérifie rapidement s'il existe des changements stagés.

    On s'appuie sur `git diff --cached --quiet`, dont le code de retour vaut :
    - 0 : pas de différence ;
    - 1 : différence présente ;
    - >1 : erreur.
    """
    args = ["diff", "--cached", "--quiet"]

    if paths:
        args.append("--")
        args.extend(paths)

    result = run_git_command(args, repo_path=repo_path, check=False)

    if result.returncode == 0:
        return False
    if result.returncode == 1:
        return True

    # Au-delà de 1, on veut remonter une vraie erreur Git.
    run_git_command(args, repo_path=repo_path, check=True)
    return False