output "worker_name" {
  description = "Name of the created Cloudflare Worker"
  value       = cloudflare_workers_script.status_worker.name
}

output "worker_id" {
  description = "ID of the created Cloudflare Worker"
  value       = cloudflare_workers_script.status_worker.id
}

output "route_id" {
  description = "ID of the created Worker Route"
  value       = cloudflare_worker_route.status_route.id
}

output "route_pattern" {
  description = "Route pattern for the worker"
  value       = cloudflare_worker_route.status_route.pattern
}

output "domain" {
  description = "Custom domain for the worker (if enabled)"
  value       = var.enable_custom_domain ? cloudflare_worker_domain.status_domain[0].hostname : null
}

output "health_check_enabled" {
  description = "Whether health check cron is enabled"
  value       = var.enable_health_check
}
