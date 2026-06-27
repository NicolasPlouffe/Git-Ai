from __future__ import annotations

import pytest

from git_ai.services.file_selection_service import (
    FileSelectionError,
    FileSelectionService,
    SelectedFiles,
)


class FakeGitFilesGateway:
    """
    Double de test simple pour GitFilesGateway.

    On configure ses attributs dans chaque test pour simuler les réponses Git.
    """

    def __init__(self) -> None:
        self._staged_files: list[str] = []
        self._directories: set[str] = set()
        self._tracked_files_by_dir: dict[str, list[str]] = {}
        self._existing_paths: set[str] = set()
        self._ignored_paths: set[str] = set()

    def set_staged_files(self, files: list[str]) -> None:
        self._staged_files = files

    def set_directory(self, path: str) -> None:
        self._directories.add(path)

    def set_tracked_files_in_dir(self, path: str, files: list[str]) -> None:
        self._tracked_files_by_dir[path] = files

    def set_existing_paths(self, paths: list[str]) -> None:
        self._existing_paths = set(paths)

    def set_ignored_paths(self, paths: list[str]) -> None:
        self._ignored_paths = set(paths)

    def get_staged_files(self) -> list[str]:
        return list(self._staged_files)

    def is_directory(self, path: str) -> bool:
        return path in self._directories

    def list_tracked_files_in_path(self, path: str) -> list[str]:
        return self._tracked_files_by_dir.get(path, [])

    def exists_in_worktree_or_index(self, path: str) -> bool:
        return path in self._existing_paths

    def is_ignored(self, path: str) -> bool:
        return path in self._ignored_paths


class FakeGitPathResolver:
    """
    Double de test simple pour GitPathResolver.

    Par défaut, considère que tous les chemins sont dans le repo
    et ne fait qu'une normalisation identitaire.
    """

    def __init__(self) -> None:
        self._outside_paths: set[str] = set()

    def set_outside_paths(self, paths: list[str]) -> None:
        self._outside_paths = set(paths)

    def to_repo_relative(self, path: str) -> str:
        return path

    def is_outside_repo(self, path: str) -> bool:
        return path in self._outside_paths


def test_select_from_staged_ok() -> None:
    gateway = FakeGitFilesGateway()
    resolver = FakeGitPathResolver()

    gateway.set_staged_files(["a.py", "b.py", "a.py"])

    service = FileSelectionService(gateway, resolver)

    result = service.select_files()

    assert isinstance(result, SelectedFiles)
    assert result.source == "staged"
    assert result.files == ["a.py", "b.py"]
    assert result.warnings == []


def test_select_from_staged_empty_raises() -> None:
    gateway = FakeGitFilesGateway()
    resolver = FakeGitPathResolver()

    gateway.set_staged_files([])

    service = FileSelectionService(gateway, resolver)

    with pytest.raises(FileSelectionError, match="Aucun fichier stagé"):
        service.select_files()


def test_explicit_files_ok_mixed_files() -> None:
    gateway = FakeGitFilesGateway()
    resolver = FakeGitPathResolver()

    existing = ["src/app.py", "tests/test_app.py"]
    gateway.set_existing_paths(existing)

    service = FileSelectionService(gateway, resolver)

    result = service.select_files(explicit_files=existing)

    assert result.source == "explicit"
    assert result.files == sorted(existing)
    assert result.warnings == []


def test_explicit_files_outside_repo_raises() -> None:
    gateway = FakeGitFilesGateway()
    resolver = FakeGitPathResolver()

    resolver.set_outside_paths(["../secret.txt"])

    service = FileSelectionService(gateway, resolver)

    with pytest.raises(FileSelectionError, match="en dehors du dépôt Git"):
        service.select_files(explicit_files=["../secret.txt"])


def test_explicit_file_missing_raises() -> None:
    gateway = FakeGitFilesGateway()
    resolver = FakeGitPathResolver()

    service = FileSelectionService(gateway, resolver)

    with pytest.raises(FileSelectionError, match="Fichier introuvable"):
        service.select_files(explicit_files=["src/missing.py"])


def test_explicit_file_ignored_raises() -> None:
    gateway = FakeGitFilesGateway()
    resolver = FakeGitPathResolver()

    gateway.set_existing_paths(["secret.env"])
    gateway.set_ignored_paths(["secret.env"])

    service = FileSelectionService(gateway, resolver)

    with pytest.raises(FileSelectionError, match="Fichier ignoré par Git"):
        service.select_files(explicit_files=["secret.env"])


def test_explicit_directory_expands_tracked_files() -> None:
    gateway = FakeGitFilesGateway()
    resolver = FakeGitPathResolver()

    gateway.set_directory("src")
    gateway.set_tracked_files_in_dir("src", ["src/app.py", "src/utils.py"])

    service = FileSelectionService(gateway, resolver)

    result = service.select_files(explicit_files=["src"])

    assert result.source == "explicit"
    assert result.files == ["src/app.py", "src/utils.py"]
    assert result.warnings == []


def test_explicit_directory_empty_adds_warning_and_may_fail() -> None:
    gateway = FakeGitFilesGateway()
    resolver = FakeGitPathResolver()

    gateway.set_directory("empty")
    gateway.set_tracked_files_in_dir("empty", [])

    service = FileSelectionService(gateway, resolver)

    with pytest.raises(FileSelectionError, match="aucun fichier valide"):
        service.select_files(explicit_files=["empty"])


def test_explicit_all_invalid_raises() -> None:
    gateway = FakeGitFilesGateway()
    resolver = FakeGitPathResolver()

    service = FileSelectionService(gateway, resolver)

    with pytest.raises(FileSelectionError) as exc_info:
        service.select_files(explicit_files=["does_not_exist.py"])

    assert "Fichier introuvable" in str(exc_info.value) or "aucun fichier valide" in str(
        exc_info.value
    )