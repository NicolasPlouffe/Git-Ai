from __future__ import annotations

from pathlib import Path

from git_ai.models import CommitLanguage, PromptPayload, PromptRequest


class PromptService:
    """Construit les prompts de commit à partir d'un diff normalisé."""

    _MAX_DIFF_CHARS = 4000  # à ajuster selon le modèle et max_tokens

    def __init__(self, prompts_dir: Path | None = None) -> None:
        # Par défaut, on lit les templates dans src/git_ai/prompts/.
        self._prompts_dir = prompts_dir or Path(__file__).resolve().parents[1] / "prompts"

    def build_commit_prompt(self, request: PromptRequest) -> PromptPayload:
        """Retourne un payload prêt pour le provider."""
        template = self._load_template(request.language)

        diff_text = self._truncate_diff(request.diff.text.strip())
        files_block = self._format_files(request)

        user_prompt = template.format(
            max_subject_length=request.max_subject_length,
            diff_source=request.diff.source.value,
            files_block=files_block,
            diff_text=diff_text,
        )

        return PromptPayload(
            system_prompt=self._build_system_prompt(request.language),
            user_prompt=user_prompt,
            metadata={
                "language": request.language.value,
                "diff_source": request.diff.source.value,
                "max_subject_length": str(request.max_subject_length),
            },
        )

    def _load_template(self, language: CommitLanguage) -> str:
        template_map = {
            CommitLanguage.FRENCH: "commit_fr.txt",
            CommitLanguage.ENGLISH: "commit_en.txt",
            CommitLanguage.SPANISH: "commit_es.txt",
            CommitLanguage.PORTUGUESE: "commit_pt.txt",
        }

        template_path = self._prompts_dir / template_map[language]
        if not template_path.exists():
            raise FileNotFoundError(f"Missing prompt template: {template_path}")
        return template_path.read_text(encoding="utf-8")

    def _build_system_prompt(self, language: CommitLanguage) -> str:
        prompts = {
            CommitLanguage.FRENCH: (
                "Tu es un générateur de messages de commit Git. "
                "Tu réponds uniquement avec un objet JSON valide contenant "
                "une seule clé \"commit\". Aucun texte, explication, "
                "ou Markdown avant ou après le JSON. "
                "Le sujet doit être rédigé uniquement dans la langue demandée."
            ),
            CommitLanguage.ENGLISH: (
                "You are a Git commit message generator. "
                "You reply only with one valid JSON object containing "
                "exactly one key \"commit\". No text, explanation, "
                "or Markdown before or after the JSON. "
                "The subject must be written only in the requested language."
            ),
            CommitLanguage.SPANISH: (
                "Eres un generador de mensajes de commit Git. "
                "Respondes solo con un objeto JSON válido que contiene "
                "exactamente una clave \"commit\". Sin texto, explicación "
                "ni Markdown antes o después del JSON. "
                "El asunto debe estar redactado únicamente en el idioma solicitado."
            ),
            CommitLanguage.PORTUGUESE: (
                "Você é um gerador de mensagens de commit Git. "
                "Você responde apenas com um objeto JSON válido contendo "
                "exatamente uma chave \"commit\". Sem texto, explicação "
                "ou Markdown antes ou depois do JSON. "
                "O assunto deve ser escrito apenas no idioma solicitado."
            ),
        }
        return prompts[language]

    def _format_files(self, request: PromptRequest) -> str:
        # On garde ce bloc compact pour aider le modèle sans surcharger le prompt.
        if not request.diff.files:
            return "- (none)"

        return "\n".join(f"- {path}" for path in request.diff.files)

    def _truncate_diff(self, diff_text: str) -> str:
        if len(diff_text) <= self._MAX_DIFF_CHARS:
            return diff_text

        truncated = diff_text[: self._MAX_DIFF_CHARS]
        return truncated + "\n[... diff truncated ...]"