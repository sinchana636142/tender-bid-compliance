from app.agents import run_tender_analysis


def test_agent_workflow():

    bidder = {
        "bidder_name": "ABC Technologies",
        "startup_recognized": True,
        "annual_turnover": 5,
        "years_of_experience": 2,
    }

    result = run_tender_analysis(
        question="startup turnover relaxation",
        bidder=bidder,
        required_turnover=10,
        relaxation_policy_found=False,
    )

    assert "agents" in result
    assert "screening" in result
    assert "citations" in result

    assert result["decision"] == "human_review_required"


def test_agent_escalation_without_evidence():

    bidder = {
        "bidder_name": "Test Company",
        "startup_recognized": False,
        "annual_turnover": 100,
        "years_of_experience": 5,
    }

    result = run_tender_analysis(
        question="unique_nonexistent_tender_clause_xyz",
        bidder=bidder,
        required_turnover=50,
    )

    assert result["decision"] == "human_review_required"
