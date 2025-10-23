#!/bin/bash
# Import Google Cloud Infrastructure Resources

set -e

echo "Importing Google Cloud Infrastructure Resources"
echo "=============================================="

cd /Users/rlee/dev/infra/terraform

# Load environment variables
source ../env.sh

echo "1. EXTRACTING GOOGLE CLOUD RESOURCE IDs"
echo "======================================="

# Extract Google Cloud resource IDs from local state
GCP_PROJECT_ID=$(cat google/terraform.tfstate | jq -r '.resources[] | select(.type == "google_compute_network") | .instances[0].attributes.project')
GCP_NETWORK_ID=$(cat google/terraform.tfstate | jq -r '.resources[] | select(.type == "google_compute_network") | .instances[0].attributes.id')
GCP_SUBNET_ID=$(cat google/terraform.tfstate | jq -r '.resources[] | select(.type == "google_compute_subnetwork") | .instances[0].attributes.id')
GCP_INSTANCE_ID=$(cat google/terraform.tfstate | jq -r '.resources[] | select(.type == "google_compute_instance") | .instances[0].attributes.id')
GCP_ZONE=$(cat google/terraform.tfstate | jq -r '.resources[] | select(.type == "google_compute_instance") | .instances[0].attributes.zone')

echo "Google Cloud Resource IDs:"
echo "- Project: $GCP_PROJECT_ID"
echo "- Network: $GCP_NETWORK_ID"
echo "- Subnet: $GCP_SUBNET_ID"
echo "- Instance: $GCP_INSTANCE_ID"
echo "- Zone: $GCP_ZONE"

echo ""
echo "2. IMPORTING GOOGLE CLOUD RESOURCES"
echo "==================================="

# Import Google Cloud firewall rules
echo "Importing Google Cloud Firewall Rules..."

echo "Importing SSH firewall rule..."
docker run --rm -v $(pwd):/app -w /app \
  -e AWS_ACCESS_KEY_ID="$AWS_ACCESS_KEY_ID" \
  -e AWS_SECRET_ACCESS_KEY="$AWS_SECRET_ACCESS_KEY" \
  -e GOOGLE_APPLICATION_CREDENTIALS="/app/google-credentials.json" \
  -e GCP_PROJECT_ID="$GOOGLE_PROJECT_ID" \
  -e GCP_REGION="$GOOGLE_REGION" \
  -e GCP_ZONE="$GOOGLE_ZONE" \
  callableapis:infra terraform import google_compute_firewall.callableapis_allow_ssh "projects/$GCP_PROJECT_ID/global/firewalls/callableapis-allow-ssh"

echo "Importing HTTP firewall rule..."
docker run --rm -v $(pwd):/app -w /app \
  -e AWS_ACCESS_KEY_ID="$AWS_ACCESS_KEY_ID" \
  -e AWS_SECRET_ACCESS_KEY="$AWS_SECRET_ACCESS_KEY" \
  -e GOOGLE_APPLICATION_CREDENTIALS="/app/google-credentials.json" \
  -e GCP_PROJECT_ID="$GOOGLE_PROJECT_ID" \
  -e GCP_REGION="$GOOGLE_REGION" \
  -e GCP_ZONE="$GOOGLE_ZONE" \
  callableapis:infra terraform import google_compute_firewall.callableapis_allow_http "projects/$GCP_PROJECT_ID/global/firewalls/callableapis-allow-http"

echo "Importing HTTPS firewall rule..."
docker run --rm -v $(pwd):/app -w /app \
  -e AWS_ACCESS_KEY_ID="$AWS_ACCESS_KEY_ID" \
  -e AWS_SECRET_ACCESS_KEY="$AWS_SECRET_ACCESS_KEY" \
  -e GOOGLE_APPLICATION_CREDENTIALS="/app/google-credentials.json" \
  -e GCP_PROJECT_ID="$GOOGLE_PROJECT_ID" \
  -e GCP_REGION="$GOOGLE_REGION" \
  -e GCP_ZONE="$GOOGLE_ZONE" \
  callableapis:infra terraform import google_compute_firewall.callableapis_allow_https "projects/$GCP_PROJECT_ID/global/firewalls/callableapis-allow-https"

echo "Importing Google Cloud Project Services..."
echo "Importing Compute API service..."
docker run --rm -v $(pwd):/app -w /app \
  -e AWS_ACCESS_KEY_ID="$AWS_ACCESS_KEY_ID" \
  -e AWS_SECRET_ACCESS_KEY="$AWS_SECRET_ACCESS_KEY" \
  -e GOOGLE_APPLICATION_CREDENTIALS="/app/google-credentials.json" \
  -e GCP_PROJECT_ID="$GOOGLE_PROJECT_ID" \
  -e GCP_REGION="$GOOGLE_REGION" \
  -e GCP_ZONE="$GOOGLE_ZONE" \
  callableapis:infra terraform import google_project_service.compute_api "projects/$GCP_PROJECT_ID/services/compute.googleapis.com"

echo "Importing OS Login API service..."
docker run --rm -v $(pwd):/app -w /app \
  -e AWS_ACCESS_KEY_ID="$AWS_ACCESS_KEY_ID" \
  -e AWS_SECRET_ACCESS_KEY="$AWS_SECRET_ACCESS_KEY" \
  -e GOOGLE_APPLICATION_CREDENTIALS="/app/google-credentials.json" \
  -e GCP_PROJECT_ID="$GOOGLE_PROJECT_ID" \
  -e GCP_REGION="$GOOGLE_REGION" \
  -e GCP_ZONE="$GOOGLE_ZONE" \
  callableapis:infra terraform import google_project_service.oslogin_api "projects/$GCP_PROJECT_ID/services/oslogin.googleapis.com"

echo "Importing Time Sleep resource..."
docker run --rm -v $(pwd):/app -w /app \
  -e AWS_ACCESS_KEY_ID="$AWS_ACCESS_KEY_ID" \
  -e AWS_SECRET_ACCESS_KEY="$AWS_SECRET_ACCESS_KEY" \
  -e GOOGLE_APPLICATION_CREDENTIALS="/app/google-credentials.json" \
  -e GCP_PROJECT_ID="$GOOGLE_PROJECT_ID" \
  -e GCP_REGION="$GOOGLE_REGION" \
  -e GCP_ZONE="$GOOGLE_ZONE" \
  callableapis:infra terraform import time_sleep.wait_for_apis "2025-10-21T20:00:00Z"

echo ""
echo "3. VERIFICATION"
echo "==============="

echo "Google Cloud resources in Terraform state:"
docker run --rm -v $(pwd):/app -w /app \
  -e AWS_ACCESS_KEY_ID="$AWS_ACCESS_KEY_ID" \
  -e AWS_SECRET_ACCESS_KEY="$AWS_SECRET_ACCESS_KEY" \
  callableapis:infra terraform state list | grep google

echo ""
echo "✅ Google Cloud import complete!"
