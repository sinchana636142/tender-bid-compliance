from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from app.retrieval.document_search import search_documents
from app.validation.compliance_checker import screen_turnover
from app.verification.citation_checker import verify_citation

app = FastAPI(
    title="Public Procurement Bid Compliance Screening",
    description="An AI-assisted service for checking government tender compliance.",
    version="1.0.0",
)


class SearchRequest(BaseModel):
    query: str = Field(min_length=1, max_length=500)
    max_results: int = Field(default=5, ge=1, le=20)


class BidScreeningRequest(BaseModel):
    bidder_name: str
    startup_recognized: bool
    annual_turnover: float = Field(ge=0)
    years_of_experience: float = Field(ge=0)
    required_turnover: float = Field(ge=0)
    relaxation_policy_found: bool = False


class CitationRequest(BaseModel):
    document_name: str
    page_number: int = Field(ge=1)
    supporting_text: str = ""


@app.get("/")
async def home():
    return {
        "message": "Bid Compliance Screening Service is running!",
        "status": "healthy",
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.post("/search")
async def search(request: SearchRequest):
    try:
        results = search_documents(
            request.query,
            max_results=request.max_results,
        )
        return {
            "query": request.query,
            "result_count": len(results),
            "results": results,
        }
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


@app.post("/screen")
async def screen_bid(request: BidScreeningRequest):
    bid = {
        "bidder_name": request.bidder_name,
        "startup_recognized": request.startup_recognized,
        "annual_turnover": request.annual_turnover,
        "years_of_experience": request.years_of_experience,
    }

    result = screen_turnover(
        bid,
        required_turnover=request.required_turnover,
        relaxation_policy_found=request.relaxation_policy_found,
    )

    return {
        "bidder_name": request.bidder_name,
        "screening_result": result,
        "notice": (
            "This is preliminary screening assistance, not a final "
            "procurement decision."
        ),
    }


@app.post("/verify-citation")
async def verify_citation_endpoint(request: CitationRequest):
    return verify_citation(
        document_name=request.document_name,
        page_number=request.page_number,
        supporting_text=request.supporting_text,
    )