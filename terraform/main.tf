terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  cloud {
    organization = "cloud-governance-beargewx"
    workspaces {
      name = "autonomous-cloud-governance"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

module "infrastructure" {
  source = "./modules/infrastructure"

  project_name         = var.project_name
  environment          = var.environment
  aws_region           = var.aws_region
  vpc_cidr             = var.vpc_cidr
  enable_public_ipv4   = var.enable_public_ipv4
  enable_public_ssh    = var.enable_public_ssh
  enable_vpc_flow_logs = var.enable_vpc_flow_logs
  ec2_cpu_credits      = var.ec2_cpu_credits
  common_tags          = var.common_tags
}
