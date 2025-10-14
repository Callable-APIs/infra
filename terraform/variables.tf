# Variable definitions
variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Name of the project"
  type        = string
  default     = "aws-infrastructure"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "production"
}

# Route53 zone ID for callableapis.com
variable "route53_zone_id" {
  description = "Route53 hosted zone ID for callableapis.com"
  type        = string
  default     = "ZJ57N2O5R20OE"
}

# Cloudflare configuration
variable "cloudflare_api_token" {
  description = "Cloudflare API token"
  type        = string
  sensitive   = true
}

variable "cloudflare_zone_id" {
  description = "Cloudflare zone ID for callableapis.com"
  type        = string
  default     = "c9b61ba12197864c7e0236bfb9abdcba"
}

# Add more variables as needed
variable "common_tags" {
  description = "Common tags to apply to all resources"
  type        = map(string)
  default = {
    Environment = "production"
    Project     = "aws-infrastructure"
    ManagedBy   = "terraform"
  }
}
