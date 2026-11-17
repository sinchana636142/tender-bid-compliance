
# Tender Bid Compliance — Ready-to-run enhanced prototype

This version retains the original keyword search, turnover screening and citation verification, and adds:
- React + Vite frontend
- PDF upload into `corpus/tender/`
- Semantic retrieval using Sentence Transformers (`all-MiniLM-L6-v2`)
- Persistent ChromaDB vector storage
- Page-level source metadata in search results
- Windows startup scripts and tests

## Requirements
- Python 3.11 or 3.12 recommended (Sentence Transformers / PyTorch compatibility is generally smoother here)
- Node.js 20+ and npm
- Internet on first semantic-search use to download the embedding model

## Windows setup
1. Extract the ZIP.
2. Open the extracted folder in VS Code.
3. Double-click `run_backend.bat` or run it from PowerShell.
4. In another terminal, run `run_frontend.bat`.
5. Open the Vite URL shown (normally http://localhost:5173).
6. API docs: http://127.0.0.1:8000/docs

Manual setup:
```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```
Frontend:
```powershell
cd frontend
npm install
npm run dev
```

## First use
- Open Documents and upload PDFs, or put PDFs in `corpus/government_rules/`, `corpus/policy_orders/`, or `corpus/tender/`.
- Click "Rebuild index" on Semantic Search (or use `POST /index`).
- Ask a natural-language question.
- First indexing run downloads the embedding model and may take several minutes.
- ChromaDB data is stored under `data/chroma/`.

## API
- `GET /`, `GET /health`, `GET /documents`
- `POST /search` — original keyword search
- `POST /semantic-search` — vector semantic search
- `POST /upload` — upload and index a PDF
- `POST /index` — index all corpus PDFs
- `POST /screen` — preliminary turnover screening
- `POST /verify-citation` — verify source page / exact quote

## Important limitations
- Scanned/image-only PDFs need OCR; this prototype currently indexes selectable PDF text.
- Similarity is retrieval relevance, not a legal conclusion.
- Turnover screening remains preliminary. Do not use it to accept/reject bids; a qualified procurement reviewer must inspect the tender and applicable policy.
- The original repository contains large binary PDF corpus files. This generated ZIP contains the application source and empty corpus folders, not those original PDF bytes. Re-clone the original repository or copy its PDFs into the matching folders to restore that corpus. You can also upload PDFs from the UI.
