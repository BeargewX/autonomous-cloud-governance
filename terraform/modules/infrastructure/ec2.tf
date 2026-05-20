# DynamoDB table for incident logs
resource "aws_dynamodb_table" "incident_log" {
  name         = "${var.project_name}-incident-log"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "incident_id"
  range_key    = "timestamp"

  attribute {
    name = "incident_id"
    type = "S"
  }

  attribute {
    name = "timestamp"
    type = "S"
  }

  tags = merge(var.common_tags, {
    Name        = "${var.project_name}-incident-log"
    Environment = var.environment
  })
}

# SNS topic for alerts
resource "aws_sns_topic" "alerts" {
  name = "${var.project_name}-alerts"

  tags = merge(var.common_tags, {
    Name = "${var.project_name}-alerts"
  })
}

# IAM Role for EC2
resource "aws_iam_role" "ec2_role" {
  name = "${var.project_name}-ec2-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "ec2.amazonaws.com"
      }
    }]
  })

  tags = merge(var.common_tags, {
    Name = "${var.project_name}-ec2-role"
  })
}

resource "aws_iam_role_policy_attachment" "ec2_ssm" {
  role       = aws_iam_role.ec2_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
}

resource "aws_iam_role_policy_attachment" "ec2_cloudwatch" {
  role       = aws_iam_role.ec2_role.name
  policy_arn = "arn:aws:iam::aws:policy/CloudWatchAgentServerPolicy"
}

resource "aws_iam_role_policy_attachment" "ec2_dynamodb" {
  role       = aws_iam_role.ec2_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess"
}

resource "aws_iam_instance_profile" "ec2_profile" {
  name = "${var.project_name}-ec2-profile"
  role = aws_iam_role.ec2_role.name

  tags = merge(var.common_tags, {
    Name = "${var.project_name}-ec2-profile"
  })
}

# Latest Amazon Linux 2 AMI
data "aws_ami" "amazon_linux" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["amzn2-ami-hvm-*-x86_64-gp2"]
  }
}

# EC2 Instance
resource "aws_instance" "app" {
  ami                         = data.aws_ami.amazon_linux.id
  instance_type               = "t3.micro"
  subnet_id                   = aws_subnet.public_1.id
  associate_public_ip_address = var.enable_public_ipv4
  vpc_security_group_ids      = [aws_security_group.app.id]
  iam_instance_profile        = aws_iam_instance_profile.ec2_profile.name

  credit_specification {
    cpu_credits = var.ec2_cpu_credits
  }

  user_data = base64encode(<<-EOF
#!/bin/bash
yum update -y
yum install -y python3 python3-pip amazon-cloudwatch-agent
mkdir -p /app
cat > /app/app.py << 'APPEOF'
from flask import Flask, jsonify
import sqlite3
from datetime import datetime
app = Flask(__name__)
DB_PATH = '/app/data.db'
def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute('CREATE TABLE IF NOT EXISTS incidents (id INTEGER PRIMARY KEY, message TEXT, timestamp TEXT)')
    conn.commit()
    conn.close()
@app.route('/')
def home():
    return jsonify({'status': 'healthy', 'service': 'Autonomous Cloud Governance', 'timestamp': datetime.utcnow().isoformat()})
@app.route('/health')
def health():
    return jsonify({'status': 'ok'}), 200
@app.route('/metrics')
def metrics():
    return jsonify({'cpu_usage': 'monitored', 'memory_usage': 'monitored', 'auto_healing': 'enabled', 'finops': 'enabled'})
if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=False)
APPEOF
pip3 install flask boto3
cd /app
nohup python3 app.py > /var/log/app.log 2>&1 &
EOF
  )

  tags = merge(var.common_tags, {
    Name        = "${var.project_name}-app"
    Environment = var.environment
  })
}

# Elastic IP. Disable this outside live demos to avoid public IPv4 hourly cost.
resource "aws_eip" "app" {
  count    = var.enable_public_ipv4 ? 1 : 0
  instance = aws_instance.app.id
  domain   = "vpc"

  tags = merge(var.common_tags, {
    Name = "${var.project_name}-app-eip"
  })
}

# CloudWatch CPU Alarm
resource "aws_cloudwatch_metric_alarm" "cpu_high" {
  alarm_name          = "${var.project_name}-cpu-high"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "CPUUtilization"
  namespace           = "AWS/EC2"
  period              = 120
  statistic           = "Average"
  threshold           = 70
  alarm_description   = "CPU > 70% - Self-healing triggered"
  alarm_actions       = [aws_sns_topic.alerts.arn]

  dimensions = {
    InstanceId = aws_instance.app.id
  }

  tags = merge(var.common_tags, {
    Name = "${var.project_name}-cpu-high"
  })
}
