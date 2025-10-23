#!/bin/bash
# Test script to verify container endpoints across all nodes

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Node configuration (containerd nodes only)
NODES=(
    "onode1:159.54.170.237"
    "gnode1:35.233.161.8"
    "inode1:52.116.135.43"
)

# Function to test endpoint
test_endpoint() {
    local node_name=$1
    local ip=$2
    local port=${3:-8080}
    local endpoint=$4
    local description=$5
    
    echo -n "Testing $node_name ($ip:$port$endpoint) - $description... "
    
    if response=$(curl -s -w "%{http_code}" -o /dev/null "http://$ip:$port$endpoint" --connect-timeout 10 --max-time 30 2>/dev/null); then
        if [ "$response" = "200" ]; then
            echo -e "${GREEN}PASS${NC} (HTTP $response)"
            return 0
        else
            echo -e "${RED}FAIL${NC} (Expected HTTP 200, got HTTP $response)"
            return 1
        fi
    else
        echo -e "${RED}FAIL${NC} (Connection failed)"
        return 1
    fi
}

# Function to test JSON endpoint
test_json_endpoint() {
    local node_name=$1
    local ip=$2
    local port=${3:-8080}
    local endpoint=$4
    local description=$5
    
    echo -n "Testing $node_name ($ip:$port$endpoint) - $description... "
    
    if response=$(curl -s "http://$ip:$port$endpoint" --connect-timeout 10 --max-time 30 2>/dev/null); then
        if echo "$response" | jq . >/dev/null 2>&1; then
            echo -e "${GREEN}PASS${NC} (Valid JSON)"
            return 0
        else
            echo -e "${RED}FAIL${NC} (Invalid JSON)"
            return 1
        fi
    else
        echo -e "${RED}FAIL${NC} (Connection failed)"
        return 1
    fi
}

# Main test function
main() {
    echo "Testing CallableAPIs Base Container endpoints across all nodes"
    echo "=============================================================="
    echo ""
    
    local total_tests=0
    local passed_tests=0
    
    for node_info in "${NODES[@]}"; do
        local node_name="${node_info%:*}"
        local ip="${node_info#*:}"
        echo -e "${BLUE}Testing node: $node_name ($ip)${NC}"
        echo "----------------------------------------"
        
        # Test health endpoint
        total_tests=$((total_tests + 1))
        if test_endpoint "$node_name" "$ip" 8080 "/health" "Health check"; then
            passed_tests=$((passed_tests + 1))
        fi
        
        # Test status endpoint
        total_tests=$((total_tests + 1))
        if test_endpoint "$node_name" "$ip" 8080 "/api/status" "Status endpoint"; then
            passed_tests=$((passed_tests + 1))
        fi
        
        # Test API health endpoint
        total_tests=$((total_tests + 1))
        if test_endpoint "$node_name" "$ip" 8080 "/api/health" "API health endpoint"; then
            passed_tests=$((passed_tests + 1))
        fi
        
        # Test root endpoint
        total_tests=$((total_tests + 1))
        if test_endpoint "$node_name" "$ip" 8080 "/" "Root endpoint"; then
            passed_tests=$((passed_tests + 1))
        fi
        
        # Test JSON responses
        total_tests=$((total_tests + 1))
        if test_json_endpoint "$node_name" "$ip" 8080 "/health" "Health JSON response"; then
            passed_tests=$((passed_tests + 1))
        fi
        
        total_tests=$((total_tests + 1))
        if test_json_endpoint "$node_name" "$ip" 8080 "/api/status" "Status JSON response"; then
            passed_tests=$((passed_tests + 1))
        fi
        
        echo ""
    done
    
    echo "=============================================================="
    echo "Test Summary: $passed_tests/$total_tests tests passed"
    
    if [ $passed_tests -eq $total_tests ]; then
        echo -e "${GREEN}All tests passed! All nodes are responding correctly.${NC}"
        exit 0
    else
        echo -e "${RED}Some tests failed! Check the nodes that are not responding.${NC}"
        exit 1
    fi
}

# Show usage if help requested
if [ "$1" = "-h" ] || [ "$1" = "--help" ]; then
    echo "Usage: $0"
    echo ""
    echo "This script tests the CallableAPIs Base Container endpoints"
    echo "across all configured nodes."
    echo ""
    echo "Nodes tested:"
    for node_info in "${NODES[@]}"; do
        local node_name="${node_info%:*}"
        local ip="${node_info#*:}"
        echo "  - $node_name: $ip:8080"
    done
    echo ""
    echo "Endpoints tested:"
    echo "  - GET /health"
    echo "  - GET /api/status"
    echo "  - GET /api/health"
    echo "  - GET /"
    exit 0
fi

# Run main function
main "$@"
