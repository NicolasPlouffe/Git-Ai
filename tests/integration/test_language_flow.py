from __future__ import annotations

import textwrap
from pathlib import Path
from subprocess import run

import pytest
from typer.testing import CliRunner

from git_ai.cli import app
from git_ai.models import LLMResponse
from git_ai.providers.ollama import OllamaProvider


runner = CliRunner()


class FakeProvider(OllamaProvider):
    """Provider de test qui renvoie une réponse contrôlée."""

    def __init__(self, response_text: str) -> None:
        super().__init__(model="test-model", base_url="http://localhost:11434")
        self._response_text = response_text

    def generate(self, request) -> LLMResponse:  # type: ignore[override]
        return LLMResponse(text=self._response_text, model_name="fake", raw_response={})


def _write_file(path: Path, content: str) -> None:
    path.write_text(textwrap.dedent(content).lstrip("\n"), encoding="utf-8")


def _patch_commit_message_service(
    monkeypatch: pytest.MonkeyPatch,
    response_text: str,
) -> None:
    fake_provider = FakeProvider(response_text)

    def _build_commit_message_service_with_fake(config):
        from git_ai.services.commit_message_service import CommitMessageService
        from git_ai.services.prompt_service import PromptService

        prompt_service = PromptService()
        return CommitMessageService(
            provider=fake_provider,
            prompt_service=prompt_service,
        )

    monkeypatch.setattr(
        "git_ai.cli._build_commit_message_service",
        _build_commit_message_service_with_fake,
    )


@pytest.fixture()
def temp_repo(tmp_path: Path) -> Path:
    """Crée un dépôt Git temporaire minimal avec un README et un commit initial."""
    repo = tmp_path

    run(["git", "init"], cwd=repo, check=True)
    run(["git", "config", "user.name", "Test User"], cwd=repo, check=True)
    run(["git", "config", "user.email", "test@example.com"], cwd=repo, check=True)

    _write_file(repo / "README.md", "# Polymark\n\nInitial content.\n")
    run(["git", "add", "README.md"], cwd=repo, check=True)
    run(["git", "commit", "-m", "chore: init"], cwd=repo, check=True)

    return repo


def test_yaml_without_cli_lang_uses_yaml_language(
    monkeypatch: pytest.MonkeyPatch,
    temp_repo: Path,
) -> None:
    _write_file(
        temp_repo / "git-ai.yaml",
        """
        provider: ollama
        model: llama3.1:8b
        language: fr
        base_url: http://localhost:11434
        """,
    )

    readme_path = temp_repo / "README.md"
    readme_path.write_text("# Polymark\n\nContenu mis à jour.\n", encoding="utf-8")
    run(["git", "add", "README.md"], cwd=temp_repo, check=True)

    _patch_commit_message_service(
        monkeypatch,
        "feat(cli): ajouter la commande commit",
    )

    result = runner.invoke(
        app,
        [
            "--dry-run",
            "--repo-path",
            str(temp_repo),
            "--config",
            str(temp_repo / "git-ai.yaml"),
        ],
        catch_exceptions=False,
    )

    assert result.exit_code == 0, result.output
    assert "Langue : fr" in result.output, result.output
    assert "feat(cli): ajouter la commande commit" in result.output, result.output


def test_cli_lang_overrides_yaml(
    monkeypatch: pytest.MonkeyPatch,
    temp_repo: Path,
) -> None:
    _write_file(
        temp_repo / "git-ai.yaml",
        """
        provider: ollama
        model: llama3.1:8b
        language: fr
        base_url: http://localhost:11434
        """,
    )

    readme_path = temp_repo / "README.md"
    readme_path.write_text("# Polymark\n\nUpdated content.\n", encoding="utf-8")
    run(["git", "add", "README.md"], cwd=temp_repo, check=True)

    _patch_commit_message_service(
        monkeypatch,
        "docs(readme): update language to English",
    )

    result = runner.invoke(
        app,
        [
            "--dry-run",
            "--lang",
            "en",
            "--repo-path",
            str(temp_repo),
            "--config",
            str(temp_repo / "git-ai.yaml"),
        ],
        catch_exceptions=False,
    )

    assert result.exit_code == 0, result.output
    assert "Langue : en" in result.output, result.output
    assert "docs(readme): update language to English" in result.output, result.output


def test_defaults_without_yaml_use_default_language(
    monkeypatch: pytest.MonkeyPatch,
    temp_repo: Path,
) -> None:
    yaml_path = temp_repo / "git-ai.yaml"
    if yaml_path.exists():
        yaml_path.unlink()

    readme_path = temp_repo / "README.md"
    readme_path.write_text("# Polymark\n\nAnother change.\n", encoding="utf-8")
    run(["git", "add", "README.md"], cwd=temp_repo, check=True)

    _patch_commit_message_service(
        monkeypatch,
        "docs(readme): describe polymark project in English",
    )

    result = runner.invoke(
        app,
        [
            "--dry-run",
            "--repo-path",
            str(temp_repo),
        ],
        catch_exceptions=False,
    )

    assert result.exit_code == 0, result.output
    assert "Langue : en" in result.output, result.output
    assert "docs(readme): describe polymark project in English" in result.output, result.output