#!/bin/bash
# Run infrastructure monitoring and management agent
# Usage: ./scripts/run-infrastructure-agent.sh [options]

set -e

cd "$(dirname "$0")/.."
source env.sh

# Default task
TASK="all"

# Parse arguments
ARGS=()
while [[ $# -gt 0 ]]; do
    case $1 in
        --task)
            TASK="$2"
            shift 2
            ;;
        --config)
            ARGS+=("--config" "$2")
            shift 2
            ;;
        --health-output)
            ARGS+=("--health-output" "$2")
            shift 2
            ;;
        --cost-output)
            ARGS+=("--cost-output" "$2")
            shift 2
            ;;
        *)
            ARGS+=("$1")
            shift
            ;;
    esac
done

# Run in Docker container
docker run --rm -v $(pwd):/app -w /app \
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
    -v "$HOME/.ssh:/root/.ssh:ro" \
    callableapis:infra python -m clint agent \
    --task "$TASK" "${ARGS[@]}"

