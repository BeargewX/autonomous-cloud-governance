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

output "web_sg_id" {
  description = "Web Security Group ID"
  value       = aws_security_group.web.id
}

output "app_sg_id" {
  description = "App Security Group ID"
  value       = aws_security_group.app.id
}

output "db_sg_id" {
  description = "DB Security Group ID"
  value       = aws_security_group.db.id
}

output "lambda_sg_id" {
  description = "Lambda Security Group ID"
  value       = aws_security_group.lambda.id
}