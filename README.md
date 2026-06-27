# Git AI Commit Assistant

Git AI Commit Assistant est un outil CLI Python local-first qui génère des messages de commit Git à partir d’un diff en s’appuyant sur un LLM local.

Le projet a deux objectifs :
- être utile dans un vrai workflow développeur ;
- servir de projet portfolio en AI engineering, avec une architecture modulaire, testable et lisible.

## Objectif

Réduire le temps passé à écrire des messages de commit tout en gardant :
- un contrôle local sur l’inférence ;
- une configuration explicite ;
- une intégration simple avec Git.

## MVP V1

La V1 couvre :
- la commande `commit` ;
- la génération depuis le diff stagé ;
- l’option `--files` pour cibler des fichiers précis ;
- l’option `--lang` pour choisir `fr`, `en` ou `es` ;
- l’option `--dry-run` pour prévisualiser sans committer ;
- l’option `--push` pour pousser après le commit ;
- le provider Ollama ;
- la configuration via YAML + variables d’environnement + options CLI ;
- des tests unitaires de base ;
- un wrapper Bash/Zsh minimal.

## Positionnement

Ce projet n’est pas un simple script shell :
- la logique métier reste en Python ;
- le wrapper shell est volontairement fin ;
- l’architecture prépare l’ajout d’autres providers locaux comme llama.cpp server.

## Architecture

Le projet est organisé autour de responsabilités claires :

- `src/git_ai/cli.py` : point d’entrée CLI.
- `src/git_ai/config.py` : chargement et fusion de la configuration.
- `src/git_ai/providers/` : abstraction provider + implémentations concrètes.
- `src/git_ai/git/` : encapsulation des opérations Git.
- `src/git_ai/services/` : orchestration métier.
- `src/git_ai/prompts/` : templates de prompts multilingues.
- `tests/unit/` : tests unitaires.
- `tests/integration/` : tests d’intégration ciblés.

Voir aussi `docs/architecture.md`.

## Flux d’exécution

Exemple simplifié de la commande `commit` :

1. charger la configuration ;
2. résoudre le périmètre (`staged` ou `--files`) ;
3. produire le diff Git ;
4. construire le prompt selon la langue ;
5. appeler le provider local ;
6. nettoyer et valider le message ;
7. afficher, committer, puis éventuellement pousser.

## Installation

### Prérequis

- Python 3.11+
- Git
- Ollama installé localement
- un modèle disponible dans Ollama

### Installation locale

```bash
git clone <repo-url>
cd git-ai-commit
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Configuration

Le chargement suit cet ordre de priorité :
1. valeurs par défaut ;
2. fichier YAML ;
3. variables d’environnement ;
4. options CLI.

Exemple de fichier `git-ai.yaml` :

```yaml
provider: ollama
base_url: http://localhost:11434/v1
model: qwen2.5-coder:7b
language: fr

commit:
  format: conventional
  max_subject_length: 72
  include_body: true

git:
  push_after_commit: false
  remote: origin
```

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
git-ai commit --lang en
```

### Commit + push

```bash
git-ai commit --push
```

## Tests

```bash
pytest
```

Ou pour séparer :
```bash
pytest tests/unit
pytest tests/integration
```

## Roadmap

### V2 prévue
- provider llama.cpp ;
- sélection interactive de fichiers ;
- génération de PR ;
- profils de configuration ;
- exclusions de fichiers ;
- hooks Git.

## Pourquoi ce projet est intéressant

- Intégration d’un LLM local dans un outil développeur concret.
- Architecture Python modulaire et extensible.
- Gestion propre de la configuration multi-source.
- Séparation nette entre orchestration métier et détails d’infrastructure.

## Documentation

- `docs/architecture.md`
- `docs/demo-plan.md`
- `docs/portfolio-notes.md`