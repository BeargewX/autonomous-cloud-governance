import boto3
import json
import os
import uuid
from datetime import datetime

ec2 = boto3.client('ec2', region_name='ap-southeast-1')
dynamodb = boto3.resource('dynamodb', region_name='ap-southeast-1')
sns = boto3.client('sns', region_name='ap-southeast-1')

TABLE_NAME = os.environ.get('DYNAMODB_TABLE', 'cloud-governance-incident-log')
SNS_TOPIC_ARN = os.environ.get('SNS_TOPIC_ARN', '')

def log_incident(incident_type, instance_id, action_taken, status):
    table = dynamodb.Table(TABLE_NAME)
    table.put_item(Item={
        'incident_id': str(uuid.uuid4()),
        'timestamp': datetime.utcnow().isoformat(),
        'incident_type': incident_type,
        'instance_id': instance_id,
        'action_taken': action_taken,
        'status': status
    })

def notify(subject, message):
    if SNS_TOPIC_ARN:
        sns.publish(
            TopicArn=SNS_TOPIC_ARN,
            Subject=subject,
            Message=message
        )

def heal_high_cpu(instance_id):
    print(f"[Self-Healing] CPU สูงบน {instance_id} — กำลังแก้ไข...")
    try:
        ec2.reboot_instances(InstanceIds=[instance_id])
        log_incident('HIGH_CPU', instance_id, 'REBOOT', 'SUCCESS')
        notify(
            f'[Auto-Healed] CPU High on {instance_id}',
            f'Instance {instance_id} was automatically rebooted due to high CPU usage.'
        )
        print(f"[Self-Healing] Reboot สำเร็จ: {instance_id}")
    except Exception as e:
        log_incident('HIGH_CPU', instance_id, 'REBOOT', f'FAILED: {str(e)}')
        print(f"[Self-Healing] Error: {e}")

def heal_instance_stopped(instance_id):
    print(f"[Self-Healing] Instance หยุดทำงาน {instance_id} — กำลังเปิดใหม่...")
    try:
        ec2.start_instances(InstanceIds=[instance_id])
        log_incident('INSTANCE_STOPPED', instance_id, 'START', 'SUCCESS')
        notify(
            f'[Auto-Healed] Instance Stopped {instance_id}',
            f'Instance {instance_id} was automatically started.'
        )
        print(f"[Self-Healing] Start สำเร็จ: {instance_id}")
    except Exception as e:
        log_incident('INSTANCE_STOPPED', instance_id, 'START', f'FAILED: {str(e)}')
        print(f"[Self-Healing] Error: {e}")

def lambda_handler(event, context):
    print(f"[Self-Healing] Event: {json.dumps(event)}")

    detail_type = event.get('detail-type', '')
    detail = event.get('detail', {})

    # CloudWatch Alarm — CPU High
    if detail_type == 'CloudWatch Alarm State Change':
        alarm_name = detail.get('alarmName', '')
        state = detail.get('state', {}).get('value', '')

        if 'cpu-high' in alarm_name and state == 'ALARM':
            dimensions = detail.get('configuration', {}).get('metrics', [{}])[0].get('metricStat', {}).get('metric', {}).get('dimensions', {})
            instance_id = dimensions.get('InstanceId', '')
            if instance_id:
                heal_high_cpu(instance_id)

    # EC2 State Change — Instance Stopped
    elif detail_type == 'EC2 Instance State-change Notification':
        state = detail.get('state', '')
        instance_id = detail.get('instance-id', '')
        if state == 'stopped' and instance_id:
            heal_instance_stopped(instance_id)

    return {'statusCode': 200, 'body': 'Self-healing complete'}