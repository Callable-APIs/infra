#!/usr/bin/env python3
"""
Diagnostic script to test various authentication methods for GoDaddy Production API
"""

import os
import requests
import json

PROD_API_KEY = os.environ.get('GODADDY_API_KEY')
PROD_SECRET = os.environ.get('GODADDY_API_SECRET')

def test_auth_method(method_name: str, url: str, headers: dict) -> None:
    """Test a specific authentication method"""
    print(f"\n{'='*80}")
    print(f"Testing: {method_name}")
    print(f"URL: {url}")
    print(f"Headers: {json.dumps({k: v if 'Authorization' not in k else 'sso-key ***:***' for k, v in headers.items()}, indent=2)}")
    print(f"{'='*80}")
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ SUCCESS!")
            print(f"Response: {json.dumps(response.json(), indent=2)}")
        else:
            print(f"❌ FAILED")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ ERROR: {e}")

def main():
    print("="*80)
    print("GoDaddy Production API Diagnostic")
    print("="*80)
    
    if not PROD_API_KEY or not PROD_SECRET:
        print("ERROR: Production credentials not found")
        return
    
    # Test different authentication formats
    base_url = "https://api.godaddy.com"
    
    # Method 1: Standard sso-key format
    test_auth_method(
        "Method 1: sso-key format (standard)",
        f"{base_url}/v1/domains?limit=10",
        {
            "Authorization": f"sso-key {PROD_API_KEY}:{PROD_SECRET}",
            "Accept": "application/json"
        }
    )
    
    # Method 2: Try without colon in key
    test_auth_method(
        "Method 2: Basic auth format",
        f"{base_url}/v1/domains?limit=10",
        {
            "Authorization": f"Basic {requests.auth._basic_auth_str(PROD_API_KEY, PROD_SECRET)}",
            "Accept": "application/json"
        }
    )
    
    # Method 3: Try with Bearer
    test_auth_method(
        "Method 3: Bearer token format",
        f"{base_url}/v1/domains?limit=10",
        {
            "Authorization": f"Bearer {PROD_API_KEY}:{PROD_SECRET}",
            "Accept": "application/json"
        }
    )
    
    # Test account info first
    print(f"\n{'='*80}")
    print("Test 4: Try getting account info instead of domains")
    print(f"{'='*80}")
    test_auth_method(
        "Get account info",
        f"{base_url}/v1/accounts",
        {
            "Authorization": f"sso-key {PROD_API_KEY}:{PROD_SECRET}",
            "Accept": "application/json"
        }
    )
    
    print(f"\n{'='*80}")
    print("Diagnostic Complete")
    print(f"{'='*80}")

if __name__ == "__main__":
    main()

