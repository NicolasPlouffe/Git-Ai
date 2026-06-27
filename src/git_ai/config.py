from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


DEFAULT_CONFIG_FILENAMES = ("git-ai.yaml", "git-ai.yml")

SUPPORTED_PROVIDERS = {"ollama", "llamacpp", "openai-compatible"}
SUPPORTED_LANGUAGES = {"fr", "en", "es", "pt"}
SUPPORTED_COMMIT_FORMATS = {"conventional", "simple"}

DEFAULT_PROVIDER: str = "ollama"
DEFAULT_MODEL: str = "qwen2.5-coder:7b"
DEFAULT_LANGUAGE: str = "fr"
DEFAULT_BASE_URL: str = "http://localhost:11434"
DEFAULT_COMMIT_FORMAT: str = "conventional"
DEFAULT_MAX_SUBJECT_LENGTH: int = 72
DEFAULT_INCLUDE_BODY: bool = False
DEFAULT_PUSH_AFTER_COMMIT: bool = False
DEFAULT_REMOTE: str = "origin"


class ConfigError(ValueError):
    """Raised when application configuration is invalid."""


@dataclass(slots=True)
class CommitConfig:
    format: str = DEFAULT_COMMIT_FORMAT
    max_subject_length: int = DEFAULT_MAX_SUBJECT_LENGTH
    include_body: bool = DEFAULT_INCLUDE_BODY

    def __post_init__(self) -> None:
        if self.format not in SUPPORTED_COMMIT_FORMATS:
            supported = ", ".join(sorted(SUPPORTED_COMMIT_FORMATS))
            raise ConfigError(
                f"Unsupported commit format '{self.format}'. "
                f"Supported formats: {supported}."
            )

        if self.max_subject_length <= 0:
            raise ConfigError("commit.max_subject_length must be greater than 0.")


@dataclass(slots=True)
class GitConfig:
    push_after_commit: bool = DEFAULT_PUSH_AFTER_COMMIT
    remote: str = DEFAULT_REMOTE

    def __post_init__(self) -> None:
        if not self.remote.strip():
            raise ConfigError("git.remote must not be empty.")


@dataclass(slots=True)
class AppConfig:
    provider: str = DEFAULT_PROVIDER
    model: str = DEFAULT_MODEL
    language: str = DEFAULT_LANGUAGE
    base_url: str = DEFAULT_BASE_URL
    commit: CommitConfig = field(default_factory=CommitConfig)
    git: GitConfig = field(default_factory=GitConfig)

    def __post_init__(self) -> None:
        if self.provider not in SUPPORTED_PROVIDERS:
            supported = ", ".join(sorted(SUPPORTED_PROVIDERS))
            raise ConfigError(
                f"Unsupported provider '{self.provider}'. "
                f"Supported providers: {supported}."
            )

        if self.language not in SUPPORTED_LANGUAGES:
            supported = ", ".join(sorted(SUPPORTED_LANGUAGES))
            raise ConfigError(
                f"Unsupported language '{self.language}'. "
                f"Supported languages: {supported}."
            )

        if not self.base_url.strip():
            raise ConfigError("base_url must not be empty.")

        if not self.model.strip():
            raise ConfigError("model must not be empty.")

    @classmethod
    def defaults(cls) -> "AppConfig":
        return cls()


def _deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    merged = dict(base)

    for key, value in override.items():
        if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
            merged[key] = _deep_merge(merged[key], value)
        else:
            merged[key] = value

    return merged


def _string_to_bool(value: str) -> bool:
    normalized = value.strip().lower()

    if normalized in {"1", "true", "yes", "on"}:
        return True
    if normalized in {"0", "false", "no", "off"}:
        return False

    raise ValueError(f"Invalid boolean value: {value}")


def _coerce_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value

    if isinstance(value, str):
        return _string_to_bool(value)

    if isinstance(value, int):
        return bool(value)

    raise ConfigError(f"Invalid boolean value: {value!r}")


def _find_default_config_path(cwd: Path | None = None) -> Path | None:
    search_root = cwd or Path.cwd()

    for filename in DEFAULT_CONFIG_FILENAMES:
        candidate = search_root / filename
        if candidate.exists():
            return candidate

    return None


def load_yaml_config(config_path: str | Path | None = None) -> dict[str, Any]:
    if config_path is None:
        path = _find_default_config_path()
        if path is None:
            return {}
    else:
        path = Path(config_path)

    if not path.exists():
        return {}

    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}

    if not isinstance(data, dict):
        raise ConfigError("YAML config root must be a mapping/object.")

    return data


def load_env_overrides(env: dict[str, str] | None = None) -> dict[str, Any]:
    source = env or os.environ
    result: dict[str, Any] = {}

    if provider := source.get("GIT_AI_PROVIDER"):
        result["provider"] = provider

    if model := source.get("GIT_AI_MODEL"):
        result["model"] = model

    if language := source.get("GIT_AI_LANGUAGE"):
        result["language"] = language

    # Variable canonique pour l'URL du backend.
    if base_url := source.get("GIT_AI_BASE_URL"):
        result["base_url"] = base_url
    elif ollama_host := source.get("GIT_AI_OLLAMA_HOST"):
        # Alias de compatibilité pour Ollama.
        result["base_url"] = ollama_host

    commit: dict[str, Any] = {}

    if commit_format := source.get("GIT_AI_COMMIT_FORMAT"):
        commit["format"] = commit_format

    if max_subject_length := source.get("GIT_AI_MAX_SUBJECT_LENGTH"):
        try:
            commit["max_subject_length"] = int(max_subject_length)
        except ValueError as exc:
            raise ConfigError(
                "GIT_AI_MAX_SUBJECT_LENGTH must be an integer."
            ) from exc

    if include_body := source.get("GIT_AI_INCLUDE_BODY"):
        commit["include_body"] = _string_to_bool(include_body)

    if commit:
        result["commit"] = commit

    git: dict[str, Any] = {}

    if push_after_commit := source.get("GIT_AI_PUSH_AFTER_COMMIT"):
        git["push_after_commit"] = _string_to_bool(push_after_commit)

    if remote := source.get("GIT_AI_REMOTE"):
        git["remote"] = remote

    if git:
        result["git"] = git

    return result


def _config_to_dict(config: AppConfig) -> dict[str, Any]:
    return {
        "provider": config.provider,
        "model": config.model,
        "language": config.language,
        "base_url": config.base_url,
        "commit": {
            "format": config.commit.format,
            "max_subject_length": config.commit.max_subject_length,
            "include_body": config.commit.include_body,
        },
        "git": {
            "push_after_commit": config.git.push_after_commit,
            "remote": config.git.remote,
        },
    }


def _build_app_config(raw: dict[str, Any]) -> AppConfig:
    defaults = AppConfig.defaults()
    commit_raw = raw.get("commit", {})
    git_raw = raw.get("git", {})

    if not isinstance(commit_raw, dict):
        raise ConfigError("commit config must be a mapping/object.")

    if not isinstance(git_raw, dict):
        raise ConfigError("git config must be a mapping/object.")

    try:
        max_subject_length = int(
            commit_raw.get(
                "max_subject_length",
                defaults.commit.max_subject_length,
            )
        )
    except (TypeError, ValueError) as exc:
        raise ConfigError("commit.max_subject_length must be an integer.") from exc

    return AppConfig(
        provider=raw.get("provider", defaults.provider),
        model=raw.get("model", defaults.model),
        language=raw.get("language", defaults.language),
        base_url=raw.get("base_url", defaults.base_url),
        commit=CommitConfig(
            format=commit_raw.get("format", defaults.commit.format),
            max_subject_length=max_subject_length,
            include_body=_coerce_bool(
                commit_raw.get("include_body", defaults.commit.include_body)
            ),
        ),
        git=GitConfig(
            push_after_commit=_coerce_bool(
                git_raw.get(
                    "push_after_commit",
                    defaults.git.push_after_commit,
                )
            ),
            remote=git_raw.get("remote", defaults.git.remote),
        ),
    )


def load_config(
    config_path: str | Path | None = None,
    cli_overrides: dict[str, Any] | None = None,
    env: dict[str, str] | None = None,
) -> AppConfig:
    defaults = _config_to_dict(AppConfig.defaults())
    yaml_config = load_yaml_config(config_path)
    env_config = load_env_overrides(env)
    cli_config = cli_overrides or {}

    merged = _deep_merge(defaults, yaml_config)
    merged = _deep_merge(merged, env_config)
    merged = _deep_merge(merged, cli_config)

    return _build_app_config(merged)