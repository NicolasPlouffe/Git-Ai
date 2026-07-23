from __future__ import annotations

from git_ai.cli import app


def test_init_creates_default_config_file(cli_runner, tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)

    result = cli_runner.invoke(app, ["init"])

    assert result.exit_code == 0
    target = tmp_path / "git-ai.yaml"
    assert target.exists()

    content = target.read_text(encoding="utf-8")
    assert "provider: ollama" in content
    assert "model: llama3.1:8b" in content
    assert "language: en" in content
    assert "base_url: http://localhost:11434" in content
    assert "format: conventional" in content
    assert "max_subject_length: 72" in content
    assert "include_body: false" in content
    assert "push_after_commit: false" in content
    assert "remote: origin" in content


def test_init_creates_config_at_custom_output_path(cli_runner, tmp_path) -> None:
    target = tmp_path / "custom-git-ai.yaml"

    result = cli_runner.invoke(app, ["init", "--output", str(target)])

    assert result.exit_code == 0
    assert target.exists()
    assert f"Fichier de configuration créé : {target}" in result.stdout


def test_init_refuses_existing_file_without_force(cli_runner, tmp_path) -> None:
    target = tmp_path / "git-ai.yaml"
    target.write_text("existing: true\n", encoding="utf-8")

    result = cli_runner.invoke(app, ["init", "--output", str(target)])

    assert result.exit_code == 2
    assert "Erreur : le fichier existe déjà" in result.stderr


def test_init_overwrites_existing_file_with_force(cli_runner, tmp_path) -> None:
    target = tmp_path / "git-ai.yaml"
    target.write_text("existing: true\n", encoding="utf-8")

    result = cli_runner.invoke(app, ["init", "--output", str(target), "--force"])

    assert result.exit_code == 0
    content = target.read_text(encoding="utf-8")
    assert "provider: ollama" in content
    assert "existing: true" not in content


def test_init_writes_cli_overrides_to_yaml(cli_runner, tmp_path) -> None:
    target = tmp_path / "git-ai.yaml"

    result = cli_runner.invoke(
        app,
        [
            "init",
            "--output",
            str(target),
            "--provider",
            "ollama",
            "--model",
            "mistral:7b",
            "--lang",
            "fr",
            "--base-url",
            "http://localhost:9999",
            "--push",
        ],
    )

    assert result.exit_code == 0

    content = target.read_text(encoding="utf-8")
    assert "provider: ollama" in content
    assert "model: mistral:7b" in content
    assert "language: fr" in content
    assert "base_url: http://localhost:9999" in content
    assert "push_after_commit: true" in content

    assert "- provider : ollama" in result.stdout
    assert "- model : mistral:7b" in result.stdout
    assert "- language : fr" in result.stdout
    assert "- base_url : http://localhost:9999" in result.stdout
    assert "- push_after_commit : True" in result.stdout


def test_init_rejects_unsupported_language(cli_runner, tmp_path) -> None:
    target = tmp_path / "git-ai.yaml"

    result = cli_runner.invoke(
        app,
        ["init", "--output", str(target), "--lang", "de"],
    )

    assert result.exit_code != 0
    assert "Unsupported language" in result.stdout or "Unsupported language" in result.stderr


def test_init_rejects_unsupported_provider(cli_runner, tmp_path) -> None:
    target = tmp_path / "git-ai.yaml"

    result = cli_runner.invoke(
        app,
        ["init", "--output", str(target), "--provider", "unknown-provider"],
    )

    assert result.exit_code != 0
    assert "Unsupported provider" in result.stdout or "Unsupported provider" in result.stderr