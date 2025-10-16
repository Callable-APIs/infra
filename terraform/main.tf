# Main Terraform configuration
# This file coordinates all cloud providers


# AWS Provider Configuration
provider "aws" {
  region     = var.aws_region
  access_key = var.aws_access_key_id
  secret_key = var.aws_secret_access_key
}

# Cloudflare Provider Configuration
provider "cloudflare" {
  api_token = var.cloudflare_api_token
}

# Cloudflare zone data source
data "cloudflare_zone" "callableapis" {
  name = "callableapis.com"
}

# AWS Infrastructure (moved from module for simplicity)
# Note: AWS resources are defined in aws/ directory but included here for now

# Cloudflare DNS Records
resource "cloudflare_record" "website_root" {
  zone_id = data.cloudflare_zone.callableapis.id
  name    = "callableapis.com"
  type    = "CNAME"
  content = "callableapis-usw2.com.s3-website.us-west-2.amazonaws.com"
  proxied = true
  comment = "S3 website endpoint"
}

resource "cloudflare_record" "website_www" {
  zone_id = data.cloudflare_zone.callableapis.id
  name    = "www"
  type    = "CNAME"
  content = "callableapis-usw2.com.s3-website.us-west-2.amazonaws.com"
  proxied = true
  comment = "S3 website endpoint"
}

resource "cloudflare_record" "api" {
  zone_id = data.cloudflare_zone.callableapis.id
  name    = "api"
  type    = "CNAME"
  content = "callableapis-java-env.eba-s6cewupj.us-west-2.elasticbeanstalk.com"
  proxied = true
  comment = "Elastic Beanstalk API endpoint"
}

# SSL/TLS Settings
resource "cloudflare_zone_settings_override" "ssl" {
  zone_id = data.cloudflare_zone.callableapis.id

  settings {
    ssl              = "flexible"  # Terminate SSL at Cloudflare, use HTTP to origin
    always_use_https = "on"
    min_tls_version  = "1.2"
    tls_1_3          = "on"
  }
}

# Security Settings
resource "cloudflare_zone_settings_override" "security" {
  zone_id = data.cloudflare_zone.callableapis.id

  settings {
    security_level = "medium"
    browser_check  = "on"
    challenge_ttl  = 1800
    privacy_pass   = "on"
  }
}

# Caching Settings
resource "cloudflare_zone_settings_override" "caching" {
  zone_id = data.cloudflare_zone.callableapis.id

  settings {
    cache_level       = "aggressive"
    browser_cache_ttl = 14400
    development_mode  = "off"
  }
}