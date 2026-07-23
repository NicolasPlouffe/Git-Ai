# Git-AI : Commit Assistant

> Outil CLI Python **local-first** pour générer des messages de commit Git à partir d’un diff, avec un **LLM local**.
>
> Pensé à la fois comme un vrai outil de workflow développeur et comme un projet portfolio en **AI engineering**.

## Aperçu

Git-AI aide à rédiger des messages de commit plus vite, tout en gardant le contrôle sur l’inférence, la configuration et l’environnement d’exécution.

La V1 se concentre sur un périmètre simple et utile : génération depuis le diff stagé, ciblage de fichiers, choix de langue, prévisualisation, commit, push optionnel et intégration avec **Ollama** comme provider local par défaut.

## Points clés

- Génération de message de commit à partir du diff Git stagé.
- Ciblage de fichiers précis avec `--files`.
- Sortie multilingue : français, anglais, espagnol.
- Provider local par défaut : **Ollama**.
- Configuration par défaut + YAML + variables d’environnement + options CLI.
- Architecture modulaire, testable et extensible.
- Tests unitaires et d’intégration sur les flux critiques.

## Prérequis

Avant d’utiliser Git-AI, assurez-vous de disposer de :

- [Python 3.11](https://www.python.org/downloads/) installé sur votre machine.
- [Git](https://git-scm.com/downloads).
- [Ollama](https://ollama.com/download) installé localement.
- Au moins un modèle disponible dans Ollama.

> Git-AI fonctionne en local et utilise par défaut Ollama comme provider LLM.

## Installer Ollama

### Liens utiles

- Page officielle de téléchargement : <https://ollama.com/download>
- Quickstart Ollama : <https://docs.ollama.com/quickstart>

### Windows

Dans **PowerShell**, exécuter :

```powershell
irm https://ollama.com/install.ps1 | iex
```

Ou utiliser l’installateur graphique depuis la page officielle. Ollama nécessite Windows 10 ou plus récent.

### macOS

Dans le terminal :

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

Il est aussi possible d’utiliser l’application téléchargée depuis le site officiel.

### Linux

Dans le terminal :

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

Cette méthode est la voie d’installation recommandée pour Linux.

### Vérifier l’installation

```bash
ollama --version
```

### Démarrer le service local

```bash
ollama serve
```

Selon le système, Ollama peut déjà être lancé automatiquement après installation. L’URL locale attendue par défaut est :

```text
http://localhost:11434
```

### Installer le modèle recommandé

Pour démarrer rapidement :

```bash
ollama pull llama3.1:8b
```

Option orientée code :

```bash
ollama pull qwen2.5-coder:7b
```

Vérifier les modèles disponibles :

```bash
ollama list
```

## Essayer en 5 minutes

1. Installer Ollama et un modèle (`llama3.1:8b` ou `qwen2.5-coder:7b`).
2. Démarrer le service local :

   ```bash
   ollama serve
   ```

3. Installer Git-AI avec `pipx` :

   ```bash
   pipx install "git+https://gitlab.com/NPlouffe/git-ai.git"
   ```

4. Vérifier la commande :

   ```bash
   git-ai --help
   ```

5. Générer une première prévisualisation :

   ```bash
   git-ai commit --dry-run
   ```

## Fonctionnalités V1

| Fonctionnalité      | Description                                 |
|---------------------|---------------------------------------------|
| `git-ai commit`     | Génère un message à partir du diff stagé.   |
| `--files`           | Limite la génération à des fichiers ciblés. |
| `--lang`            | Permet de choisir la langue de sortie.      |
| `--dry-run`         | Prévisualise sans créer de commit.          |
| `--push`            | Effectue un push après le commit si demandé.|
| Provider Ollama     | Utilise un backend local par défaut.        |
| Config multi-source | Fusion des défauts, YAML, env et CLI.      |

## Installation

### Option recommandée — `pipx` depuis GitLab

Cette option est la plus simple pour un utilisateur qui veut essayer l’outil sans ouvrir un environnement de développement local.

```bash
pipx install "git+https://gitlab.com/NPlouffe/git-ai.git"
```

### Option développement — clonage local

Pour contribuer au projet ou explorer le code :

```bash
git clone "https://gitlab.com/NPlouffe/git-ai.git"
cd git-ai
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

### Option développement avec dépendances complètes

```bash
git clone "https://gitlab.com/NPlouffe/git-ai.git"
cd git-ai
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
```

Dépendances de développement principales : `pytest`, `pytest-cov`, `ruff`, `mypy`.

### Option locale avec `pipx`

Si le dépôt est déjà cloné :

```bash
pipx install .
```

### Vérification post-installation

```bash
git-ai --help
```

## Configuration

Ordre de priorité de chargement :

1. Valeurs par défaut.
2. Fichier YAML.
3. Variables d’environnement.
4. Options CLI.

### Exemple `git-ai.yaml`

```yaml
provider: ollama
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
```

Variables d’environnement prévues dans l’exemple de projet : `GITAI_PROVIDER`, `GITAI_MODEL`, `GITAI_OLLAMA_HOST`, `GITAI_LANGUAGE`.

### Paramètres principaux

| Paramètre                 | Rôle                                      |
|---------------------------|-------------------------------------------|
| `provider`                | Backend LLM utilisé.                      |
| `model`                   | Modèle invoqué localement.               |
| `language`                | Langue de sortie du message.             |
| `base_url`                | URL du backend local Ollama ou compatible. |
| `commit.format`           | Format du message, par exemple `conventional`. |
| `commit.max_subject_length` | Longueur maximale du sujet.           |
| `commit.include_body`     | Ajoute ou non un corps au commit.        |
| `git.push_after_commit`   | Active le push automatique après commit. |
| `git.remote`              | Définit le remote Git ciblé.             |

## Utilisation

### Générer depuis le staging

```bash
git-ai commit
```

### Prévisualiser sans committer

```bash
git-ai commit --dry-run
```

### Cibler des fichiers précis

```bash
git-ai commit --files src/git_ai/cli.py tests/unit/test_cli.py
```

### Changer la langue

```bash
git-ai commit --lang fr
git-ai commit --lang en
```

### Commit puis push

```bash
git-ai commit --push
```

## Architecture

Le projet est organisé autour de responsabilités claires :

- `src/git_ai/cli.py` : point d’entrée CLI.
- `src/git_ai/config.py` : chargement, fusion et validation de la configuration.
- `src/git_ai/providers/` : contrat provider et implémentations concrètes.
- `src/git_ai/git/` : encapsulation des opérations Git nécessaires.
- `src/git_ai/services/` : orchestration métier, sélection de fichiers, prompts, normalisation, détection de scaffold.
- `src/git_ai/prompts/` : prompts multilingues pour commit et PR.
- `tests/unit/` et `tests/integration/` : couverture des scénarios clés.

### Flux simplifié de `commit`

1. Charger la configuration.
2. Déterminer le périmètre : staging courant ou `--files`.
3. Produire le diff Git.
4. Construire le prompt dans la langue demandée.
5. Appeler le provider local.
6. Nettoyer et valider le message généré.
7. Afficher, committer, puis éventuellement pousser.

## Tests

Le projet contient des tests unitaires et d’intégration pour la CLI, la configuration, les modèles, le provider Ollama, la couche Git, la sélection de fichiers et le flux de langue.

### Exécuter toute la suite

```bash
pytest
```

### Exécuter par catégorie

```bash
pytest tests/unit
pytest tests/integration
```

## Roadmap

Axes déjà identifiés pour la suite :

- provider `llama.cpp` ;
- sélection interactive de fichiers ;
- génération de PR ;
- profils de configuration ;
- exclusions de fichiers ;
- hooks Git.

## Positionnement portfolio

Git-AI est aussi un projet de démonstration d’AI engineering appliqué :

- usage concret d’un LLM local dans un workflow développeur ;
- architecture Python modulaire et extensible ;
- configuration multi-source propre ;
- séparation claire entre logique métier et infrastructure.

## Documentation complémentaire

- `docs/architecture.md`
- `docs/config.md`
- `docs/prompts.md`
- `docs/roadmap.md`