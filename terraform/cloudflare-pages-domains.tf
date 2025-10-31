# Cloudflare Pages Projects for GoDaddy Domains
# Each domain will have its own Pages project for Jekyll-based blogs

# Shared variables for all Pages projects
locals {
  godaddy_domain_mapping = {
    cocoonspamini = "cocoonspamini.com"
    glassbubble   = "glassbubble.net"
    iheartdinos   = "iheartdinos.com"
    jughunt       = "jughunt.com"
    lipbalmjunkie = "lipbalmjunkie.com"
    ohsorad       = "ohsorad.com"
    rosamimosa    = "rosamimosa.com"
    taicho        = "taicho.com"
    tokyo3        = "tokyo3.com"
  }
}

# Cloudflare Pages projects - one for each domain
resource "cloudflare_pages_project" "godaddy_domains" {
  for_each = local.godaddy_domain_mapping

  account_id        = var.cloudflare_account_id
  name              = each.key
  production_branch = "main"

  # Simple configuration - deployment will be managed via GitHub integration
  # Pages projects require deployment from a GitHub repository
  # For now, we'll create the projects and configure custom domains
}

# Custom domains for each Pages project
# Note: Custom domain configuration requires the Pages project to exist first
resource "cloudflare_pages_domain" "godaddy_domains" {
  for_each = local.godaddy_domain_mapping

  account_id   = var.cloudflare_account_id
  project_name = cloudflare_pages_project.godaddy_domains[each.key].name
  domain       = each.value

  depends_on = [cloudflare_pages_project.godaddy_domains]
}

# DNS records to point domains to Pages projects
# These will point to the Pages deployment once it's active
resource "cloudflare_record" "pages_root" {
  for_each = local.godaddy_domain_mapping

  zone_id = data.cloudflare_zone.godaddy_domain_data[each.key].id
  name    = "@" # Root domain
  type    = "CNAME"
  content = "${each.key}.pages.dev" # Default Pages subdomain
  proxied = false                   # Initially not proxied until Pages is configured
  comment = "Cloudflare Pages deployment - update when Pages is active"
}

resource "cloudflare_record" "pages_www" {
  for_each = local.godaddy_domain_mapping

  zone_id = data.cloudflare_zone.godaddy_domain_data[each.key].id
  name    = "www"
  type    = "CNAME"
  content = "${each.key}.pages.dev"
  proxied = false # Initially not proxied until Pages is configured
  comment = "Cloudflare Pages www subdomain - update when Pages is active"
}

# Outputs for Pages project information
output "pages_project_names" {
  description = "Names of Pages projects created"
  value = {
    for k, v in cloudflare_pages_project.godaddy_domains : k => v.name
  }
}

output "pages_project_subdomains" {
  description = "Subdomains for each Pages project"
  value = {
    for k, v in cloudflare_pages_project.godaddy_domains : k => "${v.name}.pages.dev"
  }
}
