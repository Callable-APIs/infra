variable "account_id" {
  description = "Cloudflare Account ID"
  type        = string
}

variable "worker_name" {
  description = "Name of the Cloudflare Worker"
  type        = string
  default     = "status-dashboard-worker"
}

variable "zone_id" {
  description = "Cloudflare Zone ID"
  type        = string
}

variable "route_pattern" {
  description = "Route pattern for the worker (e.g., 'status.callableapis.com/*')"
  type        = string
  default     = "status.callableapis.com/*"
}

variable "target_host" {
  description = "Target host for proxying requests"
  type        = string
  default     = "35.233.161.8"
}

variable "target_port" {
  description = "Target port for proxying requests"
  type        = string
  default     = "8081"
}

variable "enable_custom_domain" {
  description = "Enable custom domain for the worker"
  type        = bool
  default     = false
}

variable "custom_domain" {
  description = "Custom domain for the worker"
  type        = string
  default     = ""
}

variable "enable_health_check" {
  description = "Enable cron-based health checks"
  type        = bool
  default     = false
}

variable "health_check_cron" {
  description = "Cron expression for health checks"
  type        = string
  default     = "*/5 * * * *"  # Every 5 minutes
}
