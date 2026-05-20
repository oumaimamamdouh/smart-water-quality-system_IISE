"""
Model Manager - sauvegarde et charge les modèles
"""

import pickle
import json
from pathlib import Path
from datetime import datetime
from src.config import MODELS_DIR

class ModelManager:
    """Gère la sauvegarde et le chargement des modèles"""
    
    def __init__(self):
        self.model_path = MODELS_DIR / "water_quality_model.pkl"
        self.metadata_path = MODELS_DIR / "metadata.json"
    
    def save_model(self, classifier, preprocessor):
        """
        Sauvegarder le modèle et le préprocesseur
        """
        print("💾 Sauvegarde du modèle...")
        
        # Package contenant tout
        model_package = {
            'classifier': classifier,
            'preprocessor': preprocessor,
            'saved_at': datetime.now().isoformat(),
            'version': '1.0.0'
        }
        
        # Sauvegarder avec pickle
        with open(self.model_path, 'wb') as f:
            pickle.dump(model_package, f)
        
        # Sauvegarder les métadonnées
        metadata = {
            'path': str(self.model_path),
            'saved_at': datetime.now().isoformat(),
            'is_trained': classifier.is_trained
        }
        
        with open(self.metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        print(f"✅ Modèle sauvegardé dans {self.model_path}")
        return self.model_path
    
    def load_model(self):
        """
        Charger le modèle sauvegardé
        """
        if not self.model_path.exists():
            print("⚠️  Aucun modèle trouvé")
            return None, None
        
        print("📂 Chargement du modèle...")
        
        with open(self.model_path, 'rb') as f:
            model_package = pickle.load(f)
        
        classifier = model_package['classifier']
        preprocessor = model_package['preprocessor']
        
        print(f"✅ Modèle chargé (version: {model_package.get('version', 'inconnue')})")
        
        return classifier, preprocessor