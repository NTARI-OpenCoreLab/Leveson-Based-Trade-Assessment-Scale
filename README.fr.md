# Leveson-Based Trade Assessment Scale (LBTAS)

> Traduction communautaire (brouillon) — politique NTARI P2-002, Diffusion multilingue mondiale. Source : README.md (original anglais, instantané du 2026-07-29). Brouillon communautaire assisté par machine, en attente de relecture par un mainteneur régional conformément à P2-002 §3.1. Les spécifications techniques de référence restent en anglais conformément au §2.2.
>
> Vous avez remarqué une erreur de traduction ? N'hésitez pas à la corriger
> vous-même : forkez le dépôt
> https://github.com/NTARI-RAND/Leveson-Based-Trade-Assessment-Scale et ouvrez
> une pull request. Les corrections de traduction sont des contributions
> précieuses, tout autant que le code.

Un système de notation pour le commerce numérique, fondé sur la méthodologie d'évaluation des logiciels aéronautiques de Nancy Leveson et doté de critères d'évaluation bidirectionnels.

## Aperçu

La Leveson-Based Trade Assessment Scale (LBTAS) met en œuvre la méthodologie d'évaluation des logiciels aéronautiques de Nancy Leveson, élaborée pour l'aérospatiale, en l'adaptant au commerce numérique et aux contextes d'évaluation économique. LBTAS fournit un cadre permettant de recueillir des données sur la qualité des transactions à l'aide d'une échelle à 6 points.

## Le problème des systèmes de notation traditionnels

Les systèmes à 5 étoiles ne produisent pas de données qui incitent les producteurs à s'améliorer. Le système à 5 étoiles a été mis au point en 1958 par le Forbes Travel Guide (anciennement Mobil Travel Guide) afin de signaler la qualité des hôtels le long des autoroutes inter-États des États-Unis. Il a été conçu comme un système de communication à sens unique destiné aux voyages routiers, et non au commerce numérique.

**Limites :**
- Les notes n'apportent qu'une valeur limitée dans les contextes de commerce électronique
- Les responsables des relations publiques font obstacle aux changements de politique
- La granularité ne parvient pas à rendre compte de la complexité des transactions
- L'évaluation unidirectionnelle ignore la responsabilité du consommateur
- L'insuffisance des données oblige à se rabattre sur les sections de commentaires

## Pourquoi l'approche Leveson ?

Le système Leveson est issu du développement de logiciels aéronautiques, où les défaillances système se traduisent par des pertes humaines ou par le gaspillage d'investissements en R&D. Cette méthodologie :

- Utilise une échelle à 6 points (de +4 à -1) assortie de définitions de catégories
- Concentre du sens dans chaque niveau de note
- Réduit la dépendance aux sections de commentaires comme source de données
- Permet une évaluation bidirectionnelle (côté producteur comme côté consommateur)
- Soutient des cycles d'amélioration fondés sur les données

## Définitions de l'échelle

### +4 **Enchantement** (*Delight*)
L'interaction anticipe l'évolution des pratiques et des préoccupations de l'utilisateur après la transaction

### +3 **Aucune conséquence négative** (*No Negative Consequences*)
Interaction conçue pour prévenir toute perte et pour dépasser les normes de qualité de base

### +2 **Satisfaction de base** (*Basic Satisfaction*)
L'interaction respecte les normes socialement acceptables et va au-delà des demandes explicitement formulées par l'utilisateur

### +1 **Promesse de base** (*Basic Promise*)
L'interaction répond à toutes les demandes explicitement formulées par l'utilisateur, sans rien de plus

### 0 **Satisfaction cynique** (*Cynical Satisfaction*)
L'interaction tient une promesse de base qui n'exige que peu ou pas de rigueur envers la satisfaction de l'utilisateur

### -1 **Aucune confiance** (*No Trust*)
L'utilisateur a subi un préjudice, a été exploité, ou a reçu un produit ou un service portant les signes d'une absence de rigueur ou d'une intention malveillante

## Évaluation bidirectionnelle

LBTAS permet une responsabilité réciproque au sein des réseaux numériques en tenant des notes pour les deux parties :

- **Producteurs** : identifie les fournisseurs
- **Consommateurs** : identifie les clients

Cette approche facilite l'autorégulation communautaire et réduit le besoin de modération centralisée.

## Lire une réputation

Les notes ne sont jamais moyennées. Une réputation, c'est le nombre de notes reçues à chaque niveau (de `-1` à `+4`), plus le total. Le total compte en lui-même : il reflète le volume de transactions et, indirectement, l'ancienneté en service. Une distribution irréprochable sur 5 000 notes constitue un signal plus fort que la même forme sur 5 notes — et calculer une moyenne effacerait cette différence en ramenant les deux au même nombre. (Ce décompte est un décompte de notes ; les chiffres précis de transactions et d'ancienneté proviennent de l'API, qui horodate chaque événement de notation.)

Un `-1` (« Aucune confiance ») n'est jamais dilué : la commande `report` fait remonter, dans une liste `harm_flagged`, chaque échange ayant reçu une ou plusieurs notes `-1`, et `list` ajoute un signalement de préjudice à tout échange comportant un `-1`.

## Fonctionnalités

- **Méthodologie** : fondée sur des cadres d'évaluation issus de l'aérospatiale
- **Évaluation bidirectionnelle** : noter les deux parties d'une transaction
- **Granularité** : échelle à 6 points assortie de définitions
- **Dépendances** : intégration à d'autres systèmes
- **Prise en charge des bases de données** : prise en charge d'une couche de persistance
- **Open source** : développement et personnalisation portés par la communauté

## Installation

```bash
# Clone the repository
git clone https://github.com/NTARI-OpenCoreLab/Leveson-Based-Trade-Assessment-Scale.git
cd Leveson-Based-Trade-Assessment-Scale

# Make executable (optional)
chmod +x lbtas.py

# Run directly
python3 lbtas.py --help
```

Aucune dépendance externe n'est requise. Le projet n'utilise que la bibliothèque standard de Python 3.

## Démarrage rapide

```python
from lbtas import LevesonRatingSystem

# Initialize the rating system
rating_system = LevesonRatingSystem()

# Add an exchange (transaction)
rating_system.add_exchange("transaction_001")

# Add ratings (categories: reliability, usability, performance, support)
rating_system.add_rating(
    exchange_name="transaction_001",
    criterion="reliability",
    rating=3  # No Negative Consequences
)

# Read the distribution (ratings are never averaged)
ratings = rating_system.view_ratings("transaction_001")
print(ratings["reliability"])
# {'distribution': {'-1': 0, '0': 0, '1': 0, '2': 0, '3': 1, '4': 0}, 'total': 1}
```

### Interface en ligne de commande

```bash
# Interactive rating
python3 lbtas.py rate --exchange "MyService"

# Programmatic rating
python3 lbtas.py add --exchange "MyService" --criterion reliability --rating 3

# View ratings
python3 lbtas.py view --exchange "MyService"

# Generate report
python3 lbtas.py report

# Export data
python3 lbtas.py export --format json --output ratings.json
```

## Stockage

LBTAS assure la persistance au moyen d'un stockage dans un fichier JSON :

```python
# Initialize with storage file
rating_system = LevesonRatingSystem(storage_file='ratings.json')

# Ratings are saved automatically to the file
rating_system.add_exchange("service_001")
rating_system.add_rating("service_001", "reliability", 3)
```

Format du fichier de stockage :
```json
{
  "service_001": {
    "reliability": [3, 4, 3],
    "usability": [2, 3],
    "performance": [4],
    "support": [3, 3, 2],
    "_metadata": {
      "created": "2024-09-04T10:30:00",
      "total_ratings": 10
    }
  }
}
```

### Catégories de notation

Catégories par défaut :
- **Fiabilité** (`reliability`) : constance et fiabilité du service
- **Utilisabilité** (`usability`) : facilité d'utilisation et expérience utilisateur
- **Performance** (`performance`) : rapidité et efficacité
- **Support** (`support`) : qualité du service client

Des catégories personnalisées peuvent être définies à l'initialisation.

## Cas d'usage

### Recherche universitaire
- Étudier comment la conception d'une échelle de notation influe sur le comportement des utilisateurs et sur les résultats de marché
- Mesurer les effets de l'évaluation bidirectionnelle sur la confiance et la coopération
- Analyser des alternatives d'évaluation fondées sur la qualité aux cadres existants

### Plateformes de commerce électronique
- Mettre en place des indicateurs de qualité pour les transactions de place de marché
- Rendre possibles des systèmes de réputation portés par la communauté
- Réduire la charge de modération grâce à l'autorégulation

### Coopératives numériques
- Faciliter la responsabilité entre pairs
- Soutenir les structures de gouvernance
- Permettre des améliorations de politique fondées sur les données

## Architecture

LBTAS est implémentée sous la forme d'un module Python unique comprenant :

1. **Classe centrale** : `LevesonRatingSystem` gère les notes et le stockage
2. **Persistance JSON** : stockage sur fichier avec sauvegarde automatique
3. **Interface CLI** : outil en ligne de commande pour un usage interactif ou programmatique
4. **Aucune dépendance externe** : n'utilise que la bibliothèque standard de Python

Le système prend en charge :
- La collecte de notes en mode interactif
- La soumission programmatique de notes
- Des catégories de notation personnalisées
- La génération de rapports et l'export de données

## Documentation

- [Documentation complète](docs/README.md)
- [Référence de l'API](docs/api.md)
- [Guide d'intégration](docs/integration.md)
- [Applications en recherche](docs/research.md)

## Contribuer

Les contributions passent par l'espace de travail Slack de NTARI :

**Rejoindre la discussion** : https://ntari.slack.com/archives/C09N88JN2SH

Veuillez consulter nos [directives de contribution](CONTRIBUTING.md) pour connaître :

- Le style de code et les normes applicables
- Les exigences en matière de tests
- Le processus de pull request
- Le code de conduite de la communauté

## Recherche et développement

Ce programme a été produit par le **Forge Laboratory du Network Theory Applied Research Institute** (devenu NTARI Research & Development) par Jodson B. Graves, à l'aide de ChatGPT-3, le 4 septembre 2024.

### À propos de NTARI Research & Development

NTARI Research & Development est le programme de développement logiciel de NTARI, consacré à la création de systèmes et de protocoles numériques qui s'appuient sur la théorie des réseaux pour renforcer les capacités de coopération à l'échelle d'Internet. Nous développons des outils, des plateformes et des cadres open source qui donnent aux communautés les moyens de bâtir leurs propres écosystèmes en ligne.

**En savoir plus et soutenir NTARI** : [https://ntari.org](https://ntari.org)

## Citation

Si vous utilisez LBTAS dans vos travaux de recherche, veuillez citer :

```bibtex
@software{lbtas2024,
  title={Leveson-Based Trade Assessment Scale},
  author={Graves, Jodson B.},
  organization={Network Theory Applied Research Institute},
  year={2024},
  url={https://github.com/NTARI-OpenCoreLab/Leveson-Based-Trade-Assessment-Scale}
}
```

## Références

- Leveson, N. G. (2011). *Engineering a Safer World: Systems Thinking Applied to Safety*. MIT Press.
- Leveson, N. G. (2020). *CAST Handbook: How to Learn More from Incidents and Accidents*. MIT.

## Licence

Ce projet est distribué sous licence GNU Affero General Public License v3.0 (AGPL-3.0) — voir le fichier [LICENSE](LICENSE) pour les détails.

La licence AGPL-3.0 exige que :
- Le code source soit mis à disposition lorsque le logiciel est utilisé via un réseau
- Les modifications soient publiées sous la même licence
- Les changements soient documentés
- L'utilisation via un réseau soit considérée comme une distribution

## Remerciements

- **Nancy Leveson** — élaboration de la méthodologie d'origine
- **NTARI Research & Development** — recherche et implémentation
- **La communauté open source** — contributions et retours

---

**Maintenu par** : [NTARI Research & Development](https://ntari.org)  
**Des questions ?** Ouvrez une issue ou écrivez-nous à info@ntari.org
