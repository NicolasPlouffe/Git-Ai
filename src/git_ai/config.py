from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal, Mapping, Any


Language = Literal["fr", "en", "es"]
ProviderName = Literal["ollama", "llamacpp", "openai-compatible"]


@dataclass
class CommitConfig:
    format: Literal["conventional", "simple"] = "conventional"
    max_subject_length: int = 72
    include_body: bool = True


@dataclass
class GitConfig:
    push_after_commit: bool = False
    remote: str = "origin"


@dataclass
class ProviderConfig:
    name: ProviderName = "ollama"
    model: str = "llama3"
    base_url: str = "http://localhost:11434"


@dataclass
class AppConfig:
    provider: ProviderConfig = field(default_factory=ProviderConfig)
    language: Language = "fr"
    commit: CommitConfig = field(default_factory=CommitConfig)
    git: GitConfig = field(default_factory=GitConfig)

    @classmethod
    def defaults(cls) -> "AppConfig":
        """Valeurs par défaut V1."""
        return cls()