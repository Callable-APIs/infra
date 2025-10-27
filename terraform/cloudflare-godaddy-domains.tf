# Cloudflare Zones for GoDaddy Domains
# Domains to be migrated from GoDaddy DNS to Cloudflare

# Zone configurations for each domain
resource "cloudflare_zone" "godaddy_domains" {
  for_each = {
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

  account_id = var.cloudflare_account_id
  zone       = each.value
  plan       = "free"
}

# Data sources for the zones (after creation)
data "cloudflare_zone" "godaddy_domain_data" {
  for_each = {
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

  name       = each.value
  depends_on = [cloudflare_zone.godaddy_domains]
}

# Output the nameservers for each domain
# These need to be updated in GoDaddy to point to Cloudflare
output "godaddy_domain_nameservers" {
  description = "Nameservers to configure in GoDaddy for each domain"
  value = {
    for k, v in cloudflare_zone.godaddy_domains : k => v.name_servers
  }
}

