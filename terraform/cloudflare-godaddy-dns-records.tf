# DNS Records for GoDaddy domains migrated to Cloudflare
# Currently only tokyo3.com has specific DNS records (Google Workspace)

# Get zone IDs from existing zones
data "cloudflare_zone" "godaddy_zones" {
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
  name = each.value
}

# Tokyo3.com - Google Workspace MX records
# These are the Gmail/Google Workspace MX records
resource "cloudflare_record" "tokyo3_mx" {
  for_each = {
    "1" = { priority = 1, exchange = "ASPMX.L.GOOGLE.COM" }
    "2" = { priority = 5, exchange = "ALT1.ASPMX.L.GOOGLE.COM" }
    "3" = { priority = 5, exchange = "ALT2.ASPMX.L.GOOGLE.COM" }
    "4" = { priority = 10, exchange = "ALT3.ASPMX.L.GOOGLE.COM" }
    "5" = { priority = 10, exchange = "ALT4.ASPMX.L.GOOGLE.COM" }
  }

  zone_id = data.cloudflare_zone.godaddy_zones["tokyo3"].id
  name    = "tokyo3.com"
  type    = "MX"
  content = "${each.value.exchange}"
  priority = each.value.priority
  ttl     = 3600
}

# Tokyo3.com - SPF record for email authentication
resource "cloudflare_record" "tokyo3_spf" {
  zone_id = data.cloudflare_zone.godaddy_zones["tokyo3"].id
  name    = "tokyo3.com"
  type    = "TXT"
  content = "v=spf1 include:_spf.google.com ~all"
  ttl     = 3600
}

# Tokyo3.com - DMARC record
resource "cloudflare_record" "tokyo3_dmarc" {
  zone_id = data.cloudflare_zone.godaddy_zones["tokyo3"].id
  name    = "_dmarc.tokyo3.com"
  type    = "TXT"
  content = "v=DMARC1; p=none; rua=mailto:dmarc@tokyo3.com"
  ttl     = 3600
}

