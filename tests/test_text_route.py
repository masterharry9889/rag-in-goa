from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_text_route_rejects_empty_query_cleanly():
    response = client.post("/text/query", json={"query": "   "})
    assert response.status_code == 400
    assert "Empty query" in response.json()["detail"]
