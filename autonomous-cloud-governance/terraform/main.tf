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
  region = "ap-southeast-1"
}

module "infrastructure" {
  source      = "./modules/infrastructure"
  db_password = var.db_password
}
