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

    # Domain management commands
    domains_parser = subparsers.add_parser(
        "domains",
        help="Domain management utilities",
        description="Get domain information and nameservers for CallableAPIs infrastructure",
    )
    domains_subparsers = domains_parser.add_subparsers(dest="domains_command")
    
    list_parser = domains_subparsers.add_parser(
        "list",
        help="List all domains",
        description="List all GoDaddy domains migrated to Cloudflare",
    )
    
    nameservers_parser = domains_subparsers.add_parser(
        "nameservers",
        help="Get Cloudflare nameservers",
        description="Get Cloudflare nameservers for all domains",
    )
    
    mapping_parser = domains_subparsers.add_parser(
        "mapping",
        help="Get domain key mapping",
        description="Get domain key-to-domain mapping used in Terraform",
    )

    # Infrastructure agent commands
    agent_parser = subparsers.add_parser(
        "agent",
        help="Infrastructure monitoring and management agent",
        description="Run automated health checks, cost analysis, and maintenance tasks",
    )
    agent_parser.add_argument(
        "--task",
        choices=["all", "health", "cost", "maintenance"],
        default="all",
        help="Task to run (default: all)",
    )
    agent_parser.add_argument(
        "--config",
        type=str,
        help="Path to configuration YAML file",
    )
    agent_parser.add_argument(
        "--health-output",
        type=str,
        help="Path to save health check results (JSON)",
    )
    agent_parser.add_argument(
        "--cost-output",
        type=str,
        help="Path to save cost report (text)",
    )

    return parser


def run_billing(args):
    """Run unified billing application."""
    import json
    from collections import defaultdict
    from datetime import datetime
    
    from clint.billing.manager import BillingManager
    
    # Initialize billing manager
    manager = BillingManager(
        providers=args.providers,
        oci_compartment_id=args.oci_compartment_id,
    )
    
    # Show available providers
    available = manager.get_available_providers()
    if not available:
        logger.error("No billing adapters available. Check your credentials.")
        sys.exit(1)
    
    logger.info(f"Available providers: {', '.join(available)}")
    
    output_data = {}
    
    # Daily costs
    if args.daily:
        now = datetime.now()
        start_date = (
            datetime.strptime(args.start, "%Y-%m-%d")
            if args.start
            else now.replace(day=1)
        )
        end_date = (
            datetime.strptime(args.end, "%Y-%m-%d") if args.end else now
        )
        
        logger.info(f"Retrieving daily costs from {start_date.date()} to {end_date.date()}...")
        daily_costs = manager.get_daily_costs(start_date, end_date)
        output_data["daily_costs"] = daily_costs
        
        # Print formatted report
        print(_format_daily_costs_report(daily_costs))
        print()
    
    # Month-over-month comparison
    if args.compare:
        now = datetime.now()
        year = args.year or now.year
        month = args.month or now.month
        
        logger.info(f"Retrieving month-over-month comparison for {year}-{month:02d}...")
        comparison = manager.get_monthly_comparison(year, month)
        output_data["monthly_comparison"] = comparison
        
        # Print formatted report
        print(_format_monthly_comparison_report(comparison))
    
    # Save output
    if args.output:
        with open(args.output, "w") as f:
            json.dump(output_data, f, indent=2, default=str)
        logger.info(f"JSON output saved to {args.output}")
    
    if args.text_output:
        text_lines = []
        if args.daily:
            text_lines.append(_format_daily_costs_report(output_data["daily_costs"]))
            text_lines.append("")
        if args.compare:
            text_lines.append(_format_monthly_comparison_report(output_data["monthly_comparison"]))
        
        with open(args.text_output, "w") as f:
            f.write("\n".join(text_lines))
        logger.info(f"Text report saved to {args.text_output}")


def _format_daily_costs_report(costs_data: dict) -> str:
    """Format daily costs as a readable report."""
    from collections import defaultdict
    
    lines = []
    lines.append("=" * 100)
    lines.append("DAILY COST BREAKDOWN")
    lines.append("=" * 100)
    lines.append("")
    lines.append(
        f"Period: {costs_data['period']['start'][:10]} to {costs_data['period']['end'][:10]}"
    )
    lines.append("")
    
    # Show available providers
    available_providers = [p for p, costs in costs_data["providers"].items() if costs]
    if available_providers:
        lines.append(f"Providers: {', '.join(available_providers)}")
        lines.append("")
    
    # Daily breakdown
    daily_totals = costs_data.get("daily_totals", {})
    if daily_totals:
        lines.append("Daily Totals:")
        lines.append("-" * 100)
        total_period = 0.0
        for date, data in sorted(daily_totals.items()):
            total = data["total"]
            total_period += total
            by_provider = data.get("by_provider", {})
            provider_str = ", ".join(
                f"{p}: ${v:.2f}" for p, v in sorted(by_provider.items()) if v > 0
            )
            lines.append(f"  {date}: ${total:.2f} ({provider_str})")
        
        lines.append("")
        lines.append(f"Period Total: ${total_period:.2f}")
        lines.append("")
    
    # Provider breakdown
    lines.append("Provider Breakdown:")
    lines.append("-" * 100)
    for provider, costs in costs_data["providers"].items():
        if not costs:
            continue
        
        provider_total = sum(c["total_cost"] for c in costs)
        lines.append(f"\n{provider}: ${provider_total:.2f}")
        lines.append("")
        
        # Show top services/resources
        service_totals = defaultdict(float)
        for cost_record in costs:
            for service, amount in cost_record.get("services", {}).items():
                service_totals[service] += amount
        
        if service_totals:
            sorted_services = sorted(
                service_totals.items(), key=lambda x: x[1], reverse=True
            )[:10]
            for service, amount in sorted_services:
                lines.append(f"  • {service}: ${amount:.2f}")
    
    # Errors
    if costs_data.get("errors"):
        lines.append("")
        lines.append("⚠️  ERRORS")
        lines.append("-" * 100)
        for error in costs_data["errors"]:
            lines.append(f"  • {error}")
    
    lines.append("")
    lines.append("=" * 100)
    
    return "\n".join(lines)


def _format_monthly_comparison_report(comparison: dict) -> str:
    """Format month-over-month comparison as a readable report."""
    lines = []
    lines.append("=" * 100)
    lines.append("MONTH-OVER-MONTH COST COMPARISON")
    lines.append("=" * 100)
    lines.append("")
    
    current = comparison["current_month"]
    previous = comparison["previous_month"]
    comp = comparison["comparison"]
    
    # Current month
    lines.append(
        f"📅 CURRENT MONTH: {current['year']}-{current['month']:02d} "
        f"({current['period']['start'][:10]} to {current['period']['end'][:10]})"
    )
    lines.append(f"   Total: ${current['total_cost']:.2f}")
    for provider, amount in sorted(current["by_provider"].items(), key=lambda x: -x[1]):
        if amount > 0:
            lines.append(f"   • {provider}: ${amount:.2f}")
    lines.append("")
    
    # Previous month
    lines.append(
        f"📅 PREVIOUS MONTH: {previous['year']}-{previous['month']:02d} "
        f"({previous['period']['start'][:10]} to {previous['period']['end'][:10]})"
    )
    lines.append(f"   Total: ${previous['total_cost']:.2f}")
    for provider, amount in sorted(previous["by_provider"].items(), key=lambda x: -x[1]):
        if amount > 0:
            lines.append(f"   • {provider}: ${amount:.2f}")
    lines.append("")
    
    # Comparison
    lines.append("📊 COMPARISON")
    lines.append("-" * 100)
    total_change = comp["total_change"]
    total_change_percent = comp["total_change_percent"]
    change_symbol = "📈" if total_change > 0 else "📉" if total_change < 0 else "➡️"
    lines.append(
        f"   Total Change: {change_symbol} ${abs(total_change):.2f} "
        f"({total_change_percent:+.1f}%)"
    )
    lines.append("")
    
    # Provider-level changes
    lines.append("   By Provider:")
    for provider, data in sorted(
        comp["by_provider"].items(), key=lambda x: -abs(x[1]["change"])
    ):
        change = data["change"]
        change_percent = data["change_percent"]
        if change == 0 and data["current"] == 0 and data["previous"] == 0:
            continue
        
        change_symbol = "📈" if change > 0 else "📉" if change < 0 else "➡️"
        lines.append(
            f"     • {provider}: {change_symbol} ${abs(change):.2f} "
            f"({change_percent:+.1f}%) "
            f"[${data['current']:.2f} vs ${data['previous']:.2f}]"
        )
    
    lines.append("")
    lines.append("=" * 100)
    
    return "\n".join(lines)


def run_cost_report(args):
    """Run AWS cost report."""
    from clint.aws.cost_report import main as cost_main
    
    cost_args = []
    if args.internal:
        cost_args.append("--internal")
    if args.console_only:
        cost_args.append("--console-only")
    cost_args.extend(["--days", str(args.days)])
    cost_args.extend(["--output", args.output])
    
    sys.argv = ["cost_report.py"] + cost_args
    cost_main()


def run_multicloud_report(args):
    """Run multi-cloud cost report."""
    # Multi-cloud reporting is now handled by the billing command
    # This is kept for backward compatibility but redirects to billing
    logger.warning("multicloud-report is deprecated. Use 'clint billing' instead.")
    from clint.billing.manager import BillingManager
    from datetime import datetime, timedelta
    
    manager = BillingManager()
    end_date = datetime.now()
    start_date = end_date - timedelta(days=args.days)
    
    daily_costs = manager.get_daily_costs(start_date, end_date)
    print(_format_daily_costs_report(daily_costs))


def run_oracle_check_capacity(args):
    """Run Oracle Cloud capacity check."""
    from clint.oracle.capacity import main as capacity_main
    
    sys.argv = ["capacity.py"]
    capacity_main()


def run_domains(args):
    """Run domain management commands."""
    from clint.domains.manager import DomainManager
    
    if args.domains_command == "list":
        domains = DomainManager.get_domains()
        print("GoDaddy Domains (migrated to Cloudflare):")
        print("=" * 50)
        for i, domain in enumerate(domains, 1):
            print(f"{i:2}. {domain}")
        print(f"\nTotal: {len(domains)} domains")
    elif args.domains_command == "nameservers":
        nameservers = DomainManager.get_nameservers()
        print("Cloudflare Nameservers:")
        print("=" * 50)
        for i, ns in enumerate(nameservers, 1):
            print(f"{i}. {ns}")
        print("\nAll domains use these nameservers.")
        print("Configure them in GoDaddy for DNS to be managed by Cloudflare.")
    elif args.domains_command == "mapping":
        mapping = DomainManager.get_domain_mapping()
        print("Domain Key Mapping (for Terraform):")
        print("=" * 50)
        for key, domain in sorted(mapping.items()):
            print(f"{key:15} -> {domain}")
        print(f"\nTotal: {len(mapping)} domain mappings")
    else:
        print("Available commands: list, nameservers, mapping")
        print("Use 'python -m clint domains --help' for more information")


def run_agent(args):
    """Run infrastructure agent."""
    from clint.agent.manager import InfrastructureAgent
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    agent = InfrastructureAgent(config_path=args.config)
    agent.run(
        task=args.task,
        health_output=args.health_output,
        cost_output=args.cost_output
    )


def run_terraform_discover(args):
    """Run Terraform discovery."""
    from clint.terraform.discovery import main as discover_main
    
    sys.argv = ["discovery.py"]
    discover_main()


def run_terraform_generate(args):
    """Run Terraform generation."""
    from clint.terraform.generator import main as generate_main
    
    sys.argv = ["generator.py"]
    generate_main()


def run_full_analysis(args):
    """Run full infrastructure analysis."""
    import os
    
    print("🚀 Running full infrastructure analysis...")
    
    # Generate cost reports
    print("Step 1: Generating cost reports...")
    from clint.aws.cost_report import main as cost_main
    sys.argv = ["cost_report.py", "--internal", "--output", "internal_reports", "--days", "30"]
    cost_main()
    
    sys.argv = ["cost_report.py", "--output", "reports", "--days", "30"]
    cost_main()
    
    # Discover infrastructure
    print("Step 2: Discovering infrastructure...")
    from clint.terraform.discovery import main as discover_main
    sys.argv = ["discovery.py"]
    discover_main()
    
    # Generate Terraform
    print("Step 3: Generating Terraform configuration...")
    from clint.terraform.generator import main as generate_main
    sys.argv = ["generator.py"]
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
        elif args.command == "domains":
            run_domains(args)
        elif args.command == "agent":
            run_agent(args)
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

