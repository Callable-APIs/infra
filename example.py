#!/usr/bin/env python3
"""
Example script demonstrating the AWS Infrastructure Reporting Tool.

This example shows how to generate a mock report without requiring AWS credentials.
For real usage, see the README.md file.
"""

import sys
sys.path.insert(0, 'src')

from report_generator import ReportGenerator
from sanitizer import generate_summary_stats, mask_account_id

# Mock data for demonstration
mock_services = [
    {'service': 'Amazon EC2', 'cost': 150.75},
    {'service': 'Amazon S3', 'cost': 45.30},
    {'service': 'Amazon RDS', 'cost': 89.50},
    {'service': 'AWS Lambda', 'cost': 12.25},
    {'service': 'Amazon CloudWatch', 'cost': 8.90},
    {'service': 'Amazon DynamoDB', 'cost': 15.60},
    {'service': 'Amazon SNS', 'cost': 2.45},
    {'service': 'Amazon SQS', 'cost': 3.80},
]

def main():
    print("=" * 60)
    print("AWS Infrastructure Reporting Tool - Demo")
    print("=" * 60)
    print()
    
    # Generate summary stats
    summary = generate_summary_stats(mock_services)
    
    print(f"📊 Total Cost: ${summary['total_cost']:.2f}")
    print(f"📦 Active Services: {summary['service_count']}")
    print()
    
    print("🏆 Top 5 Services by Cost:")
    for i, service in enumerate(summary['top_services'], 1):
        print(f"   {i}. {service['service']}: ${service['cost']:.2f} ({service['percentage']}%)")
    print()
    
    # Mask a demo account ID
    demo_account = "123456789012"
    masked_account = mask_account_id(demo_account)
    print(f"🔒 Account ID Masking: {demo_account} -> {masked_account}")
    print()
    
    # Generate HTML report
    print("📄 Generating HTML report...")
    generator = ReportGenerator(output_dir="demo_reports")
    
    report_path = generator.generate_html_report(
        title="Demo AWS Cost Report",
        summary=summary,
        services=mock_services,
        days_back=30,
        account_id=masked_account
    )
    
    print(f"✅ Report generated: {report_path}")
    print(f"✅ Index created: demo_reports/index.html")
    print()
    print("💡 Open demo_reports/index.html in your browser to view the report")
    print()
    print("=" * 60)

if __name__ == '__main__':
    main()
