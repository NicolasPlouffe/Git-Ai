from __future__ import annotations

"""
Actions de commit et de push.

Cette couche ne décide pas *quand* committer ou pousser ; elle exécute ces
actions de façon fiable et documentée pour les couches supérieures.
"""

from pathlib import Path

from git_ai.git._common import GitCommandError, run_git_command
from git_ai.git.branch import get_current_branch, get_push_remote


def create_commit(
    message: str,
    repo_path: str | Path | None = None,
) -> None:
    """
    Crée un commit avec le message fourni.

    Le message est passé comme argument à Git, sans shell, ce qui évite
    les problèmes d'échappement usuels.
    """
    normalized_message = message.strip()
    if not normalized_message:
        raise ValueError("Commit message cannot be empty.")

    run_git_command(
        ["commit", "-m", normalized_message],
        repo_path=repo_path,
    )


def push_current_branch(
    repo_path: str | Path | None = None,
    set_upstream: bool = False,
) -> None:
    """
    Pousse la branche courante.

    Cas visés :
    - branche déjà liée à un upstream : `git push`
    - première publication optionnelle : `git push --set-upstream <remote> <branch>`

    Si `set_upstream=True`, on tente de publier la branche courante vers le
    remote configuré ; à défaut, on utilise `origin`.
    """
    branch = get_current_branch(repo_path=repo_path)
    if not branch:
        raise ValueError("Cannot push while HEAD is detached.")

    if set_upstream:
        remote = get_push_remote(repo_path=repo_path) or "origin"
        run_git_command(
            ["push", "--set-upstream", remote, branch],
            repo_path=repo_path,
        )
        return

    try:
        run_git_command(["push"], repo_path=repo_path)
    except GitCommandError as exc:
        # On laisse l'erreur remonter, mais ce commentaire documente bien
        # l'intention : sans upstream, `git push` échouera souvent, et la CLI
        # pourra ensuite proposer une action corrective plus conviviale.
        raise exc