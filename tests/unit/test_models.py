from git_ai.models import (
    CommitLanguage,
    CommitMessage,
    DiffSource,
    FileSelection,
    GitDiff,
    LLMResponse,
)


def test_file_selection_detects_staged_only_mode():
    selection = FileSelection(source=DiffSource.STAGED)

    assert selection.is_staged_only is True
    assert selection.has_files is False


def test_file_selection_detects_explicit_files():
    selection = FileSelection(
        source=DiffSource.FILES,
        files=("src/git_ai/models.py", "src/git_ai/providers/base.py"),
    )

    assert selection.is_staged_only is False
    assert selection.has_files is True


def test_git_diff_is_empty_when_text_is_blank():
    diff = GitDiff(
        text="   \n",
        files=(),
        source=DiffSource.STAGED,
    )

    assert diff.is_empty is True


def test_git_diff_is_not_empty_when_text_has_content():
    diff = GitDiff(
        text="diff --git a/file.py b/file.py",
        files=("file.py",),
        source=DiffSource.FILES,
    )

    assert diff.is_empty is False


def test_llm_response_is_empty_when_text_is_blank():
    response = LLMResponse(text="   ")

    assert response.is_empty is True


def test_commit_message_subject_returns_first_line():
    message = CommitMessage(
        text="feat: add provider contract\n\nDetailed body",
        language=CommitLanguage.FRENCH,
    )

    assert message.subject == "feat: add provider contract"
    assert message.is_empty is False


def test_commit_message_is_empty_when_blank():
    message = CommitMessage(
        text="   ",
        language=CommitLanguage.ENGLISH,
    )

    assert message.is_empty is True
    assert message.subject == ""