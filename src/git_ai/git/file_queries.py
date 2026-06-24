from __future__ import annotations

from pathlib import Path

from git_ai.git.paths import is_outside_repo, to_repo_relative

from git_ai.git.files import (
    exists_in_worktree_or_index,
    get_staged_files,
    is_directory,
    is_ignored,
    list_tracked_files_in_path,
)


class GitFilesGateway:
    """
    Adaptateur entre la couche service et les fonctions de requête Git
    orientées fichiers.

    Son rôle est de présenter une petite API objet, simple à mocker dans les tests,
    au-dessus de fonctions techniques réparties dans plusieurs modules Git.
    """

    def __init__(self, repo_path: str | Path | None = None):
        self.repo_path = repo_path

    def get_staged_files(self) -> list[str]:
        return get_staged_files(repo_path=self.repo_path)

    def is_directory(self, path: str) -> bool:
        return is_directory(path, repo_path=self.repo_path)

    def list_tracked_files_in_path(self, path: str) -> list[str]:
        return list_tracked_files_in_path(path, repo_path=self.repo_path)

    def exists_in_worktree_or_index(self, path: str) -> bool:
        return exists_in_worktree_or_index(path, repo_path=self.repo_path)

    def is_ignored(self, path: str) -> bool:
        return is_ignored(path, repo_path=self.repo_path)


class GitPathResolver:
    """
    Adaptateur orienté objet pour la résolution des chemins du dépôt.

    Il encapsule les fonctions techniques de git.paths afin que les services
    dépendent d'une interface simple et cohérente.
    """

    def __init__(self, repo_path: str | Path | None = None):
        self.repo_path = repo_path

    def to_repo_relative(self, path: str | Path) -> str:
        return to_repo_relative(path, repo_path=self.repo_path)

    def is_outside_repo(self, path: str | Path) -> bool:
        return is_outside_repo(path, repo_path=self.repo_path)