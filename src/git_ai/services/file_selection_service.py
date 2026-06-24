
"""
Service de sélection du périmètre de fichiers pour la génération du message de commit.

Rôle métier :
- Décider sur quels fichiers portera le commit à partir :
  - du staging Git actuel (aucun --files),
  - ou d'une liste explicite de chemins passés via --files.
- Appliquer les règles de validation (existence, ignore, dossiers, etc.).
- Retourner une liste de chemins fichiers propre et stable pour la couche Git/diff.

Ce module ne parle pas directement à Git (pas de subprocess ici) :
on injecte une abstraction de la couche Git pour faciliter les tests.
"""

from dataclasses import dataclass
from typing import List, Optional


@dataclass(frozen=True)
class SelectedFiles:
    """
    Représente le périmètre final de fichiers à utiliser.

    - files : chemins de fichiers relatifs à la racine du dépôt.
    - source : "staged" (staging actuel) ou "explicit" (--files).
    - warnings : messages non bloquants (ex. dossiers vides).
    """
    files: List[str]
    source: str
    warnings: List[str]


class FileSelectionError(Exception):
    """
    Erreur bloquante lorsqu'on ne peut pas déterminer un périmètre cohérent.
    Exemple : aucun fichier stagé, chemins invalides, fichiers ignorés, etc.
    """
    pass


class FileSelectionService:
    """
    Service métier chargé de déterminer les fichiers à inclure dans le commit.

    Il s'appuie sur :
    - ggit_file_query_service : pour interroger l'état Git (staged, suivis, ignorés, etc.).
    - git_path_resolver : pour normaliser les chemins par rapport à la racine du repo.
    """

    def __init__(self, git_file_query_service, git_path_resolver):
        self.git_file_query_service = git_file_query_service
        self.git_path_resolver = git_path_resolver

    def select_files(
        self,
        explicit_files: Optional[List[str]] = None,
    ) -> SelectedFiles:
        """
        Point d'entrée principal.

        - Si explicit_files est None ou vide : utilise les fichiers stagés.
        - Sinon : utilise et valide la liste de chemins fournie par l'utilisateur (--files).
        """
        if explicit_files:
            return self._select_from_explicit_files(explicit_files)
        return self._select_from_staged()


    def _normalize_final_paths(self, paths: List[str]) -> List[str]:
        """
        Nettoie la liste finale des chemins retenus.

        Objectifs :
        - supprimer les doublons ;
        - garantir un ordre stable ;
        - retourner uniquement des chemins repo-relatifs.
        """
        return sorted(set(paths))

    # --- Sélection à partir du staging actuel ---------------------------------

    def _select_from_staged(self) -> SelectedFiles:
        """
        Utilise exclusivement les fichiers actuellement stagés dans Git.

        Règles :
        - Si aucun fichier n'est stagé : on lève une erreur explicite.
        - Sinon, on retourne la liste des chemins normalisés, dédupliqués et triés.
        """
        staged_files = self.git_file_query_service.get_staged_files()

        if not staged_files:
            raise FileSelectionError(
                "Aucun fichier stagé détecté. "
                "Stager des fichiers (git add ...) ou utiliser l'option --files."
            )

        normalized = [
            self.git_path_resolver.to_repo_relative(path)
            for path in staged_files
        ]

        # On déduplique et on ordonne pour garantir un comportement stable.
        unique_sorted = self._normalize_final_paths(normalized)

        return SelectedFiles(
            files=unique_sorted,
            source="staged",
            warnings=[],
        )

    # --- Sélection à partir de --files ----------------------------------------

    def _select_from_explicit_files(self, explicit_files: List[str]) -> SelectedFiles:
        """
        Utilise une liste explicite de chemins fournis via --files.

        Règles principales :
        - Accepte fichiers et dossiers.
        - Dossiers : expansion récursive en fichiers suivis (tracked/staged).
        - Chemin inexistant : erreur.
        - Fichier ignoré (.gitignore) : erreur.
        - Dossier sans fichiers suivis : warning non bloquant.
        - Si, après validation, aucun fichier valide n'est retenu : erreur.
        """
        warnings: List[str] = []
        resolved_paths: List[str] = []

        for raw_path in explicit_files:
            # On convertit les chemins CLI (relatifs/absolus) en chemins repo-relatifs.
            repo_path = self.git_path_resolver.to_repo_relative(raw_path)

            # On interdit les chemins qui sortiraient de la racine du repo (../..).
            if self.git_path_resolver.is_outside_repo(repo_path):
                raise FileSelectionError(
                    f"Chemin en dehors du dépôt Git : {raw_path}"
                )

            # Si c'est un dossier, on l'expanse récursivement.
            if self.git_file_query_service.is_directory(repo_path):
                files_in_dir = self.git_file_query_service.list_tracked_files_in_path(repo_path)
                if not files_in_dir:
                    warnings.append(
                        f"Dossier vide ou sans fichiers suivis : {raw_path}"
                    )
                    continue

                for f in files_in_dir:
                    resolved_paths.append(
                        self.git_path_resolver.to_repo_relative(f)
                    )
                continue

            # À partir d'ici, on considère que repo_path désigne un fichier.
            if not self.git_file_query_service.exists_in_worktree_or_index(repo_path):
                raise FileSelectionError(f"Fichier introuvable : {raw_path}")

            if self.git_file_query_service.is_ignored(repo_path):
                raise FileSelectionError(
                    f"Fichier ignoré par Git (.gitignore) : {raw_path}"
                )

            resolved_paths.append(repo_path)

        # Nettoyage de la liste finale : dé-duplication + tri.
        unique_sorted = self._normalize_final_paths(resolved_paths)

        if not unique_sorted:
            raise FileSelectionError(
                "Après validation, aucun fichier valide n'a été sélectionné "
                "à partir de --files."
            )

        return SelectedFiles(
            files=unique_sorted,
            source="explicit",
            warnings=warnings,
        )