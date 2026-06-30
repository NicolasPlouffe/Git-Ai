from __future__ import annotations

from pathlib import Path

from git_ai.models import CommitLanguage, PromptPayload, PromptRequest


class PromptService:
    """Construit les prompts de commit à partir d'un diff normalisé."""

    def __init__(self, prompts_dir: Path | None = None) -> None:
        # Par défaut, on lit les templates dans src/git_ai/prompts/.
        self._prompts_dir = prompts_dir or Path(__file__).resolve().parents[1] / "prompts"

    def build_commit_prompt(self, request: PromptRequest) -> PromptPayload:
        """Retourne un payload prêt pour le provider."""
        template = self._load_template(request.language)

        files_block = self._format_files(request)
        user_prompt = template.format(
            max_subject_length=request.max_subject_length,
            diff_source=request.diff.source.value,
            files_block=files_block,
            diff_text=request.diff.text.strip(),
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
                "Tu écris uniquement un message de commit Git final. "
                "Réponds uniquement avec le message de commit final, et rien d'autre. "
                "N'ajoute aucune introduction, aucune explication, aucune liste, "
                "aucun commentaire, aucun titre, aucun label, aucun guillemet, "
                "et aucun Markdown. "
                "Le sujet doit être rédigé uniquement dans la langue demandée."
            ),
            CommitLanguage.ENGLISH: (
                "You write only the final Git commit message. "
                "Reply with the final commit message only, and nothing else. "
                "Do not add any introduction, explanation, list, commentary, "
                "title, label, quotes, or Markdown. "
                "The subject must be written only in the requested language."
            ),
            CommitLanguage.SPANISH: (
                "Escribes únicamente el mensaje final de commit Git. "
                "Devuelve solo el mensaje final de commit, y nada más. "
                "No añadas ninguna introducción, explicación, lista, comentario, "
                "título, etiqueta, comillas ni Markdown. "
                "El asunto debe estar redactado únicamente en el idioma solicitado."
            ),
            CommitLanguage.PORTUGUESE: (
                "Você escreve apenas a mensagem final de commit Git. "
                "Retorne somente a mensagem final de commit, e nada mais. "
                "Não adicione introdução, explicação, lista, comentário, "
                "título, rótulo, aspas nem Markdown. "
                "O assunto deve ser escrito apenas no idioma solicitado."
            ),
        }
        return prompts[language]

    def _format_files(self, request: PromptRequest) -> str:
        # On garde ce bloc compact pour aider le modèle sans surcharger le prompt.
        if not request.diff.files:
            return "- (none)"

        return "\n".join(f"- {path}" for path in request.diff.files)