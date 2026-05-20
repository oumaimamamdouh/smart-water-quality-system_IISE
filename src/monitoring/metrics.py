"""
Monitoring système avec Prometheus
Niveau Master - Métriques en temps réel
"""

from prometheus_client import Counter, Histogram, Gauge, generate_latest, REGISTRY, CollectorRegistry
import time
from functools import wraps
from typing import Dict
import threading

# Métriques Prometheus
PREDICTIONS_TOTAL = Counter(
    'water_quality_predictions_total',
    'Nombre total de prédictions',
    ['quality_class']
)

PREDICTION_LATENCY = Histogram(
    'water_quality_prediction_latency_seconds',
    'Latence des prédictions en secondes',
    buckets=[0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5]
)

MODEL_CONFIDENCE = Gauge(
    'water_quality_model_confidence',
    'Confiance moyenne du modèle (%)'
)

ACTIVE_REQUESTS = Gauge(
    'water_quality_active_requests',
    'Nombre de requêtes actives'
)

API_REQUESTS = Counter(
    'water_quality_api_requests_total',
    'Nombre total de requêtes API',
    ['endpoint', 'method', 'status']
)

ERROR_COUNTER = Counter(
    'water_quality_errors_total',
    'Nombre total d\'erreurs',
    ['error_type']
)

DATA_QUALITY = Gauge(
    'water_quality_data_quality',
    'Qualité des données entrantes (0-100)'
)

class MetricsMiddleware:
    """Middleware pour collecter les métriques"""
    
    def __init__(self):
        self.request_count = 0
    
    async def __call__(self, request, call_next):
        ACTIVE_REQUESTS.inc()
        start_time = time.time()
        
        try:
            response = await call_next(request)
            latency = time.time() - start_time
            
            API_REQUESTS.labels(
                endpoint=request.url.path,
                method=request.method,
                status=str(response.status_code)
            ).inc()
            
            PREDICTION_LATENCY.observe(latency)
            return response
            
        except Exception as e:
            ERROR_COUNTER.labels(error_type=type(e).__name__).inc()
            raise
        finally:
            ACTIVE_REQUESTS.dec()

def monitor_prediction(func):
    """Décorateur pour monitorer les prédictions"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        latency = time.time() - start
        
        PREDICTION_LATENCY.observe(latency)
        
        if 'prediction' in result:
            class_name = result['prediction']['class_name']
            PREDICTIONS_TOTAL.labels(quality_class=class_name).inc()
            MODEL_CONFIDENCE.set(result['prediction']['confidence'])
        
        return result
    return wrapper

def get_metrics():
    """Récupérer toutes les métriques au format Prometheus"""
    return generate_latest(REGISTRY)

def get_metrics_summary() -> Dict:
    """Résumé des métriques pour l'API"""
    try:
        # Collecter les valeurs des métriques
        predictions_total = 0
        for metric in REGISTRY.collect():
            if metric.name == 'water_quality_predictions_total':
                for sample in metric.samples:
                    if sample.name == 'water_quality_predictions_total_total':
                        predictions_total += int(sample.value)
        
        model_confidence = 0
        for metric in REGISTRY.collect():
            if metric.name == 'water_quality_model_confidence':
                for sample in metric.samples:
                    if sample.name == 'water_quality_model_confidence':
                        model_confidence = float(sample.value)
        
        active_requests = 0
        for metric in REGISTRY.collect():
            if metric.name == 'water_quality_active_requests':
                for sample in metric.samples:
                    if sample.name == 'water_quality_active_requests':
                        active_requests = int(sample.value)
        
        error_count = 0
        for metric in REGISTRY.collect():
            if metric.name == 'water_quality_errors_total':
                for sample in metric.samples:
                    if sample.name == 'water_quality_errors_total_total':
                        error_count += int(sample.value)
        
        return {
            'total_predictions': predictions_total,
            'model_confidence': round(model_confidence, 2),
            'active_requests': active_requests,
            'error_count': error_count
        }
    except Exception as e:
        return {
            'total_predictions': 0,
            'model_confidence': 0,
            'active_requests': 0,
            'error_count': 0,
            'error': str(e)
        }