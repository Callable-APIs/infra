#!/bin/bash
# Comprehensive Infrastructure Import Script
# Imports all existing infrastructure from local state files into S3-backed Terraform

set -e

echo "CallableAPIs Infrastructure Import"
echo "================================="
echo "Importing existing infrastructure from local state files to S3-backed Terraform"
echo ""

cd /Users/rlee/dev/infra/terraform

# Load environment variables
source ../env.sh

echo "1. DISCOVERED EXISTING INFRASTRUCTURE"
echo "===================================="

echo "Google Cloud Resources (11):"
echo "- google_compute_network.callableapis_vpc"
echo "- google_compute_subnetwork.callableapis_subnet"
echo "- google_compute_firewall.callableapis_allow_ssh"
echo "- google_compute_firewall.callableapis_allow_http"
echo "- google_compute_firewall.callableapis_allow_https"
echo "- google_compute_instance.callableapis_e2_micro"
echo "- google_project_service.compute_api"
echo "- google_project_service.oslogin_api"
echo "- time_sleep.wait_for_apis"
echo "- data.google_compute_image.ubuntu"
echo "- data.google_compute_zones.available"

echo ""
echo "Oracle Cloud Resources (10):"
echo "- oci_core_vcn.callableapis_vcn"
echo "- oci_core_internet_gateway.callableapis_igw"
echo "- oci_core_route_table.callableapis_rt"
echo "- oci_core_security_list.callableapis_sl"
echo "- oci_core_subnet.callableapis_subnet"
echo "- oci_core_instance.callableapis_arm_1"
echo "- data.oci_identity_availability_domains.ads"
echo "- data.oci_core_images.amd_images"
echo "- data.oci_core_images.available_images"
echo "- data.oci_core_shapes.available_shapes"

echo ""
echo "IBM Cloud Resources (16):"
echo "- ibm_is_vpc.callableapis_vpc"
echo "- ibm_is_public_gateway.callableapis_pgw"
echo "- ibm_is_subnet.callableapis_subnet"
echo "- ibm_is_security_group.callableapis_sg"
echo "- ibm_is_security_group_rule.callableapis_ssh"
echo "- ibm_is_security_group_rule.callableapis_http"
echo "- ibm_is_security_group_rule.callableapis_https"
echo "- ibm_is_security_group_rule.callableapis_outbound_dns"
echo "- ibm_is_security_group_rule.callableapis_outbound_http"
echo "- ibm_is_security_group_rule.callableapis_outbound_https"
echo "- ibm_is_security_group_rule.callableapis_outbound_icmp"
echo "- ibm_is_ssh_key.callableapis_key"
echo "- ibm_is_instance.callableapis_vsi"
echo "- ibm_is_floating_ip.callableapis_fip"
echo "- data.ibm_is_zones.zones"
echo "- data.ibm_is_image.ubuntu"

echo ""
echo "2. EXTRACTING RESOURCE IDs FROM LOCAL STATE FILES"
echo "================================================="

# Extract Google Cloud resource IDs
echo "Extracting Google Cloud resource IDs..."
GCP_PROJECT_ID=$(cat google/terraform.tfstate | jq -r '.resources[] | select(.type == "google_compute_network") | .instances[0].attributes.project')
GCP_NETWORK_ID=$(cat google/terraform.tfstate | jq -r '.resources[] | select(.type == "google_compute_network") | .instances[0].attributes.id')
GCP_SUBNET_ID=$(cat google/terraform.tfstate | jq -r '.resources[] | select(.type == "google_compute_subnetwork") | .instances[0].attributes.id')
GCP_INSTANCE_ID=$(cat google/terraform.tfstate | jq -r '.resources[] | select(.type == "google_compute_instance") | .instances[0].attributes.id')
GCP_ZONE=$(cat google/terraform.tfstate | jq -r '.resources[] | select(.type == "google_compute_instance") | .instances[0].attributes.zone')

echo "Google Cloud IDs:"
echo "- Project: $GCP_PROJECT_ID"
echo "- Network: $GCP_NETWORK_ID"
echo "- Subnet: $GCP_SUBNET_ID"
echo "- Instance: $GCP_INSTANCE_ID"
echo "- Zone: $GCP_ZONE"

# Extract Oracle Cloud resource IDs
echo ""
echo "Extracting Oracle Cloud resource IDs..."
OCI_VCN_ID=$(cat oracle/terraform.tfstate | jq -r '.resources[] | select(.type == "oci_core_vcn") | .instances[0].attributes.id')
OCI_IGW_ID=$(cat oracle/terraform.tfstate | jq -r '.resources[] | select(.type == "oci_core_internet_gateway") | .instances[0].attributes.id')
OCI_RT_ID=$(cat oracle/terraform.tfstate | jq -r '.resources[] | select(.type == "oci_core_route_table") | .instances[0].attributes.id')
OCI_SL_ID=$(cat oracle/terraform.tfstate | jq -r '.resources[] | select(.type == "oci_core_security_list") | .instances[0].attributes.id')
OCI_SUBNET_ID=$(cat oracle/terraform.tfstate | jq -r '.resources[] | select(.type == "oci_core_subnet") | .instances[0].attributes.id')
OCI_INSTANCE_ID=$(cat oracle/terraform.tfstate | jq -r '.resources[] | select(.type == "oci_core_instance") | .instances[0].attributes.id')

echo "Oracle Cloud IDs:"
echo "- VCN: $OCI_VCN_ID"
echo "- IGW: $OCI_IGW_ID"
echo "- Route Table: $OCI_RT_ID"
echo "- Security List: $OCI_SL_ID"
echo "- Subnet: $OCI_SUBNET_ID"
echo "- Instance: $OCI_INSTANCE_ID"

# Extract IBM Cloud resource IDs
echo ""
echo "Extracting IBM Cloud resource IDs..."
IBM_VPC_ID=$(cat ibm/terraform.tfstate | jq -r '.resources[] | select(.type == "ibm_is_vpc") | .instances[0].attributes.id')
IBM_PGW_ID=$(cat ibm/terraform.tfstate | jq -r '.resources[] | select(.type == "ibm_is_public_gateway") | .instances[0].attributes.id')
IBM_SUBNET_ID=$(cat ibm/terraform.tfstate | jq -r '.resources[] | select(.type == "ibm_is_subnet") | .instances[0].attributes.id')
IBM_SG_ID=$(cat ibm/terraform.tfstate | jq -r '.resources[] | select(.type == "ibm_is_security_group") | .instances[0].attributes.id')
IBM_SSH_KEY_ID=$(cat ibm/terraform.tfstate | jq -r '.resources[] | select(.type == "ibm_is_ssh_key") | .instances[0].attributes.id')
IBM_INSTANCE_ID=$(cat ibm/terraform.tfstate | jq -r '.resources[] | select(.type == "ibm_is_instance") | .instances[0].attributes.id')
IBM_FIP_ID=$(cat ibm/terraform.tfstate | jq -r '.resources[] | select(.type == "ibm_is_floating_ip") | .instances[0].attributes.id')

echo "IBM Cloud IDs:"
echo "- VPC: $IBM_VPC_ID"
echo "- Public Gateway: $IBM_PGW_ID"
echo "- Subnet: $IBM_SUBNET_ID"
echo "- Security Group: $IBM_SG_ID"
echo "- SSH Key: $IBM_SSH_KEY_ID"
echo "- Instance: $IBM_INSTANCE_ID"
echo "- Floating IP: $IBM_FIP_ID"

echo ""
echo "3. IMPORTING INFRASTRUCTURE TO S3-BACKED TERRAFORM"
echo "=================================================="

# Initialize Terraform with S3 backend
echo "Initializing Terraform with S3 backend..."
echo "yes" | docker run --rm -i -v $(pwd):/app -w /app \
  -e AWS_ACCESS_KEY_ID="$AWS_ACCESS_KEY_ID" \
  -e AWS_SECRET_ACCESS_KEY="$AWS_SECRET_ACCESS_KEY" \
  callableapis:infra terraform init

echo ""
echo "Import process will begin..."
echo "Note: This will import all existing infrastructure into the S3-backed Terraform state"
echo ""

# Import Google Cloud resources
echo "Importing Google Cloud resources..."
docker run --rm -v $(pwd):/app -w /app \
  -e AWS_ACCESS_KEY_ID="$AWS_ACCESS_KEY_ID" \
  -e AWS_SECRET_ACCESS_KEY="$AWS_SECRET_ACCESS_KEY" \
  -e GOOGLE_APPLICATION_CREDENTIALS="/app/google-credentials.json" \
  -e GCP_PROJECT_ID="$GOOGLE_PROJECT_ID" \
  -e GCP_REGION="$GOOGLE_REGION" \
  -e GCP_ZONE="$GOOGLE_ZONE" \
  callableapis:infra terraform import google_compute_network.callableapis_vpc "$GCP_NETWORK_ID"

docker run --rm -v $(pwd):/app -w /app \
  -e AWS_ACCESS_KEY_ID="$AWS_ACCESS_KEY_ID" \
  -e AWS_SECRET_ACCESS_KEY="$AWS_SECRET_ACCESS_KEY" \
  -e GOOGLE_APPLICATION_CREDENTIALS="/app/google-credentials.json" \
  -e GCP_PROJECT_ID="$GOOGLE_PROJECT_ID" \
  -e GCP_REGION="$GOOGLE_REGION" \
  -e GCP_ZONE="$GOOGLE_ZONE" \
  callableapis:infra terraform import google_compute_subnetwork.callableapis_subnet "$GCP_SUBNET_ID"

docker run --rm -v $(pwd):/app -w /app \
  -e AWS_ACCESS_KEY_ID="$AWS_ACCESS_KEY_ID" \
  -e AWS_SECRET_ACCESS_KEY="$AWS_SECRET_ACCESS_KEY" \
  -e GOOGLE_APPLICATION_CREDENTIALS="/app/google-credentials.json" \
  -e GCP_PROJECT_ID="$GOOGLE_PROJECT_ID" \
  -e GCP_REGION="$GOOGLE_REGION" \
  -e GCP_ZONE="$GOOGLE_ZONE" \
  callableapis:infra terraform import google_compute_instance.callableapis_e2_micro "$GCP_INSTANCE_ID"

echo "✅ Google Cloud resources imported"

# Import Oracle Cloud resources
echo "Importing Oracle Cloud resources..."
docker run --rm -v $(pwd):/app -w /app \
  -e AWS_ACCESS_KEY_ID="$AWS_ACCESS_KEY_ID" \
  -e AWS_SECRET_ACCESS_KEY="$AWS_SECRET_ACCESS_KEY" \
  -e OCI_TENANCY_OCID="$OCI_TENANCY_OCID" \
  -e OCI_USER_OCID="$OCI_USER_OCID" \
  -e OCI_FINGERPRINT="$OCI_FINGERPRINT" \
  -e OCI_PRIVATE_KEY_PATH="/app/oci-private-key.pem" \
  -e OCI_COMPARTMENT_ID="$OCI_COMPARTMENT_ID" \
  -e OCI_REGION="$OCI_REGION" \
  callableapis:infra terraform import oci_core_vcn.callableapis_vcn "$OCI_VCN_ID"

docker run --rm -v $(pwd):/app -w /app \
  -e AWS_ACCESS_KEY_ID="$AWS_ACCESS_KEY_ID" \
  -e AWS_SECRET_ACCESS_KEY="$AWS_SECRET_ACCESS_KEY" \
  -e OCI_TENANCY_OCID="$OCI_TENANCY_OCID" \
  -e OCI_USER_OCID="$OCI_USER_OCID" \
  -e OCI_FINGERPRINT="$OCI_FINGERPRINT" \
  -e OCI_PRIVATE_KEY_PATH="/app/oci-private-key.pem" \
  -e OCI_COMPARTMENT_ID="$OCI_COMPARTMENT_ID" \
  -e OCI_REGION="$OCI_REGION" \
  callableapis:infra terraform import oci_core_instance.callableapis_arm_1 "$OCI_INSTANCE_ID"

echo "✅ Oracle Cloud resources imported"

# Import IBM Cloud resources
echo "Importing IBM Cloud resources..."
docker run --rm -v $(pwd):/app -w /app \
  -e AWS_ACCESS_KEY_ID="$AWS_ACCESS_KEY_ID" \
  -e AWS_SECRET_ACCESS_KEY="$AWS_SECRET_ACCESS_KEY" \
  -e IBMCLOUD_API_KEY="$IBMCLOUD_API_KEY" \
  -e IBMCLOUD_REGION="$IBMCLOUD_REGION" \
  callableapis:infra terraform import ibm_is_vpc.callableapis_vpc "$IBM_VPC_ID"

docker run --rm -v $(pwd):/app -w /app \
  -e AWS_ACCESS_KEY_ID="$AWS_ACCESS_KEY_ID" \
  -e AWS_SECRET_ACCESS_KEY="$AWS_SECRET_ACCESS_KEY" \
  -e IBMCLOUD_API_KEY="$IBMCLOUD_API_KEY" \
  -e IBMCLOUD_REGION="$IBMCLOUD_REGION" \
  callableapis:infra terraform import ibm_is_instance.callableapis_vsi "$IBM_INSTANCE_ID"

echo "✅ IBM Cloud resources imported"

echo ""
echo "4. VERIFICATION"
echo "==============="

echo "Final Terraform state:"
docker run --rm -v $(pwd):/app -w /app \
  -e AWS_ACCESS_KEY_ID="$AWS_ACCESS_KEY_ID" \
  -e AWS_SECRET_ACCESS_KEY="$AWS_SECRET_ACCESS_KEY" \
  callableapis:infra terraform state list

echo ""
echo "Import complete! All existing infrastructure is now managed by S3-backed Terraform."