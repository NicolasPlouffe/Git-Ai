# Git AI Commit Assistant

Git AI Commit Assistant est un outil CLI Python **local-first** pour générer des messages de commit Git à partir d’un diff en s’appuyant sur un LLM local. Le projet est conçu à la fois comme un vrai outil de workflow développeur et comme un projet portfolio en AI engineering, avec une architecture modulaire, testable et lisible.[1]

## Objectif

L’objectif est de réduire le temps passé à rédiger des messages de commit tout en conservant un contrôle local sur l’inférence, une configuration explicite et une intégration simple avec Git.[1]

La V1 couvre la commande `commit`, la génération depuis le diff stagé, l’option `--files`, le choix de langue, le mode `--dry-run`, l’option `--push`, le provider Ollama et la configuration via YAML, variables d’environnement et options CLI.[1]

## Fonctionnalités

- Génération de message de commit à partir du diff Git stagé.[1]
- Ciblage de fichiers précis avec `--files`.[1]
- Sortie multilingue : français, anglais, espagnol, et présence de prompts portugais dans le dépôt.[1][2]
- Provider local par défaut : **Ollama**.[1]
- Architecture préparée pour d’autres backends, notamment `llama.cpp` et `openai-compatible`.[1][2]
- Configuration multi-source : valeurs par défaut, fichier YAML, variables d’environnement, puis options CLI.[1]
- Tests unitaires et d’intégration dédiés aux flux critiques.[1][2]

## Architecture

Le projet est organisé autour de responsabilités claires :

- `src/git_ai/cli.py` : point d’entrée CLI.[1]
- `src/git_ai/config.py` : chargement, fusion et validation de la configuration.[1]
- `src/git_ai/providers/` : contrat provider et implémentations concrètes (`ollama`, `llama.cpp`, `openai_compat`).[1][2]
- `src/git_ai/git/` : encapsulation des opérations Git nécessaires au produit.[1][2]
- `src/git_ai/services/` : orchestration métier, sélection de fichiers, génération de prompts, normalisation du message, détection de scaffold.[1][2]
- `src/git_ai/prompts/` : prompts multilingues pour commit et PR.[1][2]
- `tests/unit/` et `tests/integration/` : couverture des scénarios clés.[1][2]

Flux simplifié de la commande `commit` :

1. Charger la configuration.
2. Déterminer le périmètre : staging courant ou `--files`.
3. Produire le diff Git.
4. Construire le prompt dans la langue demandée.
5. Appeler le provider local.
6. Nettoyer et valider le message généré.
7. Afficher, committer, puis éventuellement pousser.[1]

## Prérequis

Avant d’utiliser l’outil, il faut disposer de :

- Python 3.11.[1]
- Git.[1]
- Ollama installé localement si le provider par défaut est utilisé.[1]
- Un modèle disponible dans Ollama.[1]

## Installer Ollama

L’installation d’Ollama doit être expliquée directement dans le README, car elle fait partie du chemin critique d’onboarding pour la V1 fondée sur le provider par défaut.[1]

### Option 1 — Installation via le site officiel

Installer Ollama depuis le site officiel selon le système d’exploitation utilisé, puis vérifier que le binaire est disponible dans le shell :

```bash
ollama --version
```

### Option 2 — Démarrer le service Ollama

Une fois Ollama installé, lancer le serveur local :

```bash
ollama serve
```

Selon l’environnement, le service peut déjà être démarré automatiquement. La configuration du projet montre que l’URL locale attendue est `http://localhost:11434`.[1]

## Installer le modèle par défaut

Le dépôt expose Ollama comme provider par défaut et mentionne notamment `llama3.1:8b` et `qwen2.5-coder:7b` parmi les modèles disponibles dans la configuration applicative.[1]

### Modèle recommandé pour démarrer

Pour un démarrage simple, installer un modèle disponible localement, par exemple :

```bash
ollama pull llama3.1:8b
```

Ou, si l’on veut aligner l’environnement avec l’exemple documentaire centré sur le code :

```bash
ollama pull qwen2.5-coder:7b
```

### Vérifier les modèles disponibles

```bash
ollama list
```

## Installation du projet

Le README doit présenter plusieurs façons d’installer le projet, car cela améliore l’onboarding et correspond bien à un outil CLI réutilisable.[1]

### Option 1 — Cloner le dépôt puis installer localement

C’est l’option la plus adaptée pour contribuer au projet ou explorer l’architecture.

```bash
git clone <repo-url>
cd git-ai
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

### Option 2 — Cloner puis installer avec les dépendances de développement

Pour travailler sur le projet, exécuter les tests et le lint :

```bash
git clone <repo-url>
cd git-ai
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
```

Les dépendances de développement visibles dans `pyproject.toml` incluent notamment `pytest`, `pytest-cov`, `ruff` et `mypy`.[1]

### Option 3 — Installer avec `pipx` depuis un dépôt Git

Cette option est pertinente pour un usage CLI isolé du système Python global. Elle est particulièrement utile si l’objectif est d’utiliser l’outil sans ouvrir l’environnement de développement du projet.

```bash
pipx install "git+<repo-url>"
```

Si le dépôt ou la branche doivent être ciblés explicitement :

```bash
pipx install "git+<repo-url>@<branch>"
```

Après installation, vérifier la commande :

```bash
git-ai --help
```

### Option 4 — Installation locale avec `pipx` depuis le dépôt cloné

Si le dépôt est déjà cloné localement :

```bash
pipx install .
```

Cette variante est pratique pour tester l’expérience utilisateur de la CLI de manière plus proche d’une installation “outil”.

## Configuration

Le chargement suit cet ordre de priorité :

1. valeurs par défaut ;
2. fichier YAML ;
3. variables d’environnement ;
4. options CLI.[1]

### Exemple de fichier `git-ai.yaml`

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

Le dépôt contient aussi un exemple d’environnement avec des variables comme `GITAI_PROVIDER`, `GITAI_MODEL`, `GITAI_OLLAMA_HOST` et `GITAI_LANGUAGE`.[1]

### Paramètres importants

| Paramètre | Rôle |
|---|---|
| `provider` | Backend LLM utilisé, `ollama` par défaut.[1] |
| `model` | Modèle invoqué localement.[1] |
| `language` | Langue de sortie du message.[1] |
| `base_url` | URL du backend local Ollama ou compatible.[1] |
| `commit.format` | Format du message, par exemple `conventional`.[1] |
| `commit.max_subject_length` | Longueur maximale du sujet.[1] |
| `commit.include_body` | Ajout ou non d’un corps au commit.[1] |
| `git.push_after_commit` | Push automatique après le commit.[1] |
| `git.remote` | Remote Git ciblée.[1] |

## Utilisation

### Générer un commit depuis le staging

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
```

Ou :

```bash
git-ai commit --lang en
```

### Commit puis push

```bash
git-ai commit --push
```

## Tests

Le dépôt contient des tests unitaires et des tests d’intégration couvrant notamment la CLI, la configuration, les modèles, le provider Ollama, la couche Git, la sélection de fichiers et le flux de langue.[1][2]

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

La documentation existante mentionne déjà plusieurs axes pour la suite :

- provider `llama.cpp` ;
- sélection interactive de fichiers ;
- génération de PR ;
- profils de configuration ;
- exclusions de fichiers ;
- hooks Git.[1]

## Positionnement portfolio

Ce projet est intéressant comme démonstration d’AI engineering appliqué, car il combine :

- un usage concret d’un LLM local dans un workflow développeur ;[1]
- une architecture Python modulaire et extensible ;[1]
- une gestion propre de la configuration multi-source ;[1]
- une séparation claire entre logique métier et détails d’infrastructure.[1]

## Documentation complémentaire

Le dépôt contient déjà plusieurs documents complémentaires :

- `docs/architecture.md` ;[2]
- `docs/config.md` ;[2]
- `docs/prompts.md` ;[2]
- `docs/roadmap.md`.[2]