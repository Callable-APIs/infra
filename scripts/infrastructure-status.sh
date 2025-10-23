#!/bin/bash
# Comprehensive Infrastructure State Report

set -e

echo "CallableAPIs Infrastructure State Report"
echo "========================================"
echo "Generated: $(date)"
echo ""

cd /Users/rlee/dev/infra/terraform

echo "1. CURRENT TERRAFORM STATE (S3 Backend)"
echo "======================================="
docker run --rm -v $(pwd):/app -w /app \
  -e AWS_ACCESS_KEY_ID="$AWS_ACCESS_KEY_ID" \
  -e AWS_SECRET_ACCESS_KEY="$AWS_SECRET_ACCESS_KEY" \
  callableapis:infra terraform state list

echo ""
echo "2. PLANNED INFRASTRUCTURE CHANGES"
echo "================================="
docker run --rm -v $(pwd):/app -w /app \
  -e AWS_ACCESS_KEY_ID="$AWS_ACCESS_KEY_ID" \
  -e AWS_SECRET_ACCESS_KEY="$AWS_SECRET_ACCESS_KEY" \
  callableapis:infra terraform plan -detailed-exitcode || true

echo ""
echo "3. INFRASTRUCTURE VISUALIZATION"
echo "================================"
echo "Files generated:"
echo "- infrastructure.dot (Graphviz DOT format)"
echo "- infrastructure.svg (SVG diagram)"
echo ""
echo "To view the SVG diagram:"
echo "- Open infrastructure.svg in a web browser"
echo "- Or use: open infrastructure.svg (macOS)"
echo ""

echo "4. CONTAINER ENDPOINTS STATUS"
echo "============================="
echo "Testing external access to container endpoints..."

# Test each node
test_endpoint() {
    local node_name=$1
    local ip=$2
    local url="http://$ip:8080/health"
    
    echo -n "  $node_name ($ip:8080): "
    if curl -s -o /dev/null -w "%{http_code}" --max-time 5 "$url" | grep -q "200"; then
        echo "✅ ACCESSIBLE"
        return 0
    else
        echo "❌ BLOCKED"
        return 1
    fi
}

test_endpoint "Oracle (onode1)" "159.54.170.237"
test_endpoint "Google (gnode1)" "35.233.161.8"
test_endpoint "IBM (inode1)" "52.116.135.43"

echo ""
echo "5. NEXT STEPS"
echo "============"
echo "1. Import existing infrastructure from cloud provider state files"
echo "2. Apply firewall rules to open port 8080 on containerd nodes"
echo "3. Test external access to container endpoints"
echo "4. Verify all infrastructure is properly managed by Terraform"
echo ""
echo "Commands to run:"
echo "- Import infrastructure: ./scripts/import-existing-state.sh"
echo "- Apply firewall rules: docker run --rm -v \$(pwd):/app -w /app callableapis:infra terraform apply"
echo "- Test endpoints: ./test-container-endpoints.sh"
