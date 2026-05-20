import os
import sys
import importlib

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

app_module = importlib.import_module("app")
app = app_module.app


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


def test_cockpit_endpoints_work_in_mock_mode():
    app.config["TESTING"] = True
    endpoints = [
        "/api/cockpit-summary",
        "/api/cost-guard",
        "/api/security-risks",
        "/api/runbooks",
        "/api/topology",
        "/api/evidence-report",
    ]

    with app.test_client() as client:
        for endpoint in endpoints:
            response = client.get(endpoint)
            assert response.status_code == 200
            assert response.get_json()["mode"] == app_module.APP_MODE


def test_cost_guard_flags_zero_cost_risks(monkeypatch):
    monkeypatch.setattr(app_module, "ENABLE_PUBLIC_IPV4", True)
    monkeypatch.setattr(app_module, "HAS_NAT_GATEWAY", True)
    monkeypatch.setattr(app_module, "HAS_ALB", True)
    monkeypatch.setattr(app_module, "HAS_RDS", True)
    monkeypatch.setattr(app_module, "ENABLE_VPC_FLOW_LOGS", True)

    data = app_module.build_cost_guard()

    assert data["status"] == "risk"
    flagged = {check["id"] for check in data["checks"] if check["status"] == "risk"}
    assert {"public-ipv4", "nat-gateway", "load-balancer", "database", "flow-logs"} <= flagged


def test_security_scanner_detects_common_terraform_risks():
    risks = app_module.scan_security_texts(
        [
            {
                "path": "main.tf",
                "text": '''
                policy_arn = "arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess"
                policy = jsonencode({"Statement":[{"Resource":"*"}]})
                cidr_blocks = ["0.0.0.0/0"]
                ''',
            }
        ]
    )
    ids = {risk["id"] for risk in risks}

    assert {"iam-full-access", "iam-resource-star", "network-public-ingress"} <= ids
