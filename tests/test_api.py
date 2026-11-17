
from fastapi.testclient import TestClient
from app.main import app
client=TestClient(app)

def test_health():
    assert client.get("/health").json()["status"]=="healthy"

def test_search_validation():
    assert client.post("/search",json={"query":""}).status_code==422

def test_semantic_validation():
    assert client.post("/semantic-search",json={"query":""}).status_code==422

def test_screen_escalates_shortfall():
    response=client.post("/screen",json={"bidder_name":"Startup","startup_recognized":True,"annual_turnover":4,"years_of_experience":1,"required_turnover":10,"relaxation_policy_found":True})
    assert response.status_code==200
    assert response.json()["screening_result"]["human_review_required"] is True
