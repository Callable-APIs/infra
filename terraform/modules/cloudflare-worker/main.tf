# Cloudflare Worker for Status Dashboard
# Proxies status.callableapis.com to Google Cloud Node 1 port 8081

# Cloudflare Worker Script
resource "cloudflare_workers_script" "status_worker" {
  account_id = var.account_id
  name       = var.worker_name
  content    = file("${path.module}/status-worker.js")
  
  # Worker settings
  compatibility_date = "2023-10-30"
  compatibility_flags = ["nodejs_compat"]
  
  # Environment variables (if needed)
  # vars = {
  #   TARGET_HOST = var.target_host
  #   TARGET_PORT = var.target_port
  # }
}

# Cloudflare Worker Route
resource "cloudflare_worker_route" "status_route" {
  zone_id     = var.zone_id
  pattern     = var.route_pattern
  script_name = cloudflare_workers_script.status_worker.name
}

# Optional: Worker Domain (if using custom domain)
resource "cloudflare_worker_domain" "status_domain" {
  count = var.enable_custom_domain ? 1 : 0
  
  account_id = var.account_id
  zone_id    = var.zone_id
  hostname   = var.custom_domain
  service    = cloudflare_workers_script.status_worker.name
  environment = "production"
}

# Optional: Worker Cron Trigger (for health checks)
resource "cloudflare_worker_cron_trigger" "status_health_check" {
  count = var.enable_health_check ? 1 : 0
  
  account_id  = var.account_id
  script_name = cloudflare_workers_script.status_worker.name
  schedules   = [var.health_check_cron]
}
