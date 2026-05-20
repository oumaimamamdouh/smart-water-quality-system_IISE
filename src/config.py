"""
Configuration module - hadi hiya les paramètres de base dial projet
"""

import os
from pathlib import Path

# Chemin racine (où se trouve le projet)
BASE_DIR = Path(__file__).parent.parent

# Les dossiers importants
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
PREDICTIONS_DIR = DATA_DIR / "predictions"
MODELS_DIR = BASE_DIR / "models"
LOGS_DIR = BASE_DIR / "logs"

# Créer les dossiers s'ils n'existent pas
for dir_path in [RAW_DATA_DIR, PROCESSED_DATA_DIR, PREDICTIONS_DIR, MODELS_DIR, LOGS_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)

# Les classes de qualité d'eau
WATER_QUALITY_CLASSES = {
    0: "Potable",      # Salive tayra - bonne à boire
    1: "Acceptable",   # Moyenne - acceptable pour industrie
    2: "Polluée",      # Machi mzyana - contamination
    3: "Dangereuse"    # Khatira - risque élevé
}

# Les limites normales des capteurs
SENSOR_RANGES = {
    'temperature': (0, 40),      # 0-40 degrés Celsius
    'ph': (0, 14),               # 0-14 pH
    'turbidity': (0, 100),       # 0-100 NTU
    'dissolved_oxygen': (0, 15), # 0-15 mg/L
    'conductivity': (0, 2000)    # 0-2000 µS/cm
}

# Configuration API
API_HOST = "127.0.0.1"
API_PORT = 8000

# Random seed pour reproduire les résultats
RANDOM_STATE = 42