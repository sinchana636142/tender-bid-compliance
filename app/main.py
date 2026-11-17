from collections import Counter
import time
from fastapi import Request
from app.agents import run_tender_analysis
from pathlib import Path
import shutil
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from app.retrieval.document_search import (
    search_documents,
    DOCUMENT_FOLDERS,
    PROJECT_ROOT,
)
from app.validation.compliance_checker import screen_turnover
from app.verification.citation_checker import verify_citation
from app.semantic_search import semantic_search, index_pdf, index_corpus

app = FastAPI(
    title="Tender Bid Compliance",
    description="Tender document search and preliminary compliance screening.",
    version="2.0.0",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class SearchRequest(BaseModel):
    query: str = Field(min_length=1, max_length=500)
    max_results: int = Field(default=5, ge=1, le=20)


class SemanticRequest(BaseModel):
    query: str = Field(min_length=1, max_length=1000)
    top_k: int = Field(default=5, ge=1, le=20)


class BidScreeningRequest(BaseModel):
    bidder_name: str
    startup_recognized: bool
    annual_turnover: float = Field(ge=0)
    years_of_experience: float = Field(ge=0)
    required_turnover: float = Field(ge=0)
    relaxation_policy_found: bool = False


class AnalysisRequest(BidScreeningRequest):
    question: str = Field(min_length=1, max_length=500)
    max_results: int = Field(default=5, ge=1, le=10)


class CitationRequest(BaseModel):
    document_name: str
    page_number: int = Field(ge=1)
    supporting_text: str = ""


@app.get("/")
async def home():
    return {
        "message": "Tender Bid Compliance is running",
        "status": "healthy",
        "docs": "/docs",
    }


@app.get("/health")
async def health():
    return {"status": "healthy"}


@app.get("/documents")
async def documents():
    items = []
    for folder in DOCUMENT_FOLDERS:
        if folder.exists():
            items.extend(
                {
                    "name": p.name,
                    "folder": str(p.parent.relative_to(PROJECT_ROOT)),
                    "size_bytes": p.stat().st_size,
                }
                for p in folder.glob("*.pdf")
            )
    return {"count": len(items), "documents": items}


@app.post("/search")
async def search(req: SearchRequest):
    try:
        results = search_documents(req.query, req.max_results)
        return {"query": req.query, "result_count": len(results), "results": results}
    except ValueError as exc:
        raise HTTPException(400, str(exc))


@app.post("/semantic-search")
async def semantic(req: SemanticRequest):
    try:
        results = semantic_search(req.query, req.top_k)
        return {"query": req.query, "result_count": len(results), "results": results}
    except ValueError as exc:
        raise HTTPException(400, str(exc))
    except Exception as exc:
        raise HTTPException(500, f"Semantic search failed: {exc}")


@app.post("/index")
async def index():
    try:
        return {"indexed": index_corpus()}
    except Exception as exc:
        raise HTTPException(500, str(exc))


@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    if not file.filename or Path(file.filename).suffix.lower() != ".pdf":
        raise HTTPException(400, "Only PDF files are accepted.")
    safe_name = Path(file.filename).name
    target = DOCUMENT_FOLDERS[2]
    target.mkdir(parents=True, exist_ok=True)
    destination = target / safe_name
    if destination.exists():
        raise HTTPException(409, "A document with this filename already exists.")
    try:
        with destination.open("wb") as out:
            shutil.copyfileobj(file.file, out)
        # Validate PDF and index its extracted text.
        try:
            result = index_pdf(destination)
        except Exception:
            destination.unlink(missing_ok=True)
            raise
        return {"message": "PDF uploaded and indexed", "file": safe_name, **result}
    except ValueError as exc:
        raise HTTPException(400, str(exc))
    finally:
        await file.close()


@app.post("/screen")
async def screen(req: BidScreeningRequest):
    bid = {
        "bidder_name": req.bidder_name,
        "startup_recognized": req.startup_recognized,
        "annual_turnover": req.annual_turnover,
        "years_of_experience": req.years_of_experience,
    }
    result = screen_turnover(bid, req.required_turnover, req.relaxation_policy_found)
    return {
        "bidder_name": req.bidder_name,
        "screening_result": result,
        "notice": "Preliminary assistance only. Human procurement review is mandatory.",
    }


@app.post("/verify-citation")
async def verify(req: CitationRequest):
    return verify_citation(req.document_name, req.page_number, req.supporting_text)


# Request monitoring
request_counts = Counter()


@app.middleware("http")
async def monitor_requests(request: Request, call_next):
    start = time.perf_counter()

    response = await call_next(request)

    duration = time.perf_counter() - start

    key = (request.method, request.url.path, response.status_code)

    request_counts[key] += 1

    response.headers["X-Process-Time-Ms"] = str(round(duration * 1000, 2))

    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"

    return response


# Prometheus-compatible basic metrics
@app.get("/metrics")
async def metrics():

    output = ["# TYPE tender_http_requests_total counter"]

    for (method, path, status), count in request_counts.items():

        output.append(
            f"tender_http_requests_total"
            f'{{method="{method}",path="{path}",status="{status}"}} '
            f"{count}"
        )

    return "\n".join(output) + "\n"


# Combined AI-agent workflow
@app.post("/analyze")
async def analyze(req: AnalysisRequest):

    bidder = {
        "bidder_name": req.bidder_name,
        "startup_recognized": req.startup_recognized,
        "annual_turnover": req.annual_turnover,
        "years_of_experience": req.years_of_experience,
    }

    result = run_tender_analysis(
        question=req.question,
        bidder=bidder,
        required_turnover=req.required_turnover,
        relaxation_policy_found=req.relaxation_policy_found,
        max_results=req.max_results,
    )

    return result


FRONTEND = PROJECT_ROOT / "frontend" / "dist"
if FRONTEND.exists():
    app.mount("/", StaticFiles(directory=str(FRONTEND), html=True), name="frontend")
