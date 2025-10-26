#!/usr/bin/env python3
import subprocess
import sys

Py3 = sys.version_info[0] >= 3

domains = [
    "cocoonspamini.com",
    "glassbubble.net",
    "iheartdinos.com",
    "jughunt.com",
    "lipbalmjunkie.com",
    "ohsorad.com",
    "rosamimosa.com",
    "taicho.com",
    "tokyo3.com"
]

cloudflare_ns = ["nora.ns.cloudflare.com", "wells.ns.cloudflare.com"]

def check_nameservers(domain):
    """Check nameservers for a domain using dig"""
    print(f"\n{'='*80}")
    print(f"Checking: {domain}")
    print(f"{'='*80}")
    
    try:
        # Use dig to query nameservers directly
        result = subprocess.run(
            ['dig', '+short', 'NS', domain],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            nameservers = [line.strip().rstrip('.') for line in result.stdout.strip().split('\n') if line.strip()]
            
            print(f"Current nameservers:")
            for ns in nameservers:
                print(f"  - {ns}")
            
            # Check if Cloudflare nameservers are present
            cloudflare_found = any('cloudflare.com' in ns for ns in nameservers)
            
            if cloudflare_found:
                print(f"\n✅ Cloudflare nameservers detected!")
                # Check for both specific nameservers
                has_nora = any('nora.ns.cloudflare.com' in ns for ns in nameservers)
                has_wells = any('wells.ns.cloudflare.com' in ns for ns in nameservers)
                
                if has_nora or has_wells:
                    print(f"✅ Using correct Cloudflare nameservers")
                else:
                    print(f"⚠️  Using different Cloudflare nameservers")
            else:
                print(f"❌ No Cloudflare nameservers found - still pointing elsewhere")
            
            return cloudflare_found
        else:
            print(f"❌ Error querying DNS: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print(f"❌ DNS query timed out")
        return False
    except FileNotFoundError:
        print(f"❌ 'dig' command not found. Install bind-utils or dnsutils")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    print("="*80)
    print("Verifying Nameservers - GoDaddy to Cloudflare Migration")
    print("="*80)
    print("\nExpected Cloudflare nameservers:")
    for ns in cloudflare_ns:
        print(f"  - {ns}")
    
    results = {}
    for domain in domains:
        results[domain] = check_nameservers(domain)
    
    # Summary
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    
    cloudflare_count = sum(1 for v in results.values() if v)
    total = len(results)
    
    print(f"\nDomains using Cloudflare nameservers: {cloudflare_count}/{total}")
    
    if cloudflare_count == total:
        print("\n✅ ALL DOMAINS ARE NOW USING CLOUDFLARE NAMESERVERS!")
        print("   Migration complete! DNS is now fully managed by Cloudflare.")
    elif cloudflare_count > 0:
        print(f"\n⚠️  {total - cloudflare_count} domain(s) not yet pointing to Cloudflare")
        print("   Waiting for DNS propagation... (can take up to 48 hours)")
    else:
        print("\n❌ No domains are using Cloudflare nameservers yet")
        print("   Check your nameserver settings in GoDaddy")
    
    print("\nDomains not using Cloudflare:")
    for domain, result in results.items():
        if not result:
            print(f"  - {domain}")

if __name__ == "__main__":
    main()

