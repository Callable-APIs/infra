#!/bin/bash
# Import Oracle Cloud Infrastructure Resources

set -e

echo "Importing Oracle Cloud Infrastructure Resources"
echo "=============================================="

cd /Users/rlee/dev/infra/terraform

# Load environment variables
source ../env.sh

echo "1. EXTRACTING ORACLE CLOUD RESOURCE IDs"
echo "======================================="

# Extract Oracle Cloud resource IDs from local state
OCI_VCN_ID=$(cat oracle/terraform.tfstate | jq -r '.resources[] | select(.type == "oci_core_vcn") | .instances[0].attributes.id')
OCI_IGW_ID=$(cat oracle/terraform.tfstate | jq -r '.resources[] | select(.type == "oci_core_internet_gateway") | .instances[0].attributes.id')
OCI_RT_ID=$(cat oracle/terraform.tfstate | jq -r '.resources[] | select(.type == "oci_core_route_table") | .instances[0].attributes.id')
OCI_SL_ID=$(cat oracle/terraform.tfstate | jq -r '.resources[] | select(.type == "oci_core_security_list") | .instances[0].attributes.id')
OCI_SUBNET_ID=$(cat oracle/terraform.tfstate | jq -r '.resources[] | select(.type == "oci_core_subnet") | .instances[0].attributes.id')
OCI_INSTANCE_ID=$(cat oracle/terraform.tfstate | jq -r '.resources[] | select(.type == "oci_core_instance") | .instances[0].attributes.id')

echo "Oracle Cloud Resource IDs:"
echo "- VCN: $OCI_VCN_ID"
echo "- Internet Gateway: $OCI_IGW_ID"
echo "- Route Table: $OCI_RT_ID"
echo "- Security List: $OCI_SL_ID"
echo "- Subnet: $OCI_SUBNET_ID"
echo "- Instance: $OCI_INSTANCE_ID"

echo ""
echo "2. IMPORTING ORACLE CLOUD RESOURCES"
echo "==================================="

# Import Oracle Cloud resources one by one
echo "Importing OCI Internet Gateway..."
docker run --rm -v $(pwd):/app -w /app \
  -e AWS_ACCESS_KEY_ID="$AWS_ACCESS_KEY_ID" \
  -e AWS_SECRET_ACCESS_KEY="$AWS_SECRET_ACCESS_KEY" \
  -e OCI_TENANCY_OCID="$OCI_TENANCY_OCID" \
  -e OCI_USER_OCID="$OCI_USER_OCID" \
  -e OCI_FINGERPRINT="$OCI_FINGERPRINT" \
  -e OCI_PRIVATE_KEY_PATH="/app/oci-private-key.pem" \
  -e OCI_COMPARTMENT_ID="$OCI_COMPARTMENT_ID" \
  -e OCI_REGION="$OCI_REGION" \
  callableapis:infra terraform import oci_core_internet_gateway.callableapis_igw "$OCI_IGW_ID"

echo "Importing OCI Route Table..."
docker run --rm -v $(pwd):/app -w /app \
  -e AWS_ACCESS_KEY_ID="$AWS_ACCESS_KEY_ID" \
  -e AWS_SECRET_ACCESS_KEY="$AWS_SECRET_ACCESS_KEY" \
  -e OCI_TENANCY_OCID="$OCI_TENANCY_OCID" \
  -e OCI_USER_OCID="$OCI_USER_OCID" \
  -e OCI_FINGERPRINT="$OCI_FINGERPRINT" \
  -e OCI_PRIVATE_KEY_PATH="/app/oci-private-key.pem" \
  -e OCI_COMPARTMENT_ID="$OCI_COMPARTMENT_ID" \
  -e OCI_REGION="$OCI_REGION" \
  callableapis:infra terraform import oci_core_route_table.callableapis_rt "$OCI_RT_ID"

echo "Importing OCI Security List..."
docker run --rm -v $(pwd):/app -w /app \
  -e AWS_ACCESS_KEY_ID="$AWS_ACCESS_KEY_ID" \
  -e AWS_SECRET_ACCESS_KEY="$AWS_SECRET_ACCESS_KEY" \
  -e OCI_TENANCY_OCID="$OCI_TENANCY_OCID" \
  -e OCI_USER_OCID="$OCI_USER_OCID" \
  -e OCI_FINGERPRINT="$OCI_FINGERPRINT" \
  -e OCI_PRIVATE_KEY_PATH="/app/oci-private-key.pem" \
  -e OCI_COMPARTMENT_ID="$OCI_COMPARTMENT_ID" \
  -e OCI_REGION="$OCI_REGION" \
  callableapis:infra terraform import oci_core_security_list.callableapis_sl "$OCI_SL_ID"

echo "Importing OCI Subnet..."
docker run --rm -v $(pwd):/app -w /app \
  -e AWS_ACCESS_KEY_ID="$AWS_ACCESS_KEY_ID" \
  -e AWS_SECRET_ACCESS_KEY="$AWS_SECRET_ACCESS_KEY" \
  -e OCI_TENANCY_OCID="$OCI_TENANCY_OCID" \
  -e OCI_USER_OCID="$OCI_USER_OCID" \
  -e OCI_FINGERPRINT="$OCI_FINGERPRINT" \
  -e OCI_PRIVATE_KEY_PATH="/app/oci-private-key.pem" \
  -e OCI_COMPARTMENT_ID="$OCI_COMPARTMENT_ID" \
  -e OCI_REGION="$OCI_REGION" \
  callableapis:infra terraform import oci_core_subnet.callableapis_subnet "$OCI_SUBNET_ID"

echo "Importing OCI Instance..."
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

echo ""
echo "3. VERIFICATION"
echo "==============="

echo "Oracle Cloud resources in Terraform state:"
docker run --rm -v $(pwd):/app -w /app \
  -e AWS_ACCESS_KEY_ID="$AWS_ACCESS_KEY_ID" \
  -e AWS_SECRET_ACCESS_KEY="$AWS_SECRET_ACCESS_KEY" \
  callableapis:infra terraform state list | grep oci

echo ""
echo "✅ Oracle Cloud import complete!"
