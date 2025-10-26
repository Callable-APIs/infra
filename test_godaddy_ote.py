#!/usr/bin/env python3
"""
Test script for GoDaddy OTE (Sandbox/Development) API
Tests various endpoints to verify API credentials work
"""

import os
import requests
import json
from typing import Dict, Any

# GoDaddy API Configuration
OTE_API_KEY = os.environ.get('GODADDY_OTE_KEY')
OTE_SECRET = os.environ.get('GODADDY_OTE_SECRET')
PROD_API_KEY = os.environ.get('GODADDY_API_KEY')
PROD_SECRET = os.environ.get('GODADDY_API_SECRET')

# API Base URLs
OTE_BASE_URL = "https://api.ote-godaddy.com"
PROD_BASE_URL = "https://api.godaddy.com"

def make_request(url: str, api_key: str, api_secret: str) -> Dict[str, Any]:
    """Make a request to GoDaddy API"""
    headers = {
        "Authorization": f"sso-key {api_key}:{api_secret}",
        "Accept": "application/json"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        return {
            "status_code": response.status_code,
            "headers": dict(response.headers),
            "body": response.text,
            "json": response.json() if response.headers.get('content-type', '').startswith('application/json') else None
        }
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}

def test_endpoint(description: str, url: str, api_key: str, api_secret: str) -> None:
    """Test a specific API endpoint"""
    print(f"\n{'='*80}")
    print(f"Testing: {description}")
    print(f"URL: {url}")
    print(f"{'='*80}")
    
    result = make_request(url, api_key, api_secret)
    
    print(f"Status Code: {result.get('status_code', 'N/A')}")
    
    if 'error' in result:
        print(f"Error: {result['error']}")
    else:
        print(f"Response Headers: {json.dumps(result['headers'], indent=2)}")
        print(f"Response Body:")
        if result.get('json'):
            print(json.dumps(result['json'], indent=2))
        else:
            print(result.get('body', 'No body'))

def main():
    print("="*80)
    print("GoDaddy API Test Script")
    print("="*80)
    
    if not OTE_API_KEY or not OTE_SECRET:
        print("❌ ERROR: OTE credentials not found in environment")
        print("   Expected: GODADDY_OTE_KEY and GODADDY_OTE_SECRET")
        return
    
    if not PROD_API_KEY or not PROD_SECRET:
        print("⚠️  WARNING: Production credentials not found")
    
    print(f"\nOTE Key (first 8 chars): {OTE_API_KEY[:8]}...")
    print(f"OTE Secret (first 8 chars): {OTE_SECRET[:8]}...")
    
    # Test OTE (Sandbox) Endpoints
    print(f"\n{'='*80}")
    print("Testing OTE (Sandbox) Environment")
    print(f"{'='*80}")
    
    # Test 1: List domains
    test_endpoint(
        "List domains (limit 10)",
        f"{OTE_BASE_URL}/v1/domains?limit=10",
        OTE_API_KEY,
        OTE_SECRET
    )
    
    # Test 2: Get all domains (if first worked)
    test_endpoint(
        "Get all domains",
        f"{OTE_BASE_URL}/v1/domains",
        OTE_API_KEY,
        OTE_SECRET
    )
    
    # Test 3: List domains with expanded info
    test_endpoint(
        "List domains with info",
        f"{OTE_BASE_URL}/v1/domains?includes=expired,locked,transferAwayEligible",
        OTE_API_KEY,
        OTE_SECRET
    )
    
    # Test Production Environment
    if PROD_API_KEY and PROD_SECRET:
        print(f"\n{'='*80}")
        print("Testing Production Environment")
        print(f"{'='*80}")
        
        test_endpoint(
            "List domains (Production)",
            f"{PROD_BASE_URL}/v1/domains?limit=10",
            PROD_API_KEY,
            PROD_SECRET
        )
    
    print(f"\n{'='*80}")
    print("Test Complete")
    print(f"{'='*80}")

if __name__ == "__main__":
    main()

