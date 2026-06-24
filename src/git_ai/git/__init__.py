"""
API publique de la couche Git.

Ce package encapsule les opérations Git utilisées par l'application :
- lecture du statut du dépôt ;
- récupération de diff ;
- staging ;
- informations de branche ;
- commit et push.

Les modules internes peuvent évoluer, mais les symboles réexportés ici
constituent le point d'entrée recommandé pour le reste de l'application.
"""

from ._common import (
    GitCommandError,
    GitCommandResult,
    GitError,
    GitRepositoryError,
    run_git_command,
)
from .branch import (
    get_branch_status,
    get_current_branch,
    get_push_remote,
    get_upstream_branch,
    has_upstream,
)
from .commit import create_commit, push_current_branch
from .diff import get_staged_diff, get_unstaged_diff, has_staged_changes
from .stage import stage_files, unstage_files
from .status import BranchStatus, FileStatus, RepoStatus, get_repo_status

__all__ = [
    "BranchStatus",
    "FileStatus",
    "GitCommandError",
    "GitCommandResult",
    "GitError",
    "GitRepositoryError",
    "RepoStatus",
    "create_commit",
    "get_branch_status",
    "get_current_branch",
    "get_push_remote",
    "get_repo_status",
    "get_staged_diff",
    "get_unstaged_diff",
    "get_upstream_branch",
    "has_staged_changes",
    "has_upstream",
    "push_current_branch",
    "run_git_command",
    "stage_files",
    "unstage_files",
]