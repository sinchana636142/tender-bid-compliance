
from typing import Any
REQUIRED_BID_FIELDS = ["bidder_name", "startup_recognized", "annual_turnover", "years_of_experience"]

def validate_bid_fields(bid: dict[str, Any]) -> dict[str, Any]:
    missing = [key for key in REQUIRED_BID_FIELDS if key not in bid or bid[key] is None]
    return {"valid": not missing, "missing_fields": missing}

def screen_turnover(bid: dict[str, Any], required_turnover: float, relaxation_policy_found: bool) -> dict[str, Any]:
    validation = validate_bid_fields(bid)
    if not validation["valid"]:
        return {"status":"seek_clarification","reason":"Required bid information is missing.",
                "missing_fields":validation["missing_fields"],"human_review_required":True}
    try:
        actual, required = float(bid["annual_turnover"]), float(required_turnover)
    except (TypeError, ValueError):
        return {"status":"seek_clarification","reason":"Turnover information is not a valid number.","human_review_required":True}
    if actual >= required:
        return {"status":"pass_to_technical_evaluation","reason":"Reported turnover meets the specified threshold.","human_review_required":False}
    if bid["startup_recognized"] and relaxation_policy_found:
        reason = "Potential startup relaxation evidence was identified. Verify applicability and tender conditions."
    else:
        reason = "Reported turnover is below the threshold. Check tender wording and applicable policies."
    return {"status":"seek_clarification","reason":reason,"human_review_required":True}
