# Couche Git — Git AI Commit Assistant

## Objectif

La couche Git encapsule les opérations nécessaires à la V1 de l'application afin de
fournir une interface Python stable, testable et lisible au-dessus de la CLI Git.

Elle sert de fondation technique pour les étapes suivantes :

- sélection de fichiers ;
- génération de diff ;
- construction des prompts ;
- génération du message de commit ;
- exécution du commit et préparation du push.

## Pourquoi cette couche est critique

Cette couche est critique car elle constitue le point de contact entre :

1. l'état réel du dépôt Git ;
2. les services applicatifs qui consomment cet état ;
3. les actions irréversibles ou semi-sensibles comme le staging, le commit et le push.

En pratique, une mauvaise abstraction ici peut entraîner :

- un diff incomplet ou erroné envoyé au LLM ;
- un mauvais périmètre de fichiers pris en compte ;
- des erreurs difficiles à diagnostiquer dans la CLI ;
- des comportements incohérents entre modules.

L'objectif de cette couche est donc double :

- **fiabilité fonctionnelle** ;
- **lisibilité de maintenance**.

## Principes de conception

### 1. Utiliser la CLI Git via `subprocess`

Le projet reste local-first et léger.  
La couche Git s'appuie donc sur la commande `git` disponible sur la machine, via
`subprocess.run(...)`, plutôt que sur une bibliothèque externe plus lourde.

### 2. Centraliser l'exécution dans `_common.py`

Le module `_common.py` sert d'infrastructure interne commune :

- normalisation du `repo_path` ;
- exécution des commandes Git ;
- capture systématique de `stdout` / `stderr` ;
- conversion des erreurs système en exceptions applicatives.

Cela évite la duplication de logique dans chaque module.

### 3. Séparer lecture et action

La couche distingue :

- les modules de **lecture** : `status.py`, `diff.py`, `branch.py` ;
- les modules d'**action** : `stage.py`, `commit.py`.

Cette séparation rend l'intention plus claire et facilite les tests.

### 4. Favoriser les formats parseables par script

Pour lire l'état du dépôt, on privilégie les sorties conçues pour l'automatisation.

Exemple :
- `git status --porcelain=v1 --branch`

Ce format est plus stable que la sortie humaine de `git status`.

## Responsabilités des modules

### `_common.py`

Responsabilité :
- exécuter une commande Git dans un dépôt donné ;
- retourner un résultat standardisé ;
- lever des exceptions cohérentes.

Types principaux :
- `GitError`
- `GitRepositoryError`
- `GitCommandError`
- `GitCommandResult`

### `status.py`

Responsabilité :
- lire l'état du dépôt ;
- parser les changements fichier par fichier ;
- exposer un statut de branche simplifié.

Types principaux :
- `FileStatus`
- `BranchStatus`
- `RepoStatus`

Point important :
- le statut Git distingue l'index (staging area) et le working tree ;
- cette distinction est essentielle pour savoir ce qui sera réellement committé.

### `diff.py`

Responsabilité :
- retourner le diff texte utilisé par les couches supérieures.

Fonctions principales :
- `get_staged_diff(...)`
- `get_unstaged_diff(...)`
- `has_staged_changes(...)`

Point important :
- la V1 repose principalement sur le diff stagé, car il représente l'intention
  de commit la plus sûre.

### `stage.py`

Responsabilité :
- ajouter ou retirer explicitement des fichiers de l'index.

Fonctions principales :
- `stage_files(...)`
- `unstage_files(...)`

Point important :
- l'usage de `--` avant les chemins protège contre les ambiguïtés d'interprétation.

### `branch.py`

Responsabilité :
- exposer les informations utiles sur la branche courante et son upstream.

Fonctions principales :
- `get_current_branch(...)`
- `get_branch_status(...)`
- `has_upstream(...)`
- `get_upstream_branch(...)`
- `get_push_remote(...)`

### `commit.py`

Responsabilité :
- créer un commit ;
- pousser la branche courante si demandé.

Fonctions principales :
- `create_commit(...)`
- `push_current_branch(...)`

## Flux cible dans la V1

### Cas nominal : commit depuis le staging actuel

1. La CLI ou un service appelle `get_repo_status(...)`.
2. Le service vérifie qu'il existe des changements stagés.
3. Le service appelle `get_staged_diff(...)`.
4. Le diff est transmis à la couche de génération de message.
5. Le message validé est envoyé à `create_commit(...)`.
6. Si `--push` est demandé, la CLI appelle `push_current_branch(...)`.

### Cas `--files`

1. L'utilisateur fournit une liste de chemins.
2. Le service de sélection appelle `stage_files(paths)`.
3. Le service appelle `get_staged_diff(paths=paths)`.
4. Le reste du flux est identique au cas nominal.

## Conventions et invariants

- Toutes les commandes Git passent par `run_git_command(...)`.
- Les modules de la couche Git ne gèrent pas l'interactivité CLI.
- Les fonctions retournent des objets ou des chaînes simples, pas des structures ad hoc.
- Les erreurs Git doivent remonter sous forme d'exceptions applicatives.
- Les chemins ciblés sont passés après `--` lorsqu'ils peuvent être interprétés comme des paths.

## Stratégie de test recommandée

### Tests unitaires

À couvrir en priorité :

- parsing de la ligne `## ...` dans `status.py` ;
- parsing des lignes `XY path` ;
- validation des propriétés `is_staged`, `is_untracked`, `is_modified_in_worktree` ;
- validation de `create_commit(...)` si le message est vide.

### Tests d'intégration

Dans un dépôt temporaire :

- créer un repo Git ;
- créer et modifier un fichier ;
- stage du fichier ;
- vérifier que `get_repo_status(...)` reflète l'état attendu ;
- vérifier que `get_staged_diff(...)` retourne un diff non vide ;
- exécuter `create_commit(...)` ;
- vérifier que le commit a bien été créé.

## Limites connues de la V1

- parsing volontairement simple des renommages/copies ;
- pas de gestion interactive ;
- pas de sélection partielle intra-fichier ;
- pas de stratégie avancée de résolution d'erreurs Git côté UX.

Ces limites sont acceptables pour la V1 car l'objectif est d'obtenir un socle fiable,
modulaire et testable.

## Évolutions possibles

- support plus fin des renommages ;
- helpers pour `git rev-parse` et validation explicite du dépôt ;
- meilleure détection des états de branche pour le push ;
- enrichissement des erreurs pour une UX CLI plus pédagogique ;
- support futur de workflows avancés (PR, hooks, exclusions, sélection interactive).