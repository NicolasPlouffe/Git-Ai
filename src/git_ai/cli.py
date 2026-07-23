from __future__ import annotations

import typer

from git_ai.commands.commit import register_commit_command
from git_ai.commands.init import register_init_command

app = typer.Typer(
    name="git-ai",
    help="Assistant CLI local-first pour générer des messages de commit Git.",
    no_args_is_help=True,
    add_completion=False,
)

register_commit_command(app)
register_init_command(app)


def main() -> None:
    app()


if __name__ == "__main__":
    main()