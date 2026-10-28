from typing import Any

REQUIRED_BID_FIELDS = [
    "bidder_name",
    "startup_recognized",
    "annual_turnover",
    "years_of_experience",
]


def validate_bid_fields(bid: dict[str, Any]) -> dict[str, Any]:
    """Check whether the bid contains the fields needed for screening."""
    missing_fields = [
        field
        for field in REQUIRED_BID_FIELDS
        if field not in bid or bid[field] is None
    ]

    return {
        "valid": len(missing_fields) == 0,
        "missing_fields": missing_fields,
    }


def screen_turnover(
    bid: dict[str, Any],
    required_turnover: float,
    relaxation_policy_found: bool,
) -> dict[str, Any]:
    """Flag turnover issues without making a final procurement decision."""
    validation = validate_bid_fields(bid)

    if not validation["valid"]:
        return {
            "status": "seek_clarification",
            "reason": "Required bid information is missing.",
            "missing_fields": validation["missing_fields"],
            "human_review_required": True,
        }

    try:
        actual_turnover = float(bid["annual_turnover"])
        required_turnover = float(required_turnover)
    except (TypeError, ValueError):
        return {
            "status": "seek_clarification",
            "reason": "Turnover information is not a valid number.",
            "human_review_required": True,
        }

    if actual_turnover >= required_turnover:
        return {
            "status": "pass_to_technical_evaluation",
            "reason": "The reported turnover meets the specified threshold.",
            "human_review_required": False,
        }

    if bid["startup_recognized"] and relaxation_policy_found:
        return {
            "status": "seek_clarification",
            "reason": (
                "The reported turnover is below the threshold, but a "
                "potential startup relaxation policy was found. Verify "
                "the policy's applicability and the tender conditions."
            ),
            "human_review_required": True,
        }

    return {
        "status": "seek_clarification",
        "reason": (
            "The reported turnover is below the threshold. Check the "
            "tender wording and applicable policies before deciding."
        ),
        "human_review_required": True,
    }