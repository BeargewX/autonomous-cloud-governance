variable "project_name" {
  description = "Project name used for resource naming"
  type        = string
  default     = "cloud-governance"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "dev"
}

variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "ap-southeast-1"
}

variable "vpc_cidr" {
  description = "CIDR block for VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "db_password" {
  description = "RDS database password"
  type        = string
  sensitive   = true
  default     = "ChangeMe123!"
}
