#!/usr/bin/env python3
"""
Test script for GoDaddy Production API
Tests new production credentials
"""

import os
import requests
import json

PROD_API_KEY = os.environ.get('GODADDY_API_KEY')
PROD_SECRET = os.environ.get('GODADDY_API_SECRET')
PROD_BASE_URL = "https://api.godaddy.com"

def test_endpoint(description, url):
    """Test a specific API endpoint"""
    print(f"\n{'='*80}")
    print(f"Testing: {description}")
    print(f"URL: {url}")
    print(f"{'='*80}")
    
    headers = {
        "Authorization": f"sso-key {PROD_API_KEY}:{PROD_SECRET}",
        "Accept": "application/json"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ SUCCESS!")
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)}")
            return True
        else:
            print(f"❌ FAILED")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def main():
    print("="*80)
    print("GoDaddy Production API Test")
    print("="*80)
    
    if not PROD_API_KEY or not PROD_SECRET:
        print("❌ ERROR: Production credentials not found")
        print("   Expected: GODADDY_API_KEY and GODADDY_API_SECRET")
        return
    
    print(f"\nProduction Key (first 10 chars): {PROD_API_KEY[:10]}...")
    print(f"Production Secret (first 10 chars): {PROD_SECRET[:10]}...")
    
    # Test 1: List domains
    success1 = test_endpoint(
        "List domains (limit 10)",
        f"{PROD_BASE_URL}/v1/domains?limit=10"
    )
    
    # Test 2: Get all domains
    success2 = test_endpoint(
        "List all domains",
        f"{PROD_BASE_URL}/v1/domains"
    )
    
    # Test 3: List with status filter
    success3 = test_endpoint(
        "List active domains",
        f"{PROD_BASE_URL}/v1/domains?statuses=ACTIVE"
    )
    
    print("\n" + "="*80)
    print("Summary")
    print("="*80)
    if success1 or success2 or success3:
        print("✅ Production credentials are working!")
        print("   API access is granted and domains can be retrieved.")
    else:
        print("❌ Production credentials still have issues")
        print("   Check error messages above for details")
    
    print("="*80)

if __name__ == "__main__":
    main()

