"""Check IBM Cloud regions for free tier instance availability."""
import logging
import os
import subprocess
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

# Common IBM Cloud regions
REGIONS = [
    "us-south",      # Dallas
    "us-east",       # Washington DC
    "eu-gb",         # London
    "eu-de",         # Frankfurt
    "eu-fr",         # Paris
    "jp-tok",        # Tokyo
    "jp-osa",        # Osaka
    "au-syd",        # Sydney
    "ca-tor",        # Toronto
    "br-sao",        # São Paulo
]

# Free tier eligible instance profiles
# Note: IBM Cloud doesn't have a traditional "always free" tier for VPC instances
# but some profiles may be eligible for free tier credits or have lower costs
FREE_TIER_PROFILES = [
    "bx2-2x8",      # 2 vCPU, 8GB RAM (mentioned in terraform configs)
    "cx2-2x4",      # 2 vCPU, 4GB RAM (mentioned in terraform configs)
    "bx2-4x16",     # 4 vCPU, 16GB RAM (may be eligible with credits)
]


def check_region_instance_availability(
    region: str,
    api_key: Optional[str] = None,
) -> Dict:
    """
    Check if instances can be created in a specific IBM Cloud region.
    
    Uses IBM Cloud CLI to check region availability and instance profiles.
    
    Args:
        region: IBM Cloud region name
        api_key: IBM Cloud API key (optional, from env if not provided)
    
    Returns:
        Dictionary with availability status
    """
    result = {
        "region": region,
        "available": False,
        "zones": [],
        "profiles_available": [],
        "error": None,
    }
    
    api_key = api_key or os.environ.get("IBMCLOUD_API_KEY")
    if not api_key:
        result["error"] = "IBM Cloud API key required"
        return result
    
    try:
        # Use IBM Cloud CLI to check region and zones
        # Set API key for this check
        env = os.environ.copy()
        env["IBMCLOUD_API_KEY"] = api_key
        
        # Check if region is accessible
        try:
            # List zones in the region
            cmd = ["ibmcloud", "is", "zones", region, "--output", "json"]
            zones_output = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                env=env,
                timeout=10
            )
            
            if zones_output.returncode == 0:
                import json
                zones_data = json.loads(zones_output.stdout)
                if isinstance(zones_data, list):
                    result["zones"] = [zone.get("name", "") for zone in zones_data if zone.get("name")]
                elif isinstance(zones_data, dict) and "zones" in zones_data:
                    result["zones"] = [zone.get("name", "") for zone in zones_data["zones"] if zone.get("name")]
                
                if result["zones"]:
                    result["available"] = True
                    
                    # Try to list instance profiles
                    try:
                        cmd = ["ibmcloud", "is", "instance-profiles", "--output", "json"]
                        profiles_output = subprocess.run(
                            cmd,
                            capture_output=True,
                            text=True,
                            env=env,
                            timeout=10
                        )
                        
                        if profiles_output.returncode == 0:
                            profiles_data = json.loads(profiles_output.stdout)
                            if isinstance(profiles_data, list):
                                available_profiles = [p.get("name", "") for p in profiles_data if p.get("name")]
                            elif isinstance(profiles_data, dict) and "profiles" in profiles_data:
                                available_profiles = [p.get("name", "") for p in profiles_data["profiles"] if p.get("name")]
                            else:
                                available_profiles = []
                            
                            # Check which free tier profiles are available
                            result["profiles_available"] = [
                                p for p in FREE_TIER_PROFILES 
                                if p in available_profiles
                            ]
                    except Exception as e:
                        logger.warning(f"Could not list instance profiles: {e}")
            else:
                result["error"] = zones_output.stderr or "Failed to list zones"
                
        except subprocess.TimeoutExpired:
            result["error"] = "Timeout checking region"
        except Exception as e:
            result["error"] = str(e)
            logger.error(f"Error checking region {region}: {e}")
            
    except Exception as e:
        result["error"] = f"Failed to check region: {e}"
        logger.error(f"Error checking IBM Cloud region {region}: {e}")
    
    return result


def check_all_regions(api_key: Optional[str] = None) -> List[Dict]:
    """
    Check all common IBM Cloud regions for instance availability.
    
    Args:
        api_key: IBM Cloud API key (optional, from env if not provided)
    
    Returns:
        List of region availability dictionaries
    """
    results = []
    for region in REGIONS:
        logger.info(f"Checking IBM Cloud region: {region}")
        result = check_region_instance_availability(region, api_key)
        results.append(result)
    return results


def find_available_regions(api_key: Optional[str] = None) -> List[str]:
    """
    Find all regions where instances are available.
    
    Args:
        api_key: IBM Cloud API key (optional, from env if not provided)
    
    Returns:
        List of available region names
    """
    results = check_all_regions(api_key)
    return [r["region"] for r in results if r["available"]]


def main():
    """Main function for CLI usage."""
    import sys
    
    print("=" * 80)
    print("IBM Cloud Free Tier Instance Availability Check")
    print("=" * 80)
    print()
    
    api_key = os.environ.get("IBMCLOUD_API_KEY")
    if not api_key:
        print("❌ Error: IBMCLOUD_API_KEY environment variable not set")
        print("   Set it in env.sh or export it before running this command")
        sys.exit(1)
    
    print("Checking IBM Cloud regions for instance availability...")
    print("This may take a few minutes...")
    print()
    
    results = check_all_regions(api_key)
    
    available_regions = [r for r in results if r["available"]]
    regions_with_free_tier = [r for r in results if r["available"] and r["profiles_available"]]
    
    if available_regions:
        print(f"\n✓ Accessible regions: {len(available_regions)}")
        for result in available_regions:
            zones_status = f" ({len(result['zones'])} zones)" if result.get("zones") else ""
            free_tier_status = ""
            if result.get("profiles_available"):
                free_tier_status = f" [Free tier profiles: {', '.join(result['profiles_available'])}]"
            print(f"  - {result['region']}{zones_status}{free_tier_status}")
            if result.get("zones"):
                for zone in result["zones"][:3]:  # Show first 3 zones
                    print(f"    • {zone}")
                if len(result["zones"]) > 3:
                    print(f"    ... and {len(result['zones']) - 3} more")
        
        if regions_with_free_tier:
            print(f"\n✓ Regions with free tier profiles available: {len(regions_with_free_tier)}")
            for result in regions_with_free_tier:
                print(f"  - {result['region']}: {', '.join(result['profiles_available'])}")
        
        # Show regions with errors
        error_regions = [r for r in results if r.get("error")]
        if error_regions:
            print(f"\n⚠ Regions with errors: {len(error_regions)}")
            for result in error_regions:
                print(f"  - {result['region']}: {result.get('error', 'Unknown error')}")
    else:
        print("\n✗ No accessible regions found")
        print("  This may indicate:")
        print("  - Authentication issues (check IBMCLOUD_API_KEY)")
        print("  - Region access restrictions")
        print("  - IBM Cloud CLI not installed or not in PATH")
        print("  - Need to check IBM Cloud Console manually")
    
    print()
    print("=" * 80)
    print("\nNote: IBM Cloud doesn't have traditional 'always free' VPC instances.")
    print("      Free tier typically includes:")
    print("      - $200 credit for new accounts (30 days)")
    print("      - Some services with Lite plans (always free)")
    print("      - Check billing to see current costs")
    print()
    print("To check current IBM Cloud billing:")
    print("  docker run --rm -v $(pwd):/app -w /app -e IBMCLOUD_API_KEY=\"$IBMCLOUD_API_KEY\" \\")
    print("    callableapis:infra python3 -m clint billing --daily --providers ibm")


if __name__ == "__main__":
    main()

