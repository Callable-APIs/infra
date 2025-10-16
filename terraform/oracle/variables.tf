# Oracle Cloud Infrastructure (OCI) Variables

variable "tenancy_ocid" {
  description = "The OCID of the tenancy"
  type        = string
  sensitive   = true
}

variable "user_ocid" {
  description = "The OCID of the user"
  type        = string
  sensitive   = true
}

variable "fingerprint" {
  description = "The fingerprint of the API key"
  type        = string
  sensitive   = true
}

variable "private_key_path" {
  description = "Path to the private key file"
  type        = string
  sensitive   = true
}

variable "compartment_id" {
  description = "The OCID of the compartment"
  type        = string
  sensitive   = true
}

variable "region" {
  description = "The OCI region"
  type        = string
  default     = "us-ashburn-1"
}

variable "ssh_public_key" {
  description = "SSH public key for instance access"
  type        = string
}

