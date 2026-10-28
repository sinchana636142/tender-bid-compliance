from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_home_and_health_endpoints_are_healthy():
    assert client.get('/').status_code == 200
    assert client.get('/health').json()['status'] == 'healthy'


def test_search_returns_page_level_evidence():
    response = client.post('/search', json={'query': 'startup turnover experience', 'max_results': 3})
    assert response.status_code == 200
    payload = response.json()
    assert payload['result_count'] > 0
    assert all({'document', 'page', 'text'} <= result.keys() for result in payload['results'])


def test_search_rejects_empty_query():
    response = client.post('/search', json={'query': ''})
    assert response.status_code == 422


def test_screen_flags_startup_turnover_shortfall_for_human_review():
    response = client.post('/screen', json={
        'bidder_name': 'Example Startup',
        'startup_recognized': True,
        'annual_turnover': 4,
        'years_of_experience': 1,
        'required_turnover': 10,
        'relaxation_policy_found': True,
    })
    assert response.status_code == 200
    result = response.json()['screening_result']
    assert result['status'] == 'seek_clarification'
    assert result['human_review_required'] is True


def test_screen_rejects_negative_turnover_at_api_boundary():
    response = client.post('/screen', json={
        'bidder_name': 'Example Bidder',
        'startup_recognized': False,
        'annual_turnover': -1,
        'years_of_experience': 1,
        'required_turnover': 10,
    })
    assert response.status_code == 422


def test_citation_verifier_rejects_unknown_document():
    response = client.post('/verify-citation', json={
        'document_name': 'not_in_corpus.pdf',
        'page_number': 1,
    })
    assert response.status_code == 200
    assert response.json()['verified'] is False


def test_citation_verifier_accepts_existing_document_page():
    response = client.post('/verify-citation', json={
        'document_name': 'GFR2017.pdf',
        'page_number': 1,
    })
    assert response.status_code == 200
    assert response.json()['verified'] is True
