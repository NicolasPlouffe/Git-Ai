from __future__ import annotations

import json

from git_ai.exceptions import ProviderResponseError
from git_ai.models import CommitMessage, LLMRequest, LLMResponse, PromptRequest
from git_ai.providers.base import LLMProvider
from git_ai.services.prompt_service import PromptService
from git_ai.services.scaffold_detection import ScaffoldDetectionService


class CommitMessageService:
    """Orchestre détection scaffold + prompt + provider + nettoyage final."""

    def __init__(
        self,
        provider: LLMProvider,
        prompt_service: PromptService,
        temperature: float = 0.2,
        max_tokens: int | None = 120,
        scaffold_detection_service: ScaffoldDetectionService | None = None,
    ) -> None:
        self._provider = provider
        self._prompt_service = prompt_service
        self._temperature = temperature
        self._max_tokens = max_tokens
        self._scaffold_detection_service = scaffold_detection_service

    def generate(self, request: PromptRequest) -> CommitMessage:
        """Produit un message de commit propre à partir d'un diff."""
        if request.diff.is_empty:
            raise ValueError("Cannot generate a commit message from an empty diff.")

        fallback = self._detect_scaffold_fallback(request)
        if fallback is not None:
            commit_text = self._sanitize_plain_commit_text(
                text=fallback.commit_text,
                max_subject_length=request.max_subject_length,
            )
            return CommitMessage(
                text=commit_text,
                language=request.language,
            )

        prompt_payload = self._prompt_service.build_commit_prompt(request)

        llm_request = LLMRequest(
            prompt=prompt_payload.user_prompt,
            system_prompt=prompt_payload.system_prompt,
            temperature=self._temperature,
            max_tokens=self._max_tokens,
        )

        llm_response = self._provider.generate(llm_request)
        commit_text = self._sanitize_response(
            response=llm_response,
            max_subject_length=request.max_subject_length,
        )

        return CommitMessage(
            text=commit_text,
            language=request.language,
        )

    def _detect_scaffold_fallback(self, request: PromptRequest):
        if self._scaffold_detection_service is None:
            return None
        return self._scaffold_detection_service.detect(request)

    def _sanitize_plain_commit_text(
        self,
        text: str,
        max_subject_length: int,
    ) -> str:
        response = LLMResponse(text=text)
        return self._sanitize_response(
            response=response,
            max_subject_length=max_subject_length,
        )

    def _sanitize_response(
        self,
        response: LLMResponse,
        max_subject_length: int,
    ) -> str:
        if response.is_empty:
            raise ProviderResponseError("The provider returned an empty commit message.")

        text = response.text.strip()
        text = self._extract_commit_text(text)

        if not text:
            raise ProviderResponseError("The commit message is empty after sanitization.")

        lines = [line.rstrip() for line in text.splitlines()]
        lines = self._drop_leading_empty_lines(lines)

        if not lines:
            raise ProviderResponseError("The commit message has no usable content.")

        subject = self._normalize_subject(lines[0])

        if not subject:
            raise ProviderResponseError("The commit subject is empty.")

        subject = self._truncate_subject(subject, max_subject_length)

        body_lines = self._normalize_body_lines(lines[1:])

        if not body_lines:
            return subject

        body = "\n".join(body_lines)
        return f"{subject}\n\n{body}"

    def _extract_commit_text(self, text: str) -> str:
        json_commit = self._extract_commit_from_json(text)
        if json_commit is not None:
            return json_commit.strip()

        cleaned = text
        cleaned = self._strip_code_fences(cleaned)
        cleaned = self._strip_known_prefixes(cleaned)
        cleaned = self._strip_prompt_echo(cleaned)
        return cleaned.strip()

    def _extract_commit_from_json(self, text: str) -> str | None:
        candidate = text.strip()

        try:
            payload = json.loads(candidate)
        except json.JSONDecodeError:
            return None

        if not isinstance(payload, dict):
            return None

        commit = payload.get("commit")
        if not isinstance(commit, str):
            return None

        normalized = commit.strip()
        return normalized or None

    def _strip_code_fences(self, text: str) -> str:
        lines = text.splitlines()
        cleaned_lines = [
            line
            for line in lines
            if line.strip() not in {"```", "```txt", "```text", "```markdown", "```json"}
        ]
        return "\n".join(cleaned_lines).strip()

    def _strip_known_prefixes(self, text: str) -> str:
        prefixes = (
            "commit message:",
            "message de commit :",
            "message de commit:",
            "mensaje de commit:",
            "mensagem de commit:",
            "réponse :",
            "reponse :",
            "answer:",
            "respuesta:",
            "response:",
        )

        stripped = text.strip()
        lowered = stripped.lower()

        for prefix in prefixes:
            if lowered.startswith(prefix):
                return stripped[len(prefix):].strip()

        return stripped

    def _drop_leading_empty_lines(self, lines: list[str]) -> list[str]:
        index = 0
        while index < len(lines) and not lines[index].strip():
            index += 1
        return lines[index:]

    def _normalize_subject(self, subject: str) -> str:
        subject = subject.strip().strip('"').strip("'")
        subject = subject.replace("`", "")
        subject = " ".join(subject.split())

        if subject.endswith("."):
            subject = subject[:-1].rstrip()

        lowered = subject.lower()
        explanatory_starts = (
            "voici",
            "il semble",
            "it appears",
            "here is",
            "this commit",
            "ce commit",
            "esta respuesta",
            "parece que",
        )

        for prefix in explanatory_starts:
            if lowered.startswith(prefix):
                raise ProviderResponseError(
                    "The provider returned an explanatory response instead of a commit subject."
                )

        return subject

    def _normalize_body_lines(self, lines: list[str]) -> list[str]:
        cleaned_lines: list[str] = []
        previous_blank = False

        for raw_line in lines:
            line = raw_line.strip()
            line = line.replace("`", "")

            if not line:
                if cleaned_lines and not previous_blank:
                    cleaned_lines.append("")
                previous_blank = True
                continue

            cleaned_lines.append(" ".join(line.split()))
            previous_blank = False

        while cleaned_lines and cleaned_lines[-1] == "":
            cleaned_lines.pop()

        return cleaned_lines

    def _truncate_subject(self, subject: str, max_subject_length: int) -> str:
        if len(subject) <= max_subject_length:
            return subject

        truncated = subject[:max_subject_length].rstrip(" .:-")

        last_space = truncated.rfind(" ")
        if last_space > 0:
            truncated = truncated[:last_space].rstrip(" .:-")

        truncated = self._trim_incomplete_ending(truncated)

        if truncated:
            return truncated

        fallback = subject[:max_subject_length].rstrip(" .:-")
        return self._trim_incomplete_ending(fallback) or fallback

    def _trim_incomplete_ending(self, subject: str) -> str:
        weak_endings = {
            "pour",
            "avec",
            "sans",
            "via",
            "en",
            "sur",
            "de",
            "d",
        }

        cleaned = subject.strip()

        while cleaned:
            last_word = cleaned.split()[-1].lower()
            if last_word not in weak_endings:
                return cleaned

            last_space = cleaned.rfind(" ")
            if last_space <= 0:
                return ""
            cleaned = cleaned[:last_space].rstrip(" .:-")

        return cleaned

    def _strip_prompt_echo(self, text: str) -> str:
        markers = (
            "\nRédige un message de commit",
            "\nRedige un message de commit",
            "\nContraintes :",
            "\nChoix du type :",
            "\nFormat attendu :",
            "\nRègles de sortie :",
            "\nRegles de sortie :",
            "\nSi un corps est nécessaire :",
            "\nSi un corps est necessaire :",
            "\nExemples de bons sujets :",
            "\nSource du diff :",
            "\nFichiers concernés :",
            "\nFichiers concernes :",
            "\nDiff :",
        )

        cleaned = text.strip()

        for marker in markers:
            index = cleaned.find(marker)
            if index != -1:
                cleaned = cleaned[:index].rstrip()

        return cleaned