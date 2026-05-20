"""
Système d'alertes - Email + Notifications
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import json
import os

class AlertSystem:
    """Système d'alertes pour qualités dangereuses"""
    
    def __init__(self, alert_file="alerts.json"):
        self.alert_file = alert_file
        self.alerts = self.load_alerts()
        self.email_enabled = False  # Configurer avec vos identifiants
    
    def load_alerts(self):
        if os.path.exists(self.alert_file):
            with open(self.alert_file, 'r') as f:
                return json.load(f)
        return []
    
    def save_alerts(self):
        with open(self.alert_file, 'w') as f:
            json.dump(self.alerts, f, indent=2)
    
    def check_and_alert(self, prediction, input_data):
        """Vérifier si une alerte est nécessaire"""
        
        # Alerte pour eau dangereuse
        if prediction['class_id'] == 3:
            alert = {
                'timestamp': datetime.now().isoformat(),
                'type': 'CRITICAL',
                'class': 'Dangereuse',
                'confidence': prediction['confidence'],
                'data': input_data,
                'message': f"⚠️ ALERTE CRITIQUE! Eau dangereuse détectée! Confiance: {prediction['confidence']}%"
            }
            self.alerts.append(alert)
            self.save_alerts()
            
            # Envoyer email si configuré
            if self.email_enabled:
                self.send_email_alert(alert)
            
            return True
        
        # Alerte pour eau polluée
        elif prediction['class_id'] == 2 and prediction['confidence'] > 80:
            alert = {
                'timestamp': datetime.now().isoformat(),
                'type': 'WARNING',
                'class': 'Polluée',
                'confidence': prediction['confidence'],
                'data': input_data,
                'message': f"⚠️ Attention: Eau polluée détectée! Confiance: {prediction['confidence']}%"
            }
            self.alerts.append(alert)
            self.save_alerts()
            return True
        
        return False
    
    def send_email_alert(self, alert):
        """Envoyer alerte par email"""
        # Configuration (à remplacer par vos identifiants)
        sender = "votre_email@gmail.com"
        password = "votre_mot_de_passe"
        receiver = "alertes@example.com"
        
        try:
            msg = MIMEMultipart()
            msg['From'] = sender
            msg['To'] = receiver
            msg['Subject'] = f"[URGENT] Alerte Qualité d'Eau - {alert['type']}"
            
            body = f"""
            Alerte Système de Qualité d'Eau
            
            Type: {alert['type']}
            Date: {alert['timestamp']}
            Qualité: {alert['class']}
            Confiance: {alert['confidence']}%
            
            Mesures:
            - Température: {alert['data']['temperature']}°C
            - pH: {alert['data']['ph']}
            - Turbidité: {alert['data']['turbidity']} NTU
            - Oxygène: {alert['data']['dissolved_oxygen']} mg/L
            - Conductivité: {alert['data']['conductivity']} µS/cm
            
            Action requise: Intervention immédiate!
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(sender, password)
            server.send_message(msg)
            server.quit()
            
            print(f"📧 Email d'alerte envoyé")
        except Exception as e:
            print(f"❌ Erreur envoi email: {e}")
    
    def get_active_alerts(self):
        """Récupérer les alertes non résolues"""
        return [a for a in self.alerts if not a.get('resolved', False)]
    
    def resolve_alert(self, alert_index):
        """Marquer une alerte comme résolue"""
        if alert_index < len(self.alerts):
            self.alerts[alert_index]['resolved'] = True
            self.alerts[alert_index]['resolved_at'] = datetime.now().isoformat()
            self.save_alerts()
            return True
        return False