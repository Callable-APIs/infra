# Google Cloud Platform (GCP) Configuration
# Always Free Tier: 1x e2-micro (1 vCPU, 1GB RAM)

terraform {
  required_version = ">= 1.5"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

# GCP Provider Configuration
provider "google" {
  project = var.project_id
  region  = var.region
  zone    = var.zone
}

# Data sources
data "google_compute_zones" "available" {
  region = var.region
}

data "google_compute_image" "ubuntu" {
  family  = "ubuntu-2204-lts"
  project = "ubuntu-os-cloud"
}

# VPC Network
resource "google_compute_network" "callableapis_vpc" {
  name                    = "callableapis-vpc"
  auto_create_subnetworks = false
  mtu                     = 1460
}

# Subnet
resource "google_compute_subnetwork" "callableapis_subnet" {
  name          = "callableapis-subnet"
  ip_cidr_range = "10.1.0.0/24"
  region        = var.region
  network       = google_compute_network.callableapis_vpc.id
}

# Firewall rules
resource "google_compute_firewall" "callableapis_allow_ssh" {
  name    = "callableapis-allow-ssh"
  network = google_compute_network.callableapis_vpc.name

  allow {
    protocol = "tcp"
    ports    = ["22"]
  }

  source_ranges = ["0.0.0.0/0"]
  target_tags   = ["callableapis-ssh"]
}

resource "google_compute_firewall" "callableapis_allow_http" {
  name    = "callableapis-allow-http"
  network = google_compute_network.callableapis_vpc.name

  allow {
    protocol = "tcp"
    ports    = ["80"]
  }

  source_ranges = ["0.0.0.0/0"]
  target_tags   = ["callableapis-web"]
}

resource "google_compute_firewall" "callableapis_allow_https" {
  name    = "callableapis-allow-https"
  network = google_compute_network.callableapis_vpc.name

  allow {
    protocol = "tcp"
    ports    = ["443"]
  }

  source_ranges = ["0.0.0.0/0"]
  target_tags   = ["callableapis-web"]
}

resource "google_compute_firewall" "callableapis_allow_8080" {
  name    = "callableapis-allow-8080"
  network = google_compute_network.callableapis_vpc.name

  allow {
    protocol = "tcp"
    ports    = ["8080"]
  }

  source_ranges = ["0.0.0.0/0"]
  target_tags   = ["callableapis-web"]
}

# e2-micro Instance (Always Free)
resource "google_compute_instance" "callableapis_e2_micro" {
  name         = "callableapis-e2-micro"
  machine_type = "e2-micro"
  zone         = var.zone

  tags = ["callableapis-ssh", "callableapis-web", "callableapis"]

  boot_disk {
    initialize_params {
      image = data.google_compute_image.ubuntu.self_link
      size  = 30
      type  = "pd-standard"
    }
  }

  network_interface {
    network    = google_compute_network.callableapis_vpc.id
    subnetwork = google_compute_subnetwork.callableapis_subnet.id

    access_config {
      // Ephemeral public IP
    }
  }

  metadata = {
    ssh-keys = "ubuntu:${var.ssh_public_key}"
  }

  metadata_startup_script = file("${path.module}/user_data.sh")

  service_account {
    scopes = ["cloud-platform"]
  }

  labels = {
    name        = "callableapis-e2-micro"
    environment = "production"
    managed_by  = "terraform"
    provider    = "google"
    role        = "monitoring"
  }
}

