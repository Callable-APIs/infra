#!/usr/bin/env python3
"""
Parse GoDaddy domains from the portfolio export
Extract domain names and their details
"""

import re
from datetime import datetime

def parse_domains(filename):
    """Parse domains from the GoDaddy export file"""
    with open(filename, 'r') as f:
        content = f.read()
    
    # Extract domain names (simple text extraction)
    lines = [line.strip() for line in content.split('\n') if line.strip()]
    
    domains = []
    for line in lines:
        # Check if it looks like a domain (contains dot and common TLDs)
        if '.' in line and any(line.endswith(f'.{tld}') for tld in ['com', 'net', 'org', 'io', 'co']):
            domains.append(line)
    
    # Also try to extract dates and values
    dates = re.findall(r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d+,\s+\d{4}', content)
    values = re.findall(r'\$\d+[,\d]*', content)
    
    return domains, dates, values

def main():
    domains, dates, values = parse_domains('godaddy-domains.txt')
    
    print("="*80)
    print("Parsed GoDaddy Domains")
    print("="*80)
    
    print(f"\nFound {len(domains)} domains:")
    for i, domain in enumerate(domains, 1):
        print(f"  {i}. {domain}")
    
    print(f"\nDates found: {len(dates)}")
    if dates:
        for date in dates[:5]:
            print(f"  - {date}")
    
    print(f"\nValues found: {len(values)}")
    if values:
        for value in values[:5]:
            print(f"  - {value}")
    
    # Write domains to a clean file
    with open('godaddy-domains-clean.txt', 'w') as f:
        for domain in domains:
            f.write(f"{domain}\n")
    
    print("\n" + "="*80)
    print("Saved clean domain list to: godaddy-domains-clean.txt")
    print("="*80)

if __name__ == "__main__":
    main()

