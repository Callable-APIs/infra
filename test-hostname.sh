#!/bin/bash

echo "Testing endpoints with hostname..."

# Test HTTP endpoint with hostname
echo -n "HTTP (hostname): "
timeout 10 curl -s -o /dev/null -w "%{http_code}" http://callableapis-arm-1/health 2>/dev/null || echo "TIMEOUT/ERROR"
echo

# Test HTTPS endpoint with hostname
echo -n "HTTPS (hostname): "
timeout 10 curl -k -s -o /dev/null -w "%{http_code}" https://callableapis-arm-1/health 2>/dev/null || echo "TIMEOUT/ERROR"
echo

# Test with Host header
echo -n "HTTP (IP with Host header): "
timeout 10 curl -s -o /dev/null -w "%{http_code}" -H "Host: callableapis-arm-1" http://192.9.154.97/health 2>/dev/null || echo "TIMEOUT/ERROR"
echo

echo -n "HTTPS (IP with Host header): "
timeout 10 curl -k -s -o /dev/null -w "%{http_code}" -H "Host: callableapis-arm-1" https://192.9.154.97/health 2>/dev/null || echo "TIMEOUT/ERROR"
echo

echo "Test completed."
