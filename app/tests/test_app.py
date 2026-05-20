import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import app as app_module
from app import app

TEST_API_KEY = "test-key-12345"


@pytest.fixture(autouse=True)
def clear_api_key():
    """Reset API_KEY ก่อนทุก test"""
    original = app_module.API_KEY
    yield
    app_module.API_KEY = original


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


# ─── Public endpoints (ไม่ต้อง auth) ─────────────────────────────────────────

def test_home(client):
    response = client.get("/")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "healthy"


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "ok"


def test_metrics(client):
    response = client.get("/metrics")
    assert response.status_code == 200


# ─── API endpoints ไม่มี API_KEY set (local dev — เปิดได้เลย) ────────────────

def test_api_cpu_no_auth_required_when_key_not_set(client):
    app_module.API_KEY = ""
    response = client.get("/api/cpu")
    assert response.status_code == 200


def test_api_governance_score_no_auth_required_when_key_not_set(client):
    app_module.API_KEY = ""
    response = client.get("/api/governance-score")
    assert response.status_code == 200


def test_api_cockpit_summary_no_auth_required_when_key_not_set(client):
    app_module.API_KEY = ""
    response = client.get("/api/cockpit-summary")
    assert response.status_code == 200


# ─── API endpoints เมื่อ API_KEY set — ต้องการ header ────────────────────────

def test_api_cpu_returns_401_without_key(client):
    app_module.API_KEY = TEST_API_KEY
    response = client.get("/api/cpu")
    assert response.status_code == 401
    assert "Unauthorized" in response.get_json()["error"]


def test_api_cpu_returns_200_with_correct_key(client):
    app_module.API_KEY = TEST_API_KEY
    response = client.get("/api/cpu", headers={"X-API-Key": TEST_API_KEY})
    assert response.status_code == 200
    data = response.get_json()
    assert "current" in data


def test_api_cpu_returns_401_with_wrong_key(client):
    app_module.API_KEY = TEST_API_KEY
    response = client.get("/api/cpu", headers={"X-API-Key": "wrong-key"})
    assert response.status_code == 401


def test_api_incidents_with_key(client):
    app_module.API_KEY = TEST_API_KEY
    response = client.get("/api/incidents", headers={"X-API-Key": TEST_API_KEY})
    assert response.status_code == 200
    data = response.get_json()
    assert "incidents" in data


def test_api_cost_guard_with_key(client):
    app_module.API_KEY = TEST_API_KEY
    response = client.get("/api/cost-guard", headers={"X-API-Key": TEST_API_KEY})
    assert response.status_code == 200
    data = response.get_json()
    assert "checks" in data


def test_api_security_risks_with_key(client):
    app_module.API_KEY = TEST_API_KEY
    response = client.get("/api/security-risks", headers={"X-API-Key": TEST_API_KEY})
    assert response.status_code == 200
    data = response.get_json()
    assert "risks" in data


def test_api_drift_with_key(client):
    app_module.API_KEY = TEST_API_KEY
    response = client.get("/api/drift", headers={"X-API-Key": TEST_API_KEY})
    assert response.status_code == 200


def test_api_runbooks_with_key(client):
    app_module.API_KEY = TEST_API_KEY
    response = client.get("/api/runbooks", headers={"X-API-Key": TEST_API_KEY})
    assert response.status_code == 200
    data = response.get_json()
    assert "runbooks" in data


# ─── health / home ไม่โดน auth แม้ key จะ set ────────────────────────────────

def test_health_always_public(client):
    app_module.API_KEY = TEST_API_KEY
    response = client.get("/health")
    assert response.status_code == 200


def test_home_always_public(client):
    app_module.API_KEY = TEST_API_KEY
    response = client.get("/")
    assert response.status_code == 200