#!/bin/bash
# Script to set up Terraform S3 backend and import existing infrastructure

set -e

echo "Setting up Terraform S3 backend and importing existing infrastructure..."
echo "======================================================================"

# Step 1: Bootstrap S3 backend
echo "Step 1: Creating S3 bucket and DynamoDB table for Terraform state..."
cd /Users/rlee/dev/infra/terraform/bootstrap

# Initialize and apply bootstrap configuration
docker run --rm -v $(pwd):/app -w /app \
  -e AWS_ACCESS_KEY_ID="$AWS_ACCESS_KEY_ID" \
  -e AWS_SECRET_ACCESS_KEY="$AWS_SECRET_ACCESS_KEY" \
  callableapis:infra terraform init

docker run --rm -v $(pwd):/app -w /app \
  -e AWS_ACCESS_KEY_ID="$AWS_ACCESS_KEY_ID" \
  -e AWS_SECRET_ACCESS_KEY="$AWS_SECRET_ACCESS_KEY" \
  callableapis:infra terraform plan -var="aws_access_key_id=$AWS_ACCESS_KEY_ID" -var="aws_secret_access_key=$AWS_SECRET_ACCESS_KEY"

docker run --rm -v $(pwd):/app -w /app \
  -e AWS_ACCESS_KEY_ID="$AWS_ACCESS_KEY_ID" \
  -e AWS_SECRET_ACCESS_KEY="$AWS_SECRET_ACCESS_KEY" \
  callableapis:infra terraform apply -auto-approve -var="aws_access_key_id=$AWS_ACCESS_KEY_ID" -var="aws_secret_access_key=$AWS_SECRET_ACCESS_KEY"

echo "✅ S3 backend created successfully"
echo ""

# Step 2: Migrate main Terraform to S3 backend
echo "Step 2: Migrating main Terraform configuration to S3 backend..."
cd /Users/rlee/dev/infra/terraform

# Initialize with S3 backend
echo "yes" | docker run --rm -i -v $(pwd):/app -w /app \
  -e AWS_ACCESS_KEY_ID="$AWS_ACCESS_KEY_ID" \
  -e AWS_SECRET_ACCESS_KEY="$AWS_SECRET_ACCESS_KEY" \
  callableapis:infra terraform init -migrate-state

echo "✅ Terraform state migrated to S3 backend"
echo ""

# Step 3: Import existing infrastructure
echo "Step 3: Importing existing infrastructure into Terraform state..."
echo "Note: You'll need to provide the actual resource IDs for your infrastructure"
echo ""

# Google Cloud firewall rule
echo "Importing Google Cloud firewall rule..."
echo "You'll need to run:"
echo "docker run --rm -v \$(pwd):/app -w /app callableapis:infra terraform import google_compute_firewall.callableapis_allow_8080 projects/YOUR_PROJECT_ID/global/firewalls/callableapis-allow-8080"
echo ""

# Oracle Cloud security list
echo "Importing Oracle Cloud security list..."
echo "You'll need to run:"
echo "docker run --rm -v \$(pwd):/app -w /app callableapis:infra terraform import oci_core_security_list.callableapis_sl ocid1.securitylist.oc1.xxxxx"
echo ""

# IBM Cloud security group rule
echo "Importing IBM Cloud security group rule..."
echo "You'll need to run:"
echo "docker run --rm -v \$(pwd):/app -w /app callableapis:infra terraform import ibm_is_security_group_rule.callableapis_8080 YOUR_SECURITY_GROUP_ID/YOUR_RULE_ID"
echo ""

echo "After importing the existing resources, you can manage firewall rules with:"
echo "docker run --rm -v \$(pwd):/app -w /app callableapis:infra terraform plan"
echo "docker run --rm -v \$(pwd):/app -w /app callableapis:infra terraform apply"
echo ""

echo "🎉 Terraform backend setup complete!"
echo "State is now stored in S3: callableapis-terraform-state"
echo "State locking is enabled with DynamoDB: callableapis-terraform-locks"
