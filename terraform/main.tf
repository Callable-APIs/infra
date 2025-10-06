# Main Terraform configuration
# Generated on 2025-01-05 16:57:00 UTC
# 
# This file contains the main infrastructure configuration
# generated from your current AWS deployment.
# 
# IMPORTANT: This configuration uses import blocks to import existing resources.
# Run 'terraform plan' to verify the configuration matches your current infrastructure.

terraform {
  required_version = ">= 1.5"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

# This file now serves as the main configuration file.
# Region-specific resources are defined in:
# - us_east_1.tf (us-east-1 resources)
# - us_east_2.tf (us-east-2 resources)
# - providers.tf (multi-region provider configuration)