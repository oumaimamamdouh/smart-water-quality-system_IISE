"""
API FastAPI pour le système
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Dict
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.services.prediction_service import PredictionService

# Créer l'application
app = FastAPI(
    title="Smart Water Quality API",
    description="API pour classifier la qualité de l'eau",
    version="1.0.0"
)

# Initialiser le service
service = PredictionService()

# Modèle de données pour la requête
class SensorData(BaseModel):
    temperature: float = Field(..., ge=0, le=40, description="Température en °C")
    ph: float = Field(..., ge=0, le=14, description="pH de l'eau")
    turbidity: float = Field(..., ge=0, le=100, description="Turbidité en NTU")
    dissolved_oxygen: float = Field(..., ge=0, le=15, description="Oxygène dissous mg/L")
    conductivity: float = Field(..., ge=0, le=2000, description="Conductivité µS/cm")
    
    class Config:
        schema_extra = {
            "example": {
                "temperature": 22.5,
                "ph": 7.2,
                "turbidity": 3.5,
                "dissolved_oxygen": 7.8,
                "conductivity": 450
            }
        }

# Endpoints
@app.get("/")
def root():
    return {"message": "Smart Water Quality API", "status": "running"}

@app.get("/status")
def get_status():
    return service.get_status()

@app.post("/train")
def train_model(n_samples: int = 1000):
    """Entraîner le modèle"""
    try:
        metrics = service.train_with_simulated_data(n_samples)
        return {"status": "success", "metrics": metrics}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/predict")
def predict(data: SensorData):
    """Prédire la qualité d'eau"""
    if not service.classifier.is_trained:
        raise HTTPException(status_code=400, detail="Model not trained yet. Call /train first")
    
    try:
        result = service.predict(data.dict())
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/classes")
def get_classes():
    """Obtenir les classes disponibles"""
    from src.config import WATER_QUALITY_CLASSES
    return WATER_QUALITY_CLASSES