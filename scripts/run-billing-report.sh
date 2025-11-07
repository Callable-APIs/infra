#!/bin/bash
# Run unified billing application
# Usage: ./scripts/run-billing-report.sh [options]

set -e

cd "$(dirname "$0")/.."
source env.sh

# Default to showing both daily and comparison
DAILY="--daily"
COMPARE="--compare"

# Parse arguments
ARGS=()
while [[ $# -gt 0 ]]; do
    case $1 in
        --daily-only)
            DAILY="--daily"
            COMPARE=""
            shift
            ;;
        --compare-only)
            DAILY=""
            COMPARE="--compare"
            shift
            ;;
        --no-daily)
            DAILY=""
            shift
            ;;
        --no-compare)
            COMPARE=""
            shift
            ;;
        --providers)
            # Pass through providers argument
            ARGS+=("$1")
            shift
            if [[ $# -gt 0 ]]; then
                ARGS+=("$1")
                shift
            fi
            ;;
        *)
            ARGS+=("$1")
            shift
            ;;
    esac
done

# Run in Docker container
docker run --rm -v $(pwd):/app -w /app --entrypoint python3 \
    -e AWS_ACCESS_KEY_ID="$AWS_ACCESS_KEY_ID" \
    -e AWS_SECRET_ACCESS_KEY="$AWS_SECRET_ACCESS_KEY" \
    -e OCI_TENANCY_OCID="$OCI_TENANCY_OCID" \
    -e OCI_USER_OCID="$OCI_USER_OCID" \
    -e OCI_FINGERPRINT="$OCI_FINGERPRINT" \
    -e OCI_PRIVATE_KEY_PATH="/app/oci-private-key.pem" \
    -e OCI_COMPARTMENT_ID="$OCI_COMPARTMENT_ID" \
    -e OCI_REGION="$OCI_REGION" \
    -e IBMCLOUD_API_KEY="$IBMCLOUD_API_KEY" \
    -e IBMCLOUD_REGION="$IBMCLOUD_REGION" \
    callableapis:infra -m clint billing \
    $DAILY $COMPARE "${ARGS[@]}"

