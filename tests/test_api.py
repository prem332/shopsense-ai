import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock


# ── Test Health Endpoints ──────────────────────────────────────

def test_main_health():
    """Test main server health endpoint"""
    with patch(
        'app.backend.database.get_db',
        return_value=None
    ):
        from app.backend.main import app
        client = TestClient(app)
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"


def test_health_returns_correct_fields():
    """Test health endpoint returns required fields"""
    with patch(
        'app.backend.database.get_db',
        return_value=None
    ):
        from app.backend.main import app
        client = TestClient(app)
        response = client.get("/health")
        data = response.json()
        assert "status" in data
        assert "agent" in data or "status" in data


# ── Test Chat Endpoint ─────────────────────────────────────────

def test_chat_endpoint_exists():
    """Test chat endpoint responds"""
    with patch(
        'app.backend.agents.graph.shopping_graph.ainvoke',
        new_callable=AsyncMock,
        return_value={
            "intent": "recommendation",
            "is_valid": True,
            "category": "shirts",
            "color": None,
            "size": None,
            "occasion": None,
            "budget_max": 2000,
            "brand": None,
            "ranked_products": [],
            "reflection_attempts": 0,
            "alert_id": None,
            "final_response": "Found 0 products"
        }
    ):
        from app.backend.main import app
        client = TestClient(app)
        response = client.post(
            "/api/chat",
            json={
                "query": "blue shirt",
                "user_id": "test-user",
                "platforms": ["amazon"]
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "status" in data


# ── Test Input Validation ──────────────────────────────────────

def test_chat_requires_query():
    """Test chat endpoint requires query field"""
    from app.backend.main import app
    client = TestClient(app)
    response = client.post(
        "/api/chat",
        json={"user_id": "test-user"}
    )
    assert response.status_code == 422


def test_chat_accepts_optional_fields():
    """Test chat endpoint accepts optional fields"""
    with patch(
        'app.backend.agents.graph.shopping_graph.ainvoke',
        new_callable=AsyncMock,
        return_value={
            "intent": "recommendation",
            "is_valid": True,
            "category": None,
            "color": None,
            "size": None,
            "occasion": None,
            "budget_max": 0,
            "brand": None,
            "ranked_products": [],
            "reflection_attempts": 0,
            "alert_id": None,
            "final_response": "Done"
        }
    ):
        from app.backend.main import app
        client = TestClient(app)
        response = client.post(
            "/api/chat",
            json={
                "query": "shirt",
                "gender": "male",
                "budget_min": 500,
                "budget_max": 2000,
                "platforms": ["amazon"]
            }
        )
        assert response.status_code == 200