
from app.validation.compliance_checker import screen_turnover, validate_bid_fields

def test_missing_required_field():
    result=validate_bid_fields({"bidder_name":"Example"})
    assert not result["valid"] and "annual_turnover" in result["missing_fields"]

def test_threshold_pass():
    result=screen_turnover({"bidder_name":"Example","startup_recognized":False,"annual_turnover":12,"years_of_experience":2},10,False)
    assert result["status"]=="pass_to_technical_evaluation"

def test_shortfall_requires_human_review():
    result=screen_turnover({"bidder_name":"Startup","startup_recognized":True,"annual_turnover":4,"years_of_experience":1},10,True)
    assert result["status"]=="seek_clarification" and result["human_review_required"]
