#!/usr/bin/env python3
"""
Unified Multi-Cloud Billing Application
Uses adapter pattern to consolidate billing data from multiple cloud providers
Provides daily cost breakdowns and month-over-month comparisons
"""
import argparse
import json
import logging
import os
import sys
from collections import defaultdict
from datetime import datetime
from typing import Any, Dict, List, Optional

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.billing.manager import BillingManager

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def format_daily_costs_report(costs_data: Dict[str, Any]) -> str:
    """Format daily costs as a readable report."""
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


def format_monthly_comparison_report(comparison: Dict[str, Any]) -> str:
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


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="Unified Multi-Cloud Billing Application",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Daily costs for current month (all providers)
  python3 src/unified_billing_app.py --daily

  # Daily costs for specific date range
  python3 src/unified_billing_app.py --daily --start 2024-01-01 --end 2024-01-31

  # Month-over-month comparison
  python3 src/unified_billing_app.py --compare

  # Both daily and comparison
  python3 src/unified_billing_app.py --daily --compare

  # Only AWS costs
  python3 src/unified_billing_app.py --daily --providers aws

  # Only Oracle and IBM Cloud costs
  python3 src/unified_billing_app.py --daily --providers oracle ibm

  # Save to JSON
  python3 src/unified_billing_app.py --daily --output costs.json
        """,
    )

    parser.add_argument(
        "--daily",
        action="store_true",
        help="Show daily cost breakdown",
    )
    parser.add_argument(
        "--compare",
        action="store_true",
        help="Show month-over-month comparison",
    )
    parser.add_argument(
        "--start",
        type=str,
        help="Start date (YYYY-MM-DD). Defaults to start of current month for --daily",
    )
    parser.add_argument(
        "--end",
        type=str,
        help="End date (YYYY-MM-DD). Defaults to today for --daily",
    )
    parser.add_argument(
        "--year",
        type=int,
        help="Year for comparison (defaults to current year)",
    )
    parser.add_argument(
        "--month",
        type=int,
        help="Month for comparison (1-12, defaults to current month)",
    )
    parser.add_argument(
        "--providers",
        nargs="+",
        choices=["aws", "oracle", "oci", "ibm", "ibmcloud"],
        help="Specific providers to include (default: all available)",
    )
    parser.add_argument(
        "--oci-compartment-id",
        type=str,
        default=os.environ.get("OCI_COMPARTMENT_ID"),
        help="OCI compartment OCID",
    )
    parser.add_argument(
        "--output",
        type=str,
        help="Output JSON file path",
    )
    parser.add_argument(
        "--text-output",
        type=str,
        help="Output text report file path",
    )

    args = parser.parse_args()

    # If no mode specified, default to both
    if not args.daily and not args.compare:
        args.daily = True
        args.compare = True

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
        print(format_daily_costs_report(daily_costs))
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
        print(format_monthly_comparison_report(comparison))

    # Save output
    if args.output:
        with open(args.output, "w") as f:
            json.dump(output_data, f, indent=2, default=str)
        logger.info(f"JSON output saved to {args.output}")

    if args.text_output:
        text_lines = []
        if args.daily:
            text_lines.append(format_daily_costs_report(output_data["daily_costs"]))
            text_lines.append("")
        if args.compare:
            text_lines.append(format_monthly_comparison_report(output_data["monthly_comparison"]))

        with open(args.text_output, "w") as f:
            f.write("\n".join(text_lines))
        logger.info(f"Text report saved to {args.text_output}")


if __name__ == "__main__":
    main()
