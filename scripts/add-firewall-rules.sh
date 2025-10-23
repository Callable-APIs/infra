#!/bin/bash
# Script to add port 8080 firewall rules to containerd nodes only
# This script provides manual commands to open port 8080 for container services

set -e

echo "Adding firewall rules for port 8080 to containerd nodes..."
echo "=========================================================="
echo "Target nodes:"
echo "  - Oracle Cloud (onode1): 159.54.170.237"
echo "  - Google Cloud (gnode1): 35.233.161.8" 
echo "  - IBM Cloud (inode1): 52.116.135.43"
echo ""
echo "Note: AWS Elastic Beanstalk is a managed service and doesn't run our custom containers"
echo ""

# AWS - Skip (Elastic Beanstalk is managed service)
echo "AWS - SKIPPED:"
echo "-------------"
echo "Elastic Beanstalk is a managed service that doesn't run our custom containers."
echo "No firewall rules needed for AWS in this setup."
echo ""

# Google Cloud - Add firewall rule
echo "Google Cloud Firewall Rule:"
echo "---------------------------"
echo "gcloud compute firewall-rules create allow-8080 \\"
echo "  --allow tcp:8080 \\"
echo "  --source-ranges 0.0.0.0/0 \\"
echo "  --target-tags callableapis-web \\"
echo "  --description 'Allow port 8080 for container services'"
echo ""

# Oracle Cloud - Add security list rule
echo "Oracle Cloud Security List Rule:"
echo "-------------------------------"
echo "1. Go to Oracle Cloud Console"
echo "2. Navigate to Networking > Virtual Cloud Networks"
echo "3. Select your VCN > Security Lists"
echo "4. Add ingress rule:"
echo "   - Source: 0.0.0.0/0"
echo "   - IP Protocol: TCP"
echo "   - Source Port Range: All"
echo "   - Destination Port Range: 8080"
echo "   - Description: Allow port 8080 for container services"
echo ""

# IBM Cloud - Add security group rule
echo "IBM Cloud Security Group Rule:"
echo "-----------------------------"
echo "1. Go to IBM Cloud Console"
echo "2. Navigate to VPC Infrastructure > Security Groups"
echo "3. Select your security group"
echo "4. Add rule:"
echo "   - Direction: Inbound"
echo "   - Type: TCP"
echo "   - Port: 8080"
echo "   - Source: 0.0.0.0/0"
echo "   - Description: Allow port 8080 for container services"
echo ""

echo "After adding these rules, test the endpoints:"
echo "curl http://159.54.170.237:8080/health  # Oracle"
echo "curl http://35.233.161.8:8080/health    # Google"
echo "curl http://52.116.135.43:8080/health    # IBM"
echo ""

echo "Note: You may need to replace the security group IDs and adjust"
echo "the commands based on your actual cloud provider configurations."
