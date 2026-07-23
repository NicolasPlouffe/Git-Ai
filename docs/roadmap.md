# Roadmap du projet

Git AI Commit Assistant est pensé comme un outil CLI Python local-first, utile dans un vrai workflow développeur et suffisamment propre pour servir de projet portfolio en AI engineering.[1] La roadmap doit donc concilier deux exigences : livrer une V1 utilisable rapidement et préparer une évolution progressive vers un outil plus riche sans compromettre la lisibilité de l’architecture.[1]

## Vision produit

Le projet vise à réduire le temps passé à rédiger des messages de commit tout en gardant un contrôle local sur l’inférence, une configuration explicite et une intégration simple avec Git.[1] À moyen terme, l’ambition n’est pas seulement de produire un message de commit, mais de bâtir un assistant Git local-first capable d’orchestrer plusieurs tâches textuelles liées au cycle de développement.[1][2]

Cette vision repose sur une base architecturale déjà visible dans le dépôt : séparation entre CLI, configuration, couche Git, services métier, prompts et providers ; présence de plusieurs backends ; préparation de prompts PR ; et début de services dédiés à des usages plus larges que le seul commit message.[1][2]

## Statut actuel

Le README documente une V1 centrée sur la commande `commit`, la génération depuis le diff stagé, l’option `--files`, le choix de langue, le mode `--dry-run`, l’option `--push`, le provider Ollama, la configuration multi-source et un wrapper Bash/Zsh minimal.[1] Le dépôt montre aussi des briques déjà en place autour de `llama.cpp`, d’un provider `openai-compatible`, de prompts PR et d’un `pr_description_service.py`, ce qui suggère que certaines fondations de la suite sont déjà amorcées.[2]

La roadmap doit donc distinguer ce qui relève du MVP stabilisé, de la V2 fonctionnelle et d’améliorations plus transverses liées à l’expérience développeur, à la fiabilité et à la démonstration portfolio.[1][2]

## Priorité 1 — Stabiliser la V1

La première priorité reste de consolider la version déjà définie dans la documentation du projet.[1] Le périmètre V1 documenté comprend les éléments suivants :

- commande `commit` ;[1]
- génération depuis le diff stagé ;[1]
- support de `--files` ;[1]
- support de `--lang` ;[1]
- support de `--dry-run` ;[1]
- support de `--push` ;[1]
- provider Ollama ;[1]
- configuration via YAML, variables d’environnement et options CLI ;[1]
- tests unitaires de base ;[1]
- wrapper Bash/Zsh minimal.[1]

À ce stade, terminer la V1 ne signifie pas ajouter beaucoup de nouvelles fonctionnalités, mais surtout rendre le comportement prévisible, bien documenté et démontrable de bout en bout.[1] Cela inclut aussi l’installation d’Ollama, la clarté des exemples, la cohérence entre README et docs, et la fiabilité des scénarios critiques testés.[1][2]

## Priorité 2 — V2 fonctionnelle

La documentation actuelle mentionne déjà plusieurs axes pour la V2.[1] Ils peuvent être regroupés en quatre sous-familles cohérentes.

### Providers supplémentaires

L’ajout de `llama.cpp` figure explicitement dans la V2 prévue.[1] Le dépôt contient déjà un fichier `src/git_ai/providers/llama.cpp.py`, ce qui indique que l’architecture prépare cette évolution et qu’une partie du travail de structuration a probablement déjà été anticipée.[2]

La présence de `openai_compat.py` montre aussi une ouverture potentielle vers des backends compatibles API, même si ce n’est pas présenté comme priorité produit principale dans le README actuel.[2] La roadmap doit donc garder Ollama comme voie nominale, tout en consolidant progressivement un socle multi-provider crédible.[1][2]

### Sélection de périmètre plus riche

La sélection interactive de fichiers est un axe naturel après le support actuel de `--files` et du staging courant.[1] Elle améliorerait l’expérience utilisateur sans remettre en cause l’architecture existante, car le dépôt contient déjà `file_selection_service.py` et plusieurs modules Git dédiés aux fichiers et au statut du dépôt.[2]

Une bonne V2 dans ce domaine pourrait inclure une sélection interactive simple, lisible et non intrusive, tout en préservant la possibilité de rester entièrement scriptable depuis la ligne de commande.[1][2]

### Génération de PR

La génération de pull request figure dans la V2 prévue du projet.[1] Ce chantier est cohérent avec la présence de prompts `pr_*.txt` et de `pr_description_service.py`, qui montrent que le terrain a déjà été préparé dans la structure du dépôt.[2]

Cette évolution a un fort intérêt produit et portfolio, car elle montre comment réutiliser les mêmes briques d’orchestration pour une tâche voisine : récupérer un contexte Git, produire un prompt structuré et générer une sortie utile dans un vrai workflow développeur.[1][2]

### Profils et exclusions

Les profils de configuration et les exclusions de fichiers sont également listés dans la V2 prévue.[1] Ces deux axes prolongent naturellement la logique déjà présente dans `config.py`, qui gère des valeurs par défaut, des surcharges et des validations structurées.[1]

Les profils permettraient de mieux séparer des usages comme projet personnel, repo professionnel, style conventional strict ou workflow PR first.[1] Les exclusions, elles, aideraient à mieux contrôler le bruit lié à certains fichiers générés, artefacts ou modifications peu pertinentes pour la génération du message.[1]

## Priorité 3 — Ergonomie CLI

Même avec une base fonctionnelle saine, un outil CLI n’est réellement adoptable que si son expérience quotidienne est fluide.[1] La roadmap peut donc inclure un axe spécifique sur l’ergonomie, sans pour autant sortir du périmètre local-first et scriptable du projet.[1]

Les pistes les plus naturelles sont :
- messages d’erreur plus guidants ;[1]
- sorties plus lisibles en `dry-run` ;[1]
- meilleure découverte des options via l’aide CLI ;[1][2]
- sous-commandes plus homogènes à mesure que le projet grandit ;[2]
- wrapper shell simple, mais suffisamment pratique pour s’intégrer à un usage réel.[1]

L’objectif ici n’est pas de faire une interface magique, mais de réduire les frictions tout en gardant une CLI sobre et robuste.[1]

## Priorité 4 — Qualité et fiabilité

Le dépôt contient déjà un ensemble de tests unitaires et d’intégration couvrant la CLI, la configuration, Git, Ollama, les prompts, les modèles et plusieurs services métier.[1][2] Cette base est précieuse et doit rester une priorité de la roadmap, car un outil qui manipule Git et dépend d’un backend local gagne beaucoup à être validé par scénarios réalistes.[1][2]

Dans cette perspective, les axes de progression naturels sont :
- enrichir les tests autour des cas limites Git ;[2]
- mieux couvrir les variations de configuration et de providers ;[1][2]
- renforcer la validation de normalisation des sorties LLM ;[2]
- mieux documenter les comportements en absence de backend disponible.[1][2]

Cette priorité est importante pour l’usage réel, mais aussi pour la crédibilité portfolio du projet.[1]

## Priorité 5 — Valeur portfolio

Le projet est explicitement présenté comme un projet portfolio en AI engineering autant qu’un outil réel.[1] La roadmap doit donc intégrer des livrables qui rendent cette valeur lisible pour une personne externe : README solide, documentation d’architecture, documentation de configuration, documentation des prompts, notes de démo et positionnement clair du projet.[1][2]

L’intérêt portfolio ne vient pas seulement des fonctionnalités visibles, mais aussi de la capacité à montrer une architecture raisonnée, une stratégie de test, une gestion de configuration propre et une approche structurée de l’intégration d’un LLM local dans un outil développeur.[1] En ce sens, la documentation produite dans E12 fait déjà partie intégrante de la roadmap produit.[1]

## Proposition de phasage

### Phase A — Finalisation documentaire et stabilisation

Objectif : rendre la V1 lisible, installable et démontrable.[1]

- finaliser `README.md` ;[1]
- consolider `docs/architecture.md`, `docs/config.md`, `docs/prompts.md` et `docs/roadmap.md` ;[2]
- vérifier les exemples d’installation, notamment avec Ollama ;[1]
- stabiliser les chemins critiques via les tests existants.[2]

### Phase B — Consolidation produit V1

Objectif : fiabiliser l’usage quotidien de la commande `commit`.[1]

- améliorer l’ergonomie des messages CLI ;[1]
- durcir la validation des erreurs de configuration, de provider et de contexte Git ;[1][2]
- réduire les écarts entre comportement réel et documentation ;[1]
- clarifier l’expérience wrapper shell sans déplacer la logique métier hors de Python.[1]

### Phase C — Extension V2 ciblée

Objectif : ajouter de la valeur sans casser la simplicité de l’outil.[1]

- activer réellement `llama.cpp` comme alternative crédible ;[1][2]
- ajouter la sélection interactive de fichiers ;[1]
- introduire la génération de PR ;[1][2]
- ajouter profils de configuration et exclusions de fichiers.[1]

### Phase D — Maturité et démonstration

Objectif : transformer le projet en référence de portfolio démontrable.[1]

- produire un plan de démo clair ;[1]
- montrer plusieurs scénarios d’usage réel ;[1]
- documenter les compromis d’architecture et les choix techniques ;[1][2]
- préparer la suite vers des hooks Git ou d’autres automatisations locales.[1]

## Ce qui ne doit pas dériver

La roadmap doit préserver quelques invariants importants déjà visibles dans le positionnement du projet.[1] D’abord, la logique métier doit rester principalement en Python et non migrer progressivement vers un wrapper shell trop intelligent.[1]

Ensuite, le projet doit rester local-first, avec Ollama comme chemin nominal de la V1, même si d’autres backends sont ajoutés ensuite.[1] Enfin, l’architecture doit continuer à privilégier des modules simples, testables et lisibles, plutôt qu’une accumulation de comportements spéciaux difficiles à maintenir.[1][2]

## Résumé des priorités

| Horizon | Priorité | Résultat attendu |
|---|---|---|
| Court terme | Stabiliser la V1 | README, docs, installation Ollama, flux `commit` fiable.[1] |
| Court terme | Renforcer la qualité | Tests plus solides, erreurs plus claires, cohérence doc/code.[1][2] |
| Moyen terme | Étendre les capacités | `llama.cpp`, sélection interactive, génération de PR, profils.[1][2] |
| Moyen terme | Améliorer l’ergonomie | CLI plus confortable, wrapper minimal utile, sorties plus lisibles.[1] |
| Long terme | Renforcer la valeur portfolio | démonstration complète, documentation mature, scénarios concrets.[1] |

Cette roadmap garde une ligne simple : d’abord rendre excellent le flux `commit`, puis étendre le produit par couches, sans sacrifier la lisibilité de l’architecture ni le positionnement local-first qui fait l’identité du projet.[1]