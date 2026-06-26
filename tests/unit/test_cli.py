from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from typer.testing import CliRunner

from git_ai.cli import app
from git_ai.exceptions import ProviderError

runner = CliRunner()


def make_config(
    *,
    language: str = "fr",
    provider: str = "ollama",
    model: str = "qwen2.5-coder:7b",
    base_url: str = "http://localhost:11434",
    push_after_commit: bool = False,
    max_subject_length: int = 72,
):
    return SimpleNamespace(
        language=language,
        provider=provider,
        model=model,
        base_url=base_url,
        commit=SimpleNamespace(max_subject_length=max_subject_length),
        git=SimpleNamespace(push_after_commit=push_after_commit),
    )


def make_selected_files_result(
    *,
    files: list[str] | None = None,
    source: str = "staged",
    warnings: list[str] | None = None,
):
    return SimpleNamespace(
        files=files or [],
        source=source,
        warnings=warnings or [],
    )


def make_git_diff(
    *,
    text: str = "diff --git a/a.py b/a.py",
    files: tuple[str, ...] = ("a.py",),
    source: str = "staged",
    is_empty: bool = False,
):
    return SimpleNamespace(
        text=text,
        files=files,
        source=source,
        is_empty=is_empty,
    )


def make_commit_message(text: str = "feat(cli): ajouter la commande de commit"):
    return SimpleNamespace(text=text, language="fr")


@patch("git_ai.cli.create_commit")
@patch("git_ai.cli.push_current_branch")
@patch("git_ai.cli._build_commit_message_service")
@patch("git_ai.cli._build_git_diff")
@patch("git_ai.cli._build_selection_service")
@patch("git_ai.cli.load_config")
def test_cli_dry_run_does_not_create_commit(
    mock_load_config,
    mock_build_selection_service,
    mock_build_git_diff,
    mock_build_commit_message_service,
    mock_push_current_branch,
    mock_create_commit,
) -> None:
    mock_load_config.return_value = make_config()
    mock_build_selection_service.return_value.select_files.return_value = (
        make_selected_files_result(files=["a.py"], source="staged")
    )
    mock_build_git_diff.return_value = make_git_diff(is_empty=False)

    commit_service = MagicMock()
    commit_service.generate.return_value = make_commit_message("feat: message de test")
    mock_build_commit_message_service.return_value = commit_service

    result = runner.invoke(app, ["--dry-run"])

    assert result.exit_code == 0
    assert "Message généré :" in result.stdout
    assert "feat: message de test" in result.stdout
    assert "Dry-run activé" in result.stdout
    mock_create_commit.assert_not_called()
    mock_push_current_branch.assert_not_called()


@patch("git_ai.cli.create_commit")
@patch("git_ai.cli.push_current_branch")
@patch("git_ai.cli._build_commit_message_service")
@patch("git_ai.cli._build_git_diff")
@patch("git_ai.cli._build_selection_service")
@patch("git_ai.cli.load_config")
def test_cli_creates_commit_without_push_by_default(
    mock_load_config,
    mock_build_selection_service,
    mock_build_git_diff,
    mock_build_commit_message_service,
    mock_push_current_branch,
    mock_create_commit,
) -> None:
    mock_load_config.return_value = make_config(push_after_commit=False)
    mock_build_selection_service.return_value.select_files.return_value = (
        make_selected_files_result(files=["a.py"], source="staged")
    )
    mock_build_git_diff.return_value = make_git_diff(is_empty=False)

    commit_service = MagicMock()
    commit_service.generate.return_value = make_commit_message("feat: message réel")
    mock_build_commit_message_service.return_value = commit_service

    result = runner.invoke(app, [])

    assert result.exit_code == 0
    assert "Commit créé avec succès." in result.stdout
    mock_create_commit.assert_called_once_with(message="feat: message réel", repo_path=None)
    mock_push_current_branch.assert_not_called()


@patch("git_ai.cli.create_commit")
@patch("git_ai.cli.push_current_branch")
@patch("git_ai.cli._build_commit_message_service")
@patch("git_ai.cli._build_git_diff")
@patch("git_ai.cli._build_selection_service")
@patch("git_ai.cli.load_config")
def test_cli_creates_commit_and_push_when_config_enabled(
    mock_load_config,
    mock_build_selection_service,
    mock_build_git_diff,
    mock_build_commit_message_service,
    mock_push_current_branch,
    mock_create_commit,
) -> None:
    mock_load_config.return_value = make_config(push_after_commit=True)
    mock_build_selection_service.return_value.select_files.return_value = (
        make_selected_files_result(files=["a.py"], source="staged")
    )
    mock_build_git_diff.return_value = make_git_diff(is_empty=False)

    commit_service = MagicMock()
    commit_service.generate.return_value = make_commit_message("feat: message avec push")
    mock_build_commit_message_service.return_value = commit_service

    result = runner.invoke(app, [])

    assert result.exit_code == 0
    assert "Commit créé avec succès." in result.stdout
    assert "Push effectué avec succès." in result.stdout
    mock_create_commit.assert_called_once_with(
        message="feat: message avec push",
        repo_path=None,
    )
    mock_push_current_branch.assert_called_once_with(repo_path=None)


@patch("git_ai.cli._build_commit_message_service")
@patch("git_ai.cli._build_git_diff")
@patch("git_ai.cli._build_selection_service")
@patch("git_ai.cli.load_config")
def test_cli_propagates_provider_error(
    mock_load_config,
    mock_build_selection_service,
    mock_build_git_diff,
    mock_build_commit_message_service,
) -> None:
    mock_load_config.return_value = make_config()
    mock_build_selection_service.return_value.select_files.return_value = (
        make_selected_files_result(files=["a.py"], source="staged")
    )
    mock_build_git_diff.return_value = make_git_diff(is_empty=False)

    commit_service = MagicMock()
    commit_service.generate.side_effect = ProviderError("Provider down")
    mock_build_commit_message_service.return_value = commit_service

    result = runner.invoke(app, [])

    assert result.exit_code == 1
    assert "Provider error: Provider down" in result.stderr


@patch("git_ai.cli._build_git_diff")
@patch("git_ai.cli._build_selection_service")
@patch("git_ai.cli.load_config")
def test_cli_fails_cleanly_on_empty_diff(
    mock_load_config,
    mock_build_selection_service,
    mock_build_git_diff,
) -> None:
    mock_load_config.return_value = make_config()
    mock_build_selection_service.return_value.select_files.return_value = (
        make_selected_files_result(files=[], source="staged")
    )
    mock_build_git_diff.return_value = make_git_diff(
        text="",
        files=(),
        is_empty=True,
    )

    result = runner.invoke(app, [])

    assert result.exit_code == 2
    assert "Erreur : Le diff Git est vide." in result.stderr


@patch("git_ai.cli._build_commit_message_service")
@patch("git_ai.cli._build_git_diff")
@patch("git_ai.cli._build_selection_service")
@patch("git_ai.cli.load_config")
def test_cli_passes_explicit_files_to_selection_service(
    mock_load_config,
    mock_build_selection_service,
    mock_build_git_diff,
    mock_build_commit_message_service,
) -> None:
    mock_load_config.return_value = make_config()

    selection_service = MagicMock()
    selection_service.select_files.return_value = make_selected_files_result(
        files=["src/git_ai/cli.py"],
        source="explicit",
    )
    mock_build_selection_service.return_value = selection_service
    mock_build_git_diff.return_value = make_git_diff(
        files=("src/git_ai/cli.py",),
        source="explicit",
        is_empty=False,
    )

    commit_service = MagicMock()
    commit_service.generate.return_value = make_commit_message(
        "feat(cli): ajouter la commande de commit"
    )
    mock_build_commit_message_service.return_value = commit_service

    result = runner.invoke(
        app,
        ["--files", "src/git_ai/cli.py", "--dry-run"],
    )

    assert result.exit_code == 0
    selection_service.select_files.assert_called_once_with(
        explicit_files=["src/git_ai/cli.py"]
    )
    assert "Périmètre : fichiers ciblés." in result.stdout
    assert " - src/git_ai/cli.py" in result.stdout