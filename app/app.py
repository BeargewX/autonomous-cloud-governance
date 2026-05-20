from flask import Flask, jsonify
import sqlite3
import boto3
import os
from datetime import datetime, timedelta

app = Flask(__name__)

APP_MODE = os.getenv("APP_MODE", "mock").lower()
DB_PATH = os.getenv("DB_PATH", "data.db")
REGION = os.getenv("AWS_REGION", "ap-southeast-1")
INSTANCE_ID = os.getenv("EC2_INSTANCE_ID", "i-0327c7e7774cbc046")
DYNAMODB_TABLE = os.getenv("DYNAMODB_TABLE", "cloud-governance-incident-log")
PORT = int(os.getenv("PORT", os.getenv("FLASK_RUN_PORT", "5000")))

ENABLE_PUBLIC_IPV4 = os.getenv("ENABLE_PUBLIC_IPV4", "true").lower() == "true"
ENABLE_PUBLIC_SSH = os.getenv("ENABLE_PUBLIC_SSH", "false").lower() == "true"
ENABLE_VPC_FLOW_LOGS = os.getenv("ENABLE_VPC_FLOW_LOGS", "true").lower() == "true"
HAS_NAT_GATEWAY = os.getenv("HAS_NAT_GATEWAY", "false").lower() == "true"
EC2_CPU_CREDITS = os.getenv("EC2_CPU_CREDITS", "standard").lower()
API_AUTH_ENABLED = os.getenv("API_AUTH_ENABLED", "false").lower() == "true"


def init_db():
    db_dir = os.path.dirname(DB_PATH)
    if db_dir:
        os.makedirs(db_dir, exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """CREATE TABLE IF NOT EXISTS incidents
                    (id INTEGER PRIMARY KEY, message TEXT, timestamp TEXT)"""
    )
    conn.commit()
    conn.close()


def utc_now():
    return datetime.utcnow().isoformat()


def is_mock_mode():
    return APP_MODE != "aws"


def severity_rank(severity):
    return {"critical": 4, "high": 3, "medium": 2, "low": 1, "info": 0}.get(
        severity, 0
    )


def mock_cpu_payload():
    history = [12, 16, 18, 22, 19, 26, 24, 21, 18, 17, 23, 20]
    current = history[-1]
    return {
        "current": current,
        "history": history,
        "instance_id": INSTANCE_ID,
        "status": "ok",
        "mode": APP_MODE,
    }


def mock_incident_payload():
    return {
        "incidents": [
            {
                "incident_id": "demo-001",
                "timestamp": utc_now(),
                "incident_type": "EC2_STOPPED",
                "instance_id": INSTANCE_ID,
                "action_taken": "started_instance",
                "mode": "mock",
            },
            {
                "incident_id": "demo-002",
                "timestamp": (datetime.utcnow() - timedelta(minutes=12)).isoformat(),
                "incident_type": "HIGH_CPU",
                "instance_id": INSTANCE_ID,
                "action_taken": "sent_alert",
                "mode": "mock",
            },
            {
                "incident_id": "demo-003",
                "timestamp": (datetime.utcnow() - timedelta(minutes=25)).isoformat(),
                "incident_type": "COST_RISK",
                "instance_id": INSTANCE_ID,
                "action_taken": "recommended_free_mode",
                "mode": "mock",
            },
        ],
        "count": 3,
        "mode": APP_MODE,
    }


def mock_lambda_stats_payload():
    return {
        "self_healing": {"invocations": 2, "errors": 0},
        "finops": {"invocations": 1, "errors": 0},
        "cost_anomaly": {"invocations": 1, "errors": 0},
        "s3_lifecycle": {"invocations": 1, "errors": 0},
        "mode": APP_MODE,
    }


def get_cpu_payload():
    if is_mock_mode():
        return mock_cpu_payload()

    try:
        cw = boto3.client("cloudwatch", region_name=REGION)
        end = datetime.utcnow()
        start = end - timedelta(minutes=30)
        response = cw.get_metric_statistics(
            Namespace="AWS/EC2",
            MetricName="CPUUtilization",
            Dimensions=[{"Name": "InstanceId", "Value": INSTANCE_ID}],
            StartTime=start,
            EndTime=end,
            Period=300,
            Statistics=["Average"],
        )
        points = sorted(response["Datapoints"], key=lambda x: x["Timestamp"])
        history = [round(p["Average"], 1) for p in points]
        current = history[-1] if history else 0
        return {
            "current": current,
            "history": history,
            "instance_id": INSTANCE_ID,
            "status": "alarm"
            if current > 70
            else "warning"
            if current > 50
            else "ok",
            "mode": APP_MODE,
        }
    except Exception as e:
        return {"current": 0, "history": [], "error": str(e), "mode": APP_MODE}


def get_incidents_payload():
    if is_mock_mode():
        return mock_incident_payload()

    try:
        db = boto3.resource("dynamodb", region_name=REGION)
        table = db.Table(DYNAMODB_TABLE)
        response = table.scan(Limit=20)
        items = sorted(
            response.get("Items", []), key=lambda x: x.get("timestamp", ""), reverse=True
        )
        return {"incidents": items, "count": len(items), "mode": APP_MODE}
    except Exception as e:
        return {"incidents": [], "count": 0, "error": str(e), "mode": APP_MODE}


def get_lambda_stats_payload():
    if is_mock_mode():
        return mock_lambda_stats_payload()

    try:
        cw = boto3.client("cloudwatch", region_name=REGION)
        end = datetime.utcnow()
        start = end - timedelta(days=7)

        def get_lambda_metric(func_name, metric):
            r = cw.get_metric_statistics(
                Namespace="AWS/Lambda",
                MetricName=metric,
                Dimensions=[{"Name": "FunctionName", "Value": func_name}],
                StartTime=start,
                EndTime=end,
                Period=604800,
                Statistics=["Sum"],
            )
            pts = r.get("Datapoints", [])
            return int(pts[0]["Sum"]) if pts else 0

        return {
            "self_healing": {
                "invocations": get_lambda_metric(
                    "cloud-governance-self-healing", "Invocations"
                ),
                "errors": get_lambda_metric("cloud-governance-self-healing", "Errors"),
            },
            "finops": {
                "invocations": get_lambda_metric(
                    "cloud-governance-finops", "Invocations"
                ),
                "errors": get_lambda_metric("cloud-governance-finops", "Errors"),
            },
            "mode": APP_MODE,
        }
    except Exception as e:
        return {"error": str(e), "mode": APP_MODE}


def get_status_payload():
    if is_mock_mode():
        return {
            "ec2": "running",
            "instance_id": INSTANCE_ID,
            "mode": APP_MODE,
            "timestamp": utc_now(),
        }

    try:
        ec2 = boto3.client("ec2", region_name=REGION)
        response = ec2.describe_instances(InstanceIds=[INSTANCE_ID])
        instance = response["Reservations"][0]["Instances"][0]
        state = instance["State"]["Name"]
        public_ip = instance.get("PublicIpAddress")
        return {
            "ec2": state,
            "instance_id": INSTANCE_ID,
            "public_ip": public_ip,
            "mode": APP_MODE,
            "timestamp": utc_now(),
        }
    except Exception as e:
        return {"ec2": "unknown", "error": str(e), "mode": APP_MODE}


def build_policy_checks():
    cpu = get_cpu_payload()
    lambdas = get_lambda_stats_payload()

    checks = [
        {
            "id": "cost.no_nat_gateway",
            "category": "cost",
            "severity": "high",
            "status": "fail" if HAS_NAT_GATEWAY else "pass",
            "title": "No NAT Gateway in free-first mode",
            "finding": "NAT Gateway is present" if HAS_NAT_GATEWAY else "No NAT Gateway detected",
            "recommendation": "Keep NAT Gateway out of this student/demo version.",
        },
        {
            "id": "cost.public_ipv4",
            "category": "cost",
            "severity": "medium",
            "status": "warn" if ENABLE_PUBLIC_IPV4 else "pass",
            "title": "Public IPv4 is intentionally controlled",
            "finding": "Public IPv4/EIP is enabled for live demo"
            if ENABLE_PUBLIC_IPV4
            else "Public IPv4/EIP disabled",
            "recommendation": "Set enable_public_ipv4=false after demos to reduce hourly IPv4 cost.",
        },
        {
            "id": "cost.vpc_flow_logs",
            "category": "cost",
            "severity": "low",
            "status": "warn" if ENABLE_VPC_FLOW_LOGS else "pass",
            "title": "VPC Flow Logs are optional",
            "finding": "VPC Flow Logs are enabled"
            if ENABLE_VPC_FLOW_LOGS
            else "VPC Flow Logs disabled",
            "recommendation": "Disable flow logs outside governance demos if CloudWatch log cost matters.",
        },
        {
            "id": "cost.t3_credits",
            "category": "cost",
            "severity": "medium",
            "status": "pass" if EC2_CPU_CREDITS == "standard" else "warn",
            "title": "EC2 CPU credits avoid unlimited burst charges",
            "finding": f"T3 CPU credit mode is {EC2_CPU_CREDITS}",
            "recommendation": "Use ec2_cpu_credits=standard for predictable free-tier behavior.",
        },
        {
            "id": "security.public_ssh",
            "category": "security",
            "severity": "high",
            "status": "fail" if ENABLE_PUBLIC_SSH else "pass",
            "title": "SSH is not open to the internet",
            "finding": "Public SSH is enabled" if ENABLE_PUBLIC_SSH else "Public SSH disabled",
            "recommendation": "Use SSM Session Manager instead of 0.0.0.0/0 SSH.",
        },
        {
            "id": "security.api_auth",
            "category": "security",
            "severity": "medium",
            "status": "pass" if API_AUTH_ENABLED else "warn",
            "title": "Dashboard API authentication",
            "finding": "API auth enabled" if API_AUTH_ENABLED else "API auth is not enabled",
            "recommendation": "Add token auth before exposing any write/remediation action.",
        },
        {
            "id": "security.least_privilege",
            "category": "security",
            "severity": "medium",
            "status": "warn",
            "title": "IAM policies should be reviewed for least privilege",
            "finding": "Some Lambda permissions use broad resources for demo simplicity",
            "recommendation": "Scope IAM actions by ARN before production use.",
        },
        {
            "id": "reliability.ec2_state",
            "category": "reliability",
            "severity": "high",
            "status": "pass" if get_status_payload().get("ec2") == "running" else "fail",
            "title": "Demo EC2 application is running",
            "finding": f"EC2 state is {get_status_payload().get('ec2')}",
            "recommendation": "If stopped unexpectedly, use self-healing or restart through SSM.",
        },
        {
            "id": "reliability.cpu_alarm",
            "category": "reliability",
            "severity": "medium",
            "status": "pass" if cpu.get("status") != "alarm" else "warn",
            "title": "CPU stays below alarm threshold",
            "finding": f"Current CPU is {cpu.get('current', 0)}%",
            "recommendation": "Investigate high CPU or trigger self-healing workflow.",
        },
        {
            "id": "reliability.lambda_errors",
            "category": "reliability",
            "severity": "medium",
            "status": "pass"
            if lambdas.get("self_healing", {}).get("errors", 0) == 0
            and lambdas.get("finops", {}).get("errors", 0) == 0
            else "warn",
            "title": "Automation Lambda functions have no errors",
            "finding": "No Lambda errors found in current window",
            "recommendation": "Check CloudWatch logs if Lambda errors increase.",
        },
        {
            "id": "operations.mock_mode",
            "category": "operations",
            "severity": "info",
            "status": "pass",
            "title": "Free local mode is available",
            "finding": f"APP_MODE={APP_MODE}",
            "recommendation": "Use mock mode for development and UI demos without AWS cost.",
        },
        {
            "id": "operations.evidence",
            "category": "operations",
            "severity": "info",
            "status": "pass",
            "title": "Incident evidence pipeline exists",
            "finding": "Incident API and DynamoDB-backed workflow are available",
            "recommendation": "Capture incidents in reports after demos.",
        },
    ]

    for check in checks:
        check["free_safe"] = check["status"] != "fail"

    return checks


def build_governance_score():
    checks = build_policy_checks()
    categories = {
        "cost": {"score": 100, "label": "Cost"},
        "security": {"score": 100, "label": "Security"},
        "reliability": {"score": 100, "label": "Reliability"},
        "operations": {"score": 100, "label": "Operations"},
    }
    penalties = {"fail": 22, "warn": 9, "pass": 0}

    for check in checks:
        category = check["category"]
        if category in categories:
            categories[category]["score"] = max(
                0, categories[category]["score"] - penalties.get(check["status"], 0)
            )

    overall = round(
        sum(category["score"] for category in categories.values()) / len(categories)
    )
    findings = sorted(
        [check for check in checks if check["status"] != "pass"],
        key=lambda item: severity_rank(item["severity"]),
        reverse=True,
    )

    return {
        "overall": overall,
        "grade": "A"
        if overall >= 90
        else "B"
        if overall >= 80
        else "C"
        if overall >= 70
        else "D",
        "categories": categories,
        "findings": findings,
        "recommended_actions": [
            {
                "title": finding["title"],
                "recommendation": finding["recommendation"],
                "severity": finding["severity"],
            }
            for finding in findings[:5]
        ],
        "mode": APP_MODE,
        "generated_at": utc_now(),
    }


def build_drift_report():
    checks = [
        {
            "id": "terraform.public_ipv4",
            "resource": "aws_eip.app",
            "expected": "controlled by enable_public_ipv4",
            "observed": "enabled" if ENABLE_PUBLIC_IPV4 else "disabled",
            "status": "watch" if ENABLE_PUBLIC_IPV4 else "clean",
            "recommendation": "Disable after live demos if public access is not required.",
        },
        {
            "id": "terraform.flow_logs",
            "resource": "aws_flow_log.main",
            "expected": "controlled by enable_vpc_flow_logs",
            "observed": "enabled" if ENABLE_VPC_FLOW_LOGS else "disabled",
            "status": "watch" if ENABLE_VPC_FLOW_LOGS else "clean",
            "recommendation": "Keep disabled for lowest-cost local/demo posture.",
        },
        {
            "id": "terraform.ssh",
            "resource": "aws_security_group.app",
            "expected": "public SSH disabled",
            "observed": "enabled" if ENABLE_PUBLIC_SSH else "disabled",
            "status": "drift" if ENABLE_PUBLIC_SSH else "clean",
            "recommendation": "Remove 0.0.0.0/0 SSH and use SSM.",
        },
    ]

    if not is_mock_mode():
        status = get_status_payload()
        checks.append(
            {
                "id": "aws.ec2_state",
                "resource": INSTANCE_ID,
                "expected": "running during live demo",
                "observed": status.get("ec2", "unknown"),
                "status": "clean" if status.get("ec2") == "running" else "drift",
                "recommendation": "Restart only if a live demo endpoint is required.",
            }
        )

    summary = "drift"
    if all(check["status"] == "clean" for check in checks):
        summary = "clean"
    elif all(check["status"] in ["clean", "watch"] for check in checks):
        summary = "watch"

    return {
        "status": summary,
        "checks": checks,
        "mode": APP_MODE,
        "generated_at": utc_now(),
    }


def prioritize_incidents():
    incidents = get_incidents_payload().get("incidents", [])
    severity_by_type = {
        "EC2_STOPPED": ("critical", 95, "Confirm self-healing started the instance and record recovery time."),
        "HIGH_CPU": ("high", 82, "Check CPU trend and Lambda remediation logs."),
        "COST_ANOMALY": ("high", 80, "Review recent resource changes and disable nonessential public resources."),
        "COST_RISK": ("medium", 68, "Switch to mock/free mode after demo."),
        "S3_LIFECYCLE": ("medium", 58, "Confirm lifecycle policy is applied only to intended buckets."),
    }

    prioritized = []
    for incident in incidents:
        incident_type = incident.get("incident_type", "EVENT")
        severity, base_score, action = severity_by_type.get(
            incident_type, ("low", 35, "Review and annotate the event.")
        )
        prioritized.append(
            {
                **incident,
                "severity": severity,
                "priority_score": base_score,
                "next_action": action,
            }
        )

    prioritized.sort(key=lambda item: item["priority_score"], reverse=True)
    return {"incidents": prioritized, "count": len(prioritized), "mode": APP_MODE}


def build_report_markdown():
    score = build_governance_score()
    drift = build_drift_report()
    incidents = prioritize_incidents()

    lines = [
        "# Cloud Governance Report",
        "",
        f"Generated: {utc_now()}",
        f"Mode: {APP_MODE}",
        f"Overall Score: {score['overall']} ({score['grade']})",
        "",
        "## Category Scores",
    ]

    for key, item in score["categories"].items():
        lines.append(f"- {item['label']}: {item['score']}")

    lines.extend(["", "## Recommended Actions"])
    if score["recommended_actions"]:
        for action in score["recommended_actions"]:
            lines.append(
                f"- [{action['severity'].upper()}] {action['title']}: {action['recommendation']}"
            )
    else:
        lines.append("- No high-priority actions.")

    lines.extend(["", "## Drift Detector", f"Status: {drift['status']}"])
    for check in drift["checks"]:
        lines.append(
            f"- {check['resource']}: {check['status']} "
            f"(expected: {check['expected']}, observed: {check['observed']})"
        )

    lines.extend(["", "## Incident Priority"])
    if incidents["incidents"]:
        for incident in incidents["incidents"][:5]:
            lines.append(
                f"- {incident['incident_type']} / {incident['severity']} / "
                f"{incident['priority_score']}: {incident['next_action']}"
            )
    else:
        lines.append("- No incidents.")

    return "\n".join(lines)


@app.route("/")
def home():
    return jsonify(
        {
            "status": "healthy",
            "service": "Autonomous Cloud Governance",
            "assistant": "enabled",
            "mode": APP_MODE,
            "timestamp": utc_now(),
        }
    )


@app.route("/health")
def health():
    return jsonify({"status": "ok", "assistant": "enabled", "mode": APP_MODE}), 200


@app.route("/metrics")
def metrics():
    return jsonify(
        {
            "cpu_usage": "monitored",
            "memory_usage": "monitored",
            "auto_healing": "enabled",
            "finops": "enabled",
            "governance_assistant": "enabled",
            "mode": APP_MODE,
        }
    )


@app.route("/api/cpu")
def api_cpu():
    return jsonify(get_cpu_payload())


@app.route("/api/incidents")
def api_incidents():
    return jsonify(get_incidents_payload())


@app.route("/api/lambda-stats")
def api_lambda_stats():
    return jsonify(get_lambda_stats_payload())


@app.route("/api/status")
def api_status():
    return jsonify(get_status_payload())


@app.route("/api/policy-checks")
def api_policy_checks():
    checks = build_policy_checks()
    return jsonify(
        {
            "checks": checks,
            "count": len(checks),
            "failing": len([check for check in checks if check["status"] == "fail"]),
            "warnings": len([check for check in checks if check["status"] == "warn"]),
            "mode": APP_MODE,
            "generated_at": utc_now(),
        }
    )


@app.route("/api/governance-score")
def api_governance_score():
    return jsonify(build_governance_score())


@app.route("/api/drift")
def api_drift():
    return jsonify(build_drift_report())


@app.route("/api/incident-priority")
def api_incident_priority():
    return jsonify(prioritize_incidents())


@app.route("/api/report")
def api_report():
    markdown = build_report_markdown()
    return jsonify(
        {
            "markdown": markdown,
            "summary": {
                "score": build_governance_score()["overall"],
                "drift": build_drift_report()["status"],
                "incident_count": prioritize_incidents()["count"],
            },
            "mode": APP_MODE,
            "generated_at": utc_now(),
        }
    )


@app.route("/api/assistant-summary")
def api_assistant_summary():
    return jsonify(
        {
            "score": build_governance_score(),
            "policies": build_policy_checks(),
            "drift": build_drift_report(),
            "incidents": prioritize_incidents(),
            "mode": APP_MODE,
            "generated_at": utc_now(),
        }
    )


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=PORT, debug=False)
