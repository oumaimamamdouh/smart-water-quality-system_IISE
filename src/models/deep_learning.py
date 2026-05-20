"""
Deep Learning Model - LSTM pour la qualité d'eau
Niveau Master - TensorFlow/Keras
"""

import numpy as np
from sklearn.preprocessing import MinMaxScaler
import warnings
warnings.filterwarnings('ignore')

try:
    from tensorflow.keras.models import Sequential
    from tensorflow.keras.layers import LSTM, Dense, Dropout, Input
    from tensorflow.keras.callbacks import EarlyStopping
    TF_AVAILABLE = True
    print("✅ TensorFlow chargé avec succès")
except ImportError:
    TF_AVAILABLE = False
    print("⚠️ TensorFlow non disponible")

class WaterQualityLSTM:
    """Modèle LSTM avancé pour prédiction de qualité d'eau"""
    
    def __init__(self, sequence_length=10):
        self.sequence_length = sequence_length
        self.model = None
        self.scaler = MinMaxScaler()
        self.is_trained = False
        self.history = None
        
    def create_sequences(self, data, target):
        """Créer des séquences temporelles"""
        X, y = [], []
        for i in range(len(data) - self.sequence_length):
            X.append(data[i:i + self.sequence_length])
            y.append(target[i + self.sequence_length])
        return np.array(X), np.array(y)
    
    def build_model(self, input_shape):
        """Construire l'architecture LSTM"""
        if not TF_AVAILABLE:
            return None
            
        model = Sequential([
            Input(shape=input_shape),
            LSTM(128, return_sequences=True),
            Dropout(0.3),
            LSTM(64, return_sequences=False),
            Dropout(0.3),
            Dense(32, activation='relu'),
            Dense(16, activation='relu'),
            Dense(4, activation='softmax')
        ])
        
        model.compile(
            optimizer='adam',
            loss='sparse_categorical_crossentropy',
            metrics=['accuracy']
        )
        
        print(f"📊 Architecture LSTM: {model.summary()}")
        return model
    
    def train(self, X, y, epochs=100, validation_split=0.2):
        """Entraîner le modèle LSTM"""
        if not TF_AVAILABLE:
            print("❌ TensorFlow non disponible")
            return None
        
        print(f"📚 Entraînement LSTM sur {len(X)} échantillons...")
        
        # Normaliser
        X_scaled = self.scaler.fit_transform(X)
        
        # Créer séquences
        X_seq, y_seq = self.create_sequences(X_scaled, y)
        print(f"📊 Séquences créées: {X_seq.shape}")
        
        # Build model
        self.model = self.build_model((self.sequence_length, X.shape[1]))
        
        # Early stopping
        early_stop = EarlyStopping(
            monitor='val_loss',
            patience=10,
            restore_best_weights=True,
            verbose=1
        )
        
        # Entraîner
        self.history = self.model.fit(
            X_seq, y_seq,
            epochs=epochs,
            batch_size=32,
            validation_split=validation_split,
            callbacks=[early_stop],
            verbose=1
        )
        
        self.is_trained = True
        print(f"✅ Modèle LSTM entraîné! Accuracy finale: {self.history.history['accuracy'][-1]:.4f}")
        
        return self.history.history
    
    def predict(self, X):
        """Prédire avec LSTM"""
        if not self.is_trained or self.model is None:
            raise ValueError("Modèle non entraîné")
        
        X_scaled = self.scaler.transform(X)
        
        # Prendre la dernière séquence
        if len(X_scaled) >= self.sequence_length:
            X_seq = X_scaled[-self.sequence_length:].reshape(1, self.sequence_length, -1)
        else:
            raise ValueError(f"Besoin d'au moins {self.sequence_length} échantillons")
        
        predictions = self.model.predict(X_seq, verbose=0)
        class_id = np.argmax(predictions[0])
        confidence = np.max(predictions[0])
        
        return class_id, confidence
    
    def get_feature_importance(self):
        """Obtenir l'importance des features (méthode approximative)"""
        if not self.is_trained:
            return None
        
        # Pour LSTM, on peut regarder les poids des premières couches
        weights = self.model.layers[0].get_weights()[0]
        importance = np.mean(np.abs(weights), axis=(0, 1))
        
        features = ['Température', 'pH', 'Turbidité', 'Oxygène', 'Conductivité']
        return dict(zip(features, importance))