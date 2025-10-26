#!/usr/bin/env python3
import os
import requests
import json

token = os.environ.get('CLOUDFLARE_API_TOKEN')
zone_name = 'tokyo3.com'

# Get zone ID
headers = {
    'Authorization': f'Bearer {token}',
    'Content-Type': 'application/json'
}

print(f"Looking up zone for: {zone_name}")

r = requests.get(f'https://api.cloudflare.com/client/v4/zones?name={zone_name}', headers=headers)
result = r.json()

if result.get('result') and len(result['result']) > 0:
    zone_id = result['result'][0]['id']
    print(f"✅ Zone found: {zone_id}")
    
    # Get all DNS records
    r = requests.get(f'https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records', headers=headers)
    data = r.json()
    
    records = data.get('result', [])
    print(f"\nTotal DNS records: {len(records)}")
    
    if records:
        print("\nAll DNS records:")
        for record in sorted(records, key=lambda x: (x['type'], x['name'])):
            content = record.get('content', 'N/A')
            if record['type'] == 'MX':
                print(f"  MX  {record['name']:30} Priority {record.get('priority', 0)}: {content}")
            else:
                print(f"  {record['type']:6} {record['name']:30} -> {content}")
    else:
        print("\n❌ No DNS records found in Cloudflare")
    
    # Check specifically for MX records
    print("\n" + "="*80)
    print("MX Records Check")
    print("="*80)
    mx_records = [r for r in records if r['type'] == 'MX']
    if mx_records:
        print(f"✅ Found {len(mx_records)} MX record(s):")
        for record in mx_records:
            print(f"   Priority {record.get('priority', 0)}: {record['content']}")
    else:
        print("❌ No MX records found!")
        print("\n⚠️  MX records need to be added to Cloudflare for email to work.")
        
else:
    print(f"❌ Zone {zone_name} not found in Cloudflare")

