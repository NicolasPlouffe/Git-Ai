from __future__ import annotations

"""
Lecture et parsing du statut Git.

Ce module transforme la sortie machine-friendly de `git status --porcelain=v1 --branch`
en objets Python simples à consommer par les services applicatifs.

Mandat dans la V1 :
- savoir quels fichiers sont modifiés ;
- distinguer ce qui est stagé de ce qui ne l'est pas ;
- exposer l'information de branche utile aux étapes suivantes.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import List

from git_ai.git._common import run_git_command


@dataclass(frozen=True)
class FileStatus:
    """
    Statut d'un fichier vu par Git.

    index_status:
        état dans l'index (staging area)
    worktree_status:
        état dans le répertoire de travail
    """

    path: str
    index_status: str
    worktree_status: str

    @property
    def is_staged(self) -> bool:
        """True si le fichier a un changement présent dans l'index."""
        return self.index_status not in {" ", "?"}

    @property
    def is_untracked(self) -> bool:
        """True si Git considère le fichier comme non suivi."""
        return self.index_status == "?" and self.worktree_status == "?"

    @property
    def is_modified_in_worktree(self) -> bool:
        """True si le working tree contient une modification non encore indexée."""
        return self.worktree_status not in {" ", "?"}


@dataclass(frozen=True)
class BranchStatus:
    """
    État simplifié de la branche courante.
    """

    name: str | None
    upstream: str | None
    ahead: int
    behind: int
    is_detached: bool


@dataclass(frozen=True)
class RepoStatus:
    """
    Vue agrégée de l'état du dépôt.
    """

    branch: BranchStatus
    files: List[FileStatus]

    @property
    def staged_files(self) -> List[FileStatus]:
        """Liste des fichiers ayant des changements stagés."""
        return [file for file in self.files if file.is_staged]

    @property
    def unstaged_files(self) -> List[FileStatus]:
        """Liste des fichiers ayant des changements non stagés."""
        return [file for file in self.files if file.is_modified_in_worktree]

    @property
    def untracked_files(self) -> List[FileStatus]:
        """Liste des fichiers non suivis."""
        return [file for file in self.files if file.is_untracked]


def get_repo_status(repo_path: str | Path | None = None) -> RepoStatus:
    """
    Retourne l'état courant du dépôt.

    On s'appuie sur `git status --porcelain=v1 --branch` car ce format est prévu
    pour les scripts et reste stable entre versions de Git.
    """
    result = run_git_command(
        ["status", "--porcelain=v1", "--branch"],
        repo_path=repo_path,
    )

    lines = result.stdout.splitlines()
    branch = _parse_branch_line(lines[0] if lines else "")
    files = [_parse_file_status_line(line) for line in lines[1:] if line.strip()]

    return RepoStatus(branch=branch, files=files)


def _parse_branch_line(line: str) -> BranchStatus:
    """
    Parse la ligne `## ...` produite par `git status --porcelain=v1 --branch`.

    Exemples possibles :
    - ## main
    - ## main...origin/main
    - ## main...origin/main [ahead 2]
    - ## main...origin/main [ahead 2, behind 1]
    - ## HEAD (no branch)
    """
    if not line.startswith("## "):
        return BranchStatus(
            name=None,
            upstream=None,
            ahead=0,
            behind=0,
            is_detached=False,
        )

    raw = line[3:]

    if raw.startswith("HEAD "):
        return BranchStatus(
            name=None,
            upstream=None,
            ahead=0,
            behind=0,
            is_detached=True,
        )

    name_part = raw
    tracking_part = ""

    if " [" in raw:
        name_part, tracking_part = raw.split(" [", 1)
        tracking_part = tracking_part.rstrip("]")

    branch_name = name_part
    upstream = None

    if "..." in name_part:
        branch_name, upstream = name_part.split("...", 1)

    ahead = 0
    behind = 0

    if tracking_part:
        parts = [part.strip() for part in tracking_part.split(",")]
        for part in parts:
            if part.startswith("ahead "):
                ahead = int(part.removeprefix("ahead ").strip())
            elif part.startswith("behind "):
                behind = int(part.removeprefix("behind ").strip())

    return BranchStatus(
        name=branch_name,
        upstream=upstream,
        ahead=ahead,
        behind=behind,
        is_detached=False,
    )


def _parse_file_status_line(line: str) -> FileStatus:
    """
    Parse une ligne porcelain v1.

    Format simplifié :
    XY path

    X = statut dans l'index
    Y = statut dans le working tree

    Exemples :
    - 'M  file.py'
    - ' M file.py'
    - 'A  new_file.py'
    - '?? untracked.txt'

    Remarque :
    Les renommages/copies peuvent inclure `old -> new`. Pour la V1, on garde la
    portion chemin telle que fournie par Git afin d'éviter un parsing excessif.
    """
    if len(line) < 4:
        raise ValueError(f"Invalid porcelain status line: {line!r}")

    index_status = line[0]
    worktree_status = line[1]
    path = line[3:]

    return FileStatus(
        path=path,
        index_status=index_status,
        worktree_status=worktree_status,
    )