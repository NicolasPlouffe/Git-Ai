# Prompts du projet

Git AI Commit Assistant s’appuie sur des prompts versionnés dans le dépôt pour piloter la génération de messages de commit et, plus largement, préparer des usages futurs comme la génération de descriptions de pull request.[1][2] Cette approche fait du prompt une ressource applicative explicite, maintenable et testable, plutôt qu’une simple chaîne de caractères dispersée dans le code.[1][2]

## Rôle des prompts

Dans l’architecture du projet, les prompts servent d’interface entre le diff Git produit localement et le provider LLM appelé en bout de chaîne.[1] Ils traduisent une intention produit précise : obtenir une sortie courte, exploitable et alignée avec les contraintes du projet, comme la langue demandée ou le format attendu du message de commit.[1]

Le prompt n’est donc pas un détail d’implémentation annexe.[1] Dans un outil de ce type, il constitue une partie du comportement fonctionnel lui-même, car la qualité du résultat dépend directement de la clarté des instructions envoyées au modèle.[1]

## Organisation dans le dépôt

Les prompts sont stockés dans `src/git_ai/prompts/`.[1][2] Le snapshot documentaire montre la présence des fichiers suivants :

- `commit_fr.txt` ;[2]
- `commit_en.txt` ;[2]
- `commit_es.txt` ;[2]
- `commit_pt.txt` ;[2]
- `pr_fr.txt` ;[2]
- `pr_en.txt` ;[2]
- `pr_es.txt` ;[2]
- `pr_pt.txt`.[2]

Cette organisation montre un découpage par cas d’usage et par langue, ce qui reste simple à comprendre et facile à faire évoluer.[2] Elle évite aussi d’entrelacer des conditions linguistiques ou fonctionnelles complexes dans le code Python lui-même.[1][2]

## Types de prompts

### Prompts de commit

Les fichiers `commit_*.txt` servent à la génération du message de commit à partir d’un diff Git.[2] Ils constituent le chemin principal de la V1, puisque le MVP documenté est centré sur la commande `commit`, la génération depuis le diff stagé, le ciblage par fichiers et le choix de langue.[1]

Ces prompts doivent guider le modèle vers une sortie concise, pertinente et alignée avec la forme attendue par l’application.[1] Ils sont utilisés conjointement avec les paramètres de configuration, notamment la langue, le format de commit et la longueur maximale du sujet.[1]

### Prompts de PR

Les fichiers `pr_*.txt` montrent que le projet prépare aussi la génération de descriptions de pull request.[2] Même si cette capacité ne fait pas encore partie du cœur du MVP V1 décrit dans le README, sa présence dans l’arborescence confirme que l’architecture et les ressources documentaires ont été pensées pour évoluer au-delà du seul commit message.[1][2]

Ce choix est cohérent avec la présence de `src/git_ai/services/pr_description_service.py`, qui indique un point d’orchestration prévu pour cette fonctionnalité.[2] Les prompts PR peuvent donc être documentés dès maintenant comme une extension structurée du système, même si leur usage reste secondaire à ce stade.[2]

## Multilingue

Le dépôt contient des prompts en français, anglais, espagnol et portugais.[2] Cette couverture linguistique est cohérente avec `src/git_ai/config.py`, qui expose `fr`, `en`, `es` et `pt` comme langues supportées, ainsi qu’avec le `.env.example` qui mentionne ces quatre codes de langue.[1]

Le README met surtout en avant `fr`, `en` et `es` dans le périmètre fonctionnel de la V1, mais le code et les fichiers présents montrent que le portugais est déjà pris en compte dans la structure du projet.[1][2] La documentation des prompts doit donc refléter cette réalité : certaines capacités sont au cœur du MVP, d’autres sont déjà préparées dans l’architecture et les ressources versionnées.[1][2]

## Intégration avec le code

Le service `src/git_ai/services/prompt_service.py` est le point naturel d’intégration entre les données du domaine et les fichiers de prompts.[2] Son rôle, dans l’architecture générale documentée, est de construire le prompt exploitable par le provider en fonction du diff Git, de la langue et des contraintes issues de la configuration applicative.[1][2]

Autrement dit, les fichiers de prompt ne sont pas utilisés isolément : ils sont assemblés dans un flux où interviennent aussi `GitDiff`, `PromptRequest`, `PromptPayload` et les services d’orchestration autour de la génération de message.[1] Cette intégration explicite est importante, car elle montre que le prompt fait partie d’un contrat applicatif et non d’un texte libre injecté sans structure.[1]

## Ce qu’un bon prompt doit porter

Dans ce projet, un bon prompt doit exprimer plusieurs dimensions du besoin produit :

- la tâche attendue, par exemple résumer un diff sous forme de message de commit ;[1]
- la langue de sortie ;[1]
- le style ou le format attendu, par exemple `conventional` ou `simple` ;[1]
- les contraintes de longueur, comme `max_subject_length` ;[1]
- l’attente de clarté et d’exploitabilité pour un vrai workflow Git.[1]

Ces contraintes ne doivent pas être réparties de manière arbitraire entre code et prompt.[1] La documentation doit au contraire rappeler que le code porte la validation et l’orchestration, tandis que le prompt porte surtout les instructions rédactionnelles et sémantiques destinées au modèle.[1][2]

## Pourquoi stocker les prompts en fichiers

Le choix de stocker les prompts dans `src/git_ai/prompts/` apporte plusieurs bénéfices concrets.[2]

- **Lisibilité** : le texte envoyé au modèle peut être relu sans ouvrir les services Python.[2]
- **Versioning** : les changements de consignes sont suivis dans Git comme n’importe quelle ressource métier.[2]
- **Séparation des responsabilités** : la logique de construction reste dans `prompt_service.py`, tandis que les instructions métier restent dans les fichiers texte.[2]
- **Évolutivité** : ajouter une langue ou un type de prompt devient une opération locale et peu risquée.[2]

Ce choix est particulièrement pertinent pour un projet portfolio en AI engineering, parce qu’il rend visible la manière dont la couche prompting est gérée comme un composant du système.[1] Il facilite aussi la relecture produit, même pour une personne qui ne souhaite pas entrer immédiatement dans le code Python.[1][2]

## Convention de nommage

La convention actuelle suit le motif `<usage>_<lang>.txt`, par exemple `commit_fr.txt` ou `pr_en.txt`.[2] Cette convention est simple, explicite et suffisante tant que les variations de prompts restent principalement organisées par cas d’usage et par langue.[2]

Si le projet devait ajouter plus tard des variantes par style, provider ou profil, il faudrait préserver cette lisibilité en évitant une explosion de conventions implicites.[1][2] À ce stade, la structure actuelle est un bon compromis entre clarté et extensibilité.[2]

## Interaction avec la configuration

La configuration applicative influence directement la sélection et l’usage des prompts.[1] La langue, le format de commit et certaines règles de sortie sont déterminés à travers `AppConfig` et ses sous-configurations, puis consommés dans le flux de génération.[1]

Par exemple, `language` est validé contre l’ensemble `fr`, `en`, `es`, `pt`, tandis que `commit.format` est validé contre `conventional` et `simple`.[1] La documentation des prompts doit donc être reliée à `docs/config.md`, car la configuration ne fait pas que choisir un backend : elle influence aussi la forme textuelle attendue du résultat.[1]

## Interaction avec les modèles de domaine

Le projet contient plusieurs objets de domaine qui structurent le passage entre Git, prompts et providers, notamment `GitDiff`, `PromptRequest`, `PromptPayload`, `LLMRequest` et `LLMResponse`.[1] Cette modélisation montre que la couche prompts n’est pas simplement un répertoire de templates, mais une étape insérée dans un pipeline de données bien défini.[1]

La documentation des prompts gagne donc à être lue avec `docs/architecture.md` : on comprend mieux à quel moment le prompt est construit, quelles données il reçoit et comment son résultat est ensuite transformé en message de commit utilisable.[1] Cela aide à expliquer le comportement du système sans surcharger le README principal.[1]

## Testabilité

Le dépôt contient `tests/unit/test_prompt_service.py`, ce qui montre que la construction ou la sélection des prompts fait déjà partie des comportements testés.[2] C’est un point important : dans un projet orienté LLM, la couche prompts ne doit pas rester implicite ou non vérifiée.[2]

Même sans reproduire ici le contenu exact des templates, la présence de tests dédiés indique que l’équipe cherche à stabiliser les règles d’assemblage, de sélection de langue et d’intégration avec les services métier.[2] Cette testabilité renforce la crédibilité du projet comme outil réel et comme démonstration portfolio.[1][2]

## Bonnes pratiques pour faire évoluer les prompts

Plusieurs règles simples sont recommandées pour maintenir cette couche proprement :

- garder les prompts courts, explicites et orientés tâche ;[1]
- éviter de dupliquer dans le prompt des validations déjà gérées par le code ;[1]
- séparer clairement les prompts de commit et de PR ;[2]
- conserver une correspondance stable entre langues supportées et fichiers présents ;[1][2]
- faire évoluer les prompts par versioning Git et valider les changements avec les tests associés.[2]

Ces pratiques aident à contenir la complexité lorsque le projet grandit.[1][2] Elles évitent aussi que la logique applicative se déplace progressivement vers des templates opaques et difficiles à relire.[1]

## Limites actuelles et évolution

Le contexte documentaire disponible confirme la présence des fichiers de prompts et de leur intégration architecturale, mais il n’expose pas ici le contenu exact de chaque template.[1][2] La présente documentation décrit donc la structure, le rôle et les principes d’usage des prompts, sans chercher à recopier ou figer ligne par ligne leur texte interne.[1][2]

Cette limite n’empêche pas de documenter correctement la couche prompts pour E12, car le point important à ce stade est de rendre clair le pourquoi, le où et le comment de ces ressources dans l’architecture globale.[1] Une itération ultérieure pourra compléter ce document avec une description plus précise du style attendu de chaque famille de prompt, à condition de partir du dépôt stabilisé.[2]