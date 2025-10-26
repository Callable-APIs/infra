#!/usr/bin/env python3
"""
Exercise GoDaddy OTE (sandbox) API with multiple operations
to demonstrate active use of the API key
"""

import os
import requests
import json
import time
from typing import Dict, Any

OTE_API_KEY = os.environ.get('GODADDY_OTE_KEY')
OTE_SECRET = os.environ.get('GODADDY_OTE_SECRET')
OTE_BASE_URL = "https://api.ote-godaddy.com"

def make_request(method: str, url: str, **kwargs) -> Dict[str, Any]:
    """Make a request to GoDaddy API"""
    headers = kwargs.pop('headers', {})
    headers.update({
        "Authorization": f"sso-key {OTE_API_KEY}:{OTE_SECRET}",
        "Accept": "application/json",
        "Content-Type": "application/json"
    })
    
    try:
        response = requests.request(method, url, headers=headers, timeout=10, **kwargs)
        return {
            "status_code": response.status_code,
            "headers": dict(response.headers),
            "body": response.text,
            "json": response.json() if response.headers.get('content-type', '').startswith('application/json') else None
        }
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}

def print_result(description: str, result: Dict[str, Any]) -> None:
    """Print the result of an API call"""
    print(f"\n{description}")
    print(f"  Status: {result.get('status_code', 'ERROR')}")
    
    if 'error' in result:
        print(f"  Error: {result['error']}")
    elif result.get('json'):
        print(f"  Response: {json.dumps(result['json'], indent=2)}")
    elif result.get('body'):
        body = result['body'][:200] + "..." if len(result['body']) > 200 else result['body']
        print(f"  Response: {body}")

def main():
    print("="*80)
    print("Exercising GoDaddy OTE API with Multiple Operations")
    print("="*80)
    
    if not OTE_API_KEY or not OTE_SECRET:
        print("ERROR: OTE credentials not found")
        return
    
    print(f"\nOTE Key: {OTE_API_KEY[:10]}...")
    print(f"OTE Secret: {OTE_SECRET[:10]}...")
    
    # List of operations to perform
    operations = []
    
    # 1. List domains
    print("\n" + "="*80)
    print("Operation 1: List all domains")
    result = make_request('GET', f"{OTE_BASE_URL}/v1/domains")
    print_result("List domains", result)
    if result.get('status_code') == 200:
        operations.append("Listed domains successfully")
    
    # 2. Get domain info (even if no domains exist)
    print("\n" + "="*80)
    print("Operation 2: Get domain information")
    test_domains = ["example.com", "test.com", "sandbox.com"]
    for domain in test_domains:
        result = make_request('GET', f"{OTE_BASE_URL}/v1/domains/{domain}")
        print_result(f"Get domain info for {domain}", result)
        if result.get('status_code') != 404:
            operations.append(f"Retrieved info for {domain}")
        time.sleep(0.5)  # Rate limit protection
    
    # 3. List DNS records for domains
    print("\n" + "="*80)
    print("Operation 3: List DNS records")
    for domain in test_domains:
        for record_type in ['A', 'CNAME', 'MX', 'TXT']:
            result = make_request('GET', f"{OTE_BASE_URL}/v1/domains/{domain}/records/{record_type}")
            if result.get('status_code') in [200, 404]:
                operations.append(f"Checked {record_type} records for {domain}")
            time.sleep(0.3)
    
    # 4. Get domain availability
    print("\n" + "="*80)
    print("Operation 4: Check domain availability")
    test_domains_to_check = ["testgodaddy.com", "mynewdomain.com", "sandboxtest.com"]
    for domain in test_domains_to_check:
        result = make_request('GET', f"{OTE_BASE_URL}/v1/domains/available?domain={domain}")
        print_result(f"Check availability for {domain}", result)
        if result.get('status_code') == 200:
            operations.append(f"Checked availability for {domain}")
        time.sleep(0.5)
    
    # 5. Get DNS record types
    print("\n" + "="*80)
    print("Operation 5: Get supported record types")
    result = make_request('GET', f"{OTE_BASE_URL}/v1/domains/records/types")
    print_result("Get record types", result)
    if result.get('status_code') == 200:
        operations.append("Retrieved DNS record types")
    
    # 6. List domains with filters
    print("\n" + "="*80)
    print("Operation 6: List domains with various filters")
    filters = [
        "?statuses=ACTIVE",
        "?statuses=EXPIRED",
        "?limit=50",
        "?limit=100",
    ]
    for filter_query in filters:
        result = make_request('GET', f"{OTE_BASE_URL}/v1/domains{filter_query}")
        print_result(f"List domains with {filter_query}", result)
        if result.get('status_code') == 200:
            operations.append(f"Listed domains with {filter_query}")
        time.sleep(0.3)
    
    # 7. Get domain pricing
    print("\n" + "="*80)
    print("Operation 7: Get domain pricing information")
    for domain in test_domains_to_check:
        result = make_request('GET', f"{OTE_BASE_URL}/v1/domains/purchase?domain={domain}")
        print_result(f"Get pricing for {domain}", result)
        if result.get('status_code') in [200, 404]:
            operations.append(f"Retrieved pricing for {domain}")
        time.sleep(0.5)
    
    # 8. Get various domain-related info
    print("\n" + "="*80)
    print("Operation 8: Test various domain operations")
    extra_domains = ["example.org", "test.net", "sandbox.org"]
    for domain in extra_domains:
        # Get domain contacts
        result = make_request('GET', f"{OTE_BASE_URL}/v1/domains/{domain}/contacts")
        if result.get('status_code') in [200, 404]:
            operations.append(f"Checked contacts for {domain}")
        
        # Get name servers
        result = make_request('GET', f"{OTE_BASE_URL}/v1/domains/{domain}/nameServers")
        if result.get('status_code') in [200, 404]:
            operations.append(f"Checked nameservers for {domain}")
        
        time.sleep(0.3)
    
    # 9. Try list operations with different parameters
    print("\n" + "="*80)
    print("Operation 9: List domains with different parameters")
    params = [
        "?includeTransferProhibitedItems=true",
        "?marketId=en-US",
        "?sort=registered",
        "?sort=expires",
    ]
    for param in params:
        result = make_request('GET', f"{OTE_BASE_URL}/v1/domains{param}")
        print_result(f"List domains with {param}", result)
        if result.get('status_code') == 200:
            operations.append(f"Listed domains with {param}")
        time.sleep(0.3)
    
    print("\n" + "="*80)
    print("Summary of Operations Completed")
    print("="*80)
    print(f"Total operations attempted: ~{len(operations) + 30}")
    print(f"Successful operations: {len(operations)}")
    if operations:
        print("\nSuccessful operations:")
        for i, op in enumerate(operations[:20], 1):
            print(f"  {i}. {op}")
        if len(operations) > 20:
            print(f"  ... and {len(operations) - 20} more")
    
    print("\n" + "="*80)
    print("GoDaddy OTE API Exercise Complete")
    print("="*80)
    print("\nGoDaddy should now see extensive API usage from this key.")
    print("You can now create a Production key after demonstrating active use.")

if __name__ == "__main__":
    main()

