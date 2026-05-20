"""
Machine Learning Classifier - Random Forest
Niveau professionnel
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import accuracy_score, classification_report
import joblib
import os

class MLWaterQualityClassifier:
    """Classifieur Machine Learning pour la qualité d'eau"""
    
    def __init__(self):
        self.model = None
        self.is_trained = False
        self.feature_importance = None
        self.accuracy = 0
        
    def generate_training_data(self, n_samples=5000):
        """Générer des données d'entraînement réalistes"""
        np.random.seed(42)
        
        data = []
        for _ in range(n_samples):
            # Générer des valeurs aléatoires
            temp = np.random.uniform(0, 40)
            ph = np.random.uniform(0, 14)
            turb = np.random.uniform(0, 100)
            oxygen = np.random.uniform(0, 15)
            cond = np.random.uniform(0, 2000)
            
            # Règle de classification (similaire à notre logique)
            score = 0
            if oxygen < 3: score += 3
            elif oxygen < 5: score += 2
            elif oxygen < 7: score += 1
            
            if turb > 30: score += 3
            elif turb > 10: score += 2
            elif turb > 2: score += 1
            
            if ph < 5 or ph > 9: score += 2
            elif ph < 6 or ph > 8.5: score += 1
            
            if temp > 30: score += 2
            elif temp > 25: score += 1
            
            if cond > 800: score += 2
            elif cond > 400: score += 1
            
            if score <= 2: label = 0  # Potable
            elif score <= 5: label = 1  # Acceptable
            elif score <= 8: label = 2  # Polluée
            else: label = 3  # Dangereuse
            
            data.append([temp, ph, turb, oxygen, cond, label])
        
        df = pd.DataFrame(data, columns=['temperature', 'ph', 'turbidity', 'dissolved_oxygen', 'conductivity', 'label'])
        return df
    
    def train(self, n_samples=5000):
        """Entraîner le modèle Random Forest"""
        print("🤖 Entraînement du modèle Machine Learning...")
        
        # Générer données
        df = self.generate_training_data(n_samples)
        
        X = df[['temperature', 'ph', 'turbidity', 'dissolved_oxygen', 'conductivity']].values
        y = df['label'].values
        
        # Split
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Random Forest
        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42,
            n_jobs=-1
        )
        
        self.model.fit(X_train, y_train)
        
        # Évaluation
        y_pred = self.model.predict(X_test)
        self.accuracy = accuracy_score(y_test, y_pred)
        self.feature_importance = dict(zip(
            ['Température', 'pH', 'Turbidité', 'Oxygène', 'Conductivité'],
            self.model.feature_importances_
        ))
        
        self.is_trained = True
        
        print(f"✅ Modèle entraîné! Précision: {self.accuracy:.2%}")
        print("📊 Importance des features:")
        for f, imp in self.feature_importance.items():
            print(f"   {f}: {imp:.2%}")
        
        return self.accuracy
    
    def predict(self, data):
        """Prédire avec le modèle ML"""
        if not self.is_trained or self.model is None:
            raise ValueError("Modèle non entraîné")
        
        X = np.array([[data['temperature'], data['ph'], data['turbidity'], 
                       data['dissolved_oxygen'], data['conductivity']]])
        
        prediction = self.model.predict(X)[0]
        probabilities = self.model.predict_proba(X)[0]
        confidence = probabilities[prediction] * 100
        
        return int(prediction), confidence
    
    def save_model(self, path="models/ml_model.pkl"):
        """Sauvegarder le modèle"""
        if self.model:
            joblib.dump(self.model, path)
            print(f"💾 Modèle sauvegardé: {path}")
    
    def load_model(self, path="models/ml_model.pkl"):
        """Charger un modèle existant"""
        if os.path.exists(path):
            self.model = joblib.load(path)
            self.is_trained = True
            print(f"📂 Modèle chargé: {path}")
            return True
        return False