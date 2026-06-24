from __future__ import annotations

"""
Informations sur la branche courante.

Ce module expose des helpers orientés usage applicatif plutôt qu'un inventaire
complet des commandes Git liées aux branches.
"""

from pathlib import Path

from git_ai.git._common import run_git_command
from git_ai.git.status import BranchStatus, get_repo_status


def get_current_branch(
    repo_path: str | Path | None = None,
) -> str | None:
    """
    Retourne le nom de la branche courante, ou None si HEAD détaché.
    """
    status = get_repo_status(repo_path=repo_path)
    return status.branch.name


def get_branch_status(
    repo_path: str | Path | None = None,
) -> BranchStatus:
    """
    Retourne l'état simplifié de la branche courante.
    """
    status = get_repo_status(repo_path=repo_path)
    return status.branch


def has_upstream(
    repo_path: str | Path | None = None,
) -> bool:
    """
    Indique si la branche courante suit une branche distante.
    """
    status = get_repo_status(repo_path=repo_path)
    return status.branch.upstream is not None


def get_upstream_branch(
    repo_path: str | Path | None = None,
) -> str | None:
    """
    Retourne la branche distante suivie par la branche courante.
    """
    status = get_repo_status(repo_path=repo_path)
    return status.branch.upstream


def get_push_remote(
    repo_path: str | Path | None = None,
) -> str | None:
    """
    Retourne le remote de push configuré pour la branche courante.

    On utilise `git config --get branch.<name>.remote` plutôt que de parser
    des sorties humaines plus fragiles.
    """
    branch = get_current_branch(repo_path=repo_path)
    if not branch:
        return None

    result = run_git_command(
        ["config", "--get", f"branch.{branch}.remote"],
        repo_path=repo_path,
        check=False,
    )

    if result.returncode != 0:
        return None

    value = result.stdout.strip()
    return value or None