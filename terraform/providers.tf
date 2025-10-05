# Provider configuration
provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      ManagedBy = "terraform"
      Generated = "true"
      Project   = var.project_name
    }
  }
}

# Configure multiple AWS providers for different regions if needed
# provider "aws" {
#   alias  = "us-west-2"
#   region = "us-west-2"
# }
