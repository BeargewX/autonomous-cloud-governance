# IAM Role สำหรับ Lambda
resource "aws_iam_role" "lambda_role" {
  name = "${var.project_name}-lambda-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "lambda.amazonaws.com"
      }
    }]
  })
}

resource "aws_iam_role_policy" "lambda_policy" {
  name = "${var.project_name}-lambda-policy"
  role = aws_iam_role.lambda_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "arn:aws:logs:*:*:*"
      },
      {
        Effect = "Allow"
        Action = [
          "ec2:DescribeInstances",
          "ec2:RebootInstances",
          "ec2:StartInstances",
          "ec2:StopInstances"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "dynamodb:PutItem",
          "dynamodb:GetItem",
          "dynamodb:Scan"
        ]
        Resource = aws_dynamodb_table.incident_log.arn
      },
      {
        Effect = "Allow"
        Action = ["sns:Publish"]
        Resource = aws_sns_topic.alerts.arn
      },
      {
        Effect = "Allow"
        Action = ["cloudwatch:GetMetricStatistics"]
        Resource = "*"
      }
      {
        Effect = "Allow"
        Action = [
          "ce:GetCostAndUsage",
          "ce:GetCostForecast"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "s3:ListBuckets",
          "s3:ListAllMyBuckets",
          "s3:GetBucketLifecycleConfiguration",
          "s3:PutBucketLifecycleConfiguration"
        ]
        Resource = "*"
      }
    ]
  })
}

# Lambda Self-Healing
# Lambda Self-Healing
resource "aws_lambda_function" "self_healing" {
  filename         = "${path.module}/lambda/self_healing.zip"
  function_name    = "${var.project_name}-self-healing"
  role             = aws_iam_role.lambda_role.arn
  handler          = "self_healing.lambda_handler"
  runtime          = "python3.11"
  source_code_hash = filebase64sha256("${path.module}/lambda/self_healing.zip")
  timeout          = 60

  environment {
    variables = {
      DYNAMODB_TABLE = aws_dynamodb_table.incident_log.name
      SNS_TOPIC_ARN  = aws_sns_topic.alerts.arn
    }
  }

  tags = {
    Name = "${var.project_name}-self-healing"
  }
}

# Lambda FinOps
resource "aws_lambda_function" "finops" {
  filename         = "${path.module}/lambda/finops.zip"
  function_name    = "${var.project_name}-finops"
  role             = aws_iam_role.lambda_role.arn
  handler          = "finops.lambda_handler"
  runtime          = "python3.11"
  source_code_hash = filebase64sha256("${path.module}/lambda/finops.zip")
  timeout          = 300

  environment {
    variables = {
      DYNAMODB_TABLE = aws_dynamodb_table.incident_log.name
      SNS_TOPIC_ARN  = aws_sns_topic.alerts.arn
    }
  }

  tags = {
    Name = "${var.project_name}-finops"
  }
}

# EventBridge — ตรวจจับ CloudWatch Alarm
resource "aws_cloudwatch_event_rule" "cpu_alarm" {
  name        = "${var.project_name}-cpu-alarm-rule"
  description = "Trigger self-healing when CPU alarm fires"

  event_pattern = jsonencode({
    source      = ["aws.cloudwatch"]
    detail-type = ["CloudWatch Alarm State Change"]
    detail = {
      alarmName = [{ prefix = "${var.project_name}-cpu" }]
      state = {
        value = ["ALARM"]
      }
    }
  })
}

resource "aws_cloudwatch_event_target" "self_healing" {
  rule      = aws_cloudwatch_event_rule.cpu_alarm.name
  target_id = "SelfHealingLambda"
  arn       = aws_lambda_function.self_healing.arn
}

resource "aws_lambda_permission" "allow_eventbridge_cpu" {
  statement_id  = "AllowEventBridgeCPU"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.self_healing.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.cpu_alarm.arn
}

# EventBridge — ตรวจจับ EC2 stopped
resource "aws_cloudwatch_event_rule" "ec2_stopped" {
  name        = "${var.project_name}-ec2-stopped-rule"
  description = "Trigger self-healing when EC2 stops"

  event_pattern = jsonencode({
    source      = ["aws.ec2"]
    detail-type = ["EC2 Instance State-change Notification"]
    detail = {
      state = ["stopped"]
    }
  })
}

resource "aws_cloudwatch_event_target" "self_healing_ec2" {
  rule      = aws_cloudwatch_event_rule.ec2_stopped.name
  target_id = "SelfHealingLambdaEC2"
  arn       = aws_lambda_function.self_healing.arn
}

resource "aws_lambda_permission" "allow_eventbridge_ec2" {
  statement_id  = "AllowEventBridgeEC2"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.self_healing.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.ec2_stopped.arn
}

# EventBridge — FinOps รันทุกคืนเที่ยงคืน
resource "aws_cloudwatch_event_rule" "finops_schedule" {
  name                = "${var.project_name}-finops-schedule"
  description         = "Run FinOps check every night at midnight"
  schedule_expression = "cron(0 0 * * ? *)"
}

resource "aws_cloudwatch_event_target" "finops" {
  rule      = aws_cloudwatch_event_rule.finops_schedule.name
  target_id = "FinOpsLambda"
  arn       = aws_lambda_function.finops.arn
}

resource "aws_lambda_permission" "allow_eventbridge_finops" {
  statement_id  = "AllowEventBridgeFinOps"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.finops.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.finops_schedule.arn
}

data "archive_file" "cost_anomaly" {
  type        = "zip"
  source_file = "${path.module}/lambda/cost_anomaly.py"
  output_path = "${path.module}/lambda/cost_anomaly.zip"
}

data "archive_file" "s3_lifecycle" {
  type        = "zip"
  source_file = "${path.module}/lambda/s3_lifecycle.py"
  output_path = "${path.module}/lambda/s3_lifecycle.zip"
}

resource "aws_lambda_function" "cost_anomaly" {
  filename         = "${path.module}/lambda/cost_anomaly.zip"
  function_name    = "${var.project_name}-cost-anomaly"
  role             = aws_iam_role.lambda_role.arn
  handler          = "cost_anomaly.lambda_handler"
  runtime          = "python3.11"
  source_code_hash = filebase64sha256("${path.module}/lambda/cost_anomaly.zip")
  timeout          = 300

  environment {
    variables = {
      DYNAMODB_TABLE = aws_dynamodb_table.incident_log.name
      SNS_TOPIC_ARN  = aws_sns_topic.alerts.arn
    }
  }

  tags = {
    Name = "${var.project_name}-cost-anomaly"
  }
}

resource "aws_lambda_function" "s3_lifecycle" {
  filename         = "${path.module}/lambda/s3_lifecycle.zip"
  function_name    = "${var.project_name}-s3-lifecycle"
  role             = aws_iam_role.lambda_role.arn
  handler          = "s3_lifecycle.lambda_handler"
  runtime          = "python3.11"
  source_code_hash = filebase64sha256("${path.module}/lambda/s3_lifecycle.zip")
  timeout          = 300

  environment {
    variables = {
      SNS_TOPIC_ARN = aws_sns_topic.alerts.arn
    }
  }

  tags = {
    Name = "${var.project_name}-s3-lifecycle"
  }
}

resource "aws_cloudwatch_event_rule" "cost_anomaly_schedule" {
  name                = "${var.project_name}-cost-anomaly-schedule"
  description         = "Run cost anomaly check every morning"
  schedule_expression = "cron(0 8 * * ? *)"
}

resource "aws_cloudwatch_event_target" "cost_anomaly" {
  rule      = aws_cloudwatch_event_rule.cost_anomaly_schedule.name
  target_id = "CostAnomalyLambda"
  arn       = aws_lambda_function.cost_anomaly.arn
}

resource "aws_lambda_permission" "allow_eventbridge_cost" {
  statement_id  = "AllowEventBridgeCost"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.cost_anomaly.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.cost_anomaly_schedule.arn
}