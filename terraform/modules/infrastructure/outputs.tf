output "vpc_id" {
  description = "VPC ID"
  value       = aws_vpc.main.id
}

output "public_subnet_ids" {
  description = "Public Subnet IDs"
  value       = [aws_subnet.public_1.id, aws_subnet.public_2.id]
}

output "private_subnet_ids" {
  description = "Private Subnet IDs"
  value       = [aws_subnet.private_1.id, aws_subnet.private_2.id]
}

output "app_public_ip" {
  description = "EC2 public IP. Null when enable_public_ipv4=false."
  value       = try(aws_eip.app[0].public_ip, null)
}

output "dynamodb_table_name" {
  description = "DynamoDB incident log table name"
  value       = aws_dynamodb_table.incident_log.name
}

output "sns_topic_arn" {
  description = "SNS alerts topic ARN"
  value       = aws_sns_topic.alerts.arn
}
