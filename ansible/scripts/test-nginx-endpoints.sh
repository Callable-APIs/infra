#!/bin/bash
# Test script for nginx container proxy endpoints

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to test endpoint
test_endpoint() {
    local url=$1
    local expected_status=${2:-200}
    local description=$3
    
    echo -n "Testing $description... "
    
    if response=$(curl -s -w "%{http_code}" -o /dev/null "$url" 2>/dev/null); then
        if [ "$response" = "$expected_status" ]; then
            echo -e "${GREEN}PASS${NC} (HTTP $response)"
            return 0
        else
            echo -e "${RED}FAIL${NC} (Expected HTTP $expected_status, got HTTP $response)"
            return 1
        fi
    else
        echo -e "${RED}FAIL${NC} (Connection failed)"
        return 1
    fi
}

# Function to test JSON endpoint
test_json_endpoint() {
    local url=$1
    local description=$2
    
    echo -n "Testing $description... "
    
    if response=$(curl -s "$url" 2>/dev/null); then
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
    local host=${1:-localhost}
    local port=${2:-80}
    local base_url="http://$host:$port"
    
    echo "Testing nginx container proxy endpoints on $base_url"
    echo "=================================================="
    
    local tests_passed=0
    local tests_total=0
    
    # Test root endpoint
    tests_total=$((tests_total + 1))
    if test_endpoint "$base_url/" 200 "Root endpoint"; then
        tests_passed=$((tests_passed + 1))
    fi
    
    # Test health endpoint
    tests_total=$((tests_total + 1))
    if test_endpoint "$base_url/health" 200 "Health endpoint"; then
        tests_passed=$((tests_passed + 1))
    fi
    
    # Test API status endpoint
    tests_total=$((tests_total + 1))
    if test_endpoint "$base_url/api/status" 200 "API status endpoint"; then
        tests_passed=$((tests_passed + 1))
    fi
    
    # Test API health endpoint
    tests_total=$((tests_total + 1))
    if test_endpoint "$base_url/api/health" 200 "API health endpoint"; then
        tests_passed=$((tests_passed + 1))
    fi
    
    # Test JSON responses
    tests_total=$((tests_total + 1))
    if test_json_endpoint "$base_url/health" "Health JSON response"; then
        tests_passed=$((tests_passed + 1))
    fi
    
    tests_total=$((tests_total + 1))
    if test_json_endpoint "$base_url/api/status" "Status JSON response"; then
        tests_passed=$((tests_passed + 1))
    fi
    
    # Test 404 handling
    tests_total=$((tests_total + 1))
    if test_endpoint "$base_url/nonexistent" 404 "404 error handling"; then
        tests_passed=$((tests_passed + 1))
    fi
    
    echo "=================================================="
    echo "Tests completed: $tests_passed/$tests_total passed"
    
    if [ $tests_passed -eq $tests_total ]; then
        echo -e "${GREEN}All tests passed!${NC}"
        exit 0
    else
        echo -e "${RED}Some tests failed!${NC}"
        exit 1
    fi
}

# Show usage if help requested
if [ "$1" = "-h" ] || [ "$1" = "--help" ]; then
    echo "Usage: $0 [host] [port]"
    echo "  host: Target host (default: localhost)"
    echo "  port: Target port (default: 80)"
    echo ""
    echo "Examples:"
    echo "  $0                    # Test localhost:80"
    echo "  $0 192.168.1.100     # Test 192.168.1.100:80"
    echo "  $0 192.168.1.100 8080 # Test 192.168.1.100:8080"
    exit 0
fi

# Run main function
main "$@"

