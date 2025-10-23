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
  value       = cloudflare_workers_route.status_route.id
}

output "route_pattern" {
  description = "Route pattern for the worker"
  value       = cloudflare_workers_route.status_route.pattern
}
