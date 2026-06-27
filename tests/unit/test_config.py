from pathlib import Path

import pytest

from git_ai.config import (
    AppConfig,
    ConfigError,
    DEFAULT_BASE_URL,
    DEFAULT_COMMIT_FORMAT,
    DEFAULT_INCLUDE_BODY,
    DEFAULT_LANGUAGE,
    DEFAULT_MAX_SUBJECT_LENGTH,
    DEFAULT_MODEL,
    DEFAULT_PROVIDER,
    DEFAULT_PUSH_AFTER_COMMIT,
    DEFAULT_REMOTE,
    _string_to_bool,
    load_config,
    load_env_overrides,
    load_yaml_config,
)


def test_load_config_returns_defaults_when_no_yaml_env_or_cli() -> None:
    config = load_config(config_path=Path("does-not-exist.yaml"), env={})

    assert isinstance(config, AppConfig)
    assert config.provider == DEFAULT_PROVIDER
    assert config.model == DEFAULT_MODEL
    assert config.language == DEFAULT_LANGUAGE
    assert config.base_url == DEFAULT_BASE_URL
    assert config.commit.format == DEFAULT_COMMIT_FORMAT
    assert config.commit.max_subject_length == DEFAULT_MAX_SUBJECT_LENGTH
    assert config.commit.include_body == DEFAULT_INCLUDE_BODY
    assert config.git.push_after_commit == DEFAULT_PUSH_AFTER_COMMIT
    assert config.git.remote == DEFAULT_REMOTE


def test_load_yaml_config_reads_mapping(tmp_path: Path) -> None:
    config_file = tmp_path / "git-ai.yaml"
    config_file.write_text(
        """
provider: ollama
model: mistral
language: en
base_url: http://localhost:11434
commit:
  format: simple
  max_subject_length: 60
  include_body: true
git:
  push_after_commit: true
  remote: upstream
""".strip(),
        encoding="utf-8",
    )

    data = load_yaml_config(config_file)

    assert data["provider"] == "ollama"
    assert data["model"] == "mistral"
    assert data["language"] == "en"
    assert data["base_url"] == "http://localhost:11434"
    assert data["commit"]["format"] == "simple"
    assert data["commit"]["max_subject_length"] == 60
    assert data["commit"]["include_body"] is True
    assert data["git"]["push_after_commit"] is True
    assert data["git"]["remote"] == "upstream"


def test_load_yaml_config_returns_empty_dict_when_missing_file() -> None:
    data = load_yaml_config("missing-file.yaml")

    assert data == {}


def test_load_env_overrides_reads_flat_and_nested_values() -> None:
    env = {
        "GIT_AI_PROVIDER": "ollama",
        "GIT_AI_MODEL": "custom-env-model",
        "GIT_AI_LANGUAGE": "es",
        "GIT_AI_OLLAMA_HOST": "http://127.0.0.1:11434",
        "GIT_AI_COMMIT_FORMAT": "simple",
        "GIT_AI_MAX_SUBJECT_LENGTH": "50",
        "GIT_AI_INCLUDE_BODY": "true",
        "GIT_AI_PUSH_AFTER_COMMIT": "yes",
        "GIT_AI_REMOTE": "origin",
    }

    data = load_env_overrides(env)

    assert data["provider"] == "ollama"
    assert data["model"] == "custom-env-model"
    assert data["language"] == "es"
    assert data["base_url"] == "http://127.0.0.1:11434"
    assert data["commit"]["format"] == "simple"
    assert data["commit"]["max_subject_length"] == 50
    assert data["commit"]["include_body"] is True
    assert data["git"]["push_after_commit"] is True
    assert data["git"]["remote"] == "origin"


def test_load_env_overrides_prefers_base_url_over_ollama_host() -> None:
    env = {
        "GIT_AI_BASE_URL": "http://base-url:11434",
        "GIT_AI_OLLAMA_HOST": "http://ollama-host:11434",
    }

    data = load_env_overrides(env)

    # La variable canonique l'emporte.
    assert data["base_url"] == "http://base-url:11434"

def test_load_env_overrides_uses_ollama_host_when_base_url_missing() -> None:
    env = {
        "GIT_AI_OLLAMA_HOST": "http://ollama-host:11434",
    }

    data = load_env_overrides(env)

    assert data["base_url"] == "http://ollama-host:11434"


def test_load_env_overrides_handles_minimal_env() -> None:
    env = {
        "GIT_AI_PROVIDER": "ollama",
        "GIT_AI_MODEL": "env-model",
        "GIT_AI_LANGUAGE": "es",
    }

    data = load_env_overrides(env)

    assert data["provider"] == "ollama"
    assert data["model"] == "env-model"
    assert data["language"] == "es"
    assert "commit" not in data
    assert "git" not in data


def test_load_env_overrides_rejects_non_integer_max_subject_length() -> None:
    env = {
        "GIT_AI_MAX_SUBJECT_LENGTH": "abc",
    }

    with pytest.raises(ConfigError, match="must be an integer"):
        load_env_overrides(env)


def test_load_env_overrides_rejects_non_integer_max_subject_length() -> None:
    env = {
        "GIT_AI_MAX_SUBJECT_LENGTH": "abc",
    }

    with pytest.raises(ConfigError, match="must be an integer"):
        load_env_overrides(env)


def test_load_config_applies_precedence_defaults_yaml_env_cli(tmp_path: Path) -> None:
    config_file = tmp_path / "git-ai.yaml"
    config_file.write_text(
        """
provider: ollama
model: yaml-model
language: fr
base_url: http://yaml-host:11434
commit:
  format: conventional
  max_subject_length: 70
  include_body: false
git:
  push_after_commit: false
  remote: origin
""".strip(),
        encoding="utf-8",
    )

    env = {
        "GIT_AI_MODEL": "env-model",
        "GIT_AI_LANGUAGE": "en",
        "GIT_AI_INCLUDE_BODY": "true",
    }

    cli_overrides = {
        "language": "es",
        "commit": {
            "format": "simple",
        },
    }

    config = load_config(
        config_path=config_file,
        cli_overrides=cli_overrides,
        env=env,
    )

    assert config.provider == "ollama"
    assert config.model == "env-model"
    assert config.language == "es"
    assert config.base_url == "http://yaml-host:11434"
    assert config.commit.format == "simple"
    assert config.commit.max_subject_length == 70
    assert config.commit.include_body is True
    assert config.git.push_after_commit is False
    assert config.git.remote == "origin"


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("1", True),
        ("true", True),
        ("yes", True),
        ("on", True),
        ("0", False),
        ("false", False),
        ("no", False),
        ("off", False),
    ],
)
def test_string_to_bool_supports_common_values(value: str, expected: bool) -> None:
    assert _string_to_bool(value) is expected


def test_string_to_bool_raises_on_invalid_value() -> None:
    with pytest.raises(ValueError):
        _string_to_bool("maybe")


def test_load_config_accepts_portuguese_pr_language(tmp_path: Path) -> None:
    config_file = tmp_path / "git-ai.yaml"
    config_file.write_text(
        """
language: pt
""".strip(),
        encoding="utf-8",
    )

    config = load_config(config_path=config_file, env={})

    assert config.language == "pt"


def test_load_config_rejects_unsupported_language(tmp_path: Path) -> None:
    config_file = tmp_path / "git-ai.yaml"
    config_file.write_text(
        """
language: de
""".strip(),
        encoding="utf-8",
    )

    with pytest.raises(ConfigError, match="Unsupported language"):
        load_config(config_path=config_file, env={})


def test_load_config_rejects_unsupported_provider(tmp_path: Path) -> None:
    config_file = tmp_path / "git-ai.yaml"
    config_file.write_text(
        """
provider: anthropic
""".strip(),
        encoding="utf-8",
    )

    with pytest.raises(ConfigError, match="Unsupported provider"):
        load_config(config_path=config_file, env={})


def test_load_config_rejects_invalid_commit_format(tmp_path: Path) -> None:
    config_file = tmp_path / "git-ai.yaml"
    config_file.write_text(
        """
commit:
  format: semantic
""".strip(),
        encoding="utf-8",
    )

    with pytest.raises(ConfigError, match="Unsupported commit format"):
        load_config(config_path=config_file, env={})


def test_load_config_rejects_non_positive_max_subject_length(tmp_path: Path) -> None:
    config_file = tmp_path / "git-ai.yaml"
    config_file.write_text(
        """
commit:
  max_subject_length: 0
""".strip(),
        encoding="utf-8",
    )

    with pytest.raises(ConfigError, match="max_subject_length"):
        load_config(config_path=config_file, env={})


def test_load_config_rejects_empty_remote(tmp_path: Path) -> None:
    config_file = tmp_path / "git-ai.yaml"
    config_file.write_text(
        """
git:
  remote: "   "
""".strip(),
        encoding="utf-8",
    )

    with pytest.raises(ConfigError, match="git.remote"):
        load_config(config_path=config_file, env={})


def test_load_config_rejects_empty_base_url_from_cli_override() -> None:
    with pytest.raises(ConfigError, match="base_url"):
        load_config(
            config_path="does-not-exist.yaml",
            env={},
            cli_overrides={"base_url": "   "},
        )