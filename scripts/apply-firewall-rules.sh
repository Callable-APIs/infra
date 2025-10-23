#!/bin/bash
# Script to apply firewall rules for port 8080 on containerd nodes
# This script provides specific commands for each cloud provider

set -e

echo "Applying firewall rules for port 8080 on containerd nodes..."
echo "=========================================================="
echo "Target nodes:"
echo "  - Oracle Cloud (onode1): 159.54.170.237"
echo "  - Google Cloud (gnode1): 35.233.161.8" 
echo "  - IBM Cloud (inode1): 52.116.135.43"
echo ""

# Test current connectivity
echo "Testing current connectivity..."
echo "=============================="
for node in "Oracle:159.54.170.237" "Google:35.233.161.8" "IBM:52.116.135.43"; do
    provider=$(echo $node | cut -d: -f1)
    ip=$(echo $node | cut -d: -f2)
    echo -n "Testing $provider ($ip:8080)... "
    if timeout 3 curl -s http://$ip:8080/health > /dev/null 2>&1; then
        echo "✅ OPEN"
    else
        echo "❌ BLOCKED"
    fi
done
echo ""

# Google Cloud - Try to apply firewall rule
echo "Google Cloud Firewall Rule:"
echo "---------------------------"
echo "Attempting to apply Google Cloud firewall rule..."

# Check if gcloud is available
if command -v gcloud >/dev/null 2>&1; then
    echo "gcloud CLI found, attempting to create firewall rule..."
    if gcloud compute firewall-rules create allow-8080 \
        --allow tcp:8080 \
        --source-ranges 0.0.0.0/0 \
        --target-tags callableapis-web \
        --description 'Allow port 8080 for container services' 2>/dev/null; then
        echo "✅ Google Cloud firewall rule created successfully"
    else
        echo "❌ Failed to create Google Cloud firewall rule (may already exist or need authentication)"
        echo "Manual command: gcloud compute firewall-rules create allow-8080 --allow tcp:8080 --source-ranges 0.0.0.0/0 --target-tags callableapis-web --description 'Allow port 8080 for container services'"
    fi
else
    echo "gcloud CLI not found. Please install it or run manually:"
    echo "gcloud compute firewall-rules create allow-8080 --allow tcp:8080 --source-ranges 0.0.0.0/0 --target-tags callableapis-web --description 'Allow port 8080 for container services'"
fi
echo ""

# Oracle Cloud - Manual instructions
echo "Oracle Cloud Security List Rule:"
echo "-------------------------------"
echo "1. Go to Oracle Cloud Console: https://cloud.oracle.com/"
echo "2. Navigate to: Networking > Virtual Cloud Networks"
echo "3. Select your VCN (likely named 'callableapis-vcn')"
echo "4. Click on 'Security Lists' in the left menu"
echo "5. Click on your security list (likely named 'callableapis-sl')"
echo "6. Click 'Add Ingress Rules'"
echo "7. Add rule with these settings:"
echo "   - Source Type: CIDR"
echo "   - Source CIDR: 0.0.0.0/0"
echo "   - IP Protocol: TCP"
echo "   - Source Port Range: All"
echo "   - Destination Port Range: 8080"
echo "   - Description: Allow port 8080 for container services"
echo "8. Click 'Add Ingress Rules'"
echo ""

# IBM Cloud - Manual instructions
echo "IBM Cloud Security Group Rule:"
echo "-----------------------------"
echo "1. Go to IBM Cloud Console: https://cloud.ibm.com/"
echo "2. Navigate to: VPC Infrastructure > Security Groups"
echo "3. Find your security group (likely named 'callableapis-sg')"
echo "4. Click on the security group name"
echo "5. Click 'Add rule' in the Inbound rules section"
echo "6. Add rule with these settings:"
echo "   - Direction: Inbound"
echo "   - Type: TCP"
echo "   - Port: 8080"
echo "   - Source: 0.0.0.0/0"
echo "   - Description: Allow port 8080 for container services"
echo "7. Click 'Add rule'"
echo ""

echo "After applying these rules, test the endpoints:"
echo "curl http://159.54.170.237:8080/health  # Oracle"
echo "curl http://35.233.161.8:8080/health    # Google"
echo "curl http://52.116.135.43:8080/health    # IBM"
echo ""

echo "To test all endpoints at once, run:"
echo "./test-container-endpoints.sh"
