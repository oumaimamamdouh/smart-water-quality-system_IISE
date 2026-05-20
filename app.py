"""
Smart Water Quality System - Final Backend
"""

from pathlib import Path
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, Response, StreamingResponse
from pydantic import BaseModel, Field, ValidationError
from typing import Dict, List
from datetime import datetime
import sqlite3
import json
from contextlib import contextmanager
import pandas as pd
import io
import csv
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer
from reportlab.lib import colors

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
DB_PATH = BASE_DIR / "water_quality.db"

# ============ BASE DE DONNÉES ============
class DatabaseManager:
    def __init__(self, db_path=None):
        if db_path is None:
            db_path = DB_PATH
        self.db_path = str(db_path)
        self.init_database()

    @contextmanager
    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    def init_database(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
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
            conn.commit()

    def save_prediction(self, data: Dict, prediction: Dict, model_version: str = "2.0.0"):
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
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) as total FROM predictions")
            total = cursor.fetchone()['total']
            cursor.execute("SELECT AVG(confidence) as avg_conf FROM predictions")
            avg_conf = cursor.fetchone()['avg_conf'] or 0
            cursor.execute("SELECT class_name, COUNT(*) as count FROM predictions GROUP BY class_name")
            by_class = [dict(row) for row in cursor.fetchall()]
            return {
                'total_predictions': total,
                'average_confidence': round(avg_conf, 2),
                'by_class': by_class
            }

    def get_history(self, limit: int = 50):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if limit is None or limit <= 0:
                cursor.execute('''
                    SELECT * FROM predictions
                    ORDER BY timestamp DESC
                ''')
            else:
                cursor.execute('''
                    SELECT * FROM predictions
                    ORDER BY timestamp DESC
                    LIMIT ?
                ''', (limit,))
            return [dict(row) for row in cursor.fetchall()]

    def get_all_predictions(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM predictions ORDER BY timestamp DESC")
            return [dict(row) for row in cursor.fetchall()]

# ============ CONFIGURATION ============
WATER_QUALITY_CLASSES = {
    0: {"name": "Potable", "risk": "Aucun risque", "color": "🟢", "action": "Buvable sans traitement"},
    1: {"name": "Acceptable", "risk": "Risque faible", "color": "🟡", "action": "Traitement léger recommandé"},
    2: {"name": "Polluée", "risk": "Risque modéré", "color": "🟠", "action": "Ne pas boire sans traitement"},
    3: {"name": "Dangereuse", "risk": "Risque élevé", "color": "🔴", "action": "INTERVENTION IMMÉDIATE REQUISE"}
}

# ============ MODÈLES PYDANTIC ============
class SensorData(BaseModel):
    temperature: float = Field(..., ge=0, le=40, description="Température en °C")
    ph: float = Field(..., ge=0, le=14, description="pH de l'eau")
    turbidity: float = Field(..., ge=0, le=100, description="Turbidité en NTU")
    dissolved_oxygen: float = Field(..., ge=0, le=15, description="Oxygène dissous mg/L")
    conductivity: float = Field(..., ge=0, le=2000, description="Conductivité µS/cm")

    class Config:
        json_schema_extra = {
            "example": {
                "temperature": 22.5,
                "ph": 7.2,
                "turbidity": 3.5,
                "dissolved_oxygen": 7.8,
                "conductivity": 450
            }
        }

class PredictionResponse(BaseModel):
    input_data: Dict
    prediction: Dict
    timestamp: str
    model_version: str

# ============ SERVICE DE PRÉDICTION ============
class WaterQualityService:
    def __init__(self):
        self.db = DatabaseManager()
        self.model_version = "2.0.0"
        self.prediction_count = 0

    def predict(self, data: Dict) -> Dict:
        score = 0
        analysis = []

        if data['dissolved_oxygen'] >= 7:
            analysis.append("✅ Oxygène dissous excellent (>7 mg/L)")
        elif data['dissolved_oxygen'] >= 5:
            score += 1
            analysis.append("⚠️ Oxygène dissous acceptable (5-7 mg/L)")
        elif data['dissolved_oxygen'] >= 3:
            score += 2
            analysis.append("⚠️ Oxygène dissous faible (3-5 mg/L)")
        else:
            score += 3
            analysis.append("🔴 Oxygène dissous critique (<3 mg/L)")

        if data['turbidity'] < 2:
            analysis.append("✅ Eau claire (<2 NTU)")
        elif data['turbidity'] < 10:
            score += 1
            analysis.append("⚠️ Légèrement trouble (2-10 NTU)")
        elif data['turbidity'] < 30:
            score += 2
            analysis.append("⚠️ Très trouble (10-30 NTU)")
        else:
            score += 3
            analysis.append("🔴 Extrêmement trouble (>30 NTU)")

        if 6.5 <= data['ph'] <= 8.0:
            analysis.append("✅ pH neutre (6.5-8.0)")
        elif 6.0 <= data['ph'] <= 8.5:
            score += 1
            analysis.append("⚠️ pH légèrement hors norme")
        else:
            score += 2
            analysis.append("🔴 pH dangereux")

        if data['temperature'] < 25:
            analysis.append("✅ Température normale (<25°C)")
        elif data['temperature'] < 30:
            score += 1
            analysis.append("⚠️ Température élevée (25-30°C)")
        else:
            score += 2
            analysis.append("🔴 Température très élevée (>30°C)")

        if data['conductivity'] < 400:
            analysis.append("✅ Conductivité normale (<400 µS/cm)")
        elif data['conductivity'] < 800:
            score += 1
            analysis.append("⚠️ Conductivité élevée (400-800 µS/cm)")
        else:
            score += 2
            analysis.append("🔴 Conductivité très élevée (>800 µS/cm)")

        if score <= 2:
            class_id = 0
            confidence = 90 - (score * 5)
        elif score <= 5:
            class_id = 1
            confidence = 80 - ((score - 2) * 7)
        elif score <= 8:
            class_id = 2
            confidence = 70 - ((score - 5) * 7)
        else:
            class_id = 3
            confidence = 60 - ((score - 8) * 5)

        confidence = max(50, min(95, confidence))

        if score <= 2:
            risk_level = "🟢 AUCUN RISQUE"
        elif score <= 5:
            risk_level = "🟡 RISQUE FAIBLE"
        elif score <= 8:
            risk_level = "🟠 RISQUE MODÉRÉ"
        else:
            risk_level = "🔴 RISQUE ÉLEVÉ - Intervention immédiate!"

        return {
            "class_id": class_id,
            "class_name": WATER_QUALITY_CLASSES[class_id]["name"],
            "risk_level": risk_level,
            "action": WATER_QUALITY_CLASSES[class_id]["action"],
            "confidence": confidence,
            "score": score,
            "max_score": 12,
            "analysis": analysis
        }

# ============ APP FASTAPI ============
app = FastAPI(
    title="Smart Water Quality Classification System",
    description="API de classification de la qualité de l'eau avec import, export et rapport PDF.",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

if not STATIC_DIR.exists():
    STATIC_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

service = WaterQualityService()

# ============ ROUTES FRONTEND ============
@app.get("/")
async def root():
    return FileResponse(str(STATIC_DIR / "login.html"))

@app.get("/dashboard")
async def dashboard():
    return FileResponse(str(STATIC_DIR / "dashboard_pro.html"))

@app.get("/statistics")
async def statistics_page():
    return FileResponse(str(STATIC_DIR / "statistics.html"))

# ============ API ENDPOINTS ============
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "Smart Water Quality System",
        "version": service.model_version,
        "database": "SQLite",
        "predictions_count": service.prediction_count
    }

@app.get("/classes")
async def get_classes():
    return WATER_QUALITY_CLASSES

@app.post("/predict", response_model=PredictionResponse)
async def predict_quality(data: SensorData):
    try:
        input_data = data.dict()
        prediction = service.predict(input_data)
        service.db.save_prediction(input_data, prediction, service.model_version)
        service.prediction_count += 1
        return PredictionResponse(
            input_data=input_data,
            prediction=prediction,
            timestamp=datetime.now().isoformat(),
            model_version=service.model_version
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/predict/batch")
async def predict_batch(samples: List[SensorData]):
    results = []
    for sample in samples:
        input_data = sample.dict()
        prediction = service.predict(input_data)
        service.db.save_prediction(input_data, prediction, service.model_version)
        service.prediction_count += 1
        results.append({"input": input_data, "prediction": prediction})
    return {"total": len(results), "results": results}

@app.get("/stats")
async def get_statistics():
    db_stats = service.db.get_statistics()
    return {
        "service_stats": {
            "model_version": service.model_version,
            "total_predictions_session": service.prediction_count,
            "status": "operational"
        },
        "database_stats": db_stats
    }

@app.get("/history")
async def get_history(limit: int = 50):
    history = service.db.get_history(limit)
    return {"history": history, "total": len(history), "limit": limit}

@app.get("/metrics")
async def get_metrics():
    stats = service.db.get_statistics()
    return {
        "total_predictions_all_time": stats['total_predictions'],
        "average_confidence": stats['average_confidence'],
        "classes_distribution": stats['by_class'],
        "current_session_predictions": service.prediction_count
    }

@app.post("/api/upload-tests")
async def upload_tests(file: UploadFile = File(...)):
    filename = file.filename or ""
    ext = filename.rsplit('.', 1)[-1].lower()
    if ext not in {"csv", "xlsx"}:
        raise HTTPException(status_code=400, detail="Format de fichier invalide. Seuls .csv et .xlsx sont acceptés.")

    try:
        contents = await file.read()
        if not contents:
            raise HTTPException(status_code=400, detail="Le fichier est vide.")
        if ext == "csv":
            try:
                text = contents.decode('utf-8-sig')
            except UnicodeDecodeError:
                text = contents.decode('latin1')
            df = pd.read_csv(io.StringIO(text))
        else:
            df = pd.read_excel(io.BytesIO(contents), engine='openpyxl')
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Impossible de lire le fichier : {str(e)}")

    if df.empty:
        raise HTTPException(status_code=400, detail="Le fichier contient zéro ligne de données.")

    df.columns = [str(col).strip().lower() for col in df.columns]
    required_columns = {"temperature", "ph", "turbidity", "dissolved_oxygen", "conductivity"}
    missing = required_columns - set(df.columns)
    if missing:
        raise HTTPException(status_code=400, detail=f"Colonnes manquantes : {', '.join(sorted(missing))}")

    results = []
    counts = {"Potable": 0, "Acceptable": 0, "Polluée": 0, "Dangereuse": 0}
    total_confidence = 0.0

    for index, row in df.iterrows():
        try:
            input_data = {
                "temperature": float(row["temperature"]),
                "ph": float(row["ph"]),
                "turbidity": float(row["turbidity"]),
                "dissolved_oxygen": float(row["dissolved_oxygen"]),
                "conductivity": float(row["conductivity"])
            }
        except Exception:
            raise HTTPException(status_code=400, detail=f"Valeurs invalides à la ligne {index + 2}.")

        try:
            SensorData(**input_data)
        except ValidationError as exc:
            raise HTTPException(status_code=400, detail=f"Erreur de validation à la ligne {index + 2} : {exc}")

        prediction = service.predict(input_data)
        service.db.save_prediction(input_data, prediction, service.model_version)
        service.prediction_count += 1

        counts[prediction['class_name']] += 1
        total_confidence += prediction['confidence']
        results.append({
            "temperature": input_data['temperature'],
            "ph": input_data['ph'],
            "turbidity": input_data['turbidity'],
            "dissolved_oxygen": input_data['dissolved_oxygen'],
            "conductivity": input_data['conductivity'],
            "class_name": prediction['class_name'],
            "confidence": prediction['confidence'],
            "score": prediction['score']
        })

    total_tests = len(results)
    average_confidence = round(total_confidence / total_tests, 2) if total_tests else 0.0
    return {
        "total_tests": total_tests,
        "potable_count": counts["Potable"],
        "acceptable_count": counts["Acceptable"],
        "polluted_count": counts["Polluée"],
        "dangerous_count": counts["Dangereuse"],
        "average_confidence": average_confidence,
        "results": results
    }

def build_pdf_report() -> bytes:
    stats = service.db.get_statistics()
    latest = service.db.get_history(limit=20)
    class_counts = {item['class_name']: item['count'] for item in stats['by_class']}
    total = stats['total_predictions']
    potable = class_counts.get('Potable', 0)
    acceptable = class_counts.get('Acceptable', 0)
    polluted = class_counts.get('Polluée', 0)
    dangerous = class_counts.get('Dangereuse', 0)

    if total == 0:
        conclusion = "Aucune analyse n'a encore été enregistrée."
    elif dangerous > 0:
        conclusion = "Des conditions dangereuses ont été détectées. Une action immédiate est recommandée."
    elif polluted > 0:
        conclusion = "La qualité de l'eau est compromise et nécessite une intervention."
    elif acceptable > 0:
        conclusion = "L'eau est acceptable mais des améliorations sont conseillées."
    else:
        conclusion = "L'eau est potable et la qualité est satisfaisante."

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = [
        Paragraph("Smart Water Quality Report", styles['Title']),
        Spacer(1, 12),
        Paragraph(f"Date de génération : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']),
        Spacer(1, 12),
        Paragraph(f"Total des analyses : {total}", styles['Normal']),
        Paragraph(f"Potable : {potable}", styles['Normal']),
        Paragraph(f"Acceptable : {acceptable}", styles['Normal']),
        Paragraph(f"Polluée : {polluted}", styles['Normal']),
        Paragraph(f"Dangereuse : {dangerous}", styles['Normal']),
        Paragraph(f"Confiance moyenne : {stats['average_confidence']}%", styles['Normal']),
        Spacer(1, 12),
        Paragraph("Conclusion :", styles['Heading2']),
        Paragraph(conclusion, styles['BodyText']),
        Spacer(1, 16)
    ]

    table_data = [[
        "Timestamp", "Température", "pH", "Turbidité", "Oxygène dissous", "Conductivité", "Classe", "Confiance", "Score"
    ]]

    if latest:
        for row in latest:
            table_data.append([
                row['timestamp'],
                row['temperature'],
                row['ph'],
                row['turbidity'],
                row['dissolved_oxygen'],
                row['conductivity'],
                row['class_name'],
                f"{row['confidence']}%",
                row['score']
            ])
    else:
        table_data.append(["Aucune donnée", "", "", "", "", "", "", "", ""])

    table = Table(table_data, repeatRows=1, hAlign='LEFT')
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a73e8')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('GRID', (0, 0), (-1, -1), 0.25, colors.grey),
        ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (7, 1), (7, -1), 'RIGHT')
    ]))
    elements.append(table)
    doc.build(elements)
    buffer.seek(0)
    return buffer.getvalue()

@app.get("/api/reports/pdf")
async def download_pdf_report():
    report_bytes = build_pdf_report()
    return Response(
        content=report_bytes,
        media_type='application/pdf',
        headers={'Content-Disposition': 'attachment; filename="smart_water_quality_report.pdf"'}
    )

@app.get("/api/reports/csv")
async def download_all_analyses_csv():
    rows = service.db.get_all_predictions()
    output = io.StringIO()
    fieldnames = [
        'id', 'timestamp', 'temperature', 'ph', 'turbidity',
        'dissolved_oxygen', 'conductivity', 'class_name', 'confidence', 'score'
    ]
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    for row in rows:
        writer.writerow({key: row.get(key, '') for key in fieldnames})
    return Response(
        content=output.getvalue(),
        media_type='text/csv',
        headers={'Content-Disposition': 'attachment; filename="all_water_quality_analyses.csv"'}
    )

@app.get("/api/statistics")
async def get_statistics_api():
    stats = service.db.get_statistics()
    total = stats['total_predictions']
    counts = {item['class_name']: item['count'] for item in stats['by_class']}
    percentages = {class_name: round((count / total * 100), 2) if total else 0.0 for class_name, count in counts.items()}
    latest = service.db.get_history(limit=20)
    return {
        'total_analyses': total,
        'average_confidence': stats['average_confidence'],
        'counts': counts,
        'percentages': percentages,
        'critical_alerts': counts.get('Dangereuse', 0),
        'latest_analyses': latest,
        'by_class': stats['by_class']
    }

@app.get("/export/csv")
async def export_csv():
    return await download_all_analyses_csv()

@app.get("/export/report")
async def export_report():
    return await download_pdf_report()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
