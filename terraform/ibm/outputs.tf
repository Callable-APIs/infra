# IBM Cloud Outputs

output "vsi_public_ip" {
  description = "Public IP of VSI instance"
  value       = ibm_is_floating_ip.callableapis_fip.address
}

output "vsi_private_ip" {
  description = "Private IP of VSI instance"
  value       = ibm_is_instance.callableapis_vsi.primary_network_interface[0]
}

output "vpc_id" {
  description = "VPC ID"
  value       = ibm_is_vpc.callableapis_vpc.id
}

output "subnet_id" {
  description = "Subnet ID"
  value       = ibm_is_subnet.callableapis_subnet.id
}

