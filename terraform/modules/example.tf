# Example module for reusable components
# This is a placeholder for future module development

variable "environment" {
  description = "Environment name"
  type        = string
}

variable "project_name" {
  description = "Project name"
  type        = string
}

output "module_output" {
  description = "Example module output"
  value       = "Hello from module"
}
