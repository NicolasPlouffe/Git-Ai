from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer

DEFAULT_CONFIG_CONTENT = """provider: ollama
model: llama3.1:8b
language: en
base_url: http://localhost:11434

commit:
  format: conventional
  max_subject_length: 72
  include_body: false

git:
  push_after_commit: false
  remote: origin
"""


def register_init_command(app: typer.Typer) -> None:
    @app.command("init")
    def init_command(
        output: Annotated[
            Path,
            typer.Option(
                "--output",
                help="Chemin du fichier de configuration à créer.",
            ),
        ] = Path("git-ai.yaml"),
        force: Annotated[
            bool,
            typer.Option(
                "--force",
                help="Écrase le fichier s'il existe déjà.",
            ),
        ] = False,
    ) -> None:
        if output.exists() and not force:
            typer.secho(
                f"Erreur : le fichier existe déjà : {output}",
                fg=typer.colors.RED,
                err=True,
            )
            raise typer.Exit(code=2)

        output.write_text(DEFAULT_CONFIG_CONTENT, encoding="utf-8")
        typer.secho(
            f"Fichier de configuration créé : {output}",
            fg=typer.colors.GREEN,
        )