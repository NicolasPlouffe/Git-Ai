class GitAIError(Exception):
    """Base exception for the application."""


class ConfigError(GitAIError):
    """Raised when configuration is invalid or incomplete."""


class GitRepositoryError(GitAIError):
    """Raised when the current directory is not a valid Git repository."""


class GitDiffError(GitAIError):
    """Raised when a diff cannot be produced."""


class FileSelectionError(GitAIError):
    """Raised when the selected files are invalid or inconsistent."""


class PromptGenerationError(GitAIError):
    """Raised when prompt construction fails."""


class ProviderError(GitAIError):
    """Base error for provider failures."""


class ProviderConnectionError(ProviderError):
    """Raised when a provider backend cannot be reached."""


class ProviderResponseError(ProviderError):
    """Raised when a provider returns an invalid or unusable response."""


class CommitMessageError(GitAIError):
    """Raised when a commit message cannot be generated or normalized."""