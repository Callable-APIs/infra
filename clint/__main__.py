#!/usr/bin/env python3
"""
CLINT - Command Line INfra Tool
Main entry point for all infrastructure management tools.
"""
import argparse
import logging
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def create_parser():
    """Create the main argument parser."""
    parser = argparse.ArgumentParser(
        prog="clint",
        description="CLINT - Command Line INfra Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Billing and cost reporting
  python -m clint billing --daily --compare
  python -m clint billing --daily --providers aws oracle
  python -m clint cost-report --days 30
  python -m clint multicloud-report

  # Oracle Cloud utilities
  python -m clint oracle check-capacity

  # Terraform tools
  python -m clint terraform discover
  python -m clint terraform generate

  # Full analysis
  python -m clint full-analysis
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Billing command
    billing_parser = subparsers.add_parser(
        "billing",
        help="Unified multi-cloud billing reports",
        description="Generate billing reports from AWS, Oracle Cloud, and IBM Cloud",
    )
    billing_parser.add_argument(
        "--daily",
        action="store_true",
        help="Show daily cost breakdown",
    )
    billing_parser.add_argument(
        "--compare",
        action="store_true",
        help="Show month-over-month comparison",
    )
    billing_parser.add_argument(
        "--start",
        type=str,
        help="Start date (YYYY-MM-DD)",
    )
    billing_parser.add_argument(
        "--end",
        type=str,
        help="End date (YYYY-MM-DD)",
    )
    billing_parser.add_argument(
        "--year",
        type=int,
        help="Year for comparison",
    )
    billing_parser.add_argument(
        "--month",
        type=int,
        help="Month for comparison (1-12)",
    )
    billing_parser.add_argument(
        "--providers",
        nargs="+",
        choices=["aws", "oracle", "oci", "ibm", "ibmcloud"],
        help="Specific providers to include",
    )
    billing_parser.add_argument(
        "--oci-compartment-id",
        type=str,
        help="OCI compartment OCID",
    )
    billing_parser.add_argument(
        "--output",
        type=str,
        help="Output JSON file path",
    )
    billing_parser.add_argument(
        "--text-output",
        type=str,
        help="Output text report file path",
    )

    # Cost report command (AWS)
    cost_report_parser = subparsers.add_parser(
        "cost-report",
        help="Generate AWS cost reports",
        description="Generate AWS cost and usage reports",
    )
    cost_report_parser.add_argument(
        "--internal",
        action="store_true",
        help="Generate internal detailed report",
    )
    cost_report_parser.add_argument(
        "--console-only",
        action="store_true",
        help="Print summary to console only",
    )
    cost_report_parser.add_argument(
        "--days",
        type=int,
        default=30,
        help="Number of days to look back (default: 30)",
    )
    cost_report_parser.add_argument(
        "--output",
        type=str,
        default="reports",
        help="Output directory (default: reports)",
    )

    # Multi-cloud report command
    multicloud_parser = subparsers.add_parser(
        "multicloud-report",
        help="Generate multi-cloud cost reports",
        description="Generate cost reports across AWS, Google Cloud, Oracle Cloud, and IBM Cloud",
    )
    multicloud_parser.add_argument(
        "--internal",
        action="store_true",
        help="Generate internal detailed report",
    )
    multicloud_parser.add_argument(
        "--console-only",
        action="store_true",
        help="Print summary to console only",
    )
    multicloud_parser.add_argument(
        "--days",
        type=int,
        default=30,
        help="Number of days to look back (default: 30)",
    )
    multicloud_parser.add_argument(
        "--output",
        type=str,
        default="reports",
        help="Output directory (default: reports)",
    )

    # Oracle Cloud commands
    oracle_parser = subparsers.add_parser(
        "oracle",
        help="Oracle Cloud utilities",
        description="Oracle Cloud infrastructure management tools",
    )
    oracle_subparsers = oracle_parser.add_subparsers(dest="oracle_command")
    
    check_capacity_parser = oracle_subparsers.add_parser(
        "check-capacity",
        help="Check Oracle Cloud ARM instance capacity across regions",
    )

    # Terraform commands
    terraform_parser = subparsers.add_parser(
        "terraform",
        help="Terraform management tools",
        description="Discover and generate Terraform configurations",
    )
    terraform_subparsers = terraform_parser.add_subparsers(dest="terraform_command")
    
    discover_parser = terraform_subparsers.add_parser(
        "discover",
        help="Discover current AWS infrastructure",
    )
    
    generate_parser = terraform_subparsers.add_parser(
        "generate",
        help="Generate Terraform configuration",
    )

    # Full analysis command
    full_analysis_parser = subparsers.add_parser(
        "full-analysis",
        help="Run complete infrastructure analysis",
        description="Run cost reports, infrastructure discovery, and Terraform generation",
    )

    # Container commands
    container_parser = subparsers.add_parser(
        "container",
        help="Container applications",
        description="Run container applications (base, status)",
    )
    container_subparsers = container_parser.add_subparsers(dest="container_command")
    
    base_parser = container_subparsers.add_parser(
        "base",
        help="Run base container application",
        description="CallableAPIs base container with health and status endpoints",
    )
    
    status_parser = container_subparsers.add_parser(
        "status",
        help="Run status container application",
        description="CallableAPIs status dashboard aggregating health from all nodes",
    )

    return parser


def run_billing(args):
    """Run unified billing application."""
    from src.unified_billing_app import main as billing_main
    
    # Build sys.argv-like list for unified_billing_app
    billing_args = []
    if args.daily:
        billing_args.append("--daily")
    if args.compare:
        billing_args.append("--compare")
    if args.start:
        billing_args.extend(["--start", args.start])
    if args.end:
        billing_args.extend(["--end", args.end])
    if args.year:
        billing_args.extend(["--year", str(args.year)])
    if args.month:
        billing_args.extend(["--month", str(args.month)])
    if args.providers:
        billing_args.extend(["--providers"] + args.providers)
    if args.oci_compartment_id:
        billing_args.extend(["--oci-compartment-id", args.oci_compartment_id])
    if args.output:
        billing_args.extend(["--output", args.output])
    if args.text_output:
        billing_args.extend(["--text-output", args.text_output])
    
    # If no mode specified, default to both
    if not args.daily and not args.compare:
        billing_args.append("--daily")
        billing_args.append("--compare")
    
    sys.argv = ["unified_billing_app.py"] + billing_args
    billing_main()


def run_cost_report(args):
    """Run AWS cost report."""
    from src.main import main as cost_main
    
    cost_args = []
    if args.internal:
        cost_args.append("--internal")
    if args.console_only:
        cost_args.append("--console-only")
    cost_args.extend(["--days", str(args.days)])
    cost_args.extend(["--output", args.output])
    
    sys.argv = ["main.py"] + cost_args
    cost_main()


def run_multicloud_report(args):
    """Run multi-cloud cost report."""
    from src.multicloud_main import main as multicloud_main
    
    multicloud_args = []
    if args.internal:
        multicloud_args.append("--internal")
    if args.console_only:
        multicloud_args.append("--console-only")
    multicloud_args.extend(["--days", str(args.days)])
    multicloud_args.extend(["--output", args.output])
    
    sys.argv = ["multicloud_main.py"] + multicloud_args
    multicloud_main()


def run_oracle_check_capacity(args):
    """Run Oracle Cloud capacity check."""
    from src.check_oracle_arm_capacity import main as capacity_main
    
    sys.argv = ["check_oracle_arm_capacity.py"]
    capacity_main()


def run_terraform_discover(args):
    """Run Terraform discovery."""
    from src.terraform_discovery import main as discover_main
    
    sys.argv = ["terraform_discovery.py"]
    discover_main()


def run_terraform_generate(args):
    """Run Terraform generation."""
    from src.terraform_generator import main as generate_main
    
    sys.argv = ["terraform_generator.py"]
    generate_main()


def run_full_analysis(args):
    """Run full infrastructure analysis."""
    import os
    
    print("🚀 Running full infrastructure analysis...")
    
    # Generate cost reports
    print("Step 1: Generating cost reports...")
    from src.main import main as cost_main
    sys.argv = ["main.py", "--internal", "--output", "internal_reports", "--days", "30"]
    cost_main()
    
    sys.argv = ["main.py", "--output", "reports", "--days", "30"]
    cost_main()
    
    # Discover infrastructure
    print("Step 2: Discovering infrastructure...")
    from src.terraform_discovery import main as discover_main
    sys.argv = ["terraform_discovery.py"]
    discover_main()
    
    # Generate Terraform
    print("Step 3: Generating Terraform configuration...")
    from src.terraform_generator import main as generate_main
    sys.argv = ["terraform_generator.py"]
    generate_main()
    
    print("✅ Full analysis complete!")
    print("📁 Reports available in:")
    print("   - reports/ (public cost report)")
    print("   - internal_reports/ (internal cost report)")
    print("   - terraform_output/ (Terraform configuration)")


def main():
    """Main entry point."""
    parser = create_parser()
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    try:
        if args.command == "billing":
            run_billing(args)
        elif args.command == "cost-report":
            run_cost_report(args)
        elif args.command == "multicloud-report":
            run_multicloud_report(args)
        elif args.command == "oracle":
            if args.oracle_command == "check-capacity":
                run_oracle_check_capacity(args)
            else:
                parser.parse_args(["oracle", "--help"])
        elif args.command == "terraform":
            if args.terraform_command == "discover":
                run_terraform_discover(args)
            elif args.terraform_command == "generate":
                run_terraform_generate(args)
            else:
                parser.parse_args(["terraform", "--help"])
        elif args.command == "full-analysis":
            run_full_analysis(args)
        elif args.command == "container":
            if args.container_command == "base":
                from clint.container.base import main as base_main
                base_main()
            elif args.container_command == "status":
                from clint.container.status import main as status_main
                status_main()
            else:
                parser.parse_args(["container", "--help"])
        else:
            parser.print_help()
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n⚠️  Interrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"Error executing command: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()

