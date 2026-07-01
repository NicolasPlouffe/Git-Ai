from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Mapping

@dataclass(frozen=True)
class ChangedFile:
    path: str
    change_type: ChangeType


class ChangeType(str, Enum):
    ADDED = "A",
    MODIFIED = "M",
    DELETED = "D",
    RENAMED = "R",
    UNTRACKED = "??",


class CommitLanguage(str, Enum):
    FRENCH = "fr"
    ENGLISH = "en"
    SPANISH = "es"
    PORTUGUESE = "pt"


@dataclass(frozen=True, slots=True)
class CommitMessage:
    text: str
    language: CommitLanguage

    @property
    def subject(self) -> str:
        stripped = self.text.strip()
        return stripped.splitlines()[0] if stripped else ""

    @property
    def is_empty(self) -> bool:
        return not self.text.strip()


class DiffSource(str, Enum):
    STAGED = "staged"
    FILES = "files"


@dataclass(frozen=True, slots=True)
class FileSelection:
    source: DiffSource
    files: tuple[str, ...] = ()

    @property
    def is_staged_only(self) -> bool:
        return self.source is DiffSource.STAGED

    @property
    def has_files(self) -> bool:
        return bool(self.files)


@dataclass(frozen=True, slots=True)
class GitDiff:
    text: str
    files: tuple[str, ...]
    source: DiffSource

    @property
    def is_empty(self) -> bool:
        return not self.text.strip()


@dataclass(frozen=True, slots=True)
class LLMResponse:
    text: str
    model_name: str | None = None
    raw_response: Mapping[str, object] | None = None

    @property
    def is_empty(self) -> bool:
        return not self.text.strip()


@dataclass(frozen=True, slots=True)
class LLMRequest:
    prompt: str
    system_prompt: str | None = None
    temperature: float = 0.2
    max_tokens: int | None = None


@dataclass(frozen=True, slots=True)
class PromptRequest:
    diff: GitDiff
    language: CommitLanguage
    max_subject_length: int = 72


@dataclass(frozen=True, slots=True)
class PromptPayload:
    system_prompt: str
    user_prompt: str
    metadata: Mapping[str, str] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class ProviderInfo:
    name: str
    model: str | None = None
    endpoint: str | None = None
    extra: Mapping[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class ScaffoldDetectionResult:
    is_bootstrap: bool
    best_match: ScaffoldMatch | None = None
    added_count: int = 0
    modified_count: int = 0
    deleted_count: int = 0
    total_count: int = 0
    added_ratio: float = 0.0


@dataclass(frozen=True)
class ScaffoldMatch:
    key:str
    label: str
    confidence: float
    matched_signals: tuple[str, ...] = ()
    generic_only: bool = False