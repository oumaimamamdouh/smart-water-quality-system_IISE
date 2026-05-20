"""
Service de prédiction pour la qualité de l'eau
Gère les prédictions et la validation des données
"""
import numpy as np
import pandas as pd
from typing import Dict, Any, Optional
import logging
from datetime import datetime

from src.models.preprocessor import DataPreprocessor
from src.services.model_manager import ModelManager
from src.utils.decorators import log_execution_time

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PredictionService:
    """Service pour gérer les prédictions de qualité d'eau"""
    
    def __init__(self):
        """Initialiser le service de prédiction"""
        self.model_manager = ModelManager()
        self.preprocessor = DataPreprocessor()
        self.model = None
        self.scaler = None
        self.is_ready = False
        self._load_model()
    
    def _load_model(self):
        """Charger le modèle sauvegardé"""
        try:
            model_data = self.model_manager.load_model()
            if model_data:
                self.model = model_data['model']
                self.scaler = model_data['scaler']
                self.is_ready = True
                logger.info("✅ Modèle chargé avec succès")
            else:
                logger.warning("⚠️ Aucun modèle trouvé")
                self.is_ready = False
        except Exception as e:
            logger.error(f"❌ Erreur lors du chargement du modèle: {e}")
            self.is_ready = False
    
    @log_execution_time
    def validate_sensor_data(self, data: Dict[str, float]) -> tuple[bool, Optional[str]]:
        """
        Valider les données des capteurs
        
        Args:
            data: Dictionnaire contenant les mesures des capteurs
            
        Returns:
            (is_valid, error_message)
        """
        try:
            # Vérifier que toutes les clés nécessaires sont présentes
            required_keys = ['temperature', 'ph', 'turbidity', 'dissolved_oxygen', 'conductivity']
            
            for key in required_keys:
                if key not in data:
                    return False, f"Champ manquant: {key}"
            
            # Vérifier les plages de valeurs
            validations = {
                'temperature': (0, 40, "Température doit être entre 0 et 40°C"),
                'ph': (0, 14, "pH doit être entre 0 et 14"),
                'turbidity': (0, 100, "Turbidité doit être entre 0 et 100 NTU"),
                'dissolved_oxygen': (0, 15, "Oxygène dissous doit être entre 0 et 15 mg/L"),
                'conductivity': (0, 2000, "Conductivité doit être entre 0 et 2000 µS/cm")
            }
            
            for key, (min_val, max_val, error_msg) in validations.items():
                value = data[key]
                if not isinstance(value, (int, float)):
                    return False, f"{key} doit être un nombre"
                if value < min_val or value > max_val:
                    return False, error_msg
            
            return True, None
            
        except Exception as e:
            return False, f"Erreur de validation: {str(e)}"
    
    @log_execution_time
    def predict(self, sensor_data: Dict[str, float]) -> Dict[str, Any]:
        """
        Prédire la qualité de l'eau à partir des données des capteurs
        
        Args:
            sensor_data: Dictionnaire avec les mesures
            
        Returns:
            Dictionnaire contenant la prédiction et les détails
        """
        # Valider les données
        is_valid, error_msg = self.validate_sensor_data(sensor_data)
        if not is_valid:
            return {
                'success': False,
                'error': error_msg,
                'prediction': None,
                'confidence': None,
                'class_label': None
            }
        
        # Vérifier si le modèle est prêt
        if not self.is_ready or self.model is None:
            return {
                'success': False,
                'error': "Modèle non disponible. Veuillez entraîner le modèle d'abord.",
                'prediction': None,
                'confidence': None,
                'class_label': None
            }
        
        try:
            # Convertir en DataFrame
            df = pd.DataFrame([sensor_data])
            
            # Prétraiter les données
            features = self.preprocessor.preprocess(df)
            
            # Standardiser les données
            if self.scaler:
                features_scaled = self.scaler.transform(features)
            else:
                features_scaled = features
            
            # Faire la prédiction
            prediction = self.model.predict(features_scaled)[0]
            
            # Obtenir les probabilités
            probabilities = self.model.predict_proba(features_scaled)[0]
            confidence = float(np.max(probabilities) * 100)
            
            # Mapping des classes
            class_mapping = {
                0: "Excellente",
                1: "Bonne",
                2: "Moyenne",
                3: "Mauvaise"
            }
            
            class_label = class_mapping.get(prediction, "Inconnue")
            
            # Détails supplémentaires
            details = {
                'temperature': sensor_data['temperature'],
                'ph': sensor_data['ph'],
                'turbidity': sensor_data['turbidity'],
                'dissolved_oxygen': sensor_data['dissolved_oxygen'],
                'conductivity': sensor_data['conductivity'],
                'probabilities': {
                    'Excellente': float(probabilities[0] * 100),
                    'Bonne': float(probabilities[1] * 100),
                    'Moyenne': float(probabilities[2] * 100),
                    'Mauvaise': float(probabilities[3] * 100)
                }
            }
            
            return {
                'success': True,
                'prediction': int(prediction),
                'confidence': confidence,
                'class_label': class_label,
                'details': details,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de la prédiction: {e}")
            return {
                'success': False,
                'error': f"Erreur de prédiction: {str(e)}",
                'prediction': None,
                'confidence': None,
                'class_label': None
            }
    
    @log_execution_time
    def predict_batch(self, batch_data: list) -> list:
        """
        Prédire pour plusieurs échantillons
        
        Args:
            batch_data: Liste de dictionnaires de données capteurs
            
        Returns:
            Liste des résultats de prédiction
        """
        results = []
        for data in batch_data:
            result = self.predict(data)
            results.append(result)
        return results
    
    def get_model_status(self) -> Dict[str, Any]:
        """
        Obtenir le statut du modèle
        
        Returns:
            Dictionnaire avec le statut du modèle
        """
        return {
            'is_ready': self.is_ready,
            'model_loaded': self.model is not None,
            'scaler_loaded': self.scaler is not None,
            'model_info': self.model_manager.get_model_info() if self.is_ready else None
        }
    
    def get_class_info(self) -> Dict[str, Any]:
        """
        Obtenir les informations sur les classes
        
        Returns:
            Dictionnaire avec les classes disponibles
        """
        classes = {
            0: {
                'name': 'Excellente',
                'description': 'Eau de très bonne qualité, potable sans traitement',
                'color': '#00FF00',
                'recommendation': 'Parfaite pour consommation'
            },
            1: {
                'name': 'Bonne',
                'description': 'Eau de bonne qualité, potable après filtration simple',
                'color': '#90EE90',
                'recommendation': 'Potable avec filtration basique'
            },
            2: {
                'name': 'Moyenne',
                'description': 'Qualité moyenne, nécessite traitement',
                'color': '#FFFF00',
                'recommendation': 'Traitement recommandé avant consommation'
            },
            3: {
                'name': 'Mauvaise',
                'description': 'Eau polluée, non potable',
                'color': '#FF0000',
                'recommendation': 'Ne pas consommer, traitement nécessaire'
            }
        }
        return classes


# Instance singleton pour toute l'application
prediction_service = PredictionService()