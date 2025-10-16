# Google Cloud Platform (GCP) Outputs

output "e2_micro_public_ip" {
  description = "Public IP of e2-micro instance"
  value       = google_compute_instance.callableapis_e2_micro.network_interface[0].access_config[0].nat_ip
}

output "e2_micro_private_ip" {
  description = "Private IP of e2-micro instance"
  value       = google_compute_instance.callableapis_e2_micro.network_interface[0].network_ip
}

output "vpc_id" {
  description = "VPC ID"
  value       = google_compute_network.callableapis_vpc.id
}

output "subnet_id" {
  description = "Subnet ID"
  value       = google_compute_subnetwork.callableapis_subnet.id
}

