"""
Preprocessor - nettoie et prépare les données
"""

import numpy as np
from src.config import SENSOR_RANGES
from src.utils.decorators import log_execution, validate_data

class DataPreprocessor:
    """Classe pour nettoyer les données des capteurs"""
    
    def __init__(self):
        self.feature_columns = ['temperature', 'ph', 'turbidity', 
                                'dissolved_oxygen', 'conductivity']
    
    @log_execution
    @validate_data(['temperature', 'ph', 'turbidity', 'dissolved_oxygen', 'conductivity'])
    def validate_sensor_data(self, data):
        """
        Vérifier si les valeurs des capteurs sont dans les limites normales
        """
        for sensor, value in data.items():
            if sensor in SENSOR_RANGES:
                min_val, max_val = SENSOR_RANGES[sensor]
                if value < min_val or value > max_val:
                    raise ValueError(f"{sensor} = {value} hors limites [{min_val}, {max_val}]")
        return True
    
    def extract_features(self, data):
        """
        Convertir le dictionnaire en tableau numpy pour le modèle
        """
        features = np.array([[
            data['temperature'],
            data['ph'],
            data['turbidity'],
            data['dissolved_oxygen'],
            data['conductivity']
        ]])
        return features