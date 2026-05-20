variable "project_name" {
  description = "Project name"
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

variable "enable_public_ipv4" {
  description = "Attach a public IPv4/Elastic IP to the EC2 demo app. Public IPv4 has hourly AWS cost, so disable this outside live demos."
  type        = bool
  default     = true
}

variable "enable_public_ssh" {
  description = "Open SSH from the internet. Prefer SSM Session Manager for safer/free operations."
  type        = bool
  default     = false
}

variable "enable_vpc_flow_logs" {
  description = "Enable VPC Flow Logs. Useful for governance demos, but can create CloudWatch Logs cost if traffic is high."
  type        = bool
  default     = true
}

variable "ec2_cpu_credits" {
  description = "T3 CPU credit mode. Use standard to avoid unlimited CPU burst charges."
  type        = string
  default     = "standard"

  validation {
    condition     = contains(["standard", "unlimited"], var.ec2_cpu_credits)
    error_message = "ec2_cpu_credits must be standard or unlimited."
  }
}

variable "common_tags" {
  description = "Tags applied to supported resources for cost tracking."
  type        = map(string)
  default = {
    Project  = "autonomous-cloud-governance"
    CostMode = "free-demo"
    Owner    = "student"
  }
}
