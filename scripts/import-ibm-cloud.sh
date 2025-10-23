#!/bin/bash
# Import IBM Cloud Infrastructure Resources

set -e

echo "Importing IBM Cloud Infrastructure Resources"
echo "==========================================="

cd /Users/rlee/dev/infra/terraform

# Load environment variables
source ../env.sh

echo "1. EXTRACTING IBM CLOUD RESOURCE IDs"
echo "===================================="

# Extract IBM Cloud resource IDs from local state
IBM_VPC_ID=$(cat ibm/terraform.tfstate | jq -r '.resources[] | select(.type == "ibm_is_vpc") | .instances[0].attributes.id')
IBM_PGW_ID=$(cat ibm/terraform.tfstate | jq -r '.resources[] | select(.type == "ibm_is_public_gateway") | .instances[0].attributes.id')
IBM_SUBNET_ID=$(cat ibm/terraform.tfstate | jq -r '.resources[] | select(.type == "ibm_is_subnet") | .instances[0].attributes.id')
IBM_SG_ID=$(cat ibm/terraform.tfstate | jq -r '.resources[] | select(.type == "ibm_is_security_group") | .instances[0].attributes.id')
IBM_SSH_KEY_ID=$(cat ibm/terraform.tfstate | jq -r '.resources[] | select(.type == "ibm_is_ssh_key") | .instances[0].attributes.id')
IBM_INSTANCE_ID=$(cat ibm/terraform.tfstate | jq -r '.resources[] | select(.type == "ibm_is_instance") | .instances[0].attributes.id')
IBM_FIP_ID=$(cat ibm/terraform.tfstate | jq -r '.resources[] | select(.type == "ibm_is_floating_ip") | .instances[0].attributes.id')

echo "IBM Cloud Resource IDs:"
echo "- VPC: $IBM_VPC_ID"
echo "- Public Gateway: $IBM_PGW_ID"
echo "- Subnet: $IBM_SUBNET_ID"
echo "- Security Group: $IBM_SG_ID"
echo "- SSH Key: $IBM_SSH_KEY_ID"
echo "- Instance: $IBM_INSTANCE_ID"
echo "- Floating IP: $IBM_FIP_ID"

echo ""
echo "2. IMPORTING IBM CLOUD RESOURCES"
echo "================================"

# Import IBM Cloud core infrastructure
echo "Importing IBM Cloud VPC..."
docker run --rm -v $(pwd):/app -w /app \
  -e AWS_ACCESS_KEY_ID="$AWS_ACCESS_KEY_ID" \
  -e AWS_SECRET_ACCESS_KEY="$AWS_SECRET_ACCESS_KEY" \
  -e IBMCLOUD_API_KEY="$IBMCLOUD_API_KEY" \
  -e IBMCLOUD_REGION="$IBMCLOUD_REGION" \
  callableapis:infra terraform import ibm_is_vpc.callableapis_vpc "$IBM_VPC_ID"

echo "Importing IBM Cloud Public Gateway..."
docker run --rm -v $(pwd):/app -w /app \
  -e AWS_ACCESS_KEY_ID="$AWS_ACCESS_KEY_ID" \
  -e AWS_SECRET_ACCESS_KEY="$AWS_SECRET_ACCESS_KEY" \
  -e IBMCLOUD_API_KEY="$IBMCLOUD_API_KEY" \
  -e IBMCLOUD_REGION="$IBMCLOUD_REGION" \
  callableapis:infra terraform import ibm_is_public_gateway.callableapis_pgw "$IBM_PGW_ID"

echo "Importing IBM Cloud Subnet..."
docker run --rm -v $(pwd):/app -w /app \
  -e AWS_ACCESS_KEY_ID="$AWS_ACCESS_KEY_ID" \
  -e AWS_SECRET_ACCESS_KEY="$AWS_SECRET_ACCESS_KEY" \
  -e IBMCLOUD_API_KEY="$IBMCLOUD_API_KEY" \
  -e IBMCLOUD_REGION="$IBMCLOUD_REGION" \
  callableapis:infra terraform import ibm_is_subnet.callableapis_subnet "$IBM_SUBNET_ID"

echo "Importing IBM Cloud Security Group..."
docker run --rm -v $(pwd):/app -w /app \
  -e AWS_ACCESS_KEY_ID="$AWS_ACCESS_KEY_ID" \
  -e AWS_SECRET_ACCESS_KEY="$AWS_SECRET_ACCESS_KEY" \
  -e IBMCLOUD_API_KEY="$IBMCLOUD_API_KEY" \
  -e IBMCLOUD_REGION="$IBMCLOUD_REGION" \
  callableapis:infra terraform import ibm_is_security_group.callableapis_sg "$IBM_SG_ID"

echo "Importing IBM Cloud SSH Key..."
docker run --rm -v $(pwd):/app -w /app \
  -e AWS_ACCESS_KEY_ID="$AWS_ACCESS_KEY_ID" \
  -e AWS_SECRET_ACCESS_KEY="$AWS_SECRET_ACCESS_KEY" \
  -e IBMCLOUD_API_KEY="$IBMCLOUD_API_KEY" \
  -e IBMCLOUD_REGION="$IBMCLOUD_REGION" \
  callableapis:infra terraform import ibm_is_ssh_key.callableapis_key "$IBM_SSH_KEY_ID"

echo "Importing IBM Cloud Instance..."
docker run --rm -v $(pwd):/app -w /app \
  -e AWS_ACCESS_KEY_ID="$AWS_ACCESS_KEY_ID" \
  -e AWS_SECRET_ACCESS_KEY="$AWS_SECRET_ACCESS_KEY" \
  -e IBMCLOUD_API_KEY="$IBMCLOUD_API_KEY" \
  -e IBMCLOUD_REGION="$IBMCLOUD_REGION" \
  callableapis:infra terraform import ibm_is_instance.callableapis_vsi "$IBM_INSTANCE_ID"

echo "Importing IBM Cloud Floating IP..."
docker run --rm -v $(pwd):/app -w /app \
  -e AWS_ACCESS_KEY_ID="$AWS_ACCESS_KEY_ID" \
  -e AWS_SECRET_ACCESS_KEY="$AWS_SECRET_ACCESS_KEY" \
  -e IBMCLOUD_API_KEY="$IBMCLOUD_API_KEY" \
  -e IBMCLOUD_REGION="$IBMCLOUD_REGION" \
  callableapis:infra terraform import ibm_is_floating_ip.callableapis_fip "$IBM_FIP_ID"

echo ""
echo "3. IMPORTING IBM CLOUD SECURITY GROUP RULES"
echo "==========================================="

# Import security group rules
echo "Importing SSH security group rule..."
docker run --rm -v $(pwd):/app -w /app \
  -e AWS_ACCESS_KEY_ID="$AWS_ACCESS_KEY_ID" \
  -e AWS_SECRET_ACCESS_KEY="$AWS_SECRET_ACCESS_KEY" \
  -e IBMCLOUD_API_KEY="$IBMCLOUD_API_KEY" \
  -e IBMCLOUD_REGION="$IBMCLOUD_REGION" \
  callableapis:infra terraform import ibm_is_security_group_rule.callableapis_ssh "$IBM_SG_ID/rule-ssh"

echo "Importing HTTP security group rule..."
docker run --rm -v $(pwd):/app -w /app \
  -e AWS_ACCESS_KEY_ID="$AWS_ACCESS_KEY_ID" \
  -e AWS_SECRET_ACCESS_KEY="$AWS_SECRET_ACCESS_KEY" \
  -e IBMCLOUD_API_KEY="$IBMCLOUD_API_KEY" \
  -e IBMCLOUD_REGION="$IBMCLOUD_REGION" \
  callableapis:infra terraform import ibm_is_security_group_rule.callableapis_http "$IBM_SG_ID/rule-http"

echo "Importing HTTPS security group rule..."
docker run --rm -v $(pwd):/app -w /app \
  -e AWS_ACCESS_KEY_ID="$AWS_ACCESS_KEY_ID" \
  -e AWS_SECRET_ACCESS_KEY="$AWS_SECRET_ACCESS_KEY" \
  -e IBMCLOUD_API_KEY="$IBMCLOUD_API_KEY" \
  -e IBMCLOUD_REGION="$IBMCLOUD_REGION" \
  callableapis:infra terraform import ibm_is_security_group_rule.callableapis_https "$IBM_SG_ID/rule-https"

echo "Importing outbound DNS security group rule..."
docker run --rm -v $(pwd):/app -w /app \
  -e AWS_ACCESS_KEY_ID="$AWS_ACCESS_KEY_ID" \
  -e AWS_SECRET_ACCESS_KEY="$AWS_SECRET_ACCESS_KEY" \
  -e IBMCLOUD_API_KEY="$IBMCLOUD_API_KEY" \
  -e IBMCLOUD_REGION="$IBMCLOUD_REGION" \
  callableapis:infra terraform import ibm_is_security_group_rule.callableapis_outbound_dns "$IBM_SG_ID/rule-outbound-dns"

echo "Importing outbound HTTP security group rule..."
docker run --rm -v $(pwd):/app -w /app \
  -e AWS_ACCESS_KEY_ID="$AWS_ACCESS_KEY_ID" \
  -e AWS_SECRET_ACCESS_KEY="$AWS_SECRET_ACCESS_KEY" \
  -e IBMCLOUD_API_KEY="$IBMCLOUD_API_KEY" \
  -e IBMCLOUD_REGION="$IBMCLOUD_REGION" \
  callableapis:infra terraform import ibm_is_security_group_rule.callableapis_outbound_http "$IBM_SG_ID/rule-outbound-http"

echo "Importing outbound HTTPS security group rule..."
docker run --rm -v $(pwd):/app -w /app \
  -e AWS_ACCESS_KEY_ID="$AWS_ACCESS_KEY_ID" \
  -e AWS_SECRET_ACCESS_KEY="$AWS_SECRET_ACCESS_KEY" \
  -e IBMCLOUD_API_KEY="$IBMCLOUD_API_KEY" \
  -e IBMCLOUD_REGION="$IBMCLOUD_REGION" \
  callableapis:infra terraform import ibm_is_security_group_rule.callableapis_outbound_https "$IBM_SG_ID/rule-outbound-https"

echo "Importing outbound ICMP security group rule..."
docker run --rm -v $(pwd):/app -w /app \
  -e AWS_ACCESS_KEY_ID="$AWS_ACCESS_KEY_ID" \
  -e AWS_SECRET_ACCESS_KEY="$AWS_SECRET_ACCESS_KEY" \
  -e IBMCLOUD_API_KEY="$IBMCLOUD_API_KEY" \
  -e IBMCLOUD_REGION="$IBMCLOUD_REGION" \
  callableapis:infra terraform import ibm_is_security_group_rule.callableapis_outbound_icmp "$IBM_SG_ID/rule-outbound-icmp"

echo ""
echo "4. VERIFICATION"
echo "==============="

echo "IBM Cloud resources in Terraform state:"
docker run --rm -v $(pwd):/app -w /app \
  -e AWS_ACCESS_KEY_ID="$AWS_ACCESS_KEY_ID" \
  -e AWS_SECRET_ACCESS_KEY="$AWS_SECRET_ACCESS_KEY" \
  callableapis:infra terraform state list | grep ibm

echo ""
echo "5. COMPLETE INFRASTRUCTURE VERIFICATION"
echo "======================================="

echo "Total resources in Terraform state:"
docker run --rm -v $(pwd):/app -w /app \
  -e AWS_ACCESS_KEY_ID="$AWS_ACCESS_KEY_ID" \
  -e AWS_SECRET_ACCESS_KEY="$AWS_SECRET_ACCESS_KEY" \
  callableapis:infra terraform state list | wc -l

echo ""
echo "✅ IBM Cloud import complete!"
echo "🎉 All infrastructure is now managed by S3-backed Terraform!"
