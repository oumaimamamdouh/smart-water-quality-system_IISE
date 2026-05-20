"""
Decorators - des fonctions spéciales qui ajoutent des fonctionnalités
"""

import time
import logging
from functools import wraps

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def log_execution(func):
    """
    Decorateur qui log quand une fonction commence et finit
    Exemple: @log_execution
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        print(f"🚀 Début de {func.__name__}")
        result = func(*args, **kwargs)
        print(f"✅ Fin de {func.__name__}")
        return result
    return wrapper

def timer_decorator(func):
    """
    Decorateur qui mesure le temps d'execution
    Exemple: @timer_decorator
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(f"⏱️  {func.__name__} a pris {end-start:.2f} secondes")
        return result
    return wrapper

def validate_data(expected_keys):
    """
    Decorateur qui verifie que les données contiennent les clés requises
    Exemple: @validate_data(['temperature', 'ph'])
    """
    def decorator(func):
        @wraps(func)
        def wrapper(data, *args, **kwargs):
            for key in expected_keys:
                if key not in data:
                    raise ValueError(f"Manque la clé: {key}")
            return func(data, *args, **kwargs)
        return wrapper
    return decorator