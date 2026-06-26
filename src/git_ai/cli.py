from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer

from git_ai.config import (
    ConfigError,
    SUPPORTED_LANGUAGES,
    SUPPORTED_PROVIDERS,
    load_config,
)
from git_ai.exceptions import ProviderError, ProviderResponseError
from git_ai.git.commit import create_commit, push_current_branch
from git_ai.git.diff import get_staged_diff
from git_ai.git.file_queries import GitFilesGateway, GitPathResolver
from git_ai.models import CommitLanguage, DiffSource, GitDiff, PromptRequest
from git_ai.providers.ollama import OllamaProvider
from git_ai.services.commit_message_service import CommitMessageService
from git_ai.services.file_selection_service import (
    FileSelectionError,
    FileSelectionService,
)
from git_ai.services.prompt_service import PromptService

app = typer.Typer(
    name="git-ai",
    help="Assistant CLI local-first pour générer des messages de commit Git.",
    no_args_is_help=True,
    add_completion=False,
)


class CLIError(Exception):
    """Erreur contrôlée côté CLI."""


def _validate_language(lang: str | None) -> str | None:
    if lang is None:
        return None

    normalized = lang.strip().lower()
    if normalized not in SUPPORTED_LANGUAGES:
        supported = ", ".join(sorted(SUPPORTED_LANGUAGES))
        raise typer.BadParameter(
            f"Unsupported language '{lang}'. Supported languages: {supported}."
        )

    return normalized


def _validate_provider(provider: str | None) -> str | None:
    if provider is None:
        return None

    normalized = provider.strip().lower()
    if normalized not in SUPPORTED_PROVIDERS:
        supported = ", ".join(sorted(SUPPORTED_PROVIDERS))
        raise typer.BadParameter(
            f"Unsupported provider '{provider}'. Supported providers: {supported}."
        )

    return normalized


def _build_cli_overrides(
    *,
    lang: str | None,
    push: bool | None,
    provider: str | None,
    model: str | None,
) -> dict:
    overrides: dict = {}

    if lang is not None:
        overrides["language"] = lang

    if provider is not None:
        overrides["provider"] = provider

    if model is not None:
        overrides["model"] = model

    if push is not None:
        overrides["git"] = {"push_after_commit": push}

    return overrides


def _to_commit_language(value: str) -> CommitLanguage:
    try:
        return CommitLanguage(value)
    except ValueError as exc:
        supported = ", ".join(language.value for language in CommitLanguage)
        raise CLIError(
            f"Unsupported language '{value}'. Supported languages: {supported}."
        ) from exc


def _build_selection_service(
    repo_path: str | Path | None = None,
) -> FileSelectionService:
    return FileSelectionService(
        git_files_gateway=GitFilesGateway(repo_path=repo_path),
        git_path_resolver=GitPathResolver(repo_path=repo_path),
    )


def _build_commit_message_service(config) -> CommitMessageService:
    if config.provider != "ollama":
        raise CLIError(
            f"Provider '{config.provider}' is not wired in the CLI yet."
        )

    provider = OllamaProvider(
        model=config.model,
        base_url=config.base_url,
    )
    prompt_service = PromptService()

    return CommitMessageService(
        provider=provider,
        prompt_service=prompt_service,
    )


def _build_git_diff(selected_files_result) -> GitDiff:
    if selected_files_result.source == "explicit":
        files = tuple(selected_files_result.files)
        source = DiffSource.FILES
        diff_text = get_staged_diff(paths=files)
    else:
        files = tuple(selected_files_result.files)
        source = DiffSource.STAGED
        diff_text = get_staged_diff()

    return GitDiff(
        text=diff_text,
        files=files,
        source=source,
    )


def _print_scope(selected_files_result) -> None:
    if selected_files_result.source == "staged":
        typer.echo("Périmètre : diff stagé courant.")
    else:
        typer.echo("Périmètre : fichiers ciblés.")
        for file_path in selected_files_result.files:
            typer.echo(f" - {file_path}")

    if selected_files_result.warnings:
        typer.echo("")
        typer.secho("Avertissements :", fg=typer.colors.YELLOW)
        for warning in selected_files_result.warnings:
            typer.secho(f" - {warning}", fg=typer.colors.YELLOW)


@app.command("commit")
def commit_command(
    files: Annotated[
        list[Path] | None,
        typer.Option(
            "--files",
            help="Restreint la génération du message à une liste de fichiers ou dossiers.",
        ),
    ] = None,
    lang: Annotated[
        str | None,
        typer.Option(
            "--lang",
            help="Langue du message de commit : fr, en, es, pt.",
        ),
    ] = None,
    provider: Annotated[
        str | None,
        typer.Option(
            "--provider",
            help="Provider LLM à utiliser (CLI > env > YAML).",
        ),
    ] = None,
    model: Annotated[
        str | None,
        typer.Option(
            "--model",
            help="Nom du modèle LLM à utiliser (CLI > env > YAML).",
        ),
    ] = None,
    dry_run: Annotated[
        bool,
        typer.Option(
            "--dry-run",
            help="Affiche le message sans créer le commit.",
        ),
    ] = False,
    push: Annotated[
        bool | None,
        typer.Option(
            "--push/--no-push",
            help="Surcharge ponctuelle du push après commit.",
        ),
    ] = None,
    config_path: Annotated[
        Path | None,
        typer.Option(
            "--config",
            help="Chemin explicite vers un fichier YAML de configuration.",
        ),
    ] = None,
    repo_path: Annotated[
        Path | None,
        typer.Option(
            "--repo-path",
            help="Chemin du dépôt Git ciblé. Par défaut : répertoire courant.",
        ),
    ] = None,
) -> None:
    """
    Génère un message de commit à partir du diff Git stagé.
    """
    try:
        validated_lang = _validate_language(lang)
        validated_provider = _validate_provider(provider)
        cli_overrides = _build_cli_overrides(
            lang=validated_lang,
            push=push,
            provider=validated_provider,
            model=model,
        )

        config = load_config(
            config_path=config_path,
            cli_overrides=cli_overrides,
        )

        explicit_files = [str(path) for path in files] if files else None

        selection_service = _build_selection_service(repo_path=repo_path)
        selected_files_result = selection_service.select_files(
            explicit_files=explicit_files
        )

        git_diff = _build_git_diff(selected_files_result)

        if git_diff.is_empty:
            raise CLIError("Le diff Git est vide. Impossible de générer un commit.")

        commit_message_service = _build_commit_message_service(config)

        request = PromptRequest(
            diff=git_diff,
            language=_to_commit_language(config.language),
            max_subject_length=config.commit.max_subject_length,
        )

        commit_message = commit_message_service.generate(request)

        typer.echo("")
        _print_scope(selected_files_result)
        typer.echo(
            f"Langue : {config.language} | Provider : {config.provider} | Modèle : {config.model}"
        )
        typer.echo("")
        typer.echo("Message généré :")
        typer.echo(commit_message.text)
        typer.echo("")

        if dry_run:
            typer.secho(
                "Dry-run activé : aucun commit ni push exécuté.",
                fg=typer.colors.YELLOW,
            )
            raise typer.Exit(code=0)

        create_commit(
            message=commit_message.text,
            repo_path=repo_path,
        )
        typer.secho("Commit créé avec succès.", fg=typer.colors.GREEN)

        if config.git.push_after_commit:
            push_current_branch(repo_path=repo_path)
            typer.secho("Push effectué avec succès.", fg=typer.colors.GREEN)

    except typer.BadParameter:
        raise
    except typer.Exit:
        raise
    except (ConfigError, CLIError, FileSelectionError, ValueError) as exc:
        typer.secho(f"Erreur : {exc}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=2) from exc
    except (ProviderError, ProviderResponseError) as exc:
        typer.secho(f"Provider error: {exc}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1) from exc
    except FileNotFoundError as exc:
        typer.secho(f"Fichier manquant : {exc}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1) from exc
    except Exception as exc:
        typer.secho(f"Erreur inattendue : {exc}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1) from exc


def main() -> None:
    app()


if __name__ == "__main__":
    main()