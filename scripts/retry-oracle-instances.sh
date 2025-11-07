#!/bin/bash
# Retry script for creating Oracle Cloud free tier ARM instances
# Usage: ./scripts/retry-oracle-instances.sh

set -e

cd "$(dirname "$0")/.."
source env.sh

cd terraform

echo "Retrying Oracle Cloud ARM instance creation..."
echo "This may fail if capacity is still unavailable."
echo ""

docker run --rm -v $(pwd)/..:/workspace -w /workspace/terraform \
  -e AWS_ACCESS_KEY_ID="$AWS_ACCESS_KEY_ID" \
  -e AWS_SECRET_ACCESS_KEY="$AWS_SECRET_ACCESS_KEY" \
  -e OCI_TENANCY_OCID="$OCI_TENANCY_OCID" \
  -e OCI_USER_OCID="$OCI_USER_OCID" \
  -e OCI_FINGERPRINT="$OCI_FINGERPRINT" \
  -e OCI_PRIVATE_KEY_PATH="/workspace/oci-private-key.pem" \
  -e OCI_COMPARTMENT_ID="$OCI_COMPARTMENT_ID" \
  -e OCI_REGION="$OCI_REGION" \
  -e IBMCLOUD_API_KEY="$IBMCLOUD_API_KEY" \
  -e IBMCLOUD_REGION="$IBMCLOUD_REGION" \
  callableapis:infra terraform apply \
  -target=oci_core_instance.callableapis_arm_1 \
  -target=oci_core_instance.callableapis_arm_2 \
  -auto-approve

echo ""
echo "If successful, instances should be created and running."
echo "Check status with: terraform state list | grep callableapis_arm"

