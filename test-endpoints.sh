#!/bin/bash

echo "Testing endpoints with timeouts..."

# Test HTTP endpoint
echo -n "HTTP (port 80): "
timeout 10 curl -s -o /dev/null -w "%{http_code}" http://192.9.154.97/health 2>/dev/null || echo "TIMEOUT/ERROR"
echo

# Test HTTPS endpoint
echo -n "HTTPS (port 443): "
timeout 10 curl -k -s -o /dev/null -w "%{http_code}" https://192.9.154.97/health 2>/dev/null || echo "TIMEOUT/ERROR"
echo

# Test container endpoints directly
echo -n "Base container (port 8080): "
timeout 10 curl -s -o /dev/null -w "%{http_code}" http://192.9.154.97:8080/health 2>/dev/null || echo "TIMEOUT/ERROR"
echo

echo -n "Status container (port 8081): "
timeout 10 curl -s -o /dev/null -w "%{http_code}" http://192.9.154.97:8081/health 2>/dev/null || echo "TIMEOUT/ERROR"
echo

echo "Test completed."
