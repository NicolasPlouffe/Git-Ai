# Git AI Commit Assistant

CLI Python local-first pour générer des messages de commit Git avec un LLM local.

## Objectif

Le projet vise à :
- générer des messages de commit depuis un diff Git ;
- supporter d'abord Ollama, puis llama.cpp server ;
- permettre une configuration via YAML, variables d'environnement et CLI ;
- proposer une sortie en français, anglais et espagnol.

## Statut

Étape actuelle : E1 - Initialisation du projet.

## Arborescence

```text
src/git_ai/
tests/unit/
tests/integration/
```

## Installation développement

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Lancement

```bash
git-ai
```# test
