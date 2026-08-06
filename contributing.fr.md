> Traduction communautaire (version préliminaire) — politique NTARI P2-002, Diffusion multilingue mondiale. Source : contributing.md (original anglais, instantané du 2026-07-29). Version préliminaire communautaire assistée par machine, en attente de relecture par un mainteneur régional conformément à P2-002 §3.1. Les spécifications techniques fondamentales restent en anglais conformément au §2.2.
>
> Vous avez remarqué une erreur de traduction ? N'hésitez pas à la corriger
> vous-même : forkez le dépôt
> https://github.com/NTARI-RAND/Leveson-Based-Trade-Assessment-Scale et ouvrez
> une pull request. Les corrections de traduction sont des contributions
> précieuses, tout autant que le code.

# Contribuer à LBTAS

## Comment contribuer

Les contributions se font via l'espace de travail Slack de NTARI.

**Rejoindre la discussion** : https://ntari.slack.com/archives/C09N88JN2SH

## Types de contributions

### Contributions de code
- Corrections de bugs
- Implémentations de fonctionnalités
- Améliorations de performance
- Mises à jour de la documentation

### Contributions de recherche
- Études de cas d'usage
- Articles universitaires utilisant LBTAS
- Exemples d'intégration
- Analyse de l'efficacité des évaluations

### Contributions de la communauté
- Signalement de problèmes
- Suggestions de fonctionnalités
- Améliorations de la documentation
- Aide à la traduction

## Processus de développement

### 1. Discussion
Discutez des modifications que vous proposez dans le canal Slack avant de commencer à travailler.

### 2. Fork et branche
```bash
git clone https://github.com/NTARI-OpenCoreLab/Leveson-Based-Trade-Assessment-Scale.git
cd Leveson-Based-Trade-Assessment-Scale
git checkout -b feature/your-feature-name
```

### 3. Normes de code

**Style Python**
- Respectez la PEP 8
- Utilisez les annotations de type (type hints)
- Incluez des docstrings pour toutes les fonctions et classes
- Gardez les fonctions ciblées et sous les 50 lignes

**Style de documentation**
- Rédigez dans un langage factuel et technique
- Évitez les adjectifs et les adverbes
- Incluez des exemples de code
- Testez tous les exemples

### 4. Tests

Testez vos modifications :
```bash
# Test basic functionality
python3 lbtas.py rate --exchange "TestService"
python3 lbtas.py view --exchange "TestService"
python3 lbtas.py report

# Test as library
python3 -c "from lbtas import LevesonRatingSystem; rs = LevesonRatingSystem(); rs.add_exchange('test'); print('OK')"
```

### 5. Messages de commit

Format : `type: brief description`

Types :
- `feat` : nouvelle fonctionnalité
- `fix` : correction de bug
- `docs` : modifications de la documentation
- `refactor` : restructuration du code
- `test` : ajouts ou modifications de tests
- `chore` : tâches de maintenance

Exemples :
```
feat: add CSV export format
fix: handle empty rating lists in report
docs: update installation instructions
```

### 6. Pull request

1. Poussez votre branche vers votre fork
2. Ouvrez une pull request vers la branche `main`
3. Référencez les tickets liés, le cas échéant
4. Décrivez les modifications apportées et leur justification
5. Attendez la relecture et la discussion sur Slack

## Code de conduite

### Règles

- Respectez tous les contributeurs
- Concentrez-vous sur le mérite technique
- Formulez des retours constructifs
- Acceptez la critique de vos contributions
- Faites primer les objectifs du projet sur les préférences personnelles

### Comportements interdits

- Attaques personnelles ou harcèlement
- Propos ou comportements discriminatoires
- Trolling ou commentaires incendiaires
- Divulgation d'informations privées d'autrui
- Conduite contraire à l'éthique ou non professionnelle

### Application

Les manquements peuvent entraîner :
1. Un avertissement
2. Une suspension temporaire du projet
3. Une exclusion définitive du projet

Signalez les manquements à : forge@ntari.org

## Licence

En contribuant, vous acceptez que vos contributions soient placées sous licence AGPL-3.0.

Toutes les contributions doivent :
- Être votre travail original ou être correctement attribuées
- Ne porter atteinte à aucun droit de tiers
- Respecter les exigences de l'AGPL-3.0

## Questions

Pour toute question sur la contribution :
1. Demandez sur Slack : https://ntari.slack.com/archives/C09N88JN2SH
2. Ouvrez un ticket sur GitHub
3. Écrivez à : forge@ntari.org

## Reconnaissance

Les contributeurs sont reconnus dans :
- L'historique des commits Git
- Les notes de version
- La documentation du projet

Types de contributions reconnus :
- Contributions de code (commits)
- Contributions de recherche (citations)
- Contributions à la documentation (crédits de documentation)
- Soutien à la communauté (remerciements)
