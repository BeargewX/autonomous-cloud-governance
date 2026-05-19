import boto3
import json
import os
from datetime import datetime, timedelta

ec2 = boto3.client('ec2', region_name='ap-southeast-1')
cloudwatch = boto3.client('cloudwatch', region_name='ap-southeast-1')
sns = boto3.client('sns', region_name='ap-southeast-1')
dynamodb = boto3.resource('dynamodb', region_name='ap-southeast-1')

SNS_TOPIC_ARN = os.environ.get('SNS_TOPIC_ARN', '')
TABLE_NAME = os.environ.get('DYNAMODB_TABLE', 'cloud-governance-incident-log')

def get_instance_cpu_avg(instance_id, days=7):
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(days=days)

    response = cloudwatch.get_metric_statistics(
        Namespace='AWS/EC2',
        MetricName='CPUUtilization',
        Dimensions=[{'Name': 'InstanceId', 'Value': instance_id}],
        StartTime=start_time,
        EndTime=end_time,
        Period=86400,
        Statistics=['Average']
    )

    datapoints = response.get('Datapoints', [])
    if not datapoints:
        return 0
    return sum(d['Average'] for d in datapoints) / len(datapoints)

def check_idle_instances():
    print("[FinOps] กำลังเช็ค idle instances...")
    response = ec2.describe_instances(
        Filters=[{'Name': 'instance-state-name', 'Values': ['running']}]
    )

    idle_instances = []
    for reservation in response['Reservations']:
        for instance in reservation['Instances']:
            instance_id = instance['InstanceId']
            cpu_avg = get_instance_cpu_avg(instance_id)
            print(f"[FinOps] {instance_id}: CPU avg = {cpu_avg:.2f}%")

            if cpu_avg < 5:
                idle_instances.append({
                    'instance_id': instance_id,
                    'cpu_avg': cpu_avg
                })

    if idle_instances:
        message = f"[FinOps Alert] พบ {len(idle_instances)} idle instances:\n"
        for i in idle_instances:
            message += f"- {i['instance_id']}: CPU avg {i['cpu_avg']:.2f}%\n"
        message += "\nแนะนำให้ stop หรือ terminate instances เหล่านี้เพื่อประหยัดค่าใช้จ่าย"

        if SNS_TOPIC_ARN:
            sns.publish(
                TopicArn=SNS_TOPIC_ARN,
                Subject='[FinOps] Idle Instances Detected',
                Message=message
            )
        print(f"[FinOps] แจ้งเตือนส่งแล้ว: {len(idle_instances)} instances")

    return idle_instances

def lambda_handler(event, context):
    print(f"[FinOps] เริ่มต้น FinOps check: {datetime.utcnow().isoformat()}")
    idle = check_idle_instances()
    return {
        'statusCode': 200,
        'body': json.dumps({
            'idle_instances_found': len(idle),
            'timestamp': datetime.utcnow().isoformat()
        })
    }