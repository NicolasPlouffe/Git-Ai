# Git-AI : Commit Assistant

> 🔗 Ce projet est disponible sur \
> [![GitLab](https://img.shields.io/badge/GitLab-FC6D26?style=flat&logo=gitlab&logoColor=white)](https://gitlab.com/NPlouffe/git-ai)
> [![GitHub](https://img.shields.io/badge/GitHub-181717?style=flat&logo=github&logoColor=white)](https://github.com/NicolasPlouffe/git-ai) (miroir)
> [![YouTube](https://img.shields.io/badge/YouTube-demo-FF0000?style=flat&logo=youtube&logoColor=white)](https://www.youtube.com/watch?v=d5HUAngFSgo&list=PLBHPWEkVEvnY)

🇫🇷 *Version française (ci-dessous)* — 🇬🇧 *English version coming soon*

> Outil CLI Python **local-first** pour générer des messages de commit Git à partir d'un diff, avec un **LLM local**.
>
> Pensé à la fois comme un vrai outil de workflow développeur et comme un projet portfolio en **AI engineering**.

## Aperçu

Git-AI aide à rédiger des messages de commit plus vite, tout en gardant le contrôle sur l'inférence, la configuration et l'environnement d'exécution.

La V1 se concentre sur un périmètre simple et utile : génération depuis le diff stagé, ciblage de fichiers, choix de langue, prévisualisation, commit, push optionnel et intégration avec **Ollama** comme provider local par défaut.

## Points clés

- Génération de message de commit à partir du diff Git stagé.
- Sortie multilingue : 🇫🇷 français, 🇬🇧 anglais, 🇪🇸 espagnol, 🇧🇷 portugais (Brésil).
- Provider local par défaut : **Ollama**.
- Configuration par défaut + YAML + variables d'environnement + options CLI.
- Architecture modulaire, testable et extensible.
- Tests unitaires et d'intégration sur les flux critiques.

## Démo vidéo

Une démo complète de Git-AI (workflow, intégration Ollama, options CLI) est disponible sur YouTube :

[![Voir la démo Git-AI](https://img.youtube.com/vi/d5HUAngFSgo/hqdefault.jpg)](https://www.youtube.com/watch?v=d5HUAngFSgo&list=PLBHPWEkVEvnY)

> La vidéo montre l’installation via `pipx`, la configuration YAML, puis l’usage de `git-ai commit` dans un vrai workflow.


## Prérequis

modifiaction démo
Une autre modification 

Avant d'utiliser Git-AI, assurez-vous de disposer de :

- [Git](https://git-scm.com/downloads).
- [Python 3.11](https://www.python.org/downloads/) installé sur votre machine.
- [pipx](https://pipx.pypa.io/latest/how-to/install-pipx.html) pour installer Git-AI de façon isolée.
- [Ollama](https://ollama.com/download) installé localement.
- Au moins un modèle disponible dans Ollama.

> Git-AI fonctionne en local et utilise par défaut Ollama comme provider LLM.

## Installer pipx

pipx n'est généralement pas installé par défaut. Installez-le selon votre système.

### Windows

Dans **PowerShell** :

```powershell
python -m pip install --user pipx
python -m pipx ensurepath
```

Fermez et rouvrez votre terminal après cette étape.

### macOS

```bash
brew install pipx
pipx ensurepath
```

### Linux (Ubuntu/Debian)

```bash
sudo apt update && sudo apt install pipx
pipx ensurepath
```

Si le paquet système n'est pas disponible ou trop ancien :

```bash
python3 -m pip install --user pipx
python3 -m pipx ensurepath
```

### Après `pipx ensurepath`

Rechargez votre shell pour que la commande `pipx` soit reconnue :

```bash
source ~/.zshrc   # ou source ~/.bashrc si vous utilisez bash
```

Sur Windows, fermez et rouvrez simplement le terminal.

### Vérifier l'installation

```bash
pipx --version
```

## Installer Ollama

### Liens utiles

- Page officielle de téléchargement : <https://ollama.com/download>
- Quickstart Ollama : <https://docs.ollama.com/quickstart>

### Windows

Dans **PowerShell**, exécuter :

```powershell
irm https://ollama.com/install.ps1 | iex
```

Ou utiliser l'installateur graphique depuis la page officielle. Ollama nécessite Windows 10 ou plus récent.

### macOS

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

Il est aussi possible d'utiliser l'application téléchargée depuis le site officiel.

### Linux

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

Cette méthode est la voie d'installation recommandée pour Linux.

### Vérifier l'installation

```bash
ollama --version
```

### Démarrer le service local

```bash
ollama serve
```

Selon le système, Ollama peut déjà être lancé automatiquement après installation. L'URL locale attendue par défaut est :

```text
http://localhost:11434
```

### Installer le modèle recommandé

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

## Installer Git-AI

### Option recommandée — `pipx` depuis GitLab

La façon la plus simple d'essayer l'outil sans ouvrir un environnement de développement local.

```bash
pipx install "git+https://gitlab.com/NPlouffe/git-ai.git"
```

**Vérification post-installation :**

```bash
git-ai --help
```

### Résoudre "command not found: git-ai"

Si la commande `git-ai` n'est pas reconnue après l'installation, le dossier d'installation de pipx n'est probablement pas encore dans votre PATH.

**Linux / macOS**

```bash
pipx ensurepath
source ~/.zshrc   # ou source ~/.bashrc si vous utilisez bash
```

**Windows (PowerShell)**

```powershell
pipx ensurepath
```

Puis fermez et rouvrez votre terminal.

**Windows (WSL)** — suivez les instructions Linux ci-dessus.

### Option développement — clonage local

Pour contribuer au projet ou explorer le code :

```bash
git clone "https://gitlab.com/NPlouffe/git-ai.git"
cd git-ai
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

Avec les dépendances de développement complètes (`pytest`, `pytest-cov`, `ruff`, `mypy`) :

```bash
pip install -e .[dev]
```

Si le dépôt est déjà cloné, vous pouvez aussi installer via pipx en local :

```bash
pipx install .
```

## Désinstallation

Pour retirer complètement Git-AI et ses dépendances de votre système.

### Désinstaller Git-AI

```bash
pipx uninstall git-ai
```

### Désinstaller pipx

**Si installé via pip**

```bash
python -m pip uninstall pipx
```

**macOS (Homebrew)**

```bash
brew uninstall pipx
```

**Linux (Ubuntu/Debian)**

```bash
sudo apt remove pipx
```

**Nettoyer les résidus**

```bash
rm -rf ~/.local/pipx
rm -rf ~/.local/share/pipx
```

Retirez également la ligne d'export PATH ajoutée par `pipx ensurepath` dans `~/.zshrc` ou `~/.bashrc`, si elle n'est plus nécessaire.

### Désinstaller Ollama

**macOS**

```bash
rm -rf ~/Library/Application\ Support/Ollama
rm -rf /Applications/Ollama.app
sudo rm /usr/local/bin/ollama
```

**Linux**

```bash
sudo systemctl stop ollama
sudo systemctl disable ollama
sudo rm /usr/local/bin/ollama
sudo rm -rf /usr/share/ollama
sudo rm /etc/systemd/system/ollama.service
sudo systemctl daemon-reload
sudo userdel ollama
sudo groupdel ollama
```

**Windows**

Désinstallez via **Paramètres > Applications > Ollama**, ou exécutez le désinstalleur dans le dossier d'installation.

**Supprimer les modèles téléchargés (tous systèmes, libère l'espace disque)**

```bash
rm -rf ~/.ollama
```

### Vérification finale

```bash
which git-ai   # command not found
which pipx     # command not found
which ollama   # command not found
```

## Essayer en 5 minutes

1. Installer pipx, Ollama et un modèle (`llama3.1:8b` ou `qwen2.5-coder:7b`), puis démarrer le service :

   ```bash
   ollama serve
   ```

2. Installer Git-AI (voir section [Installer Git-AI](#installer-git-ai) ci-dessus), puis vérifier :

   ```bash
   git-ai --help
   ```

3. Se placer à la racine d'un dépôt Git et initialiser la configuration :

   ```bash
   git-ai init
   ```

4. Ajouter un ou des fichiers au staging comme à l'habitude :

   ```bash
   git add <fichier ou dossier>
   ```

5. Générer une première prévisualisation :

   ```bash
   git-ai commit --dry-run
   ```

6. Si satisfait du message généré, committer et pousser :

   ```bash
   git-ai commit && git push
   ```

## Fonctionnalités V1

| Fonctionnalité      | Description                                 |
|---------------------|---------------------------------------------|
| `git-ai commit`     | Génère un message à partir du diff stagé.   |
| `--files`           | Limite la génération à des fichiers ciblés. |
| `--lang`            | Permet de choisir la langue de sortie.      |
| `--dry-run`         | Prévisualise sans créer de commit.          |
| Provider Ollama     | Utilise un backend local par défaut.        |
| Config multi-source | Fusion des défauts, YAML, env et CLI.       |

## Configuration

Ordre de priorité de chargement :

1. Valeurs par défaut.
2. Fichier YAML.
3. Variables d'environnement.
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

Variables d'environnement prévues : `GITAI_PROVIDER`, `GITAI_MODEL`, `GITAI_OLLAMA_HOST`, `GITAI_LANGUAGE`.

### Paramètres principaux

| Paramètre                   | Rôle                                           |
|------------------------------|-------------------------------------------------|
| `provider`                  | Backend LLM utilisé.                           |
| `model`                     | Modèle invoqué localement.                     |
| `language`                  | Langue de sortie du message.                   |
| `base_url`                  | URL du backend local Ollama ou compatible.     |
| `commit.format`             | Format du message, par exemple `conventional`. |
| `commit.max_subject_length` | Longueur maximale du sujet.                    |
| `commit.include_body`       | Ajoute ou non un corps au commit.              |
| `git.push_after_commit`     | Active le push automatique après commit.       |
| `git.remote`                | Définit le remote Git ciblé.                   |

## Utilisation

```bash
git-ai commit                        # Générer depuis le staging
git-ai commit --dry-run              # Prévisualiser sans committer
git-ai commit --lang fr              # Changer la langue
git-ai commit --push                 # Commit puis push
```

## Architecture

- `src/git_ai/cli.py` : point d'entrée CLI.
- `src/git_ai/config.py` : chargement, fusion et validation de la configuration.
- `src/git_ai/providers/` : contrat provider et implémentations concrètes.
- `src/git_ai/git/` : encapsulation des opérations Git nécessaires.
- `src/git_ai/services/` : orchestration métier, sélection de fichiers, prompts, normalisation, détection de scaffold.
- `src/git_ai/prompts/` : prompts multilingues pour commit et PR.
- `tests/unit/` et `tests/integration/` : couverture des scénarios clés.

### Flux simplifié de `commit`

1. Charger la configuration.
2. Déterminer le périmètre : staging courant.
3. Produire le diff Git.
4. Construire le prompt dans la langue demandée.
5. Appeler le provider local.
6. Nettoyer et valider le message généré.
7. Afficher, committer, puis éventuellement pousser.

## Tests

```bash
pytest                    # Toute la suite
pytest tests/unit         # Tests unitaires
pytest tests/integration  # Tests d'intégration
```

## Roadmap

- provider `llama.cpp` ;
- sélection interactive de fichiers ;
- génération de PR ;
- profils de configuration ;
- exclusions de fichiers ;
- hooks Git.

## Positionnement portfolio

Git-AI est aussi un projet de démonstration d'AI engineering appliqué :

- usage concret d'un LLM local dans un workflow développeur ;
- architecture Python modulaire et extensible ;
- configuration multi-source propre ;
- séparation claire entre logique métier et infrastructure.

## Documentation complémentaire

- `docs/architecture.md`
- `docs/config.md`
- `docs/prompts.md`
- `docs/roadmap.md`
