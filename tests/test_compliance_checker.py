from app.validation.compliance_checker import screen_turnover, validate_bid_fields


def test_missing_required_field_is_flagged():
    result = validate_bid_fields({'bidder_name': 'Example'})
    assert result['valid'] is False
    assert 'annual_turnover' in result['missing_fields']


def test_turnover_meeting_threshold_passes_to_technical_evaluation():
    result = screen_turnover(
        {'bidder_name': 'Example', 'startup_recognized': False, 'annual_turnover': 12, 'years_of_experience': 2},
        required_turnover=10,
        relaxation_policy_found=False,
    )
    assert result['status'] == 'pass_to_technical_evaluation'


def test_below_threshold_never_makes_final_decision():
    result = screen_turnover(
        {'bidder_name': 'Example Startup', 'startup_recognized': True, 'annual_turnover': 4, 'years_of_experience': 1},
        required_turnover=10,
        relaxation_policy_found=True,
    )
    assert result['status'] == 'seek_clarification'
    assert result['human_review_required'] is True
