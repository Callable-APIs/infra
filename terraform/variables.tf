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
