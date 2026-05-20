"""
Main program - Interface en ligne de commande
"""

import sys
import os

# Ajouter src au path
sys.path.insert(0, os.path.dirname(__file__))

from src.services.prediction_service import PredictionService

def print_banner():
    """Afficher la bannière du programme"""
    print("""
    ╔════════════════════════════════════════════════════════╗
    ║     🌊 SMART WATER QUALITY CLASSIFICATION SYSTEM 🌊    ║
    ║                   Version Académique                    ║
    ╚════════════════════════════════════════════════════════╝
    """)

def print_menu():
    """Afficher le menu principal"""
    print("\n" + "="*50)
    print("📋 MENU PRINCIPAL")
    print("="*50)
    print("1. 🚀 Entraîner le modèle (données simulées)")
    print("2. 🔮 Prédire la qualité d'eau")
    print("3. ℹ️  État du système")
    print("4. 📊 Exemple de prédictions")
    print("5. 🚪 Quitter")
    print("="*50)

def predict_examples(service):
    """Faire des prédictions d'exemple"""
    print("\n" + "="*50)
    print("💧 EXEMPLES DE PRÉDICTIONS")
    print("="*50)
    
    # Exemple 1: Eau potable
    eau_potable = {
        'temperature': 15.5,
        'ph': 7.1,
        'turbidity': 1.2,
        'dissolved_oxygen': 8.3,
        'conductivity': 290
    }
    
    # Exemple 2: Eau polluée
    eau_polluee = {
        'temperature': 29.5,
        'ph': 8.7,
        'turbidity': 22.5,
        'dissolved_oxygen': 2.8,
        'conductivity': 1100
    }
    
    # Exemple 3: Eau dangereuse
    eau_dangereuse = {
        'temperature': 36.8,
        'ph': 9.9,
        'turbidity': 58.3,
        'dissolved_oxygen': 0.6,
        'conductivity': 1880
    }
    
    examples = [
        ("💧 Eau de source (propre)", eau_potable),
        ("⚠️  Eau de rivière polluée", eau_polluee),
        ("🔴 Eau industrielle dangereuse", eau_dangereuse)
    ]
    
    for name, data in examples:
        print(f"\n📊 {name}:")
        print(f"   Température: {data['temperature']}°C")
        print(f"   pH: {data['ph']}")
        print(f"   Turbidité: {data['turbidity']} NTU")
        print(f"   Oxygène: {data['dissolved_oxygen']} mg/L")
        print(f"   Conductivité: {data['conductivity']} µS/cm")
        
        try:
            result = service.predict(data)
            pred = result['prediction']
            print(f"\n   🎯 RÉSULTAT: {pred['class_name']}")
            print(f"   📊 Confiance: {pred['confidence']}%")
            print(f"   {pred['risk_level']}")
        except Exception as e:
            print(f"   ❌ Erreur: {e}")
        print("-"*40)

def main():
    """Fonction principale"""
    print_banner()
    
    # Initialiser le service
    service = PredictionService()
    
    while True:
        print_menu()
        choice = input("\n👉 Votre choix (1-5): ").strip()
        
        if choice == '1':
            print("\n" + "="*50)
            print("🚀 ENTRAÎNEMENT DU MODÈLE")
            print("="*50)
            
            n_samples = input("Nombre d'échantillons? (défaut: 1000): ").strip()
            n_samples = int(n_samples) if n_samples else 1000
            
            try:
                metrics = service.train_with_simulated_data(n_samples)
                print("\n✨ Modèle entraîné avec succès!")
            except Exception as e:
                print(f"\n❌ Erreur: {e}")
        
        elif choice == '2':
            if not service.classifier.is_trained:
                print("\n⚠️  Le modèle n'est pas encore entraîné!")
                print("   Choisissez l'option 1 d'abord pour entraîner le modèle.")
                input("\nAppuyez sur Entrée pour continuer...")
                continue
            
            print("\n" + "="*50)
            print("🔮 PRÉDICTION DE QUALITÉ D'EAU")
            print("="*50)
            
            print("\nEntrez les mesures des capteurs:")
            
            try:
                temp = float(input("🌡️  Température (°C) [0-40]: "))
                ph = float(input("🧪 pH [0-14]: "))
                turb = float(input("💧 Turbidité (NTU) [0-100]: "))
                oxygen = float(input("🫧 Oxygène dissous (mg/L) [0-15]: "))
                cond = float(input("⚡ Conductivité (µS/cm) [0-2000]: "))
                
                sensor_data = {
                    'temperature': temp,
                    'ph': ph,
                    'turbidity': turb,
                    'dissolved_oxygen': oxygen,
                    'conductivity': cond
                }
                
                result = service.predict(sensor_data)
                
                print("\n" + "="*50)
                print("📊 RÉSULTAT DE LA PRÉDICTION")
                print("="*50)
                print(f"\n🎯 Qualité: {result['prediction']['class_name']}")
                print(f"📈 Confiance: {result['prediction']['confidence']}%")
                print(f"\n{result['prediction']['risk_level']}")
                
            except ValueError as e:
                print(f"\n❌ Erreur: Valeur invalide - {e}")
            except Exception as e:
                print(f"\n❌ Erreur: {e}")
            
            input("\nAppuyez sur Entrée pour continuer...")
        
        elif choice == '3':
            print("\n" + "="*50)
            print("ℹ️  ÉTAT DU SYSTÈME")
            print("="*50)
            
            status = service.get_status()
            print(f"\n📊 Modèle entraîné: {'✅ Oui' if status['model_trained'] else '❌ Non'}")
            print(f"🔧 Service: {status['status']}")
            
            if status['model_trained']:
                print("\n📋 Classes disponibles:")
                from src.config import WATER_QUALITY_CLASSES
                for class_id, name in WATER_QUALITY_CLASSES.items():
                    print(f"   {class_id}: {name}")
            
            input("\nAppuyez sur Entrée pour continuer...")
        
        elif choice == '4':
            if not service.classifier.is_trained:
                print("\n⚠️  Veuillez d'abord entraîner le modèle (option 1)")
                input("\nAppuyez sur Entr"+"ée pour continuer...")
                continue
            
            predict_examples(service)
            input("\nAppuyez sur Entrée pour continuer...")
        
        elif choice == '5':
            print("\n👋 Au revoir! Merci d'avoir utilisé Smart Water Quality System!\n")
            break
        
        else:
            print("\n❌ Choix invalide! Choisissez 1-5")
            input("\nAppuyez sur Entrée pour continuer...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Au revoir!\n")
    except Exception as e:
        print(f"\n❌ Erreur inattendue: {e}")