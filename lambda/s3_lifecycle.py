import boto3
import json
import os
from datetime import datetime

s3 = boto3.client('s3', region_name='ap-southeast-1')
sns = boto3.client('sns', region_name='ap-southeast-1')

SNS_TOPIC_ARN = os.environ.get('SNS_TOPIC_ARN', '')

def set_lifecycle_policy(bucket_name):
    lifecycle_config = {
        'Rules': [
            {
                'ID': 'move-to-ia-after-30-days',
                'Status': 'Enabled',
                'Filter': {'Prefix': ''},
                'Transitions': [
                    {
                        'Days': 30,
                        'StorageClass': 'STANDARD_IA'
                    },
                    {
                        'Days': 90,
                        'StorageClass': 'GLACIER'
                    }
                ],
                'Expiration': {
                    'Days': 365
                }
            }
        ]
    }

    s3.put_bucket_lifecycle_configuration(
        Bucket=bucket_name,
        LifecycleConfiguration=lifecycle_config
    )
    print(f"[S3 Lifecycle] ตั้งค่า lifecycle สำหรับ {bucket_name} สำเร็จ")

def lambda_handler(event, context):
    print(f"[S3 Lifecycle] เริ่มต้น: {datetime.utcnow().isoformat()}")
    try:
        response = s3.list_buckets()
        buckets = [b['Name'] for b in response['Buckets']]
        updated = []

        for bucket in buckets:
            try:
                s3.get_bucket_lifecycle_configuration(Bucket=bucket)
                print(f"[S3 Lifecycle] {bucket} มี lifecycle แล้ว")
            except s3.exceptions.ClientError:
                set_lifecycle_policy(bucket)
                updated.append(bucket)

        if updated and SNS_TOPIC_ARN:
            sns.publish(
                TopicArn=SNS_TOPIC_ARN,
                Subject='[FinOps] S3 Lifecycle Policies Applied',
                Message=f"ตั้งค่า lifecycle policy สำหรับ {len(updated)} buckets:\n" + '\n'.join(updated)
            )

        return {
            'statusCode': 200,
            'body': json.dumps({
                'buckets_updated': len(updated),
                'timestamp': datetime.utcnow().isoformat()
            })
        }
    except Exception as e:
        print(f"[S3 Lifecycle] Error: {e}")
        return {'statusCode': 500, 'body': str(e)}