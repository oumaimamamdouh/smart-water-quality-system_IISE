"""
Génère un rapport PDF automatique des analyses
"""

from datetime import datetime
import sqlite3
import pandas as pd
import json

def generate_report():
    """Générer un rapport d'analyse"""
    
    conn = sqlite3.connect('water_quality.db')
    
    # Récupérer les données
    df = pd.read_sql_query("SELECT * FROM predictions ORDER BY timestamp DESC LIMIT 20", conn)
    conn.close()
    
    if df.empty:
        print("Aucune donnée dans la base")
        return
    
    # Statistiques
    total = len(df)
    potable = len(df[df['class_name'] == 'Potable'])
    polluee = len(df[df['class_name'] == 'Polluée'])
    dangereuse = len(df[df['class_name'] == 'Dangereuse'])
    avg_confidence = df['confidence'].mean()
    
    # Générer rapport HTML
    report_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Rapport Qualité d'Eau</title>
        <style>
            body {{ font-family: Arial; padding: 40px; }}
            h1 {{ color: #1a73e8; }}
            .stat {{ background: #f0f2f5; padding: 15px; margin: 10px 0; border-radius: 8px; }}
            table {{ width: 100%; border-collapse: collapse; }}
            th, td {{ padding: 10px; border-bottom: 1px solid #ddd; text-align: left; }}
            th {{ background: #1a73e8; color: white; }}
        </style>
    </head>
    <body>
        <h1>🌊 Rapport de Qualité d'Eau</h1>
        <p>Généré le: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</p>
        
        <div class="stat">
            <h3>📊 Statistiques Globales</h3>
            <p>Total analyses: <strong>{total}</strong></p>
            <p>Eau Potable: <strong>{potable}</strong> ({potable/total*100:.1f}%)</p>
            <p>Eau Polluée: <strong>{polluee}</strong> ({polluee/total*100:.1f}%)</p>
            <p>Eau Dangereuse: <strong>{dangereuse}</strong> ({dangereuse/total*100:.1f}%)</p>
            <p>Confiance moyenne: <strong>{avg_confidence:.1f}%</strong></p>
        </div>
        
        <h3>📋 Dernières Analyses</h3>
        <table>
            <thead><tr><th>Date</th><th>Temp</th><th>pH</th><th>Qualité</th><th>Confiance</th></tr></thead>
            <tbody>
    """
    
    for _, row in df.head(10).iterrows():
        report_html += f"""
            <tr>
                <td>{row['timestamp'][:19]}</td>
                <td>{row['temperature']}°C</td>
                <td>{row['ph']}</td>
                <td>{row['class_name']}</td>
                <td>{row['confidence']}%</td>
            </tr>
        """
    
    report_html += """
            </tbody>
        </table>
        <p style="margin-top: 40px; color: #999;">Rapport généré automatiquement - Smart Water Quality System</p>
    </body>
    </html>
    """
    
    # Sauvegarder
    with open('rapport_qualite_eau.html', 'w', encoding='utf-8') as f:
        f.write(report_html)
    
    print(f"✅ Rapport généré: rapport_qualite_eau.html")
    print(f"📊 Total analyses: {total}")
    print(f"💧 Eau potable: {potable} ({potable/total*100:.1f}%)")

if __name__ == "__main__":
    generate_report()