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
                "Tu es un assistant qui rédige uniquement des messages de commit Git. "
                "Tu retournes uniquement le message final, sans explication ni Markdown."
            ),
            CommitLanguage.ENGLISH: (
                "You are an assistant that writes Git commit messages only. "
                "Return only the final message, with no explanation and no Markdown."
            ),
            CommitLanguage.SPANISH: (
                "Eres un asistente que redacta únicamente mensajes de commit Git. "
                "Devuelve solo el mensaje final, sin explicación ni Markdown."
            ),
            CommitLanguage.PORTUGUESE: (
                "Você é um assistente que escreve apenas mensagens de commit Git. "
                "Retorne apenas a mensagem final, sem explicação nem Markdown."
            ),
        }
        return prompts[language]

    def _format_files(self, request: PromptRequest) -> str:
        # On garde ce bloc compact pour aider le modèle sans surcharger le prompt.
        if not request.diff.files:
            return "- (none)"

        return "\n".join(f"- {path}" for path in request.diff.files)