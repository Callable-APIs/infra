# Oracle Cloud Infrastructure (OCI) Outputs

output "arm_instance_1_public_ip" {
  description = "Public IP of ARM instance 1"
  value       = oci_core_instance.callableapis_arm_1.public_ip
}

output "arm_instance_1_private_ip" {
  description = "Private IP of ARM instance 1"
  value       = oci_core_instance.callableapis_arm_1.private_ip
}

# output "arm_instance_2_public_ip" {
#   description = "Public IP of ARM instance 2"
#   value       = oci_core_instance.callableapis_arm_2.public_ip
# }

# output "arm_instance_2_private_ip" {
#   description = "Private IP of ARM instance 2"
#   value       = oci_core_instance.callableapis_arm_2.private_ip
# }

output "vcn_id" {
  description = "VCN ID"
  value       = oci_core_vcn.callableapis_vcn.id
}

output "subnet_id" {
  description = "Subnet ID"
  value       = oci_core_subnet.callableapis_subnet.id
}

