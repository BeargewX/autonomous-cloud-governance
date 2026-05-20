import boto3
import json
import os
from datetime import datetime, timedelta

dynamodb = boto3.resource('dynamodb', region_name='ap-southeast-1')
sns = boto3.client('sns', region_name='ap-southeast-1')
cw = boto3.client('cloudwatch', region_name='ap-southeast-1')

SNS_TOPIC_ARN = os.environ.get('SNS_TOPIC_ARN', '')
TABLE_NAME = os.environ.get('DYNAMODB_TABLE', 'cloud-governance-incident-log')
INSTANCE_ID = 'i-0327c7e7774cbc046'

def get_incidents_this_week():
    table = dynamodb.Table(TABLE_NAME)
    week_ago = (datetime.utcnow() - timedelta(days=7)).isoformat()
    response = table.scan()
    items = response.get('Items', [])
    return [i for i in items if i.get('timestamp', '') >= week_ago]

def get_avg_cpu():
    end = datetime.utcnow()
    start = end - timedelta(days=7)
    response = cw.get_metric_statistics(
        Namespace='AWS/EC2',
        MetricName='CPUUtilization',
        Dimensions=[{'Name': 'InstanceId', 'Value': INSTANCE_ID}],
        StartTime=start,
        EndTime=end,
        Period=604800,
        Statistics=['Average']
    )
    pts = response.get('Datapoints', [])
    return round(pts[0]['Average'], 2) if pts else 0

def lambda_handler(event, context):
    print(f"[Weekly Report] เริ่มต้น: {datetime.utcnow().isoformat()}")

    incidents = get_incidents_this_week()
    avg_cpu = get_avg_cpu()

    success = [i for i in incidents if i.get('status') == 'SUCCESS']
    failed = [i for i in incidents if i.get('status', '').startswith('FAILED')]

    report = f"""
╔══════════════════════════════════════════╗
   AUTONOMOUS CLOUD GOVERNANCE
   Weekly Report — {datetime.utcnow().strftime('%d %B %Y')}
╚══════════════════════════════════════════╝

📊 SYSTEM SUMMARY
─────────────────
- EC2 Instance: i-0327c7e7774cbc046
- Region: ap-southeast-1
- Average CPU: {avg_cpu}%
- Cost this week: $0.00 (Free Tier)

🔧 SELF-HEALING SUMMARY
────────────────────────
- Total incidents: {len(incidents)}
- Auto-healed successfully: {len(success)}
- Failed to heal: {len(failed)}
- Success rate: {round(len(success)/len(incidents)*100) if incidents else 100}%

📋 INCIDENT DETAILS
───────────────────
"""

    if incidents:
        for i in incidents:
            report += f"• [{i.get('timestamp', '')[:10]}] {i.get('incident_type')} → {i.get('action_taken')} ({i.get('status')})\n"
    else:
        report += "• ไม่มี incident สัปดาห์นี้ 🎉\n"

    report += f"""
💰 FINOPS
─────────
- EC2 t3.micro: Free Tier
- Lambda: Free Tier
- DynamoDB: Free Tier
- SNS: Free Tier
- Total: $0.00

═══════════════════════════════════════════
Autonomous Cloud Governance Platform
Generated: {datetime.utcnow().isoformat()}
═══════════════════════════════════════════
"""

    if SNS_TOPIC_ARN:
        sns.publish(
            TopicArn=SNS_TOPIC_ARN,
            Subject=f'[Weekly Report] Cloud Governance — {datetime.utcnow().strftime("%d %b %Y")}',
            Message=report
        )

    print(report)
    return {'statusCode': 200, 'body': json.dumps({'incidents': len(incidents), 'avg_cpu': avg_cpu})}