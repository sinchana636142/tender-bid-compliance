# Public Procurement Bid Compliance Screening Service

## Current status
This is a work in progress. The existing FastAPI prototype includes health endpoints, keyword PDF search, basic turnover screening, and basic citation checks.

## Install
Use Python 3.11+ if possible. From the project root:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

## Run
```powershell
python -m uvicorn app.main:app --reload
```
Open `http://127.0.0.1:8000/docs`.

## Existing endpoints
- `GET /`
- `GET /health`
- `POST /search`
- `POST /screen`
- `POST /verify-citation`

## Corpus
- `corpus/government_rules/GFR2017.pdf`
- `corpus/policy_orders/startup_mse_relaxation.pdf`
- Add one published, closed tender PDF under `corpus/tender/`.

The current search is keyword-based, not semantic. The screening endpoint is a prototype and must not be used for real procurement decisions. The system supports preliminary screening and escalates ambiguity to a human committee.
