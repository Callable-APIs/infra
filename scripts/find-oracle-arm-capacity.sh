#!/bin/bash
# Search Oracle Cloud regions for ARM instance availability
# Usage: ./scripts/find-oracle-arm-capacity.sh

set -e

cd "$(dirname "$0")/.."
source env.sh

echo "Searching Oracle Cloud regions for ARM (VM.Standard.A1.Flex) instance availability..."
echo "This may take a few minutes..."
echo ""

# List of common Oracle Cloud regions to check
REGIONS=(
    "us-ashburn-1"
    "us-phoenix-1"
    "us-sanjose-1"
    "us-chicago-1"
    "us-sanjose-1"
    "ca-toronto-1"
    "sa-saopaulo-1"
    "uk-london-1"
    "uk-cardiff-1"
    "eu-frankfurt-1"
    "eu-amsterdam-1"
    "eu-zurich-1"
    "ap-mumbai-1"
    "ap-seoul-1"
    "ap-sydney-1"
    "ap-tokyo-1"
    "ap-osaka-1"
    "ap-singapore-1"
    "me-jeddah-1"
    "me-dubai-1"
)

AVAILABLE_REGIONS=()

for region in "${REGIONS[@]}"; do
    echo -n "Checking $region... "
    
    # Try to get availability domains for this region
    result=$(docker run --rm -v $(pwd):/app -w /app \
        -e OCI_TENANCY_OCID="$OCI_TENANCY_OCID" \
        -e OCI_USER_OCID="$OCI_USER_OCID" \
        -e OCI_FINGERPRINT="$OCI_FINGERPRINT" \
        -e OCI_PRIVATE_KEY_PATH="/app/oci-private-key.pem" \
        -e OCI_COMPARTMENT_ID="$OCI_COMPARTMENT_ID" \
        -e OCI_REGION="$region" \
        callableapis:infra bash -c \
        "oci iam availability-domain list --compartment-id '$OCI_COMPARTMENT_ID' --region '$region' 2>&1" 2>&1 || true)
    
    if echo "$result" | grep -q "availability-domains"; then
        echo "✓ Available"
        AVAILABLE_REGIONS+=("$region")
    elif echo "$result" | grep -qi "not authorized\|unauthorized"; then
        echo "✗ Not authorized"
    elif echo "$result" | grep -qi "not found\|invalid"; then
        echo "✗ Region not found"
    else
        echo "? Unknown (may need to check manually)"
    fi
done

echo ""
echo "=========================================="
echo "Regions with potential ARM capacity:"
echo "=========================================="
if [ ${#AVAILABLE_REGIONS[@]} -eq 0 ]; then
    echo "None found automatically. You may need to check the Oracle Cloud Console."
else
    for region in "${AVAILABLE_REGIONS[@]}"; do
        echo "  - $region"
    done
    echo ""
    echo "To try creating instances in one of these regions:"
    echo "  1. Update OCI_REGION in env.sh"
    echo "  2. Run: ./scripts/retry-oracle-instances.sh"
fi

