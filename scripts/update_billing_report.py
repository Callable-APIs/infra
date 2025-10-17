#!/usr/bin/env python3
"""
Update Billing Report Script
Generates and updates the multi-cloud billing report
"""

import os
import sys
import subprocess
from datetime import datetime, timedelta

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from enhanced_billing_report import EnhancedBillingReport


def update_website_billing():
    """Update the website with current billing information"""
    print("Generating comprehensive billing report...")
    
    # Generate the report
    billing_report = EnhancedBillingReport()
    report_data = billing_report.generate_comprehensive_report()
    
    # Save detailed report
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_filename = f"multicloud_billing_report_{timestamp}.md"
    billing_report.save_report(report_filename)
    
    print(f"Detailed report saved to: {report_filename}")
    
    # Extract key metrics for website display
    aws_data = billing_report.get_aws_detailed_costs(
        (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d"),
        datetime.now().strftime("%Y-%m-%d")
    )
    
    total_cost = aws_data.get("total_cost", 0.0)
    free_tier_value = billing_report._calculate_free_tier_value()
    
    print(f"Current AWS cost: ${total_cost:.2f}")
    print(f"Free tier value: ${free_tier_value:.2f}")
    print(f"Total savings: ${free_tier_value:.2f}")
    
    return {
        "total_cost": total_cost,
        "free_tier_value": free_tier_value,
        "report_filename": report_filename
    }


def main():
    """Main function"""
    print("CallableAPIs Multi-Cloud Billing Report Update")
    print("=" * 50)
    
    try:
        # Update billing information
        billing_info = update_website_billing()
        
        print("\nBilling report updated successfully!")
        print(f"Total monthly cost: ${billing_info['total_cost']:.2f}")
        print(f"Free tier value: ${billing_info['free_tier_value']:.2f}")
        
    except Exception as e:
        print(f"Error updating billing report: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
