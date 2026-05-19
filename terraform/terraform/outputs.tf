output "alb_dns_name" {
  description = "ALB DNS Name — เอาไว้เปิดเว็บ"
  value       = module.infrastructure.alb_dns_name
}

output "dynamodb_table_name" {
  description = "DynamoDB Table Name"
  value       = module.infrastructure.dynamodb_table_name
}

output "sns_topic_arn" {
  description = "SNS Topic ARN"
  value       = module.infrastructure.sns_topic_arn
}
