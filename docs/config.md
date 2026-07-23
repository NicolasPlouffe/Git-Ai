# Configuration du projet

Git AI Commit Assistant utilise une configuration multi-source pensée pour un usage CLI local-first : l’outil peut être piloté par des valeurs par défaut, un fichier YAML, des variables d’environnement et des options de ligne de commande.[1] Cette approche permet de concilier simplicité d’usage, personnalisation locale et comportement explicite dans différents contextes d’exécution.[1]

## Objectif de la configuration

La configuration a pour rôle de décrire comment l’outil doit appeler le provider LLM, dans quelle langue générer la sortie, quel format de commit appliquer, et comment se comporter vis-à-vis de Git.[1] Elle encadre aussi des comportements plus avancés, comme la détection de scaffolding, déjà visible dans `src/git_ai/config.py`.[1]

Le projet centralise cette logique dans `src/git_ai/config.py`, ce qui permet de charger, fusionner et valider les paramètres avant l’exécution du flux métier.[1] Cette centralisation réduit les ambiguïtés et évite de disperser les règles de configuration dans la CLI, les services ou les providers.[1]

## Ordre de priorité

Le chargement suit un ordre de priorité explicite :

1. valeurs par défaut ;
2. fichier YAML ;
3. variables d’environnement ;
4. options CLI.[1]

Cela signifie qu’une valeur définie via la CLI doit l’emporter sur une variable d’environnement, elle-même prioritaire sur le YAML, lui-même prioritaire sur les valeurs codées par défaut dans l’application.[1] Ce modèle est adapté à un outil développeur, car il permet d’avoir une configuration stable dans le dépôt tout en gardant des surcharges ponctuelles pour un shell ou une commande précise.[1]

## Sources de configuration

### Valeurs par défaut

Le module `src/git_ai/config.py` définit les valeurs de base de l’application, notamment pour le provider, le modèle, la langue, l’URL du backend, le format de commit, la longueur maximale du sujet, le comportement de push et plusieurs seuils liés à la détection de scaffold.[1] Ces valeurs servent de socle minimal lorsqu’aucune configuration utilisateur n’est fournie.[1]

Le contexte documentaire montre par exemple les constantes suivantes : provider par défaut `ollama`, modèle par défaut `llama3.1:8b`, langue par défaut `en`, format de commit `conventional`, longueur maximale de sujet `72`, remote Git `origin` et push automatique désactivé par défaut.[1] La détection de scaffold est également activée par défaut, avec plusieurs seuils numériques validés au chargement.[1]

### Fichier YAML

Le projet prend en charge un fichier YAML utilisateur, recherché notamment via des noms comme `git-ai.yaml` et `git-ai.yml`.[1] Ce fichier permet de fixer la configuration principale du poste ou du projet sans répéter les mêmes options à chaque commande.[1]

Le README et le contexte documentaire montrent un exemple de structure YAML incluant `provider`, `base_url`, `model`, `language`, une section `commit` et une section `git`.[1] Cette organisation est cohérente avec les dataclasses exposées dans `config.py`, qui regroupent les paramètres par domaine fonctionnel.[1]

### Variables d’environnement

Le dépôt contient un `.env.example` qui documente les variables d’environnement prévues, notamment `GITAI_PROVIDER`, `GITAI_MODEL`, `GITAI_OLLAMA_HOST` et `GITAI_LANGUAGE`.[1] Ces variables sont utiles pour intégrer l’outil dans un shell personnel, un environnement de démonstration ou une automatisation locale.[1]

Les variables d’environnement sont particulièrement pratiques quand on veut changer rapidement de modèle, de provider ou de langue sans modifier le fichier YAML du projet.[1] Elles permettent aussi de garder certains réglages hors du dépôt tout en conservant une configuration reproductible pour l’utilisateur courant.[1]

### Options CLI

Les options CLI sont la couche de surcharge la plus haute.[1] Elles sont adaptées aux changements ponctuels de comportement, par exemple exécuter un commit en anglais, forcer un mode `dry-run` ou cibler un sous-ensemble de fichiers pour une seule commande.[1]

Dans la V1 documentée, les options d’usage visibles incluent notamment `--files`, `--lang`, `--dry-run` et `--push`.[1] La CLI devient ainsi le niveau de contrôle immédiat, tandis que YAML et variables d’environnement servent plutôt à exprimer des préférences persistantes.[1]

## Modèle de configuration

Le module `src/git_ai/config.py` met en place une configuration structurée à l’aide de dataclasses telles que `AppConfig`, `CommitConfig`, `GitConfig` et `ScaffoldDetectionConfig`.[1] Cette modélisation rend la configuration plus explicite qu’un simple dictionnaire libre et facilite la validation typée des champs.[1]

### AppConfig

`AppConfig` représente la configuration de haut niveau de l’application.[1] Elle agrège le provider, le modèle, la langue, l’URL de base du backend, puis les sous-configurations `commit`, `git` et `scaffold_detection`.[1]

Les validations associées imposent notamment :
- un provider supporté ;[1]
- une langue supportée ;[1]
- une `base_url` non vide ;[1]
- un nom de modèle non vide.[1]

### CommitConfig

`CommitConfig` regroupe les paramètres qui influencent directement la forme du message généré.[1] Le contexte documentaire montre au minimum `format`, `max_subject_length` et `include_body`.[1]

Les validations associées imposent que le format soit supporté et que la longueur maximale du sujet soit strictement positive.[1] Cela permet de garantir très tôt qu’un format ou une contrainte invalide ne remontera pas plus tard dans les services de génération de message.[1]

### GitConfig

`GitConfig` décrit le comportement Git associé à l’outil, en particulier `push_after_commit` et `remote`.[1] Une validation impose que le nom de remote ne soit pas vide.[1]

Cette sous-configuration est volontairement compacte dans la V1, ce qui aide à garder un périmètre simple.[1] Elle offre néanmoins un point d’extension naturel pour de futurs réglages Git plus avancés.[1]

### ScaffoldDetectionConfig

La configuration de détection de scaffold apparaît déjà comme une partie distincte du modèle de configuration.[1] Les champs documentés incluent notamment `enabled`, `min_added_files`, `min_added_ratio`, `max_non_added_files`, `min_confidence`, `large_commit_added_files`, `large_commit_added_ratio` et `ignore_ide_files`.[1]

Les validations imposent des bornes cohérentes : entiers non négatifs, ratios compris entre 0 et 1, et valeurs numériques correctement convertibles.[1] Ce bloc est un bon exemple d’une configuration métier spécialisée qui reste isolée du reste du système grâce à une dataclass dédiée.[1]

## Valeurs supportées

Le contexte documentaire permet déjà d’identifier plusieurs ensembles de valeurs supportées par la configuration applicative.[1]

### Providers supportés

Les providers supportés visibles dans `config.py` sont :
- `ollama` ;
- `llamacpp` ;
- `openai-compatible`.[1]

Le dépôt contient effectivement des implémentations associées dans `src/git_ai/providers/`, notamment `ollama.py`, `llama.cpp.py` et `openai_compat.py`.[2] Cela montre que la configuration n’est pas pensée uniquement pour Ollama, même si Ollama reste le backend de référence de la V1.[1][2]

### Langues supportées

Les langues supportées visibles dans `config.py` sont `fr`, `en`, `es` et `pt`.[1] Le dépôt contient aussi des prompts de commit et de PR pour ces quatre langues dans `src/git_ai/prompts/`.[2]

Le README met surtout en avant `fr`, `en` et `es` pour la V1 fonctionnelle, tandis que le code et les prompts montrent une ouverture plus large avec le portugais déjà prévu dans la structure documentaire.[1][2]

### Formats de commit supportés

Les formats de commit documentés dans `config.py` incluent au moins `conventional` et `simple`.[1] Cela permet à l’outil d’ajuster ses consignes de génération selon le style attendu pour l’équipe ou le projet.[1]

## Exemple de configuration YAML

Voici un exemple cohérent avec les informations visibles dans le README et la configuration applicative :[1]

```yaml
provider: ollama
model: qwen2.5-coder:7b
language: fr
base_url: http://localhost:11434/v1

commit:
  format: conventional
  max_subject_length: 72
  include_body: true

git:
  push_after_commit: false
  remote: origin

scaffold_detection:
  enabled: true
  min_added_files: 8
  min_added_ratio: 0.75
  max_non_added_files: 2
  min_confidence: 0.55
  large_commit_added_files: 20
  large_commit_added_ratio: 0.85
  ignore_ide_files: true
```

Cet exemple illustre une configuration adaptée à un usage local avec Ollama, un modèle orienté code, une sortie en français et un format de commit conventionnel.[1] Il donne aussi une base utile pour documenter des profils de configuration plus tard, sans changer la structure générale du système.[1]

## Exemple avec variables d’environnement

Le `.env.example` permet de documenter un usage par variables d’environnement.[1] Un exemple d’approche minimale peut être présenté ainsi :

```bash
export GITAI_PROVIDER=ollama
export GITAI_MODEL=qwen2.5-coder:7b
export GITAI_OLLAMA_HOST=http://localhost:11434
export GITAI_LANGUAGE=fr
```

Ce style de configuration convient bien à un environnement de shell personnel ou à un poste de démonstration.[1] Il est aussi utile quand plusieurs dépôts doivent partager un même backend local sans dupliquer un fichier YAML dans chacun d’eux.[1]

## Interaction entre YAML, environnement et CLI

La logique de surcharge doit être comprise comme un empilement : le YAML pose les préférences persistantes, l’environnement ajuste le contexte d’exécution, puis la CLI force les besoins ponctuels de la commande courante.[1] Ce modèle réduit les surprises, à condition que la documentation rappelle clairement l’ordre de priorité.[1]

Exemple conceptuel : si `language: fr` est défini dans `git-ai.yaml`, mais que `GITAI_LANGUAGE=en` est exporté dans le shell, la langue effective devient `en`.[1] Si ensuite la commande est lancée avec `--lang es`, la langue effective devient `es`, car la CLI a la priorité la plus haute.[1]

## Validation et erreurs

Le projet ne se contente pas de charger passivement des valeurs : il valide aussi leur cohérence au moment de construire `AppConfig`.[1] Les exemples visibles dans `config.py` montrent des erreurs explicites pour un format de commit non supporté, une longueur maximale invalide, un remote vide, un provider inconnu, une langue inconnue ou des paramètres numériques mal typés pour la détection de scaffold.[1]

Cette stratégie améliore l’expérience développeur, car les erreurs de configuration sont détectées tôt et formulées dans un vocabulaire de domaine plutôt qu’à travers une panne plus tardive dans la chaîne d’exécution.[1] Elle facilite aussi les tests dédiés à la configuration, dont la présence est visible avec `tests/unit/test_config.py`.[2]

## Recommandations d’usage

Pour un usage quotidien simple, une bonne approche consiste à garder un `git-ai.yaml` local comme source principale, puis à réserver les variables d’environnement et la CLI aux surcharges ponctuelles.[1] Cela garde la configuration lisible et reproductible tout en évitant de multiplier les paramètres en ligne de commande.[1]

Pour le développement ou la démonstration, il est utile de documenter clairement quel provider est attendu, quel modèle doit être installé, et quelle `base_url` correspond au backend local effectivement lancé.[1] Cela est particulièrement important dans la V1, où Ollama constitue le chemin nominal d’exécution.[1]

## Évolutions possibles

La roadmap du projet mentionne déjà des profils de configuration parmi les évolutions prévues.[1] Le design actuel est bien positionné pour supporter cette extension, car la configuration est déjà structurée et validée par blocs plutôt que stockée dans un fichier libre sans contrat.[1]

D’autres évolutions naturelles pourraient inclure des exclusions de fichiers plus détaillées, des stratégies de prompt par profil, ou des variantes de configuration selon le type de dépôt ou le backend utilisé.[1] La base actuelle reste suffisamment claire pour accueillir ces extensions sans refonte complète de `config.py`.[1]