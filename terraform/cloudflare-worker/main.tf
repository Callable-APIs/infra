# Cloudflare Worker for Status Dashboard
# Proxies status.callableapis.com to Google Cloud Node 1 port 8081

# Cloudflare Worker Script
resource "cloudflare_workers_script" "status_worker" {
  account_id = var.cloudflare_account_id
  name       = "status-dashboard-worker"
  content    = file("${path.module}/status-worker.js")
  
  # Worker settings
  compatibility_date = "2023-10-30"
  compatibility_flags = ["nodejs_compat"]
}

# Cloudflare Worker Route (using new resource name)
resource "cloudflare_workers_route" "status_route" {
  zone_id     = var.cloudflare_zone_id
  pattern     = "status.callableapis.com/*"
  script_name = cloudflare_workers_script.status_worker.name
}

# Optional: Worker Cron Trigger (for health checks)
# Disabled for now - requires workers.dev subdomain
# resource "cloudflare_workers_cron_trigger" "status_health_check" {
#   account_id  = var.cloudflare_account_id
#   script_name = cloudflare_workers_script.status_worker.name
#   schedules   = ["*/5 * * * *"]  # Every 5 minutes
# }
