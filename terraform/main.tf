# Terraform configuration based on ACTUAL existing infrastructure
# This matches what's really deployed, not what we think should be there

terraform {
  required_version = ">= 1.5"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    google = {
      source  = "hashicorp/google"
      version = "~> 7.0"
    }
    oci = {
      source  = "oracle/oci"
      version = "~> 7.0"
    }
    ibm = {
      source  = "IBM-Cloud/ibm"
      version = "~> 1.0"
    }
    cloudflare = {
      source  = "cloudflare/cloudflare"
      version = "~> 4.0"
    }
    local = {
      source  = "hashicorp/local"
      version = "~> 2.0"
    }
    time = {
      source  = "hashicorp/time"
      version = "~> 0.9"
    }
  }
}

# AWS Provider Configuration
provider "aws" {
  region = var.aws_region
}

# Google Cloud Provider Configuration
provider "google" {
  project     = var.gcp_project_id
  region      = var.gcp_region
  zone        = var.gcp_zone
  credentials = var.gcp_credentials_file
}

# Oracle Cloud Provider Configuration
provider "oci" {
  tenancy_ocid     = var.tenancy_ocid
  user_ocid        = var.user_ocid
  fingerprint      = var.fingerprint
  private_key_path = var.private_key_path
  region           = var.oci_region
}

# IBM Cloud Provider Configuration
provider "ibm" {
  ibmcloud_api_key = var.ibmcloud_api_key
  region           = var.ibmcloud_region
}

# Cloudflare Provider Configuration
provider "cloudflare" {
  api_token = var.cloudflare_api_token
}

# Local Provider Configuration
provider "local" {}

# Time Provider Configuration
provider "time" {}

# Cloudflare zone data source
data "cloudflare_zone" "callableapis" {
  name = "callableapis.com"
}

# =============================================================================
# GOOGLE CLOUD INFRASTRUCTURE (ACTUAL RESOURCES)
# =============================================================================

# Data sources
data "google_compute_zones" "available" {
  region = var.gcp_region
}

data "google_compute_image" "ubuntu" {
  family  = "ubuntu-2204-lts"
  project = "ubuntu-os-cloud"
}

# Project services
resource "google_project_service" "compute_api" {
  service = "compute.googleapis.com"
}

resource "google_project_service" "oslogin_api" {
  service = "oslogin.googleapis.com"
}

# Wait for APIs to be enabled
resource "time_sleep" "wait_for_apis" {
  depends_on = [
    google_project_service.compute_api,
    google_project_service.oslogin_api,
  ]

  create_duration = "60s"
}

# VPC Network
resource "google_compute_network" "callableapis_vpc" {
  name                    = "callableapis-vpc"
  auto_create_subnetworks = false
  mtu                     = 1460

  depends_on = [time_sleep.wait_for_apis]
}

# Subnet
resource "google_compute_subnetwork" "callableapis_subnet" {
  name          = "callableapis-subnet"
  ip_cidr_range = "10.1.0.0/24"
  region        = var.gcp_region
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

# HTTPS disabled - SSL terminated at Cloudflare
# resource "google_compute_firewall" "callableapis_allow_https" {
#   name    = "callableapis-allow-https"
#   network = google_compute_network.callableapis_vpc.name
#
#   allow {
#     protocol = "tcp"
#     ports    = ["443"]
#   }
#
#   source_ranges = ["0.0.0.0/0"]
#   target_tags   = ["callableapis-web"]
# }

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

resource "google_compute_firewall" "callableapis_allow_8081" {
  name    = "callableapis-allow-8081"
  network = google_compute_network.callableapis_vpc.name

  allow {
    protocol = "tcp"
    ports    = ["8081"]
  }

  source_ranges = ["0.0.0.0/0"]
  target_tags   = ["callableapis-web"]
}

# e2-micro Instance (Always Free)
resource "google_compute_instance" "callableapis_e2_micro" {
  name         = "callableapis-e2-micro"
  machine_type = "e2-micro"
  zone         = var.gcp_zone

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

  metadata_startup_script = file("${path.module}/google/user_data.sh")

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

# =============================================================================
# ORACLE CLOUD INFRASTRUCTURE (ACTUAL RESOURCES)
# =============================================================================

# Data sources
data "oci_identity_availability_domains" "ads" {
  compartment_id = var.compartment_id
}

data "oci_core_images" "arm_images" {
  compartment_id   = var.compartment_id
  operating_system = "Canonical Ubuntu"
  shape            = "VM.Standard.A1.Flex"
  sort_by          = "TIMECREATED"
  sort_order       = "DESC"
}

# VCN for OCI resources
resource "oci_core_vcn" "callableapis_vcn" {
  compartment_id = var.compartment_id
  cidr_block     = "10.0.0.0/16"
  display_name   = "callableapis-vcn"
  dns_label      = "callableapis"

  freeform_tags = {
    Name        = "callableapis-vcn"
    Environment = "production"
    ManagedBy   = "terraform"
    Project     = "callableapis-multicloud"
  }
}

# Internet Gateway
resource "oci_core_internet_gateway" "callableapis_igw" {
  compartment_id = var.compartment_id
  vcn_id         = oci_core_vcn.callableapis_vcn.id
  display_name   = "callableapis-igw"

  freeform_tags = {
    Name        = "callableapis-igw"
    Environment = "production"
    ManagedBy   = "terraform"
  }
}

# Route Table
resource "oci_core_route_table" "callableapis_rt" {
  compartment_id = var.compartment_id
  vcn_id         = oci_core_vcn.callableapis_vcn.id
  display_name   = "callableapis-rt"

  route_rules {
    destination       = "0.0.0.0/0"
    destination_type  = "CIDR_BLOCK"
    network_entity_id = oci_core_internet_gateway.callableapis_igw.id
  }

  freeform_tags = {
    Name        = "callableapis-rt"
    Environment = "production"
    ManagedBy   = "terraform"
  }
}

# Security List
resource "oci_core_security_list" "callableapis_sl" {
  compartment_id = var.compartment_id
  vcn_id         = oci_core_vcn.callableapis_vcn.id
  display_name   = "callableapis-sl"

  # SSH access
  ingress_security_rules {
    protocol  = "6"
    source    = "0.0.0.0/0"
    stateless = false

    tcp_options {
      min = 22
      max = 22
    }
  }

  # HTTP access
  ingress_security_rules {
    protocol  = "6"
    source    = "0.0.0.0/0"
    stateless = false

    tcp_options {
      min = 80
      max = 80
    }
  }

  # HTTPS access
  ingress_security_rules {
    protocol  = "6"
    source    = "0.0.0.0/0"
    stateless = false

    tcp_options {
      min = 443
      max = 443
    }
  }

  ingress_security_rules {
    protocol  = "6"
    source    = "0.0.0.0/0"
    stateless = false

    tcp_options {
      min = 8080
      max = 8080
    }
  }

  # All outbound traffic
  egress_security_rules {
    protocol    = "all"
    destination = "0.0.0.0/0"
    stateless   = false
  }

  freeform_tags = {
    Name        = "callableapis-sl"
    Environment = "production"
    ManagedBy   = "terraform"
  }
}

# Subnet
resource "oci_core_subnet" "callableapis_subnet" {
  compartment_id    = var.compartment_id
  vcn_id            = oci_core_vcn.callableapis_vcn.id
  cidr_block        = "10.0.1.0/24"
  display_name      = "callableapis-subnet"
  dns_label         = "callableapis"
  route_table_id    = oci_core_route_table.callableapis_rt.id
  security_list_ids = [oci_core_security_list.callableapis_sl.id]

  freeform_tags = {
    Name        = "callableapis-subnet"
    Environment = "production"
    ManagedBy   = "terraform"
  }
}

# ARM Instance 1 - Primary (onode1) - Free Tier
resource "oci_core_instance" "callableapis_arm_1" {
  compartment_id      = var.compartment_id
  availability_domain = data.oci_identity_availability_domains.ads.availability_domains[0].name
  display_name        = "onode1"
  shape               = "VM.Standard.A1.Flex"

  shape_config {
    ocpus         = 4
    memory_in_gbs = 24
  }

  source_details {
    source_type = "image"
    source_id   = data.oci_core_images.arm_images.images[0].id
  }

  create_vnic_details {
    subnet_id        = oci_core_subnet.callableapis_subnet.id
    display_name     = "callableapis-arm-1-vnic"
    assign_public_ip = true
    hostname_label   = "callableapis-arm-1"
  }

  metadata = {
    ssh_authorized_keys = var.ssh_public_key
    user_data           = base64encode(file("${path.module}/oracle/user_data.sh"))
  }

  freeform_tags = {
    Name        = "callableapis-arm-1"
    Environment = "production"
    ManagedBy   = "terraform"
    Role        = "primary"
    Provider    = "oracle"
  }
}

# ARM Instance 2 - Secondary (onode2) - Free Tier
resource "oci_core_instance" "callableapis_arm_2" {
  compartment_id      = var.compartment_id
  availability_domain = data.oci_identity_availability_domains.ads.availability_domains[0].name
  display_name        = "onode2"
  shape               = "VM.Standard.A1.Flex"

  shape_config {
    ocpus         = 4
    memory_in_gbs = 24
  }

  source_details {
    source_type = "image"
    source_id   = data.oci_core_images.arm_images.images[0].id
  }

  create_vnic_details {
    subnet_id        = oci_core_subnet.callableapis_subnet.id
    display_name     = "callableapis-arm-2-vnic"
    assign_public_ip = true
    hostname_label   = "callableapis-arm-2"
  }

  metadata = {
    ssh_authorized_keys = var.ssh_public_key
    user_data           = base64encode(file("${path.module}/oracle/user_data.sh"))
  }

  freeform_tags = {
    Name        = "callableapis-arm-2"
    Environment = "production"
    ManagedBy   = "terraform"
    Role        = "secondary"
    Provider    = "oracle"
  }
}

# =============================================================================
# IBM CLOUD INFRASTRUCTURE (ACTUAL RESOURCES)
# =============================================================================

# Data sources
data "ibm_is_zones" "zones" {
  region = var.ibmcloud_region
}

data "ibm_is_image" "ubuntu" {
  name = "ibm-ubuntu-20-04-6-minimal-amd64-2"
}

# VPC
resource "ibm_is_vpc" "callableapis_vpc" {
  name           = "callableapis-vpc"
  resource_group = var.resource_group_id
  tags           = ["callableapis", "production"]
}

# Public Gateway (for internet access)
resource "ibm_is_public_gateway" "callableapis_pgw" {
  name           = "callableapis-pgw"
  vpc            = ibm_is_vpc.callableapis_vpc.id
  zone           = data.ibm_is_zones.zones.zones[0]
  resource_group = var.resource_group_id
  tags           = ["callableapis", "production"]
}

# Subnet
resource "ibm_is_subnet" "callableapis_subnet" {
  name            = "callableapis-subnet"
  vpc             = ibm_is_vpc.callableapis_vpc.id
  zone            = data.ibm_is_zones.zones.zones[0]
  ipv4_cidr_block = "10.240.0.0/24"
  resource_group  = var.resource_group_id
  public_gateway  = ibm_is_public_gateway.callableapis_pgw.id
  tags            = ["callableapis", "production"]
}

# Security Group
resource "ibm_is_security_group" "callableapis_sg" {
  name           = "callableapis-sg"
  vpc            = ibm_is_vpc.callableapis_vpc.id
  resource_group = var.resource_group_id
  tags           = ["callableapis", "production"]
}

# Security Group Rules - Inbound
resource "ibm_is_security_group_rule" "callableapis_ssh" {
  group     = ibm_is_security_group.callableapis_sg.id
  direction = "inbound"
  remote    = "0.0.0.0/0"
  tcp {
    port_min = 22
    port_max = 22
  }
}

resource "ibm_is_security_group_rule" "callableapis_http" {
  group     = ibm_is_security_group.callableapis_sg.id
  direction = "inbound"
  remote    = "0.0.0.0/0"
  tcp {
    port_min = 80
    port_max = 80
  }
}

# HTTPS access
resource "ibm_is_security_group_rule" "callableapis_https" {
  group     = ibm_is_security_group.callableapis_sg.id
  direction = "inbound"
  remote    = "0.0.0.0/0"
  tcp {
    port_min = 443
    port_max = 443
  }
}

resource "ibm_is_security_group_rule" "callableapis_8080" {
  group     = ibm_is_security_group.callableapis_sg.id
  direction = "inbound"
  remote    = "0.0.0.0/0"
  tcp {
    port_min = 8080
    port_max = 8080
  }
}

# Security Group Rules - Outbound (for internet access)
resource "ibm_is_security_group_rule" "callableapis_outbound_http" {
  group     = ibm_is_security_group.callableapis_sg.id
  direction = "outbound"
  remote    = "0.0.0.0/0"
  tcp {
    port_min = 80
    port_max = 80
  }
}

# Outbound HTTPS for Docker Hub and GitHub access
resource "ibm_is_security_group_rule" "callableapis_outbound_https" {
  group     = ibm_is_security_group.callableapis_sg.id
  direction = "outbound"
  remote    = "0.0.0.0/0"
  tcp {
    port_min = 443
    port_max = 443
  }
}

resource "ibm_is_security_group_rule" "callableapis_outbound_dns" {
  group     = ibm_is_security_group.callableapis_sg.id
  direction = "outbound"
  remote    = "0.0.0.0/0"
  udp {
    port_min = 53
    port_max = 53
  }
}

resource "ibm_is_security_group_rule" "callableapis_outbound_icmp" {
  group     = ibm_is_security_group.callableapis_sg.id
  direction = "outbound"
  remote    = "0.0.0.0/0"
  icmp {
    type = 8
    code = 0
  }
}

# SSH Key
resource "ibm_is_ssh_key" "callableapis_key" {
  name           = "callableapis-key"
  public_key     = var.ssh_public_key
  resource_group = var.resource_group_id
  tags           = ["callableapis", "production"]
}

# Virtual Server Instance (Free Tier)
resource "ibm_is_instance" "callableapis_vsi" {
  name           = "callableapis-vsi"
  vpc            = ibm_is_vpc.callableapis_vpc.id
  zone           = data.ibm_is_zones.zones.zones[0]
  keys           = [ibm_is_ssh_key.callableapis_key.id]
  image          = data.ibm_is_image.ubuntu.id
  profile        = "cx2-2x4" # Free tier: 2 vCPU, 4GB RAM (smaller profile for free tier)
  resource_group = var.resource_group_id

  primary_network_interface {
    subnet          = ibm_is_subnet.callableapis_subnet.id
    security_groups = [ibm_is_security_group.callableapis_sg.id]
  }

  user_data = file("${path.module}/ibm/user_data.sh")

  tags = ["callableapis", "production", "terraform"]
}

# Floating IP
resource "ibm_is_floating_ip" "callableapis_fip" {
  name           = "callableapis-fip"
  target         = ibm_is_instance.callableapis_vsi.primary_network_interface[0].id
  resource_group = var.resource_group_id
  tags           = ["callableapis", "production"]
}

# =============================================================================
# CLOUDFLARE DNS RECORDS (EXISTING)
# =============================================================================

resource "cloudflare_record" "website_root" {
  zone_id         = data.cloudflare_zone.callableapis.id
  name            = "callableapis.com"
  type            = "CNAME"
  content         = "callableapis-usw2.com.s3-website.us-west-2.amazonaws.com"
  proxied         = true
  allow_overwrite = true
  comment         = "S3 website endpoint"
}

resource "cloudflare_record" "website_www" {
  zone_id         = data.cloudflare_zone.callableapis.id
  name            = "www"
  type            = "CNAME"
  content         = "callableapis-usw2.com.s3-website.us-west-2.amazonaws.com"
  proxied         = true
  allow_overwrite = true
  comment         = "S3 website endpoint"
}

resource "cloudflare_record" "api" {
  zone_id         = data.cloudflare_zone.callableapis.id
  name            = "api"
  type            = "A"
  content         = "35.88.22.9"  # AWS instance anode1 - updated manually due to state sync issue
  proxied         = true
  allow_overwrite = true
  comment         = "API endpoint - AWS services container (anode1)"
}

resource "cloudflare_record" "gnode1" {
  zone_id = data.cloudflare_zone.callableapis.id
  name    = "gnode1"
  type    = "A"
  content = google_compute_instance.callableapis_e2_micro.network_interface[0].access_config[0].nat_ip
  proxied = true
  comment = "Google Cloud monitoring node"
}

resource "cloudflare_record" "onode1" {
  zone_id = data.cloudflare_zone.callableapis.id
  name    = "onode1"
  type    = "A"
  content = oci_core_instance.callableapis_arm_1.public_ip
  proxied = true
  comment = "Oracle Cloud primary node"
}

resource "cloudflare_record" "onode2" {
  zone_id = data.cloudflare_zone.callableapis.id
  name    = "onode2"
  type    = "A"
  content = oci_core_instance.callableapis_arm_2.public_ip
  proxied = true
  comment = "Oracle Cloud secondary node"
}

resource "cloudflare_record" "inode1" {
  zone_id = data.cloudflare_zone.callableapis.id
  name    = "inode1"
  type    = "A"
  content = ibm_is_floating_ip.callableapis_fip.address
  proxied = true
  comment = "IBM Cloud services node"
}

# Status Dashboard DNS Record (direct to Oracle node)
resource "cloudflare_record" "status" {
  zone_id = data.cloudflare_zone.callableapis.id
  name    = "status"
  type    = "A"
  content = google_compute_instance.callableapis_e2_micro.network_interface[0].access_config[0].nat_ip
  proxied = true
  comment = "Status Dashboard - Google Cloud Node"
}

# Cloudflare Worker for Status Dashboard
# Worker module removed - using full-tunnel SSL with Nginx instead
# module "status_worker" {
#   source = "./cloudflare-worker"
#
#   cloudflare_account_id = var.cloudflare_account_id
#   cloudflare_zone_id    = data.cloudflare_zone.callableapis.id
# }

# Cloudflare Page Rule: Route /api/status from www to status endpoint
resource "cloudflare_page_rule" "www_api_status_redirect" {
  zone_id  = data.cloudflare_zone.callableapis.id
  target   = "www.callableapis.com/api/status*"
  priority = 1
  status   = "active"

  actions {
    forwarding_url {
      url         = "https://status.callableapis.com/api/status"
      status_code = 301
    }
  }
}

# Cloudflare zone settings
resource "cloudflare_zone_settings_override" "caching" {
  zone_id = data.cloudflare_zone.callableapis.id
  settings {
    cache_level = "aggressive"
  }
}

resource "cloudflare_zone_settings_override" "security" {
  zone_id = data.cloudflare_zone.callableapis.id
  settings {
    security_level = "high"
  }
}

resource "cloudflare_zone_settings_override" "ssl" {
  zone_id = data.cloudflare_zone.callableapis.id
  settings {
    ssl = "flexible" # Use flexible for S3-backed website; strict mode can be applied per-route via page rules
  }
}