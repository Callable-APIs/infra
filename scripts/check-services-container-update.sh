#!/bin/bash
# Check if services container has been updated with compliance fixes
# Usage: ./scripts/check-services-container-update.sh

set -e

echo "🔍 Checking services container for compliance fixes..."
echo ""

# Check health endpoint
echo "📊 Testing /health endpoint:"
HEALTH_RESPONSE=$(curl -s --connect-timeout 5 --max-time 10 http://35.88.22.9:8080/health 2>&1)
HEALTH_STATUS=$(echo "$HEALTH_RESPONSE" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('status', 'UNKNOWN'))" 2>/dev/null || echo "ERROR")

if [ "$HEALTH_STATUS" = "healthy" ]; then
    echo "  ✅ /health returns 'healthy' (COMPLIANT)"
else
    echo "  ❌ /health returns '$HEALTH_STATUS' (should be 'healthy')"
fi

# Check API health endpoint
echo ""
echo "📊 Testing /api/health endpoint:"
API_HEALTH_RESPONSE=$(curl -s --connect-timeout 5 --max-time 10 http://35.88.22.9:8080/api/health 2>&1)
API_HEALTH_STATUS=$(echo "$API_HEALTH_RESPONSE" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('status', 'UNKNOWN'))" 2>/dev/null || echo "ERROR")

if [ "$API_HEALTH_STATUS" = "ok" ]; then
    echo "  ✅ /api/health returns 'ok' (COMPLIANT)"
else
    echo "  ❌ /api/health returns '$API_HEALTH_STATUS' (should be 'ok')"
fi

# Check if endpoints are different
echo ""
echo "📊 Checking endpoint differences:"
if [ "$HEALTH_STATUS" != "$API_HEALTH_STATUS" ]; then
    echo "  ✅ /health and /api/health return different values (COMPLIANT)"
else
    echo "  ❌ /health and /api/health return same value (should be different)"
fi

# Check response format (minimal fields)
echo ""
echo "📊 Checking response format:"
HEALTH_FIELDS=$(echo "$HEALTH_RESPONSE" | python3 -c "import sys, json; data=json.load(sys.stdin); print(len(data))" 2>/dev/null || echo "0")
if [ "$HEALTH_FIELDS" -le 3 ]; then
    echo "  ✅ /health returns minimal fields (COMPLIANT)"
else
    echo "  ⚠️  /health returns $HEALTH_FIELDS fields (should be 3: status, timestamp, version)"
fi

API_HEALTH_FIELDS=$(echo "$API_HEALTH_RESPONSE" | python3 -c "import sys, json; data=json.load(sys.stdin); print(len(data))" 2>/dev/null || echo "0")
if [ "$API_HEALTH_FIELDS" -le 3 ]; then
    echo "  ✅ /api/health returns minimal fields (COMPLIANT)"
else
    echo "  ⚠️  /api/health returns $API_HEALTH_FIELDS fields (should be 3: status, timestamp, version)"
fi

# Summary
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if [ "$HEALTH_STATUS" = "healthy" ] && [ "$API_HEALTH_STATUS" = "ok" ] && [ "$HEALTH_STATUS" != "$API_HEALTH_STATUS" ]; then
    echo "✅ Services container is COMPLIANT with endpoint requirements!"
else
    echo "⚠️  Services container still needs compliance fixes"
    echo ""
    echo "Required fixes:"
    [ "$HEALTH_STATUS" != "healthy" ] && echo "  - /health status should be 'healthy' (currently: '$HEALTH_STATUS')"
    [ "$API_HEALTH_STATUS" != "ok" ] && echo "  - /api/health status should be 'ok' (currently: '$API_HEALTH_STATUS')"
    [ "$HEALTH_STATUS" = "$API_HEALTH_STATUS" ] && echo "  - /health and /api/health should return different values"
fi
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"


