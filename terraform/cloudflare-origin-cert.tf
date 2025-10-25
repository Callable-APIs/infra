# Cloudflare Origin Certificate for SSL termination
resource "cloudflare_origin_ca_certificate" "callableapis_origin_cert" {
  csr = var.cloudflare_csr
  hostnames = [
    "onode1.callableapis.com",
    "onode2.callableapis.com", 
    "gnode1.callableapis.com",
    "inode1.callableapis.com"
  ]
  request_type = "origin-rsa"
  requested_validity = 15 * 365 # 15 years
}

# Output the certificate
output "origin_certificate" {
  description = "Cloudflare Origin Certificate"
  value       = cloudflare_origin_ca_certificate.callableapis_origin_cert.certificate
  sensitive   = true
}
