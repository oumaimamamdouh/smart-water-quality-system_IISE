"""
Base de données SQLite pour historique
Niveau Master - Stockage et analyse
"""

import sqlite3
import json
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from contextlib import contextmanager

class DatabaseManager:
    """Gestionnaire de base de données"""
    
    def __init__(self, db_path="water_quality.db"):
        self.db_path = db_path
        self.init_database()
    
    @contextmanager
    def get_connection(self):
        """Context manager pour les connexions DB"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()
    
    def init_database(self):
        """Initialiser toutes les tables"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Table des prédictions
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS predictions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME,
                    temperature REAL,
                    ph REAL,
                    turbidity REAL,
                    dissolved_oxygen REAL,
                    conductivity REAL,
                    predicted_class INTEGER,
                    class_name TEXT,
                    confidence REAL,
                    score INTEGER,
                    analysis TEXT,
                    model_version TEXT
                )
            ''')
            
            # Table des modèles
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS models (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    version TEXT,
                    model_type TEXT,
                    trained_at DATETIME,
                    accuracy REAL,
                    loss REAL,
                    model_path TEXT
                )
            ''')
            
            # Table des alertes
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME,
                    alert_type TEXT,
                    severity TEXT,
                    message TEXT,
                    resolved BOOLEAN DEFAULT 0,
                    resolved_at DATETIME
                )
            ''')
            
            # Index pour performance
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON predictions(timestamp)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_class ON predictions(predicted_class)')
            
            conn.commit()
    
    def save_prediction(self, data: Dict, prediction: Dict, model_version: str = "1.0.0"):
        """Sauvegarder une prédiction"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO predictions (
                    timestamp, temperature, ph, turbidity, 
                    dissolved_oxygen, conductivity, predicted_class, 
                    class_name, confidence, score, analysis, model_version
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                datetime.now().isoformat(),
                data['temperature'],
                data['ph'],
                data['turbidity'],
                data['dissolved_oxygen'],
                data['conductivity'],
                prediction['class_id'],
                prediction['class_name'],
                prediction['confidence'],
                prediction['score'],
                json.dumps(prediction['analysis']),
                model_version
            ))
            conn.commit()
    
    def get_statistics(self) -> Dict:
        """Statistiques avancées"""
        with self.get_connection() as conn:
            # Statistiques générales
            df = pd.read_sql_query("""
                SELECT 
                    COUNT(*) as total,
                    AVG(confidence) as avg_confidence,
                    MIN(confidence) as min_confidence,
                    MAX(confidence) as max_confidence,
                    AVG(score) as avg_score,
                    COUNT(DISTINCT date(timestamp)) as days_active
                FROM predictions
            """, conn)
            
            # Par classe
            df_class = pd.read_sql_query("""
                SELECT 
                    class_name,
                    COUNT(*) as count,
                    AVG(confidence) as avg_confidence
                FROM predictions
                GROUP BY class_name
            """, conn)
            
            # Tendances 7 jours
            df_trend = pd.read_sql_query("""
                SELECT 
                    date(timestamp) as date,
                    COUNT(*) as count,
                    AVG(score) as avg_score
                FROM predictions
                WHERE timestamp > datetime('now', '-7 days')
                GROUP BY date(timestamp)
                ORDER BY date DESC
            """, conn)
            
            return {
                'general': df.iloc[0].to_dict() if not df.empty else {},
                'by_class': df_class.to_dict('records') if not df_class.empty else [],
                'trends': df_trend.to_dict('records') if not df_trend.empty else []
            }
    
    def check_anomalies(self, data: Dict) -> tuple:
        """Détecter les anomalies (z-score > 3) en utilisant Pandas pour le calcul"""
        with self.get_connection() as conn:
            anomalies = []
            
            # Récupérer les données historiques des 30 derniers jours
            try:
                query = """
                    SELECT temperature, ph, turbidity, dissolved_oxygen, conductivity
                    FROM predictions
                    WHERE timestamp > datetime('now', '-30 days')
                """
                df_history = pd.read_sql_query(query, conn)
                
                if not df_history.empty and len(df_history) > 1:
                    for sensor in ['temperature', 'ph', 'turbidity', 'dissolved_oxygen', 'conductivity']:
                        mean = df_history[sensor].mean()
                        std = df_history[sensor].std()
                        
                        if std > 0:
                            z_score = abs(data[sensor] - mean) / std
                            if z_score > 3:
                                anomalies.append({
                                    'sensor': sensor,
                                    'value': data[sensor],
                                    'z_score': z_score,
                                    'mean': mean
                                })
            except Exception as e:
                print(f"⚠️ Erreur lors de la détection d'anomalies: {e}")
            
            return len(anomalies) > 0, anomalies
    
    def get_history(self, limit: int = 50) -> List[Dict]:
        """Récupérer l'historique des prédictions"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM predictions 
                ORDER BY timestamp DESC 
                LIMIT ?
            ''', (limit,))
            
            return [dict(row) for row in cursor.fetchall()]
    
    def create_alert(self, alert_type: str, severity: str, message: str):
        """Créer une alerte"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO alerts (timestamp, alert_type, severity, message)
                VALUES (?, ?, ?, ?)
            ''', (datetime.now().isoformat(), alert_type, severity, message))
            conn.commit()