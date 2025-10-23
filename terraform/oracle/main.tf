# Oracle Cloud Infrastructure (OCI) Configuration
# Always Free Tier: 2x ARM instances (4 OCPU, 24GB RAM each)

terraform {
  required_version = ">= 1.5"
  required_providers {
    oci = {
      source  = "oracle/oci"
      version = "~> 5.0"
    }
  }
}

# OCI Provider Configuration
provider "oci" {
  tenancy_ocid         = var.tenancy_ocid
  user_ocid            = var.user_ocid
  fingerprint          = var.fingerprint
  private_key_path     = var.private_key_path
  region               = var.region
}

# Data sources
data "oci_identity_availability_domains" "ads" {
  compartment_id = var.compartment_id
}

data "oci_core_images" "amd_images" {
  compartment_id   = var.compartment_id
  operating_system = "Canonical Ubuntu"
  shape            = "VM.Standard.E5.Flex"
  sort_by         = "TIMECREATED"
  sort_order      = "DESC"
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

# Subnet
resource "oci_core_subnet" "callableapis_subnet" {
  compartment_id      = var.compartment_id
  vcn_id              = oci_core_vcn.callableapis_vcn.id
  cidr_block          = "10.0.1.0/24"
  display_name        = "callableapis-subnet"
  dns_label           = "callableapis"
  route_table_id      = oci_core_route_table.callableapis_rt.id
  security_list_ids   = [oci_core_security_list.callableapis_sl.id]

  freeform_tags = {
    Name        = "callableapis-subnet"
    Environment = "production"
    ManagedBy   = "terraform"
  }
}

# Security List
resource "oci_core_security_list" "callableapis_sl" {
  compartment_id = var.compartment_id
  vcn_id         = oci_core_vcn.callableapis_vcn.id
  display_name   = "callableapis-sl"

  # SSH access only - all other ports blocked for security
  ingress_security_rules {
    protocol  = "6"
    source    = "0.0.0.0/0"
    stateless = false

    tcp_options {
      min = 22
      max = 22
    }
  }

  # Container Services (port 8080)
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

# ARM Instance 1 - Primary (node1)
resource "oci_core_instance" "callableapis_arm_1" {
  compartment_id      = var.compartment_id
  availability_domain = data.oci_identity_availability_domains.ads.availability_domains[0].name
  display_name        = "node1"
  shape               = "VM.Standard.E5.Flex"

  shape_config {
    ocpus         = 1
    memory_in_gbs = 12
  }

  source_details {
    source_type = "image"
    source_id   = data.oci_core_images.amd_images.images[0].id
  }

  create_vnic_details {
    subnet_id        = oci_core_subnet.callableapis_subnet.id
    display_name     = "callableapis-arm-1-vnic"
    assign_public_ip = true
    hostname_label   = "callableapis-arm-1"
  }

  metadata = {
    ssh_authorized_keys = var.ssh_public_key
    user_data = base64encode(file("${path.module}/user_data.sh"))
  }

  freeform_tags = {
    Name        = "callableapis-arm-1"
    Environment = "production"
    ManagedBy   = "terraform"
    Role        = "primary"
    Provider    = "oracle"
  }
}

# ARM Instance 2 - Secondary (node2) - Commented out for now due to capacity issues
# resource "oci_core_instance" "callableapis_arm_2" {
#   compartment_id      = var.compartment_id
#   availability_domain = data.oci_identity_availability_domains.ads.availability_domains[2].name
#   display_name        = "node2"
#   shape               = "VM.Standard.A1.Flex"

#       shape_config {
#         ocpus         = 2
#         memory_in_gbs = 12
#       }

#   source_details {
#     source_type = "image"
#     source_id   = data.oci_core_images.amd_images.images[0].id
#   }

#   create_vnic_details {
#     subnet_id        = oci_core_subnet.callableapis_subnet.id
#     display_name     = "callableapis-arm-2-vnic"
#     assign_public_ip = true
#     hostname_label   = "callableapis-arm-2"
#   }

#   metadata = {
#     ssh_authorized_keys = var.ssh_public_key
#     user_data = base64encode(file("${path.module}/user_data.sh"))
#   }

#   freeform_tags = {
#     Name        = "callableapis-arm-2"
#     Environment = "production"
#     ManagedBy   = "terraform"
#     Role        = "secondary"
#     Provider    = "oracle"
#   }
# }

