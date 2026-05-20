# Smart Water Quality System

Un système professionnel FastAPI de classification de la qualité de l'eau avec import CSV/Excel, génération de rapports PDF, tableau de bord et statistiques avancées.

## Objectif général

Proposer une solution académique et professionnelle pour analyser la qualité de l'eau, enregistrer des résultats, générer des rapports et visualiser des tendances.

## Fonctionnalités

- API FastAPI avec persistance SQLite
- Chargement de données CSV/XLSX
- Analyse par lot et prédiction de la qualité de l'eau
- Export PDF des rapports
- Dashboard interactif
- Page de statistiques avancées

## Technologies utilisées

- Python 3.12+
- FastAPI
- Uvicorn
- Pydantic
- Pandas
- OpenPyXL
- ReportLab
- Chart.js

## Structure du projet

- `app.py` - point d'entrée principal de l'application
- `requirements.txt` - dépendances Python
- `static/` - interface utilisateur statique
- `src/` - modules Python réutilisables
- `sample_tests.csv` - exemple de jeu de données
- `_archive_old_files/` - fichiers d'archives et doublons

## Installation

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Exécution

```powershell
python app.py
```

## Utilisation

- Accéder au dashboard : `http://127.0.0.1:8000/dashboard`
- Accéder aux statistiques : `http://127.0.0.1:8000/statistics`
- Documentation API : `http://127.0.0.1:8000/docs`

### Import Excel/CSV

Utilisez la page de dashboard pour charger un fichier `.csv` ou `.xlsx`.
Le fichier doit contenir les colonnes :

- `temperature`
- `ph`
- `turbidity`
- `dissolved_oxygen`
- `conductivity`

## Export CSV

Téléchargez toutes les analyses via :

- `http://127.0.0.1:8000/api/reports/csv`

## Rapport PDF

Téléchargez le rapport PDF via :

- `http://127.0.0.1:8000/api/reports/pdf`

## Statistiques avancées

Ouvrez : `http://127.0.0.1:8000/statistics`

## Endpoints API

- `GET /` : page de démarrage
- `GET /dashboard` : interface principal
- `GET /statistics` : page de statistiques
- `GET /docs` : documentation Swagger
- `POST /api/upload-tests` : import de fichiers CSV/XLSX
- `GET /api/reports/csv` : export CSV global
- `GET /api/reports/pdf` : export PDF
- `GET /api/statistics` : données statistiques

## Conclusion

Ce projet est prêt pour une publication académique et GitHub, avec une architecture claire, une interface web moderne et des fonctionnalités d'analyse et de reporting.

## Améliorations futures

- Authentification et contrôle d'accès
- Intégration de capteurs réels
- Tests automatisés et CI/CD
- Explications de modèle et suivi des données

