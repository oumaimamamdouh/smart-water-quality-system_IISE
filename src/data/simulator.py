"""
Simulateur de capteurs - génère des données d'eau réalistes
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from src.config import SENSOR_RANGES, RANDOM_STATE
from src.utils.decorators import log_execution

class WaterSensorSimulator:
    """Simule des capteurs IoT dans l'eau"""
    
    def __init__(self):
        np.random.seed(RANDOM_STATE)
    
    @log_execution
    def generate_single_reading(self, quality_class=None):
        """
        Génère une lecture de capteur
        quality_class: 0=Potable, 1=Acceptable, 2=Polluée, 3=Dangereuse
        """
        if quality_class is None:
            quality_class = np.random.randint(0, 4)
        
        # Valeurs normales pour chaque type d'eau
        normal_values = {
            0: {  # Potable - eau propre
                'temperature': 15, 'ph': 7.0, 'turbidity': 1,
                'dissolved_oxygen': 8, 'conductivity': 300
            },
            1: {  # Acceptable - eau moyenne
                'temperature': 20, 'ph': 7.5, 'turbidity': 5,
                'dissolved_oxygen': 6, 'conductivity': 500
            },
            2: {  # Polluée - eau sale
                'temperature': 28, 'ph': 8.5, 'turbidity': 20,
                'dissolved_oxygen': 3, 'conductivity': 1000
            },
            3: {  # Dangereuse - eau très polluée
                'temperature': 35, 'ph': 9.5, 'turbidity': 50,
                'dissolved_oxygen': 1, 'conductivity': 1800
            }
        }
        
        # Générer avec un peu de bruit (10% de variation)
        reading = {}
        values = normal_values[quality_class]
        
        for sensor, base_value in values.items():
            # Ajouter du bruit aléatoire
            noise = np.random.normal(0, base_value * 0.1)
            value = base_value + noise
            
            # Garder dans les limites
            min_val, max_val = SENSOR_RANGES[sensor]
            reading[sensor] = max(min_val, min(max_val, value))
        
        return reading
    
    def generate_dataset(self, n_samples=1000):
        """
        Génère un dataset complet pour l'entraînement
        """
        print(f"📊 Génération de {n_samples} échantillons...")
        
        data = []
        samples_per_class = n_samples // 4
        
        for class_id in range(4):
            for _ in range(samples_per_class):
                reading = self.generate_single_reading(class_id)
                reading['quality_label'] = class_id
                data.append(reading)
        
        df = pd.DataFrame(data)
        print(f"✅ Dataset généré: {len(df)} lignes, {len(df.columns)} colonnes")
        
        return df