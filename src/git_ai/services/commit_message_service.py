from __future__ import annotations

import json
import re

from git_ai.exceptions import ProviderResponseError
from git_ai.models import CommitMessage, LLMRequest, LLMResponse, PromptRequest
from git_ai.providers.base import LLMProvider
from git_ai.services.prompt_service import PromptService
from git_ai.services.scaffold_detection import ScaffoldDetectionService


class CommitMessageService:
    """Orchestre detection scaffold + prompt + provider + nettoyage final.

    Contrat principal attendu du provider : un objet JSON valide avec une
    seule cle "commit", ex. {"commit": "type(scope): sujet"}.
    Si aucun JSON exploitable n'est trouve, un fallback texte plus tolerant
    est tente. Si le contenu ressemble a une reponse documentaire/explicative,
    la generation echoue avec une erreur claire plutot que de produire un
    commit de mauvaise qualite.
    """

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
        """Produit un message de commit propre a partir d'un diff."""
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

    # ------------------------------------------------------------------
    # Sanitization: orchestrateur principal (JSON-first, fallback texte)
    # ------------------------------------------------------------------

    def _sanitize_response(
        self,
        response: LLMResponse,
        max_subject_length: int,
    ) -> str:
        if response.is_empty:
            raise ProviderResponseError("The provider returned an empty commit message.")

        raw_text = response.text.strip()

        if not raw_text:
            raise ProviderResponseError("The commit message is empty after sanitization.")

        # 1. Contrat principal : JSON direct.
        commit_value = self._extract_commit_from_json(raw_text)

        # 2. Contrat secondaire : JSON embarque dans un texte plus bruite.
        if commit_value is None:
            commit_value = self._extract_embedded_commit_from_json(raw_text)

        if commit_value is not None:
            return self._sanitize_commit_value(commit_value, max_subject_length)

        # 3. Fallback texte libre, seulement si aucun JSON n'est exploitable.
        return self._sanitize_text_fallback(raw_text, max_subject_length)

    def _sanitize_commit_value(self, commit_value: str, max_subject_length: int) -> str:
        text = commit_value.strip()

        if not text:
            raise ProviderResponseError("The commit value extracted from JSON is empty.")

        if self._looks_like_explanatory_block(text):
            raise ProviderResponseError(
                "The provider returned an explanatory or documentation-style response "
                "instead of a commit message."
            )

        lines = [line.rstrip() for line in text.splitlines()]
        lines = self._drop_leading_empty_lines(lines)

        if not lines:
            raise ProviderResponseError("The commit message has no usable content.")

        subject, remaining_lines = self._extract_subject_and_body(lines)
        subject = self._truncate_subject(subject, max_subject_length)

        if not subject:
            raise ProviderResponseError("The commit subject is empty.")

        body_lines = self._normalize_body_lines(remaining_lines)

        if not body_lines:
            return subject

        body = "\n".join(body_lines)
        return f"{subject}\n\n{body}"

    def _sanitize_text_fallback(self, text: str, max_subject_length: int) -> str:
        cleaned = self._extract_commit_text(text)

        if not cleaned:
            raise ProviderResponseError("The commit message is empty after sanitization.")

        if self._looks_like_explanatory_block(cleaned):
            raise ProviderResponseError(
                "The provider returned an explanatory or documentation-style response "
                "instead of a commit message."
            )

        lines = [line.rstrip() for line in cleaned.splitlines()]
        lines = self._drop_leading_empty_lines(lines)

        if not lines:
            raise ProviderResponseError("The commit message has no usable content.")

        subject, remaining_lines = self._extract_subject_and_body(lines)
        subject = self._truncate_subject(subject, max_subject_length)

        if not subject:
            raise ProviderResponseError("The commit subject is empty.")

        body_lines = self._normalize_body_lines(remaining_lines)

        if not body_lines:
            return subject

        body = "\n".join(body_lines)
        return f"{subject}\n\n{body}"

    # ------------------------------------------------------------------
    # Extraction JSON
    # ------------------------------------------------------------------

    def _extract_commit_from_json(self, text: str) -> str | None:
        candidate = text.strip()
        candidate = self._strip_code_fences(candidate)
        candidate = candidate.strip()

        try:
            payload = json.loads(candidate)
        except json.JSONDecodeError:
            return None

        return self._read_commit_key(payload)

    def _extract_embedded_commit_from_json(self, text: str) -> str | None:
        """Cherche un objet JSON plausible avec cle "commit" a l'interieur
        d'un texte plus large (introduction, bruit avant/apres, etc.)."""
        candidates = re.findall(r"\{[^{}]*\"commit\"[^{}]*\}", text, flags=re.DOTALL)

        for candidate in candidates:
            try:
                payload = json.loads(candidate)
            except json.JSONDecodeError:
                continue

            commit_value = self._read_commit_key(payload)
            if commit_value is not None:
                return commit_value

        return None

    def _read_commit_key(self, payload: object) -> str | None:
        if not isinstance(payload, dict):
            return None

        commit = payload.get("commit")
        if not isinstance(commit, str):
            return None

        normalized = commit.strip()
        return normalized or None

    # ------------------------------------------------------------------
    # Fallback texte libre
    # ------------------------------------------------------------------

    def _extract_subject_and_body(self, lines: list[str]) -> tuple[str, list[str]]:
        for index, raw_line in enumerate(lines):
            candidate = self._normalize_subject_candidate(raw_line)
            if not candidate:
                continue

            if self._looks_explanatory(candidate):
                continue

            return candidate, lines[index + 1:]

        raise ProviderResponseError("The provider did not return a usable commit subject.")

    def _extract_commit_text(self, text: str) -> str:
        cleaned = text
        cleaned = self._strip_code_fences(cleaned)
        cleaned = self._strip_known_prefixes(cleaned)
        cleaned = self._strip_prompt_echo(cleaned)
        return cleaned.strip()

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

    def _normalize_subject_candidate(self, subject: str) -> str:
        subject = subject.strip().strip('"').strip("'")
        subject = subject.replace("`", "")
        subject = " ".join(subject.split())

        if subject.endswith("."):
            subject = subject[:-1].rstrip()

        return subject

    def _looks_explanatory(self, subject: str) -> bool:
        lowered = subject.lower()

        explanatory_starts = (
            "voici",
            "voici un message",
            "voici le message",
            "il semble",
            "it appears",
            "here is",
            "here's",
            "this commit",
            "ce commit",
            "esta respuesta",
            "parece que",
            "commit message",
            "message de commit",
            "mensaje de commit",
            "respuesta",
            "response",
            "answer",
        )

        if any(lowered.startswith(prefix) for prefix in explanatory_starts):
            return True

        if lowered.endswith(":"):
            return True

        return False

    def _looks_like_explanatory_block(self, text: str) -> bool:
        lowered = text.lower()
        lines = [line.strip() for line in text.splitlines() if line.strip()]

        markdown_heading_count = sum(
            1
            for line in lines[:6]
            if line.startswith("#") or (line.startswith("**") and line.endswith("**"))
        )

        bullet_count = sum(
            1
            for line in lines[:8]
            if line.startswith("* ") or line.startswith("- ")
        )

        explanatory_markers = (
            "introduction",
            "architecture",
            "summary",
            "résumé",
            "resume",
            "overview",
            "project",
            "ce projet",
            "this project",
        )

        marker_hits = sum(1 for marker in explanatory_markers if marker in lowered)

        if markdown_heading_count >= 1 and bullet_count >= 1:
            return True

        if markdown_heading_count >= 2:
            return True

        if bullet_count >= 3 and marker_hits >= 1:
            return True

        return False

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