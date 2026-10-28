# Current project status

## Present in the supplied project
- `app/main.py`: FastAPI app with `GET /`, `GET /health`, `POST /search`, `POST /screen`, and `POST /verify-citation`.
- `app/pdf_reader.py`: extracts readable text from PDFs and labels pages.
- `app/retrieval/document_search.py`: keyword-based search across PDF pages in the three corpus folders.
- `app/validation/compliance_checker.py`: checks four required bid fields and performs a basic turnover comparison.
- `app/verification/citation_checker.py`: checks approved corpus document/page and optionally exact quotation presence.
- `corpus/government_rules/GFR2017.pdf`: present.
- `corpus/policy_orders/startup_mse_relaxation.pdf`: present.
- `README.md`, `.gitignore`, and `requirements.txt`: present.

## Newly added in this working version
- `tests/test_api.py`: API smoke tests for health, search, screening validation, and citation verification.
- `tests/test_compliance_checker.py`: unit tests for missing fields, threshold pass, and startup shortfall escalation.
- `pytest` and `httpx` added to `requirements.txt` for running tests.

## Verified in this working environment
- `GET /` returns HTTP 200.
- `GET /health` returns HTTP 200.
- `POST /search` finds page-level results for `startup turnover experience`.
- `POST /screen` returns `seek_clarification` and requires human review for the sample startup turnover shortfall.
- `POST /verify-citation` accepts an existing corpus document/page and rejects an unknown document.

## Missing / not yet verified
- No tender PDF is present in `corpus/tender/`.
- No completed corpus confirmation or project plan.
- Search is keyword-based; no semantic index (FAISS/Chroma) is implemented.
- No LangGraph/CrewAI agent workflow or three registered agent tools.
- No automated quarantine record for rejected inputs.
- No queue/worker, async run lifecycle, frontend, Docker Compose, observability stack, load test, runbook, or incident log.
- No 20-scenario evaluation set or prompt-version comparison.
- Clean-clone Docker deployment and runtime behavior on the user's machine are not yet verified.

## Known prototype limitation to fix next
- `/screen` accepts `relaxation_policy_found` from the caller. The final service must retrieve and verify policy evidence itself instead of trusting this user-supplied flag.
- The current prototype is for educational screening assistance only; it must not make final procurement decisions.
