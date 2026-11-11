# EventFlow - SJSC Financial Report Analytics

Full-stack event ticketing and financial analytics project built from operational event exports.

## Architecture
- Frontend: React + TypeScript + Vite (dashboard and file-upload interface)
- Backend: Python + FastAPI (API, validation, analytics)
- Data processing: pandas (CSV ingestion and cleaning)
- Database: PostgreSQL (normalized, queryable records)
- Charts: Recharts (frontend visualizations)

## Data sources
1. SummerJam Ticketmelon daily sales export
2. SJSC Vol. 3 workshop finance report

Keep source CSVs in `data/raw/`. Do not commit private or participant-identifying information to a public repository. The current SummerJam file is aggregated by day; it does not contain individual ticket-holder transactions. The SJSC finance CSV contains multiple report sections in one sheet and needs reconciliation before totals are treated as authoritative.

## Initial setup

### 1. Create a virtual environment and install backend dependencies

```bash
cd backend
python -m venv .venv
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# macOS/Linux:
# source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Put the two CSV files in `data/raw/`

Use these filenames:
- `summerjam_ticket_sales_by_date.csv`
- `sjsc_workshop_finance_report.csv`

### 3. Run the initial data profile

From the project root:

```bash
python backend/scripts/profile_datasets.py
```

The script prints column names, row counts, null counts, date coverage, key totals, and a workshop reconciliation warning. It does not modify source files.

### 4. Start the API (after the first backend endpoint is implemented)

```bash
cd backend
uvicorn app.main:app --reload
```

## Planned modules
- `backend/app/services/ingestion.py`: safe CSV loading and normalization
- `backend/app/services/validation.py`: schema checks, duplicate checks, reconciliation
- `backend/app/api/`: upload and analytics endpoints
- `frontend/src/`: dashboard, upload page, filters, charts
- `docs/data-dictionary.md`: field definitions and transformation rules

## Data handling rules
- Preserve original files as raw source data.
- Never combine daily aggregated ticketing rows with individual workshop sale lines as if they were the same grain.
- Keep money as decimal values, not floating-point calculations, in the production database.
- Store source filename, import timestamp, and validation status for each import.
- Flag conflicting or unreconciled totals; do not silently overwrite them.
