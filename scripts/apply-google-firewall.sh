#!/bin/bash
# Script to apply Google Cloud firewall rule for port 8080

set -e

echo "Applying Google Cloud firewall rule for port 8080..."
echo "=================================================="

# Check if we have the required variables
if [ -z "$GCP_PROJECT_ID" ]; then
    echo "Error: GCP_PROJECT_ID environment variable is not set"
    echo "Please set it with: export GCP_PROJECT_ID=your-project-id"
    exit 1
fi

echo "Using GCP Project: $GCP_PROJECT_ID"
echo ""

# Apply the firewall rule
cd /Users/rlee/dev/infra/terraform

echo "Applying Google Cloud firewall rule..."
docker run --rm -v $(pwd):/app -w /app \
  -e AWS_ACCESS_KEY_ID="$AWS_ACCESS_KEY_ID" \
  -e AWS_SECRET_ACCESS_KEY="$AWS_SECRET_ACCESS_KEY" \
  callableapis:infra terraform plan \
  -var="gcp_project_id=$GCP_PROJECT_ID" \
  -target=google_compute_firewall.callableapis_allow_8080

echo ""
echo "If the plan looks good, run:"
echo "docker run --rm -v \$(pwd):/app -w /app -e AWS_ACCESS_KEY_ID=\"\$AWS_ACCESS_KEY_ID\" -e AWS_SECRET_ACCESS_KEY=\"\$AWS_SECRET_ACCESS_KEY\" callableapis:infra terraform apply -var=\"gcp_project_id=$GCP_PROJECT_ID\" -target=google_compute_firewall.callableapis_allow_8080"
