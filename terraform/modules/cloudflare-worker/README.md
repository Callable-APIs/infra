# Cloudflare Worker Module

This Terraform module creates a Cloudflare Worker that proxies requests to the status dashboard running on Google Cloud Node 1.

## Features

- **Request Proxying**: Forwards requests from `status.callableapis.com` to `35.233.161.8:8081`
- **CORS Headers**: Adds proper CORS headers for web access
- **Error Handling**: Graceful error handling with 503 responses
- **Health Checks**: Optional cron-based health monitoring
- **Custom Domains**: Support for custom domain configuration

## Usage

```hcl
module "status_worker" {
  source = "./modules/cloudflare-worker"
  
  zone_id       = var.cloudflare_zone_id
  route_pattern = "status.callableapis.com/*"
  target_host   = "35.233.161.8"
  target_port   = "8081"
  
  enable_health_check = true
  health_check_cron   = "*/5 * * * *"
}
```

## Variables

- `worker_name`: Name of the Cloudflare Worker (default: "status-dashboard-worker")
- `zone_id`: Cloudflare Zone ID (required)
- `route_pattern`: Route pattern for the worker (default: "status.callableapis.com/*")
- `target_host`: Target host for proxying (default: "35.233.161.8")
- `target_port`: Target port for proxying (default: "8081")
- `enable_custom_domain`: Enable custom domain (default: false)
- `custom_domain`: Custom domain name
- `enable_health_check`: Enable cron health checks (default: false)
- `health_check_cron`: Cron expression for health checks (default: "*/5 * * * *")

## Outputs

- `worker_name`: Name of the created worker
- `worker_id`: ID of the created worker
- `route_id`: ID of the worker route
- `route_pattern`: Route pattern
- `domain`: Custom domain (if enabled)
- `health_check_enabled`: Health check status

## Worker Script

The worker script (`status-worker.js`) handles:
- Request proxying to the target server
- CORS header injection
- Error handling and fallback responses
- Request/response logging
