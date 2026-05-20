"""
Classifier - le cœur du projet, décide la qualité de l'eau
"""

import numpy as np
from sklearn.ensemble import RandomForestClassifier
from src.config import WATER_QUALITY_CLASSES, RANDOM_STATE
from src.utils.decorators import log_execution, timer_decorator

class WaterQualityClassifier:
    """
    Classifieur Random Forest pour la qualité de l'eau
    """
    
    def __init__(self):
        """Initialiser le modèle"""
        self.model = RandomForestClassifier(
            n_estimators=100,  # 100 arbres de décision
            max_depth=10,
            random_state=RANDOM_STATE
        )
        self.is_trained = False
    
    @log_execution
    @timer_decorator
    def train(self, X, y):
        """
        Entraîner le modèle avec des données
        X: les features (température, pH, etc.)
        y: les labels (0,1,2,3)
        """
        print(f"📚 Entraînement sur {len(X)} échantillons...")
        self.model.fit(X, y)
        self.is_trained = True
        print("✅ Modèle entraîné avec succès!")
        
        # Afficher l'importance de chaque capteur
        features_names = ['Température', 'pH', 'Turbidité', 'Oxygène', 'Conductivité']
        importances = self.model.feature_importances_
        
        print("\n📊 Importance des capteurs:")
        for name, imp in zip(features_names, importances):
            print(f"   {name}: {imp:.2%}")
        
        return {'accuracy': self.model.score(X, y)}
    
    def predict(self, X):
        """
        Prédire la qualité pour de nouvelles données
        Retourne: (classe, confiance)
        """
        if not self.is_trained:
            raise ValueError("❌ Modèle pas encore entraîné! Appelle train() d'abord")
        
        # Obtenir les probabilités
        probabilities = self.model.predict_proba(X)
        prediction = np.argmax(probabilities, axis=1)[0]
        confidence = np.max(probabilities, axis=1)[0]
        
        return prediction, confidence
    
    def get_class_name(self, class_id):
        """Retourner le nom de la classe"""
        return WATER_QUALITY_CLASSES.get(class_id, "Inconnu")