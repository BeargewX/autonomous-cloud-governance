output "vpc_id" {
  description = "VPC ID"
  value       = module.infrastructure.vpc_id
}

output "public_subnet_ids" {
  description = "Public Subnet IDs"
  value       = module.infrastructure.public_subnet_ids
}

output "private_subnet_ids" {
  description = "Private Subnet IDs"
  value       = module.infrastructure.private_subnet_ids
}

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
