import boto3
import json
import os
from datetime import datetime, timedelta

ce = boto3.client('ce', region_name='us-east-1')
sns = boto3.client('sns', region_name='ap-southeast-1')
dynamodb = boto3.resource('dynamodb', region_name='ap-southeast-1')

SNS_TOPIC_ARN = os.environ.get('SNS_TOPIC_ARN', '')
TABLE_NAME = os.environ.get('DYNAMODB_TABLE', 'cloud-governance-incident-log')

def get_daily_cost(days_ago=1):
    end = datetime.utcnow().date()
    start = end - timedelta(days=days_ago)
    response = ce.get_cost_and_usage(
        TimePeriod={
            'Start': str(start),
            'End': str(end)
        },
        Granularity='DAILY',
        Metrics=['UnblendedCost'],
        GroupBy=[{'Type': 'DIMENSION', 'Key': 'SERVICE'}]
    )
    return response['ResultsByTime']

def detect_anomaly(results):
    anomalies = []
    for result in results:
        for group in result['Groups']:
            service = group['Keys'][0]
            amount = float(group['Metrics']['UnblendedCost']['Amount'])
            if amount > 1.0:
                anomalies.append({
                    'service': service,
                    'amount': amount,
                    'date': result['TimePeriod']['Start']
                })
    return anomalies

def lambda_handler(event, context):
    print(f"[Cost Anomaly] เริ่มต้น: {datetime.utcnow().isoformat()}")
    try:
        results = get_daily_cost(days_ago=2)
        anomalies = detect_anomaly(results)

        if anomalies:
            message = "[FinOps Alert] พบค่าใช้จ่ายผิดปกติ:\n"
            for a in anomalies:
                message += f"- {a['service']}: ${a['amount']:.4f} ({a['date']})\n"

            if SNS_TOPIC_ARN:
                sns.publish(
                    TopicArn=SNS_TOPIC_ARN,
                    Subject='[FinOps] Cost Anomaly Detected',
                    Message=message
                )
            print(f"[Cost Anomaly] แจ้งเตือน: {len(anomalies)} anomalies")
        else:
            print("[Cost Anomaly] ไม่พบความผิดปกติ")

        return {
            'statusCode': 200,
            'body': json.dumps({
                'anomalies': len(anomalies),
                'timestamp': datetime.utcnow().isoformat()
            })
        }
    except Exception as e:
        print(f"[Cost Anomaly] Error: {e}")
        return {'statusCode': 500, 'body': str(e)}