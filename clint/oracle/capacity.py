"""Check Oracle Cloud regions for ARM instance availability."""
import logging
from typing import List, Dict

try:
    import oci
    from oci.core import ComputeClient
    from oci.identity import IdentityClient
    from oci.core.models import LaunchInstanceDetails, LaunchInstanceShapeConfigDetails
    OCI_AVAILABLE = True
except ImportError:
    OCI_AVAILABLE = False
    logging.warning("OCI SDK not available. Install with: pip install oci")

logger = logging.getLogger(__name__)

# Common Oracle Cloud regions
REGIONS = [
    "us-ashburn-1",
    "us-phoenix-1",
    "us-sanjose-1",
    "us-chicago-1",
    "ca-toronto-1",
    "sa-saopaulo-1",
    "uk-london-1",
    "uk-cardiff-1",
    "eu-frankfurt-1",
    "eu-amsterdam-1",
    "eu-zurich-1",
    "ap-mumbai-1",
    "ap-seoul-1",
    "ap-sydney-1",
    "ap-tokyo-1",
    "ap-osaka-1",
    "ap-singapore-1",
    "me-jeddah-1",
    "me-dubai-1",
]


def check_region_arm_availability(
    region: str,
    compartment_id: str,
    tenancy_ocid: str,
    user_ocid: str,
    fingerprint: str,
    private_key_path: str,
) -> Dict[str, any]:
    """
    Check if ARM instances are available in a specific region.
    
    Returns:
        Dictionary with availability status
    """
    result = {
        "region": region,
        "available": False,
        "availability_domains": [],
        "arm_shape_available": False,
        "error": None,
    }
    
    if not OCI_AVAILABLE:
        result["error"] = "OCI SDK not available"
        return result
    
    try:
        # Configure OCI client
        config = {
            "tenancy": tenancy_ocid,
            "user": user_ocid,
            "fingerprint": fingerprint,
            "key_file": private_key_path,
            "region": region,
        }
        
        # Check identity client (to verify region access)
        identity_client = IdentityClient(config)
        
        # Get availability domains
        try:
            ads_response = identity_client.list_availability_domains(compartment_id)
            if ads_response.data:
                result["availability_domains"] = [ad.name for ad in ads_response.data]
                result["available"] = True
                
                # Try to check if ARM shape is available by listing shapes
                compute_client = ComputeClient(config)
                try:
                    # List shapes in the compartment
                    shapes_response = compute_client.list_shapes(compartment_id)
                    if shapes_response.data:
                        # Check if VM.Standard.A1.Flex is in the list
                        arm_shapes = [s for s in shapes_response.data if s.shape.startswith("VM.Standard.A1")]
                        if arm_shapes:
                            result["arm_shape_available"] = True
                            result["arm_shapes"] = [s.shape for s in arm_shapes]
                except Exception as e:
                    logger.debug(f"Could not check shapes for {region}: {e}")
                    # Shape listing might not work, but region is accessible
                    
        except Exception as e:
            result["error"] = str(e)
            logger.debug(f"Error checking {region}: {e}")
            
    except Exception as e:
        result["error"] = str(e)
        logger.debug(f"Error configuring client for {region}: {e}")
    
    return result


def check_all_regions() -> List[Dict[str, any]]:
    """Check all regions for ARM availability."""
    compartment_id = os.environ.get("OCI_COMPARTMENT_ID")
    tenancy_ocid = os.environ.get("OCI_TENANCY_OCID")
    user_ocid = os.environ.get("OCI_USER_OCID")
    fingerprint = os.environ.get("OCI_FINGERPRINT")
    private_key_path = os.environ.get("OCI_PRIVATE_KEY_PATH", "oci-private-key.pem")
    
    if not all([compartment_id, tenancy_ocid, user_ocid, fingerprint]):
        logger.error("Missing required OCI environment variables")
        return []
    
    results = []
    
    for region in REGIONS:
        logger.info(f"Checking {region}...")
        result = check_region_arm_availability(
            region, compartment_id, tenancy_ocid, user_ocid, fingerprint, private_key_path
        )
        results.append(result)
        
        if result["available"]:
            status = "✓"
            if result.get("arm_shape_available"):
                status += " (ARM available)"
            logger.info(f"  {status} {region}: Available (ADs: {', '.join(result['availability_domains'])})")
        elif result["error"]:
            if "NotAuthenticated" in str(result["error"]):
                logger.info(f"  ✗ {region}: Not accessible (auth required)")
            else:
                logger.info(f"  ✗ {region}: {result['error']}")
        else:
            logger.info(f"  ? {region}: Unknown")
    
    return results


def main():
    """Main function."""
    print("=" * 80)
    print("Oracle Cloud ARM Instance Capacity Checker")
    print("=" * 80)
    print("")
    print("Note: This checks region accessibility. Actual ARM capacity")
    print("      may still be unavailable even if region is accessible.")
    print("")
    
    if not OCI_AVAILABLE:
        print("ERROR: OCI SDK not available")
        print("Install with: pip install oci")
        sys.exit(1)
    
    results = check_all_regions()
    
    print("")
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    
    available_regions = [r for r in results if r["available"]]
    arm_available_regions = [r for r in available_regions if r.get("arm_shape_available")]
    
    if available_regions:
        print(f"\n✓ Found {len(available_regions)} accessible regions:")
        for result in available_regions:
            arm_status = " (ARM shape available)" if result.get("arm_shape_available") else ""
            print(f"  - {result['region']}: {len(result['availability_domains'])} ADs{arm_status}")
            for ad in result['availability_domains']:
                print(f"    • {ad}")
        
        if arm_available_regions:
            print(f"\n✓ Regions with ARM shape available: {len(arm_available_regions)}")
            for result in arm_available_regions:
                print(f"  - {result['region']}")
        
        print("\nTo try creating instances in us-sanjose-1 (current region):")
        print("  Run: ./scripts/retry-oracle-instances.sh")
        print("\nTo try a different region:")
        print("  1. Update OCI_REGION in env.sh")
        print("  2. Update terraform/main.tf if needed")
        print("  3. Run: ./scripts/retry-oracle-instances.sh")
    else:
        print("\n✗ No accessible regions found")
        print("  This may indicate:")
        print("  - Authentication issues")
        print("  - Region access restrictions")
        print("  - Need to check Oracle Cloud Console manually")
    
    print("")
    print("=" * 80)
    print("\nNote: 'Out of host capacity' errors are region-specific and")
    print("      can only be determined by attempting to create instances.")


if __name__ == "__main__":
    main()
