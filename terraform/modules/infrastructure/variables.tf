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
  description = "Attach a public IPv4/Elastic IP to the EC2 demo app."
  type        = bool
  default     = false
}

variable "enable_public_ssh" {
  description = "Open SSH from the internet."
  type        = bool
  default     = false
}

variable "enable_vpc_flow_logs" {
  description = "Enable VPC Flow Logs."
  type        = bool
  default     = false
}

variable "ec2_cpu_credits" {
  description = "T3 CPU credit mode."
  type        = string
  default     = "standard"
}

variable "common_tags" {
  description = "Tags applied to supported resources."
  type        = map(string)
  default     = {}
}
