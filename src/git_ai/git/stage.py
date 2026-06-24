from __future__ import annotations

"""
Opérations de staging Git.

Mandat V1 :
- permettre au service de sélection de fichiers d'ajouter explicitement des
  chemins à l'index ;
- garder une API simple et déterministe.
"""

from pathlib import Path
from typing import Sequence

from git_ai.git._common import run_git_command


def stage_files(
    paths: Sequence[str],
    repo_path: str | Path | None = None,
) -> None:
    """
    Ajoute les chemins fournis dans l'index via `git add`.

    Le séparateur `--` protège contre les chemins ambigus pouvant être
    interprétés comme des options ou des références Git.
    """
    if not paths:
        return

    args = ["add", "--", *paths]
    run_git_command(args, repo_path=repo_path)


def unstage_files(
    paths: Sequence[str],
    repo_path: str | Path | None = None,
) -> None:
    """
    Retire des chemins du staging sans supprimer leurs changements locaux.

    Cette fonction n'est pas indispensable à la V1 stricte, mais elle complète
    utilement la couche Git et peut simplifier certains tests ou flux futurs.
    """
    if not paths:
        return

    args = ["restore", "--staged", "--", *paths]
    run_git_command(args, repo_path=repo_path)