"""Main entry point for multi-cloud cost reporting tool."""
import argparse
import logging
import os
import sys
from datetime import datetime
from typing import Any, Dict

import yaml

from src.multicloud_cost_analyzer import MultiCloudCostAnalyzer
from src.multicloud_report_generator import MultiCloudReportGenerator

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def load_config(config_path: str = "config.yaml") -> Dict[str, Any]:
    """
    Load configuration from YAML file.

    Args:
        config_path: Path to configuration file

    Returns:
        Configuration dictionary
    """
    if not os.path.exists(config_path):
        logger.warning(f"Config file not found: {config_path}, using defaults")
        return {
            "aws": {"region": "us-east-1", "profile": None},
            "cost_explorer": {
                "days_back": 30,
                "granularity": "DAILY",
                "metrics": ["UnblendedCost", "UsageQuantity"],
            },
            "report": {
                "title": "Multi-Cloud Cost and Usage Report",
                "output_dir": "reports",
                "include_service_breakdown": True,
            },
        }

    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
        return config if config is not None else {}


def main() -> int:
    """Main function to generate multi-cloud cost reports."""
    parser = argparse.ArgumentParser(description="Multi-Cloud Infrastructure Cost Reporting Tool")
    parser.add_argument(
        "--config",
        default="config.yaml",
        help="Path to configuration file (default: config.yaml)",
    )
    parser.add_argument("--days", type=int, help="Number of days to look back (overrides config)")
    parser.add_argument("--output", help="Output directory for reports (overrides config)")
    parser.add_argument(
        "--console-only",
        action="store_true",
        help="Print summary to console only (no file output)",
    )

    args = parser.parse_args()

    try:
        # Load configuration
        config = load_config(args.config)

        # Override config with command-line arguments
        if args.days:
            config["cost_explorer"]["days_back"] = args.days
        if args.output:
            config["report"]["output_dir"] = args.output

        # Initialize multi-cloud cost analyzer
        logger.info("Initializing multi-cloud cost analyzer...")
        aws_config = config.get("aws", {})
        analyzer = MultiCloudCostAnalyzer(
            aws_region=aws_config.get("region", "us-east-1"),
            aws_profile=aws_config.get("profile"),
        )

        # Retrieve cost data from all providers
        ce_config = config.get("cost_explorer", {})
        days_back = ce_config.get("days_back", 30)

        logger.info(f"Retrieving cost data for the last {days_back} days...")
        summary = analyzer.generate_multicloud_summary(days_back=days_back)

        if args.console_only:
            # Print console summary only
            print_console_summary(summary)
        else:
            # Generate comprehensive HTML report
            logger.info("Generating comprehensive multi-cloud HTML report...")
            report_config = config.get("report", {})
            generator = MultiCloudReportGenerator(output_dir=report_config.get("output_dir", "reports"))

            report_path = generator.generate_multicloud_report(
                title=report_config.get("title", "Multi-Cloud Cost and Usage Report"),
                summary=summary,
                days_back=days_back,
            )

            logger.info(f"✅ Multi-cloud report generated: {report_path}")

            # Also print console summary
            print_console_summary(summary)

        return 0

    except Exception as e:
        logger.error(f"❌ Error generating multi-cloud report: {e}", exc_info=True)
        return 1


def print_console_summary(summary: Dict[str, Any]) -> None:
    """
    Print multi-cloud cost summary to console.

    Args:
        summary: Multi-cloud cost summary data
    """
    print("\n" + "="*80)
    print("🌐 MULTI-CLOUD COST SUMMARY")
    print("="*80)
    
    print(f"📊 Total Cost: ${summary['total_cost']:.2f}")
    print(f"🏢 Active Providers: {summary['active_providers']}")
    print(f"📅 Period: Last {summary['days_back']} days")
    print(f"🕒 Generated: {summary['generated_at']}")
    
    print("\n" + "-"*80)
    print("CLOUD PROVIDER BREAKDOWN")
    print("-"*80)
    
    for provider_name, provider_data in summary["providers"].items():
        status = summary["free_tier_status"][provider_name]
        status_icon = "🆓" if "Free" in status or "Within limits" in status else "💰"
        
        print(f"\n{status_icon} {provider_data['provider']}: ${provider_data['total_cost']:.2f} ({status})")
        
        # Show top resources by category
        for category, category_data in provider_data["resource_categories"].items():
            if category_data["cost"] > 0 or category_data["resources"]:
                print(f"   📦 {category.title()}: ${category_data['cost']:.2f}")
                for resource in category_data["resources"][:3]:  # Top 3 resources
                    cost_str = "FREE" if resource["cost"] == 0.0 else f"${resource['cost']:.2f}"
                    print(f"      • {resource['service']}: {cost_str}")
    
    print("\n" + "-"*80)
    print("RESOURCE CATEGORY TOTALS")
    print("-"*80)
    
    for category, cost in summary["resource_totals"].items():
        percentage = (cost / summary["total_cost"] * 100) if summary["total_cost"] > 0 else 0
        print(f"📊 {category.title()}: ${cost:.2f} ({percentage:.1f}%)")
    
    print("\n" + "-"*80)
    print("FREE TIER STATUS")
    print("-"*80)
    
    for provider, status in summary["free_tier_status"].items():
        status_icon = "✅" if "Free" in status or "Within limits" in status else "⚠️"
        print(f"{status_icon} {provider.title()}: {status}")
    
    print("\n" + "="*80)


if __name__ == "__main__":
    sys.exit(main())