from flask import Flask, jsonify
import sqlite3
import boto3
import os
from datetime import datetime, timedelta

app = Flask(__name__)

DB_PATH = os.getenv("DB_PATH", "data.db")
REGION = os.getenv("AWS_REGION", "ap-southeast-1")
INSTANCE_ID = os.getenv("EC2_INSTANCE_ID", "i-0327c7e7774cbc046")
DYNAMODB_TABLE = os.getenv("DYNAMODB_TABLE", "cloud-governance-incident-log")


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


@app.route("/")
def home():
    return jsonify(
        {
            "status": "healthy",
            "service": "Autonomous Cloud Governance",
            "timestamp": datetime.utcnow().isoformat(),
        }
    )


@app.route("/health")
def health():
    return jsonify({"status": "ok"}), 200


@app.route("/metrics")
def metrics():
    return jsonify(
        {
            "cpu_usage": "monitored",
            "memory_usage": "monitored",
            "auto_healing": "enabled",
            "finops": "enabled",
        }
    )


@app.route("/api/cpu")
def api_cpu():
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
        return jsonify(
            {
                "current": current,
                "history": history,
                "instance_id": INSTANCE_ID,
                "status": "alarm"
                if current > 70
                else "warning"
                if current > 50
                else "ok",
            }
        )
    except Exception as e:
        return jsonify({"current": 0, "history": [], "error": str(e)})


@app.route("/api/incidents")
def api_incidents():
    try:
        db = boto3.resource("dynamodb", region_name=REGION)
        table = db.Table(DYNAMODB_TABLE)
        response = table.scan(Limit=10)
        items = sorted(
            response.get("Items", []), key=lambda x: x.get("timestamp", ""), reverse=True
        )
        return jsonify({"incidents": items, "count": len(items)})
    except Exception as e:
        return jsonify({"incidents": [], "count": 0, "error": str(e)})


@app.route("/api/lambda-stats")
def api_lambda_stats():
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

        return jsonify(
            {
                "self_healing": {
                    "invocations": get_lambda_metric(
                        "cloud-governance-self-healing", "Invocations"
                    ),
                    "errors": get_lambda_metric(
                        "cloud-governance-self-healing", "Errors"
                    ),
                },
                "finops": {
                    "invocations": get_lambda_metric(
                        "cloud-governance-finops", "Invocations"
                    ),
                    "errors": get_lambda_metric("cloud-governance-finops", "Errors"),
                },
            }
        )
    except Exception as e:
        return jsonify({"error": str(e)})


@app.route("/api/status")
def api_status():
    try:
        ec2 = boto3.client("ec2", region_name=REGION)
        response = ec2.describe_instances(InstanceIds=[INSTANCE_ID])
        state = response["Reservations"][0]["Instances"][0]["State"]["Name"]
        return jsonify({"ec2": state, "timestamp": datetime.utcnow().isoformat()})
    except Exception as e:
        return jsonify({"ec2": "unknown", "error": str(e)})


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=False)
