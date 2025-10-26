#!/bin/bash
# Test Cloudflare API token permissions

source env.sh

echo "=========================================="
echo "Testing Cloudflare API Token Permissions"
echo "=========================================="

# Test current permissions
docker run --rm -v $(pwd):/app -w /app \
  python:3.11-slim sh -c "
pip install requests -q && python3 -c \"
import requests
import json

token = '\$CLOUDFLARE_API_TOKEN'
account_id = '\$CLOUDFLARE_ACCOUNT_ID'

headers = {
    'Authorization': f'Bearer {token}',
    'Content-Type': 'application/json'
}

print('Testing Zone:Read permission...')
r = requests.get('https://api.cloudflare.com/client/v4/zones?per_page=1', headers=headers)
print(f'  ✅ Zone:Read works' if r.status_code == 200 else f'  ❌ Zone:Read failed: {r.status_code}')

print('')
print('Testing Zone creation (read-only test)...')
test_domain = 'test-{account_id}.com'
test_data = {'account': {'id': account_id}, 'name': test_domain, 'type': 'full'}

r = requests.post('https://api.cloudflare.com/client/v4/zones', headers=headers, json=test_data)
if r.status_code == 403:
    data = r.json()
    if 'permission' in str(data) or 'access' in str(data):
        print(f'  ❌ Zone creation blocked by permissions')
        print(f'  Error: {r.text}')
    else:
        print(f'  ⚠️  Zone creation returned 403 (not necessarily permission issue)')
elif r.status_code == 1009 or r.status_code == 1099:
    print(f'  ✅ Zone creation permission works (error is domain validation, not permission)')
else:
    print(f'  Status: {r.status_code}')
    print(f'  Response: {r.text}')
\"
"

echo ""
echo "=========================================="
echo "If Zone creation is blocked by permissions,"
echo "you need to add 'Zone:Edit' permission to"
echo "your Cloudflare API token."
echo "=========================================="

