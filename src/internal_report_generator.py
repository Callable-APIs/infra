"""Internal report generator for detailed, granular cost analysis."""
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class InternalReportGenerator:
    """Generator for detailed internal cost reports with granular data."""

    def __init__(self, output_dir: str = "internal_reports"):
        """
        Initialize internal report generator.

        Args:
            output_dir: Directory to save generated reports
        """
        self.output_dir = output_dir
        import os

        os.makedirs(output_dir, exist_ok=True)

    def generate_detailed_report(
        self,
        title: str,
        summary: Dict[str, Any],
        detailed_costs: List[Dict[str, Any]],
        tag_costs: List[Dict[str, Any]],
        days_back: int,
        account_id: str,
        billing_info: Optional[Dict[str, Any]] = None,
        current_cycle_costs: Optional[List[Dict[str, Any]]] = None,
        previous_cycle_costs: Optional[List[Dict[str, Any]]] = None,
    ) -> str:
        """
        Generate detailed internal HTML report with granular cost data.

        Args:
            title: Report title
            summary: Summary statistics
            detailed_costs: Detailed cost breakdown by resource
            tag_costs: Cost breakdown by tags
            days_back: Number of days the report covers
            account_id: AWS account ID (unmasked for internal use)
            billing_info: Billing cycle information
            current_cycle_costs: Current billing cycle costs
            previous_cycle_costs: Previous billing cycle costs

        Returns:
            Path to generated report file
        """
        # Generate HTML report
        html_content = self._generate_html_report(
            title,
            summary,
            detailed_costs,
            tag_costs,
            days_back,
            account_id,
            billing_info or {},
            current_cycle_costs or [],
            previous_cycle_costs or [],
        )

        # Save as index.html for easy access
        filepath = f"{self.output_dir}/index.html"

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(html_content)

        logger.info(f"Generated internal HTML report: {filepath}")
        return filepath

    def _generate_html_report(
        self,
        title: str,
        summary: Dict[str, Any],
        detailed_costs: List[Dict[str, Any]],
        tag_costs: List[Dict[str, Any]],
        days_back: int,
        account_id: str,
        billing_info: Dict[str, Any],
        current_cycle_costs: List[Dict[str, Any]],
        previous_cycle_costs: List[Dict[str, Any]],
    ) -> str:
        """Generate HTML content for internal report."""

        # Calculate totals
        current_total = sum(item["cost"] for item in current_cycle_costs) if current_cycle_costs else 0
        previous_total = sum(item["cost"] for item in previous_cycle_costs) if previous_cycle_costs else 0
        change = current_total - previous_total
        change_pct = (change / previous_total * 100) if previous_total > 0 else 0

        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            line-height: 1.6;
            color: #333;
            background: #f5f5f5;
            padding: 20px;
        }}

        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}

        header {{
            border-bottom: 3px solid #dc3545;
            padding-bottom: 20px;
            margin-bottom: 30px;
        }}

        h1 {{
            color: #dc3545;
            font-size: 2.5em;
            margin-bottom: 10px;
        }}

        .meta {{
            color: #666;
            font-size: 0.9em;
        }}

        .alert {{
            background: #f8d7da;
            border: 1px solid #f5c6cb;
            border-radius: 4px;
            padding: 15px;
            margin: 20px 0;
            color: #721c24;
        }}

        .summary {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin: 30px 0;
        }}

        .summary-card {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 6px;
            border-left: 4px solid #dc3545;
        }}

        .summary-card h3 {{
            color: #666;
            font-size: 0.9em;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 10px;
        }}

        .summary-card .value {{
            font-size: 2em;
            font-weight: bold;
            color: #333;
        }}

        .billing-comparison {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
            margin: 40px 0;
        }}

        .billing-card {{
            background: #f8f9fa;
            padding: 25px;
            border-radius: 8px;
            border: 2px solid #e9ecef;
        }}

        .billing-card.current {{
            border-color: #28a745;
        }}

        .billing-card.previous {{
            border-color: #6c757d;
        }}

        .billing-card h3 {{
            color: #333;
            font-size: 1.4em;
            margin-bottom: 15px;
            text-align: center;
        }}

        .billing-total {{
            font-size: 2.5em;
            font-weight: bold;
            text-align: center;
            margin: 20px 0;
        }}

        .current .billing-total {{
            color: #28a745;
        }}

        .previous .billing-total {{
            color: #6c757d;
        }}

        .change-indicator {{
            text-align: center;
            font-size: 1.2em;
            font-weight: bold;
            margin: 20px 0;
            padding: 15px;
            border-radius: 6px;
        }}

        .change-positive {{
            background: #d4edda;
            color: #155724;
        }}

        .change-negative {{
            background: #f8d7da;
            color: #721c24;
        }}

        .section {{
            margin: 40px 0;
        }}

        .section h2 {{
            color: #333;
            font-size: 1.8em;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid #eee;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}

        th {{
            background: #333;
            color: white;
            padding: 12px;
            text-align: left;
            font-weight: 600;
        }}

        td {{
            padding: 12px;
            border-bottom: 1px solid #eee;
        }}

        tr:hover {{
            background: #f8f9fa;
        }}

        .cost {{
            font-weight: 600;
            color: #dc3545;
        }}

        .percentage {{
            color: #666;
            font-size: 0.9em;
        }}

        .bar-container {{
            background: #eee;
            border-radius: 4px;
            height: 20px;
            overflow: hidden;
            margin-top: 5px;
        }}

        .bar {{
            background: linear-gradient(90deg, #dc3545, #c82333);
            height: 100%;
            transition: width 0.3s ease;
        }}

        .current .bar {{
            background: linear-gradient(90deg, #28a745, #1e7e34);
        }}

        footer {{
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #eee;
            text-align: center;
            color: #666;
            font-size: 0.9em;
        }}

        .no-data {{
            text-align: center;
            padding: 40px;
            color: #999;
            font-style: italic;
        }}

        @media (max-width: 768px) {{
            .billing-comparison {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>{title}</h1>
            <div class="meta">
                <strong>Generated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}<br>
                <strong>Period:</strong> Last {days_back} days<br>
                <strong>Account:</strong> {account_id}
            </div>
        </header>

        <div class="alert">
            <strong>⚠️ INTERNAL REPORT:</strong> This report contains sensitive AWS resource information.
            Do not share this report outside your organization.
        </div>

            <div class="summary">
                <div class="summary-card">
                    <h3>Total Cost (30 days)</h3>
                    <div class="value">${summary['total_cost']:.2f}</div>
                </div>
                <div class="summary-card">
                    <h3>Active Services</h3>
                    <div class="value">{summary['service_count']}</div>
                </div>
                <div class="summary-card">
                    <h3>Current Cycle</h3>
                    <div class="value">{billing_info.get('current_cycle_days', 0) if billing_info else 0} days</div>
                </div>
            </div>

        <div class="billing-comparison">
                <div class="billing-card current">
                    <h3>Current Billing Cycle</h3>
                    <div class="billing-total">${current_total:.2f}</div>
                    <p style="text-align: center; color: #666;">
                        {billing_info.get('current_cycle_start', 'Unknown') if billing_info else 'Unknown'}
                        (Day {billing_info.get('current_cycle_days', 0) if billing_info else 0})
                    </p>
                    <p style="text-align: center; color: #666;">
                        Daily Average: ${current_total / (billing_info.get('current_cycle_days', 1) if billing_info else 1):.2f}
                    </p>
                </div>

                <div class="billing-card previous">
                    <h3>Previous Billing Cycle</h3>
                    <div class="billing-total">${previous_total:.2f}</div>
                    <p style="text-align: center; color: #666;">
                        {billing_info.get('previous_cycle_start', 'Unknown') if billing_info else 'Unknown'} to
                        {billing_info.get('previous_cycle_end', 'Unknown') if billing_info else 'Unknown'}
                    </p>
                    <p style="text-align: center; color: #666;">
                        Daily Average: ${previous_total / (billing_info.get('previous_cycle_days', 1) if billing_info else 1):.2f}
                    </p>
                </div>
        </div>

        <div class="change-indicator {'change-negative' if change < 0 else 'change-positive'}">
            Change: ${change:+.2f} ({change_pct:+.1f}%)
        </div>

        <div class="section">
            <h2>Current Cycle Service Breakdown</h2>
            {self._generate_service_table(current_cycle_costs, current_total)}
        </div>

        <div class="section">
            <h2>Previous Cycle Service Breakdown</h2>
            {self._generate_service_table(previous_cycle_costs, previous_total)}
        </div>

        <div class="section">
            <h2>Detailed Resource Costs (Last {days_back} Days)</h2>
            {self._generate_detailed_table(detailed_costs)}
        </div>

        {self._generate_tag_section(tag_costs)}

        <footer>
            <p>Generated by AWS Infrastructure Reporting Tool</p>
            <p>Data source: AWS Cost Explorer API</p>
            <p><strong>INTERNAL USE ONLY - Contains sensitive information</strong></p>
        </footer>
    </div>
</body>
</html>
"""
        return html

    def _generate_service_table(self, services: List[Dict[str, Any]], total: float) -> str:
        """Generate HTML table for service costs."""
        if not services:
            return '<div class="no-data">No service data available</div>'

        html = f"""
        <table>
            <thead>
                <tr>
                    <th>Service</th>
                    <th>Cost (USD)</th>
                    <th>% of Total</th>
                    <th>Distribution</th>
                </tr>
            </thead>
            <tbody>
        """

        for service in services[:10]:  # Top 10 services
            percentage = (service["cost"] / total * 100) if total > 0 else 0
            html += f"""
                <tr>
                    <td>{service['service']}</td>
                    <td class="cost">${service['cost']:.2f}</td>
                    <td class="percentage">{percentage:.1f}%</td>
                    <td>
                        <div class="bar-container">
                            <div class="bar" style="width: {percentage}%"></div>
                        </div>
                    </td>
                </tr>
            """

        html += """
            </tbody>
        </table>
        """
        return html

    def _generate_detailed_table(self, detailed_costs: List[Dict[str, Any]]) -> str:
        """Generate HTML table for detailed resource costs."""
        if not detailed_costs:
            return '<div class="no-data">No detailed cost data available</div>'

        total_cost = sum(item["cost"] for item in detailed_costs)

        html = f"""
        <table>
            <thead>
                <tr>
                    <th>Service</th>
                    <th>Resource/Usage Type</th>
                    <th>Cost (USD)</th>
                    <th>% of Total</th>
                </tr>
            </thead>
            <tbody>
        """

        for item in detailed_costs[:50]:  # Top 50 resources
            percentage = (item["cost"] / total_cost * 100) if total_cost > 0 else 0
            html += f"""
                <tr>
                    <td>{item['service']}</td>
                    <td>{item['resource_id']}</td>
                    <td class="cost">${item['cost']:.2f}</td>
                    <td class="percentage">{percentage:.1f}%</td>
                </tr>
            """

        if len(detailed_costs) > 50:
            html += f"""
                <tr>
                    <td colspan="4" style="text-align: center; color: #666; font-style: italic;">
                        ... and {len(detailed_costs) - 50} more resources
                    </td>
                </tr>
            """

        html += """
            </tbody>
        </table>
        """
        return html

    def _generate_tag_section(self, tag_costs: List[Dict[str, Any]]) -> str:
        """Generate HTML section for tag-based costs."""
        if not tag_costs:
            return ""

        html = f"""
        <div class="section">
            <h2>Cost by Tags</h2>
            <table>
                <thead>
                    <tr>
                        <th>Service</th>
                        <th>Tag Value</th>
                        <th>Cost (USD)</th>
                    </tr>
                </thead>
                <tbody>
        """

        for item in tag_costs[:30]:  # Top 30 tagged resources
            html += f"""
                <tr>
                    <td>{item['service']}</td>
                    <td>{item['tag_value']}</td>
                    <td class="cost">${item['cost']:.2f}</td>
                </tr>
            """

        if len(tag_costs) > 30:
            html += f"""
                <tr>
                    <td colspan="3" style="text-align: center; color: #666; font-style: italic;">
                        ... and {len(tag_costs) - 30} more tagged resources
                    </td>
                </tr>
            """

        html += """
                </tbody>
            </table>
        </div>
        """
        return html

    def _write_report_header(self, f, title: str, days_back: int, account_id: str):
        """Write report header."""
        f.write("=" * 80 + "\n")
        f.write(f"{title}\n")
        f.write("=" * 80 + "\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}\n")
        f.write(f"Period: Last {days_back} days\n")
        f.write(f"Account ID: {account_id}\n")
        f.write(f"Report Type: INTERNAL - Contains sensitive information\n")
        f.write("=" * 80 + "\n\n")

    def _write_summary_section(self, f, summary: Dict[str, Any]):
        """Write summary section."""
        f.write("SUMMARY\n")
        f.write("-" * 40 + "\n")
        f.write(f"Total Cost: ${summary['total_cost']:.2f}\n")
        f.write(f"Active Services: {summary['service_count']}\n")
        f.write(f"Top Services by Cost:\n")

        for i, service in enumerate(summary.get("top_services", [])[:10], 1):
            f.write(f"  {i:2d}. {service['service']:<40} ${service['cost']:>8.2f} ({service['percentage']:>5.1f}%)\n")
        f.write("\n")

    def _write_billing_cycle_section(
        self,
        f,
        billing_info: Dict[str, Any],
        current_cycle_costs: List[Dict[str, Any]],
        previous_cycle_costs: List[Dict[str, Any]],
    ):
        """Write billing cycle section."""
        if not billing_info:
            return

        f.write("BILLING CYCLE ANALYSIS\n")
        f.write("-" * 60 + "\n")
        f.write(f"Billing Cycle Day: {billing_info.get('billing_start_day', 'Unknown')}\n")
        f.write(
            f"Current Cycle: {billing_info.get('current_cycle_start', 'Unknown')} (Day {billing_info.get('current_cycle_days', 0)})\n"
        )
        f.write(
            f"Previous Cycle: {billing_info.get('previous_cycle_start', 'Unknown')} to {billing_info.get('previous_cycle_end', 'Unknown')} ({billing_info.get('previous_cycle_days', 0)} days)\n"
        )
        f.write("\n")

        # Current billing cycle costs
        if current_cycle_costs:
            current_total = sum(item["cost"] for item in current_cycle_costs)
            f.write("CURRENT BILLING CYCLE COSTS\n")
            f.write("-" * 40 + "\n")
            f.write(f"Total Current Cycle: ${current_total:.2f}\n")
            f.write(f"Daily Average: ${current_total / billing_info.get('current_cycle_days', 1):.2f}\n")
            f.write(f"Projected Monthly: ${current_total * 30 / billing_info.get('current_cycle_days', 1):.2f}\n")
            f.write("\n")
            f.write(f"{'Service':<40} {'Cost':<10} {'%':<6}\n")
            f.write("-" * 56 + "\n")

            for item in current_cycle_costs[:10]:  # Top 10 services
                service = item["service"][:39]
                cost = item["cost"]
                percentage = (cost / current_total * 100) if current_total > 0 else 0
                f.write(f"{service:<40} ${cost:>8.2f} {percentage:>5.1f}%\n")
            f.write("\n")

        # Previous billing cycle costs
        if previous_cycle_costs:
            prev_total = sum(item["cost"] for item in previous_cycle_costs)
            f.write("PREVIOUS BILLING CYCLE COSTS\n")
            f.write("-" * 40 + "\n")
            f.write(f"Total Previous Cycle: ${prev_total:.2f}\n")
            f.write(f"Daily Average: ${prev_total / billing_info.get('previous_cycle_days', 1):.2f}\n")
            f.write("\n")
            f.write(f"{'Service':<40} {'Cost':<10} {'%':<6}\n")
            f.write("-" * 56 + "\n")

            for item in previous_cycle_costs[:10]:  # Top 10 services
                service = item["service"][:39]
                cost = item["cost"]
                percentage = (cost / prev_total * 100) if prev_total > 0 else 0
                f.write(f"{service:<40} ${cost:>8.2f} {percentage:>5.1f}%\n")
            f.write("\n")

            # Comparison
            if current_cycle_costs:
                current_total = sum(item["cost"] for item in current_cycle_costs)
                change = current_total - prev_total
                change_pct = (change / prev_total * 100) if prev_total > 0 else 0
                f.write("CYCLE-TO-CYCLE COMPARISON\n")
                f.write("-" * 30 + "\n")
                f.write(f"Previous Cycle: ${prev_total:.2f}\n")
                f.write(f"Current Cycle:  ${current_total:.2f}\n")
                f.write(f"Change:        ${change:+.2f} ({change_pct:+.1f}%)\n")
                f.write("\n")

    def _write_detailed_costs_section(self, f, detailed_costs: List[Dict[str, Any]]):
        """Write detailed costs section."""
        f.write("DETAILED COST BREAKDOWN BY RESOURCE\n")
        f.write("-" * 80 + "\n")
        f.write(f"{'Service':<40} {'Resource ID':<30} {'Cost':<10}\n")
        f.write("-" * 80 + "\n")

        total_detailed_cost = sum(item["cost"] for item in detailed_costs)

        for item in detailed_costs[:50]:  # Top 50 resources
            service = item["service"][:39]
            resource_id = item["resource_id"][:29] if item["resource_id"] != "N/A" else "N/A"
            cost = item["cost"]
            percentage = (cost / total_detailed_cost * 100) if total_detailed_cost > 0 else 0

            f.write(f"{service:<40} {resource_id:<30} ${cost:>8.2f} ({percentage:>5.1f}%)\n")

        if len(detailed_costs) > 50:
            f.write(f"\n... and {len(detailed_costs) - 50} more resources\n")
        f.write("\n")

    def _write_tag_costs_section(self, f, tag_costs: List[Dict[str, Any]]):
        """Write tag costs section."""
        if not tag_costs:
            f.write("TAG-BASED COST BREAKDOWN\n")
            f.write("-" * 40 + "\n")
            f.write("No tag-based cost data available\n\n")
            return

        f.write("TAG-BASED COST BREAKDOWN\n")
        f.write("-" * 60 + "\n")
        f.write(f"{'Service':<30} {'Tag Value':<20} {'Cost':<10}\n")
        f.write("-" * 60 + "\n")

        for item in tag_costs[:30]:  # Top 30 tagged resources
            service = item["service"][:29]
            tag_value = item["tag_value"][:19]
            cost = item["cost"]

            f.write(f"{service:<30} {tag_value:<20} ${cost:>8.2f}\n")

        if len(tag_costs) > 30:
            f.write(f"\n... and {len(tag_costs) - 30} more tagged resources\n")
        f.write("\n")

    def _write_report_footer(self, f):
        """Write report footer."""
        f.write("=" * 80 + "\n")
        f.write("END OF INTERNAL REPORT\n")
        f.write("=" * 80 + "\n")
        f.write("WARNING: This report contains sensitive AWS resource information.\n")
        f.write("Do not share this report outside your organization.\n")
        f.write("=" * 80 + "\n")

    def print_console_summary(
        self,
        summary: Dict[str, Any],
        detailed_costs: List[Dict[str, Any]],
        days_back: int,
        account_id: str,
    ):
        """Print a summary to console for quick review."""
        logger.info("\n" + "=" * 60)
        logger.info("AWS COST ANALYSIS - INTERNAL SUMMARY")
        logger.info("=" * 60)
        logger.info(f"Account: {account_id}")
        logger.info(f"Period: Last {days_back} days")
        logger.info(f"Total Cost: ${summary['total_cost']:.2f}")
        logger.info(f"Active Services: {summary['service_count']}")

        logger.info(f"\nTop 10 Most Expensive Resources:")
        logger.info("-" * 60)
        logger.info(f"{'Service':<30} {'Resource ID':<25} {'Cost':<8}")
        logger.info("-" * 60)

        for item in detailed_costs[:10]:
            service = item["service"][:29]
            resource_id = item["resource_id"][:24] if item["resource_id"] != "N/A" else "N/A"
            cost = item["cost"]
            logger.info(f"{service:<30} {resource_id:<25} ${cost:>6.2f}")

        logger.info("=" * 60)
