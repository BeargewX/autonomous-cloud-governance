import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app import app


def test_governance_score_endpoint():
    app.config["TESTING"] = True
    with app.test_client() as client:
        response = client.get("/api/governance-score")
        assert response.status_code == 200
        data = response.get_json()
        assert "overall" in data
        assert "categories" in data


def test_policy_checks_endpoint():
    app.config["TESTING"] = True
    with app.test_client() as client:
        response = client.get("/api/policy-checks")
        assert response.status_code == 200
        data = response.get_json()
        assert data["count"] >= 1
        assert "checks" in data


def test_report_endpoint():
    app.config["TESTING"] = True
    with app.test_client() as client:
        response = client.get("/api/report")
        assert response.status_code == 200
        data = response.get_json()
        assert "# Cloud Governance Report" in data["markdown"]
