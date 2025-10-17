# IBM Cloud Configuration
# Always Free Tier: Various services with Lite plans

terraform {
  required_version = ">= 1.5"
  required_providers {
    ibm = {
      source  = "IBM-Cloud/ibm"
      version = "~> 1.0"
    }
  }
}

# IBM Cloud Provider Configuration
provider "ibm" {
  ibmcloud_api_key = var.ibmcloud_api_key
  region           = var.region
}

# Data sources
data "ibm_is_zones" "zones" {
  region = var.region
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

# Subnet
resource "ibm_is_subnet" "callableapis_subnet" {
  name            = "callableapis-subnet"
  vpc             = ibm_is_vpc.callableapis_vpc.id
  zone            = data.ibm_is_zones.zones.zones[0]
  ipv4_cidr_block = "10.240.0.0/24"
  resource_group  = var.resource_group_id
  tags            = ["callableapis", "production"]
}

# Security Group
resource "ibm_is_security_group" "callableapis_sg" {
  name           = "callableapis-sg"
  vpc            = ibm_is_vpc.callableapis_vpc.id
  resource_group = var.resource_group_id
  tags           = ["callableapis", "production"]
}

# Security Group Rules
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

resource "ibm_is_security_group_rule" "callableapis_https" {
  group     = ibm_is_security_group.callableapis_sg.id
  direction = "inbound"
  remote    = "0.0.0.0/0"
  tcp {
    port_min = 443
    port_max = 443
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
  profile        = "bx2-2x8" # Free tier eligible profile
  resource_group = var.resource_group_id

  primary_network_interface {
    subnet          = ibm_is_subnet.callableapis_subnet.id
    security_groups = [ibm_is_security_group.callableapis_sg.id]
  }

  user_data = file("${path.module}/user_data.sh")

  tags = ["callableapis", "production", "terraform"]
}

# Floating IP
resource "ibm_is_floating_ip" "callableapis_fip" {
  name           = "callableapis-fip"
  target         = ibm_is_instance.callableapis_vsi.primary_network_interface[0].id
  resource_group = var.resource_group_id
  tags           = ["callableapis", "production"]
}

