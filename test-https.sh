#!/bin/bash

echo "Testing HTTPS endpoint with Host header..."

# Test HTTPS with Host header
echo -n "HTTPS (with Host header): "
timeout 10 curl -k -s -o /dev/null -w "%{http_code}" -H "Host: callableapis-arm-1" https://192.9.154.97/health 2>/dev/null || echo "TIMEOUT/ERROR"
echo

# Test status container directly
echo -n "Status container (port 8081): "
timeout 10 curl -s -o /dev/null -w "%{http_code}" http://192.9.154.97:8081/health 2>/dev/null || echo "TIMEOUT/ERROR"
echo

echo "Test completed."
