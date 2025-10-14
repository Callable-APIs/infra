# Main Terraform configuration
# Generated on 2025-01-27 17:00:00 UTC
# 
# This file contains the main infrastructure configuration
# for the CallableAPIs infrastructure in us-west-2.

terraform {
  required_version = ">= 1.5"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    cloudflare = {
      source  = "cloudflare/cloudflare"
      version = "~> 4.0"
    }
  }
}
