#!/bin/bash
# Script to destroy non-compliant Oracle Cloud and IBM Cloud nodes
# These nodes are not free tier compliant and have been migrated away from

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Load environment variables
if [ -f "../env.sh" ]; then
    source ../env.sh
fi

echo "=========================================="
echo "Destroying Non-Compliant Cloud Resources"
echo "=========================================="
echo ""
echo "This will destroy:"
echo "  - Oracle Cloud: onode1, onode2 (VM.Standard.E5.Flex - not free tier)"
echo "  - IBM Cloud: inode1 (bx2-2x8 - not free tier)"
echo ""
read -p "Are you sure you want to proceed? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo "Aborted."
    exit 1
fi

echo ""
echo "Step 1: Destroying Oracle Cloud instances..."
echo "-------------------------------------------"

# Destroy Oracle Cloud instances
docker run --rm -v "$(pwd)/..":/app -w /app/terraform \
  -e OCI_TENANCY_OCID="$OCI_TENANCY_OCID" \
  -e OCI_USER_OCID="$OCI_USER_OCID" \
  -e OCI_FINGERPRINT="$OCI_FINGERPRINT" \
  -e OCI_PRIVATE_KEY_PATH="/app/oci-private-key.pem" \
  -e OCI_COMPARTMENT_ID="$OCI_COMPARTMENT_ID" \
  -e OCI_REGION="$OCI_REGION" \
  callableapis:infra terraform destroy \
  -target=oci_core_instance.callableapis_arm_1 \
  -target=oci_core_instance.callableapis_arm_2 \
  -auto-approve || echo "Warning: Oracle Cloud destroy failed or resources already removed"

echo ""
echo "Step 2: Destroying Oracle Cloud networking (if instances are gone)..."
echo "-------------------------------------------"

# Destroy Oracle Cloud networking (only if instances are gone)
docker run --rm -v "$(pwd)/..":/app -w /app/terraform \
  -e OCI_TENANCY_OCID="$OCI_TENANCY_OCID" \
  -e OCI_USER_OCID="$OCI_USER_OCID" \
  -e OCI_FINGERPRINT="$OCI_FINGERPRINT" \
  -e OCI_PRIVATE_KEY_PATH="/app/oci-private-key.pem" \
  -e OCI_COMPARTMENT_ID="$OCI_COMPARTMENT_ID" \
  -e OCI_REGION="$OCI_REGION" \
  callableapis:infra terraform destroy \
  -target=oci_core_subnet.callableapis_subnet \
  -target=oci_core_route_table.callableapis_rt \
  -target=oci_core_internet_gateway.callableapis_igw \
  -target=oci_core_security_list.callableapis_sl \
  -target=oci_core_vcn.callableapis_vcn \
  -auto-approve || echo "Warning: Oracle Cloud networking destroy failed or resources already removed"

echo ""
echo "Step 3: Destroying IBM Cloud instance..."
echo "-------------------------------------------"

# Destroy IBM Cloud instance
docker run --rm -v "$(pwd)/..":/app -w /app/terraform \
  -e IBMCLOUD_API_KEY="$IBMCLOUD_API_KEY" \
  -e IBMCLOUD_REGION="$IBMCLOUD_REGION" \
  callableapis:infra terraform destroy \
  -target=ibm_is_floating_ip.callableapis_fip \
  -target=ibm_is_instance.callableapis_vsi \
  -auto-approve || echo "Warning: IBM Cloud instance destroy failed or resources already removed"

echo ""
echo "Step 4: Destroying IBM Cloud networking (if instance is gone)..."
echo "-------------------------------------------"

# Destroy IBM Cloud networking (only if instance is gone)
docker run --rm -v "$(pwd)/..":/app -w /app/terraform \
  -e IBMCLOUD_API_KEY="$IBMCLOUD_API_KEY" \
  -e IBMCLOUD_REGION="$IBMCLOUD_REGION" \
  callableapis:infra terraform destroy \
  -target=ibm_is_subnet.callableapis_subnet \
  -target=ibm_is_public_gateway.callableapis_pgw \
  -target=ibm_is_security_group.callableapis_sg \
  -target=ibm_is_vpc.callableapis_vpc \
  -auto-approve || echo "Warning: IBM Cloud networking destroy failed or resources already removed"

echo ""
echo "=========================================="
echo "Cleanup Complete"
echo "=========================================="
echo ""
echo "Next steps:"
echo "  1. Verify resources are destroyed in cloud consoles"
echo "  2. Run 'terraform state list' to verify state cleanup"
echo "  3. Remove any remaining Terraform state entries manually if needed"
echo ""


