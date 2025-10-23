# Global variables for all cloud providers

# AWS Configuration
variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-west-2"
}

variable "aws_access_key_id" {
  description = "AWS access key ID"
  type        = string
  sensitive   = true
}

variable "aws_secret_access_key" {
  description = "AWS secret access key"
  type        = string
  sensitive   = true
}

# Cloudflare Configuration
variable "cloudflare_api_token" {
  description = "Cloudflare API token"
  type        = string
  sensitive   = true
}

variable "cloudflare_zone_id" {
  description = "Cloudflare zone ID"
  type        = string
}

# GitHub OAuth Configuration
variable "github_client_id" {
  description = "GitHub OAuth client ID"
  type        = string
  sensitive   = true
}

variable "github_client_secret" {
  description = "GitHub OAuth client secret"
  type        = string
  sensitive   = true
}

variable "github_token" {
  description = "GitHub token"
  type        = string
  sensitive   = true
}

# Google Cloud Configuration
variable "gcp_project_id" {
  description = "GCP project ID"
  type        = string
}

variable "gcp_region" {
  description = "GCP region"
  type        = string
  default     = "us-central1"
}

variable "gcp_zone" {
  description = "GCP zone"
  type        = string
  default     = "us-central1-a"
}

# Oracle Cloud Configuration
variable "tenancy_ocid" {
  description = "OCI tenancy OCID"
  type        = string
  sensitive   = true
}

variable "user_ocid" {
  description = "OCI user OCID"
  type        = string
  sensitive   = true
}

variable "fingerprint" {
  description = "OCI fingerprint"
  type        = string
  sensitive   = true
}

variable "private_key_path" {
  description = "Path to OCI private key"
  type        = string
  sensitive   = true
}

variable "compartment_id" {
  description = "OCI compartment ID"
  type        = string
  sensitive   = true
}

variable "oci_region" {
  description = "OCI region"
  type        = string
  default     = "us-ashburn-1"
}

variable "oci_vcn_id" {
  description = "OCI VCN ID"
  type        = string
  sensitive   = true
}

# IBM Cloud Configuration
variable "ibmcloud_api_key" {
  description = "IBM Cloud API key"
  type        = string
  sensitive   = true
}

variable "ibmcloud_region" {
  description = "IBM Cloud region"
  type        = string
  default     = "us-south"
}

variable "ibm_security_group_id" {
  description = "IBM Cloud security group ID"
  type        = string
  sensitive   = true
}

variable "resource_group_id" {
  description = "IBM Cloud resource group ID"
  type        = string
  sensitive   = true
}

# SSH Configuration
variable "ssh_public_key" {
  description = "SSH public key for instances"
  type        = string
  sensitive   = true
}