# Architecture du projet

Git AI Commit Assistant est un outil CLI Python local-first conçu pour générer des messages de commit Git à partir d’un diff, en s’appuyant sur un provider LLM local et une orchestration métier explicite.[1] L’architecture privilégie la séparation des responsabilités, la testabilité et l’extensibilité, avec un cœur applicatif en Python et un rôle minimal laissé au shell wrapper.[1]

## Principes d’architecture

L’application repose sur quelques principes simples : garder la logique métier dans Python, isoler les détails d’infrastructure derrière des modules dédiés, et permettre l’ajout de nouveaux providers sans réécrire le flux principal.[1] Cette approche est visible dans la structure du dépôt, où la CLI, la configuration, la couche Git, les providers, les services métier, les prompts et les tests sont séparés en sous-ensembles cohérents.[1][2]

Les choix de structure soutiennent deux objectifs : un usage réel dans un workflow développeur et une présentation portfolio lisible d’un projet d’AI engineering appliqué.[1] L’architecture doit donc rester assez simple pour être comprise rapidement, mais assez modulaire pour absorber des évolutions comme `llama.cpp`, la génération de PR, les profils de configuration ou des exclusions de fichiers plus fines.[1]

## Vue d’ensemble

Le flux principal de la commande `commit` suit une chaîne courte et explicite : charger la configuration, déterminer le périmètre du diff, produire le diff Git, construire le prompt, appeler le provider local, nettoyer la réponse puis créer le commit et éventuellement pousser.[1] Cette séquence reflète directement les responsabilités des modules présents dans `src/git_ai/`.[1][2]

```text
CLI
  -> chargement de la configuration
  -> sélection du périmètre Git
  -> génération du diff
  -> construction du prompt
  -> appel du provider LLM
  -> normalisation du message
  -> commit Git
  -> push optionnel
```

La CLI ne contient donc pas toute la logique métier : elle sert surtout de point d’entrée et délègue le travail à des composants plus spécialisés.[1] Cette distribution réduit le couplage entre interface utilisateur, règles métier et appels aux systèmes externes comme Git ou Ollama.[1][2]

## Structure des modules

### Entrée CLI

Le point d’entrée de l’outil est `src/git_ai/cli.py`, avec une application Typer exposée comme script console `git-ai` dans `pyproject.toml`.[1] Le dépôt contient aussi `src/git_ai/commands/commit.py` et `src/git_ai/commands/init.py`, ce qui indique une organisation par commandes plutôt qu’une CLI monolithique.[2][1]

Cette couche a pour responsabilité de : parser les options utilisateur, appeler les commandes applicatives, afficher les résultats, puis transmettre les paramètres à la logique métier sans la réimplémenter localement.[1] Elle doit rester fine, car toute règle de fond mise ici deviendrait plus difficile à tester et à réutiliser dans d’autres contextes d’exécution.[1]

### Configuration

Le module `src/git_ai/config.py` centralise le chargement, la fusion et la validation de la configuration applicative.[1] Le contexte documentaire montre que cette configuration est multi-source, avec un ordre de priorité explicite : valeurs par défaut, fichier YAML, variables d’environnement, puis options CLI.[1]

Le module porte également des validations de domaine importantes : providers supportés, langues supportées, formats de commit, longueurs maximales, paramètres Git et paramètres liés à la détection de scaffold.[1] Cela en fait un composant central de robustesse, car il permet de rejeter tôt une configuration incohérente avant l’exécution du flux métier.[1]

### Modèles et exceptions

`src/git_ai/models.py` contient les objets de domaine utilisés pour faire circuler des données structurées entre les couches, comme les fichiers modifiés, le diff Git, la sélection de fichiers, les requêtes provider, les réponses LLM et les messages de commit.[1] Cette modélisation évite de propager des dictionnaires ad hoc partout dans le code et rend les contrats plus lisibles dans les services et les tests.[1]

`src/git_ai/exceptions.py` regroupe les erreurs applicatives principales, notamment pour la configuration, Git, la génération de diff, la sélection de fichiers, les prompts, les providers et la génération du message de commit.[1] Cela clarifie la frontière entre erreurs métier attendues et erreurs techniques non gérées, tout en facilitant des messages CLI plus propres.[1]

### Couche Git

Le dossier `src/git_ai/git/` encapsule les opérations Git nécessaires au produit, avec des modules dédiés comme `status.py`, `stage.py`, `diff.py`, `commit.py`, `branch.py`, `files.py`, `file_queries.py`, `paths.py` et `_common.py`.[2] Cette séparation montre que Git est traité comme une infrastructure métier à part entière, et non comme une suite de commandes shell éparpillées dans la CLI ou les services.[2]

La responsabilité de cette couche est de produire des primitives stables : lire l’état du dépôt, déterminer des fichiers ciblables, produire un diff, valider le contexte Git, committer et préparer un éventuel push.[1][2] Elle constitue la frontière entre le cœur métier Python et l’environnement Git local de l’utilisateur.[1]

### Providers LLM

Le dossier `src/git_ai/providers/` contient au moins `base.py`, `ollama.py`, `llama.cpp.py` et `openai_compat.py`.[2] Cette structure confirme une architecture par contrat provider, où le flux métier dépend d’une abstraction commune plutôt que d’un backend spécifique.[1][2]

Dans la V1, Ollama est le provider de référence documenté dans le README et la configuration par défaut.[1] La présence d’implémentations supplémentaires montre cependant que l’architecture a déjà été préparée pour d’autres backends locaux ou compatibles API, ce qui limite l’impact de futurs changements sur la couche d’orchestration.[1][2]

### Services métier

Le dossier `src/git_ai/services/` regroupe l’orchestration métier avec `commit_message_service.py`, `file_selection_service.py`, `prompt_service.py`, `pr_description_service.py` et `scaffold_detection.py`.[2] C’est ici que se trouvent les règles applicatives qui composent les données issues de la configuration, de Git et du provider LLM.[1][2]

Le service de génération de message de commit assemble typiquement le diff, le prompt, la réponse provider et le nettoyage de sortie.[1][2] Le service de sélection de fichiers détermine le périmètre de travail entre staging actuel et sélection explicite, tandis que `prompt_service.py` traduit un diff et une langue en prompt exploitable pour le backend.[1][2]

La présence de `pr_description_service.py` et `scaffold_detection.py` suggère aussi une architecture déjà ouverte à des cas d’usage plus larges que le seul commit, sans devoir tout réorganiser plus tard.[2] C’est un bon compromis entre simplicité V1 et extensibilité V2.[1][2]

### Prompts

Le dossier `src/git_ai/prompts/` contient des prompts de commit et de PR en plusieurs langues, notamment `fr`, `en`, `es` et `pt`.[2] Le choix de stocker ces prompts dans des fichiers dédiés, plutôt qu’en chaînes dispersées dans le code, rend la maintenance plus propre et permet de faire évoluer style, ton et contraintes sans toucher directement aux services.[2]

Cette séparation est importante pour un projet orienté AI engineering, car elle matérialise le prompt comme une ressource métier versionnée.[1][2] Elle facilite également la documentation fonctionnelle des consignes envoyées au modèle, d’où la pertinence d’un document complémentaire `docs/prompts.md` déjà présent dans le dépôt.[2]

### Utilitaires

Le dossier `src/git_ai/utils/` contient des helpers transverses comme `paths.py`, `subprocesses.py` et `text.py`.[2] Leur rôle est de porter des détails techniques réutilisables sans alourdir les couches métier ou infrastructure spécialisées.[2]

Cette couche ne doit pas devenir un fourre-tout : elle est utile si elle reste limitée à des fonctions génériques de support, sans capturer de logique métier spécifique au flux de commit.[2]

## Découpage des responsabilités

Le découpage actuel peut être résumé ainsi :

| Couche | Responsabilité principale |
|---|---|
| `cli.py` et `commands/` | Interface utilisateur en ligne de commande, parsing et délégation.[1][2] |
| `config.py` | Fusion, validation et exposition de la configuration.[1] |
| `models.py` | Contrats de données entre couches.[1] |
| `exceptions.py` | Erreurs métier et techniques normalisées.[1] |
| `git/` | Accès au dépôt Git local et opérations associées.[2] |
| `providers/` | Abstraction LLM et implémentations concrètes.[1][2] |
| `services/` | Orchestration métier et règles applicatives.[2] |
| `prompts/` | Ressources de prompt versionnées.[2] |
| `tests/` | Validation des comportements unitaires et intégrés.[1][2] |

Ce découpage est cohérent avec les objectifs du projet, car il évite de mélanger logique de présentation, logique métier et intégration externe dans les mêmes fichiers.[1] Il reste aussi suffisamment simple pour être expliqué rapidement à un recruteur, un reviewer ou un utilisateur avancé du dépôt.[1]

## Flux détaillé de la commande `commit`

Le scénario principal de la V1 peut être lu comme une orchestration de composants spécialisés.[1] Voici le chemin nominal :

1. La CLI reçoit les options utilisateur, comme la langue, le mode `dry-run`, l’option `--files` ou le push éventuel.[1]
2. La configuration est chargée puis résolue selon l’ordre de priorité multi-source.[1]
3. Le service de sélection de fichiers décide si le périmètre repose sur le staging ou sur une liste explicite de fichiers.[1][2]
4. La couche Git produit le diff correspondant.[1][2]
5. Le service de prompt construit l’entrée textuelle à envoyer au modèle selon la langue et les règles du format de commit.[1][2]
6. Le provider appelle le backend local, par défaut Ollama.[1]
7. Le service de message nettoie, normalise et valide la sortie du modèle.[2]
8. Selon le mode choisi, la CLI affiche le résultat, crée le commit, puis peut déclencher un push.[1]

Cette chaîne a l’avantage d’être traçable et testable par étape.[1][2] Elle rend aussi plus facile l’identification des zones de responsabilité lorsqu’un bug ou une évolution fonctionnelle apparaît.[1]

## Configuration et extensibilité

L’un des points forts du projet est la séparation entre configuration, orchestration et backend modèle.[1] Comme le module de configuration valide déjà des providers multiples, plusieurs langues, des formats de commit et des paramètres Git, l’architecture est prête pour absorber des variantes sans réécrire le flux principal.[1]

Cette extensibilité se voit aussi dans le dépôt : présence de `llama.cpp.py`, d’un provider `openai_compat`, de prompts PR et d’un service `pr_description_service.py`.[2] Même si toutes ces capacités ne sont pas encore au centre du MVP V1, leur place dans l’arborescence montre que le design vise une croissance contrôlée plutôt qu’une accumulation opportuniste de scripts.[1][2]

## Stratégie de test

Le dépôt distingue clairement `tests/unit/` et `tests/integration/`.[1][2] Les tests unitaires couvrent notamment la CLI, la configuration, les modèles, le provider Ollama, le service de prompt, le service de commit message, la sélection de fichiers, la détection de scaffold et certains comportements Git ciblés.[2]

Les tests d’intégration couvrent des scénarios plus proches du comportement réel, comme les interactions Git, la validation de commit, le flux de langue ou le provider Ollama.[2] Ce découpage reflète bien l’architecture : les règles isolables sont testées au niveau unitaire, tandis que les frontières entre composants et dépendances externes sont validées au niveau intégration.[1][2]

## Compromis de conception

L’architecture fait un choix clair : privilégier un outil CLI Python structuré plutôt qu’un wrapper shell complexe.[1] Ce compromis améliore la lisibilité, la testabilité et la portabilité de la logique métier, au prix d’une base de code plus formelle qu’un simple script Bash, ce qui est cohérent avec l’ambition produit et portfolio du projet.[1]

Un autre compromis visible est l’anticipation de la V2 dans la structure même du dépôt.[1][2] Cela apporte de l’extensibilité, mais demande de rester vigilant pour ne pas introduire trop tôt des abstractions qui dépasseraient les besoins réels de la V1.[1]

## Évolutions attendues

La roadmap documentaire mentionne déjà l’ajout de `llama.cpp`, la sélection interactive de fichiers, la génération de PR, les profils de configuration, les exclusions de fichiers et des hooks Git.[1] L’architecture actuelle est globalement bien positionnée pour absorber ces évolutions, car les axes d’extension sont déjà localisés dans les providers, les services, les prompts et la configuration.[1][2]

Les évolutions futures devront cependant préserver deux invariants : garder une CLI légère et maintenir une frontière nette entre opérations Git, logique métier et appels LLM.[1] C’est cette discipline qui fait aujourd’hui la lisibilité du projet et sa valeur démonstrative en documentation d’architecture.[1]