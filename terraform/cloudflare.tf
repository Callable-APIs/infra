# Cloudflare configuration for callableapis.com
# Generated on 2025-10-14 02:35:00 UTC

# Cloudflare provider configuration
provider "cloudflare" {
  api_token = var.cloudflare_api_token
}

# Cloudflare zone data source
data "cloudflare_zone" "callableapis" {
  name = "callableapis.com"
}

# DNS Records for callableapis.com
# Root domain - points to S3 website
resource "cloudflare_record" "website_root" {
  zone_id = data.cloudflare_zone.callableapis.id
  name    = "callableapis.com"
  type    = "CNAME"
  content = "callableapis-usw2.com.s3-website.us-west-2.amazonaws.com"
  proxied = true
  comment = "S3 website endpoint"
}

# WWW subdomain - points to S3 website
resource "cloudflare_record" "website_www" {
  zone_id = data.cloudflare_zone.callableapis.id
  name    = "www"
  type    = "CNAME"
  content = "callableapis-usw2.com.s3-website.us-west-2.amazonaws.com"
  proxied = true
  comment = "S3 website endpoint"
}

# API subdomain - points to Elastic Beanstalk
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
    ssl              = "full"
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
