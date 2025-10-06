# Multi-region AWS provider configuration
# Generated on 2025-01-05 16:57:00 UTC

# Default provider (us-east-1)
provider "aws" {
  region = "us-east-1"
  alias  = "us_east_1"

  default_tags {
    tags = {
      ManagedBy = "terraform"
      Generated = "true"
      Project   = var.project_name
      Region    = "us-east-1"
    }
  }
}

# us-east-2 provider
provider "aws" {
  region = "us-east-2"
  alias  = "us_east_2"

  default_tags {
    tags = {
      ManagedBy = "terraform"
      Generated = "true"
      Project   = var.project_name
      Region    = "us-east-2"
    }
  }
}

# us-west-2 provider (for future migration)
provider "aws" {
  region = "us-west-2"
  alias  = "us_west_2"

  default_tags {
    tags = {
      ManagedBy = "terraform"
      Generated = "true"
      Project   = var.project_name
      Region    = "us-west-2"
    }
  }
}