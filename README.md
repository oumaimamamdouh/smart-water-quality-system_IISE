# Smart Water Quality System

A professional FastAPI water quality classification system with CSV/Excel upload, PDF report generation, dashboard UI, and advanced statistics.

## Main Features

- FastAPI backend with SQLite persistence
- Web dashboard for data upload and report export
- Advanced statistics and charts
- CSV/XLSX batch predictions
- PDF report generation with ReportLab
- Responsive static frontend

## Technologies Used

- Python 3.12+
- FastAPI
- Uvicorn
- Pydantic
- Pandas
- OpenPyXL
- ReportLab
- Chart.js

## Project Structure

- `app.py` - main FastAPI application entrypoint
- `requirements.txt` - Python dependencies
- `static/` - frontend HTML, CSS, and client-side scripts
- `src/` - reusable Python modules and services
- `sample_tests.csv` - example dataset for upload
- `_archive_old_files/` - archived legacy or duplicate files

## Installation (Windows PowerShell)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Run the Project

```powershell
python app.py
```

Open your browser:

- Dashboard: `http://127.0.0.1:8000/dashboard`
- Advanced statistics: `http://127.0.0.1:8000/statistics`
- API docs: `http://127.0.0.1:8000/docs`

## Login Information

No authentication is required by default for local testing. The dashboard is accessible directly.

## Uploading Test Data

Use the dashboard upload form to import a CSV or XLSX file. The file must contain:

```csv
temperature,ph,turbidity,dissolved_oxygen,conductivity
```

Example values are provided in `sample_tests.csv`.

## Exporting CSV

Visit `http://127.0.0.1:8000/api/reports/csv` or use the dashboard export button to download all stored analyses.

## Downloading PDF Report

Visit `http://127.0.0.1:8000/api/reports/pdf` to download the latest PDF report.

## Advanced Statistics

Open `http://127.0.0.1:8000/statistics` for charts, summary cards, and the latest predictions table.

## API Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/` | GET | Login / landing page |
| `/dashboard` | GET | Main dashboard UI |
| `/statistics` | GET | Advanced statistics page |
| `/docs` | GET | OpenAPI documentation |
| `/health` | GET | Health check |
| `/classes` | GET | Water quality classes |
| `/predict` | POST | Predict a single sample |
| `/predict/batch` | POST | Batch prediction from JSON array |
| `/api/upload-tests` | POST | Upload CSV/XLSX test data |
| `/api/reports/pdf` | GET | Download PDF report |
| `/api/reports/csv` | GET | Download CSV export |
| `/api/statistics` | GET | Retrieve dashboard statistics |

## Sample CSV Format

```csv
temperature,ph,turbidity,dissolved_oxygen,conductivity
22.5,7.2,3.5,7.8,450
15.2,7.1,1.2,8.5,280
28.4,8.5,18.5,3.2,1050
36.2,9.8,55.6,0.8,1850
40,3,100,3.4,1900
```

## Screenshots

Screenshots are not included in the repository. Add dashboard, statistics, PDF report, and API documentation images into the `screenshots/` folder.

## Academic Context

This project is designed for academic presentation and practical evaluation of water quality classification, combining data ingestion, visualization, and reporting in a single FastAPI solution.

## Future Improvements

- Add user authentication and role-based access
- Implement real sensor integration and live data streaming
- Add a RESTful API client library
- Improve model explainability and logging
- Add CI/CD and automated tests

## Author

Smart Water Quality System
