# 🌊 Smart Water Quality Classification System
**Présentation du Projet de Fin d'Études**

---

## 👥 Équipe du Projet
Ce projet a été conçu et développé avec passion par :
- **Mohamed**
- **Oumaima**
- **Salma**
- **Zineb**

---

## 🎯 Objectif du Projet
Le système **Smart Water Quality** est une application intelligente conçue pour analyser les données physico-chimiques de l'eau en temps réel et classifier sa qualité. Le système aide à prévenir les risques sanitaires en identifiant instantanément si l'eau est potable, nécessite un traitement, ou est dangereuse.

L'analyse se base sur 5 paramètres clés :
1. 🌡️ **Température** (°C)
2. 🧪 **pH** (Niveau d'acidité)
3. 💧 **Turbidité** (NTU - Clarté de l'eau)
4. 🫧 **Oxygène dissous** (mg/L)
5. ⚡ **Conductivité** (µS/cm)

---

## 🛠️ Outils & Technologies Utilisés (Stack Technique)

### 🖥️ Front-End (Interface Utilisateur)
- **HTML5 & CSS3** : Design moderne, responsive et professionnel sans framework lourd (Vanilla CSS).
- **JavaScript (ES6)** : Logique asynchrone (Fetch API) pour communiquer avec le backend sans recharger la page.
- **Architecture** : Dashboard "Single Page Application" (SPA) pour une expérience utilisateur fluide.

### ⚙️ Back-End (Serveur & Logique)
- **Python 3** : Le cœur de l'application, choisi pour sa robustesse en analyse de données.
- **FastAPI** : Framework web ultra-rapide et asynchrone utilisé pour construire l'API REST.
- **Uvicorn** : Serveur web ASGI haute performance pour exécuter FastAPI.
- **Pydantic** : Validation stricte des données entrantes (les mesures des capteurs).

### 💾 Base de Données
- **SQLite** : Base de données légère et intégrée pour stocker l'historique des analyses et générer des statistiques sur le long terme.

### 🤖 Intelligence & Logique
- **Système Expert (Rule-based)** : Algorithme principal attribuant des "scores de risque" basés sur des normes sanitaires strictes.
- **Machine Learning (Scikit-Learn, Pandas, Numpy)** : Modèles prédictifs (ex: Random Forest) intégrés pour les recherches avancées.

---

## 🔌 Architecture de l'API (Endpoints)

L'application expose une API RESTful moderne :

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| `GET` | `/` | Sert le Dashboard professionnel (Interface UI). |
| `POST` | `/predict` | Reçoit les 5 mesures, analyse la qualité, sauvegarde en BD et retourne le résultat complet (Score, Confiance, Conseils). |
| `GET` | `/history` | Récupère les dernières analyses effectuées depuis la base de données. |
| `GET` | `/stats` | Génère les statistiques globales (Confiance moyenne, nombre d'alertes). |
| `GET` | `/health` | Vérifie si le serveur et la base de données sont en ligne. |

---

## 🏗️ Structure des Classes Principales

Le code est organisé de manière modulaire et orientée objet :

1. **`SensorData` (Modèle Pydantic)**
   - Définit le schéma exact des données attendues.
   - Rejette automatiquement les valeurs impossibles (ex: un pH de 20 ou une température négative).

2. **`DatabaseManager`**
   - Gère la connexion SQLite (`water_quality.db`).
   - S'occupe de l'insertion des nouvelles analyses (`save_prediction`).
   - S'occupe de l'extraction des tendances et des statistiques (`get_statistics`).

3. **`WaterQualityService`**
   - Le "Cerveau" de l'application.
   - Contient la méthode `predict()` qui évalue chaque paramètre, calcule le score de pollution et détermine la classe finale de l'eau.

---

## 🚀 Le Cœur du Système : Comment fonctionne le processus global ?

1. **Acquisition (Front-End) :** L'utilisateur (ou les capteurs connectés) entre les 5 mesures dans le Dashboard.
2. **Validation (Pydantic) :** Les données sont envoyées à l'API via `/predict`. Pydantic vérifie instantanément que toutes les valeurs sont des nombres valides.
3. **Analyse (WaterQualityService) :** Le service compare chaque valeur aux normes internationales :
   - *Si l'oxygène est < 3 mg/L -> Pénalité sévère (+3 points de risque).*
   - *Si la turbidité est < 2 NTU -> Aucun risque (0 point).*
4. **Classification :** Le score total détermine la catégorie :
   - **🟢 Potable (Score 0-2)** : Eau sûre.
   - **🟡 Acceptable (Score 3-5)** : Traitement léger recommandé.
   - **🟠 Polluée (Score 6-8)** : Non potable sans traitement.
   - **🔴 Dangereuse (Score > 8)** : Alerte critique.
5. **Sauvegarde (DatabaseManager) :** Le résultat, accompagné de l'heure exacte, est sauvegardé dans SQLite.
6. **Réponse (Front-End) :** L'interface affiche le verdict, met à jour le graphique de confiance et rafraîchit l'historique en temps réel.
