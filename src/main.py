"""Main entry point for AWS infrastructure reporting tool."""
import argparse
import logging
import yaml
import sys
import os
from typing import Dict, Any

from cost_explorer import CostExplorerClient
from sanitizer import mask_account_id, generate_summary_stats
from report_generator import ReportGenerator


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_config(config_path: str = 'config.yaml') -> Dict[str, Any]:
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
            'aws': {'region': 'us-east-1', 'profile': None},
            'cost_explorer': {
                'days_back': 30,
                'granularity': 'DAILY',
                'metrics': ['UnblendedCost', 'UsageQuantity']
            },
            'report': {
                'title': 'AWS Cost and Usage Report',
                'output_dir': 'reports',
                'mask_account_ids': True,
                'include_service_breakdown': True
            }
        }
    
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


def main():
    """Main function to generate AWS cost reports."""
    parser = argparse.ArgumentParser(
        description='AWS Infrastructure Reporting and Management Tool'
    )
    parser.add_argument(
        '--config',
        default='config.yaml',
        help='Path to configuration file (default: config.yaml)'
    )
    parser.add_argument(
        '--days',
        type=int,
        help='Number of days to look back (overrides config)'
    )
    parser.add_argument(
        '--output',
        help='Output directory for reports (overrides config)'
    )
    parser.add_argument(
        '--no-mask',
        action='store_true',
        help='Do not mask account IDs (use with caution)'
    )
    
    args = parser.parse_args()
    
    try:
        # Load configuration
        config = load_config(args.config)
        
        # Override config with command-line arguments
        if args.days:
            config['cost_explorer']['days_back'] = args.days
        if args.output:
            config['report']['output_dir'] = args.output
        if args.no_mask:
            config['report']['mask_account_ids'] = False
        
        # Initialize AWS Cost Explorer client
        logger.info("Initializing AWS Cost Explorer client...")
        aws_config = config.get('aws', {})
        ce_client = CostExplorerClient(
            region=aws_config.get('region', 'us-east-1'),
            profile=aws_config.get('profile')
        )
        
        # Get account ID
        account_id = ce_client.get_account_id()
        if config['report']['mask_account_ids']:
            display_account_id = mask_account_id(account_id)
        else:
            display_account_id = account_id
        
        logger.info(f"Account ID: {display_account_id}")
        
        # Retrieve cost data
        ce_config = config.get('cost_explorer', {})
        days_back = ce_config.get('days_back', 30)
        
        logger.info(f"Retrieving cost data for the last {days_back} days...")
        services_data = ce_client.get_services_cost_summary(days_back=days_back)
        
        # Generate summary statistics
        logger.info("Generating summary statistics...")
        summary = generate_summary_stats(services_data)
        
        # Generate HTML report
        logger.info("Generating HTML report...")
        report_config = config.get('report', {})
        generator = ReportGenerator(
            output_dir=report_config.get('output_dir', 'reports')
        )
        
        report_path = generator.generate_html_report(
            title=report_config.get('title', 'AWS Cost and Usage Report'),
            summary=summary,
            services=services_data if report_config.get('include_service_breakdown', True) else [],
            days_back=days_back,
            account_id=display_account_id
        )
        
        logger.info(f"✅ Report generated successfully: {report_path}")
        logger.info(f"📊 Total cost: ${summary['total_cost']:.2f}")
        logger.info(f"📦 Active services: {summary['service_count']}")
        
        if summary['top_services']:
            logger.info("🏆 Top 3 services by cost:")
            for i, service in enumerate(summary['top_services'][:3], 1):
                logger.info(f"   {i}. {service['service']}: ${service['cost']:.2f}")
        
        return 0
        
    except Exception as e:
        logger.error(f"❌ Error generating report: {e}", exc_info=True)
        return 1


if __name__ == '__main__':
    sys.exit(main())
