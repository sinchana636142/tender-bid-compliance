from app.retrieval.document_search import search_documents
from app.validation.compliance_checker import screen_turnover
from app.verification.citation_checker import verify_citation


# AGENT 1: Evidence Retrieval Agent
def retrieval_agent(question, max_results=5):
    return search_documents(question, max_results)


# TOOL 1: Compliance Screening
def screening_agent(bidder, required_turnover, relaxation_policy_found):
    return screen_turnover(bidder, required_turnover, relaxation_policy_found)


# TOOL 2: Citation Verification
def citation_agent(document_name, page_number, supporting_text=""):
    return verify_citation(document_name, page_number, supporting_text)


# AGENT 2: Compliance Review Agent
def run_tender_analysis(
    question, bidder, required_turnover, relaxation_policy_found=False, max_results=5
):

    # Step 1: Retrieve relevant tender evidence
    evidence = retrieval_agent(question, max_results)

    # Step 2: Screen bidder eligibility
    screening = screening_agent(bidder, required_turnover, relaxation_policy_found)

    # Step 3: Verify citations
    citations = []

    for item in evidence:
        citations.append(
            {
                "document": item["document"],
                "page": item["page"],
                "verification": citation_agent(item["document"], item["page"]),
            }
        )

    # Step 4: Escalate uncertain decisions
    if screening.get("status") != "pass_to_technical_evaluation" or not evidence:
        decision = "human_review_required"
    else:
        decision = "preliminary_threshold_pass"

    return {
        "agents": ["Evidence Retrieval Agent", "Compliance Review Agent"],
        "evidence": evidence,
        "screening": screening,
        "citations": citations,
        "decision": decision,
        "human_review_required": True,
    }
