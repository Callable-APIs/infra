"""Multi-cloud cost report generator with real AWS data and comprehensive pivots."""
import logging
import os
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from jinja2 import Template

logger = logging.getLogger(__name__)


# Multi-cloud HTML template with comprehensive pivots
MULTICLOUD_HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }}</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            line-height: 1.6;
            color: #333;
            background: #f5f5f5;
            padding: 20px;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        header {
            border-bottom: 3px solid #FF9900;
            padding-bottom: 20px;
            margin-bottom: 30px;
        }
        
        h1 {
            color: #232F3E;
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        
        .meta {
            color: #666;
            font-size: 0.9em;
        }
        
        .alert {
            background: #fff3cd;
            border: 1px solid #ffc107;
            border-radius: 4px;
            padding: 15px;
            margin: 20px 0;
            color: #856404;
        }
        
        .summary {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 30px 0;
        }
        
        .summary-card {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 6px;
            border-left: 4px solid #FF9900;
        }
        
        .summary-card h3 {
            color: #666;
            font-size: 0.9em;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 10px;
        }
        
        .summary-card .value {
            font-size: 2em;
            font-weight: bold;
            color: #232F3E;
        }
        
        .provider-card {
            background: #f8f9fa;
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 20px;
            margin: 20px 0;
        }
        
        .provider-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 2px solid #eee;
        }
        
        .provider-name {
            font-size: 1.5em;
            font-weight: bold;
            color: #232F3E;
        }
        
        .provider-cost {
            font-size: 1.8em;
            font-weight: bold;
            color: #FF9900;
        }
        
        .free-tier-badge {
            background: #28a745;
            color: white;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 0.8em;
            font-weight: bold;
        }
        
        .paid-tier-badge {
            background: #dc3545;
            color: white;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 0.8em;
            font-weight: bold;
        }
        
        .section {
            margin: 40px 0;
        }
        
        .section h2 {
            color: #232F3E;
            font-size: 1.8em;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid #eee;
        }
        
        .pivot-table {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
            margin: 30px 0;
        }
        
        .pivot-section {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 6px;
        }
        
        .pivot-section h3 {
            color: #232F3E;
            margin-bottom: 15px;
            font-size: 1.3em;
        }
        
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }
        
        th {
            background: #232F3E;
            color: white;
            padding: 12px;
            text-align: left;
            font-weight: 600;
        }
        
        td {
            padding: 12px;
            border-bottom: 1px solid #eee;
        }
        
        tr:hover {
            background: #f8f9fa;
        }
        
        .cost {
            font-weight: 600;
            color: #FF9900;
        }
        
        .resource-category {
            font-weight: bold;
            color: #232F3E;
        }
        
        .bar-container {
            background: #eee;
            border-radius: 4px;
            height: 20px;
            overflow: hidden;
            margin-top: 5px;
        }
        
        .bar {
            background: linear-gradient(90deg, #FF9900, #FF6600);
            height: 100%;
            transition: width 0.3s ease;
        }
        
        .provider-bar {
            background: linear-gradient(90deg, #28a745, #20c997);
            height: 100%;
            transition: width 0.3s ease;
        }
        
        .resource-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }
        
        .resource-category-card {
            background: white;
            border: 1px solid #ddd;
            border-radius: 6px;
            padding: 15px;
        }
        
        .resource-category-card h4 {
            color: #232F3E;
            margin-bottom: 10px;
            font-size: 1.1em;
        }
        
        .resource-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 8px 0;
            border-bottom: 1px solid #f0f0f0;
        }
        
        .resource-item:last-child {
            border-bottom: none;
        }
        
        .resource-name {
            font-weight: 500;
        }
        
        .resource-cost {
            color: #FF9900;
            font-weight: 600;
        }
        
        .free-resource {
            color: #28a745;
            font-weight: 600;
        }
        
        .no-data {
            text-align: center;
            padding: 40px;
            color: #999;
            font-style: italic;
        }
        
        .warning {
            background: #fff3cd;
            border: 1px solid #ffc107;
            border-radius: 4px;
            padding: 10px;
            margin: 10px 0;
            color: #856404;
        }
        
        .info {
            background: #d1ecf1;
            border: 1px solid #bee5eb;
            border-radius: 4px;
            padding: 10px;
            margin: 10px 0;
            color: #0c5460;
        }
        
        footer {
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #eee;
            text-align: center;
            color: #666;
            font-size: 0.9em;
        }
        
        @media (max-width: 768px) {
            .pivot-table {
                grid-template-columns: 1fr;
            }
            
            .summary {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>{{ title }}</h1>
            <div class="meta">
                <strong>Generated:</strong> {{ generated_at }}<br>
                <strong>Period:</strong> Last {{ days_back }} days<br>
                <strong>Providers:</strong> AWS, Oracle Cloud, Google Cloud, IBM Cloud
            </div>
        </header>
        
        <div class="alert">
            <strong>⚠️ Multi-Cloud Cost Monitoring:</strong> This report tracks costs across all cloud providers 
            to help identify any changes that might push you out of free tier limits.
        </div>
        
        <!-- Summary Cards -->
        <div class="summary">
            <div class="summary-card">
                <h3>Total Cost</h3>
                <div class="value">${{ "%.2f"|format(summary.total_cost) }}</div>
            </div>
            <div class="summary-card">
                <h3>Active Providers</h3>
                <div class="value">{{ summary.active_providers }}</div>
            </div>
            <div class="summary-card">
                <h3>Free Tier Status</h3>
                <div class="value">{{ summary.free_tier_providers }}/{{ summary.total_providers }}</div>
            </div>
            <div class="summary-card">
                <h3>Reporting Period</h3>
                <div class="value">{{ days_back }} days</div>
            </div>
        </div>
        
        <!-- Provider Overview -->
        <section class="section">
            <h2>Cloud Provider Overview</h2>
            {% for provider_name, provider_data in summary.providers.items() %}
            <div class="provider-card">
                <div class="provider-header">
                    <div class="provider-name">{{ provider_data.provider }}</div>
                    <div style="display: flex; align-items: center; gap: 15px;">
                        <div class="provider-cost">${{ "%.2f"|format(provider_data.total_cost) }}</div>
                        {% if provider_data.total_cost == 0.0 %}
                        <span class="free-tier-badge">FREE TIER</span>
                        {% else %}
                        <span class="paid-tier-badge">PAID</span>
                        {% endif %}
                    </div>
                </div>
                
                {% if provider_data.resource_categories %}
                <div class="resource-grid">
                    {% for category, category_data in provider_data.resource_categories.items() %}
                    {% if category_data.resources %}
                    <div class="resource-category-card">
                        <h4>{{ category.title() }} ({{ category_data.resources|length }} resources)</h4>
                        {% for resource in category_data.resources %}
                        <div class="resource-item">
                            <div class="resource-name">{{ resource.service }}</div>
                            <div class="{% if resource.cost == 0.0 %}free-resource{% else %}resource-cost{% endif %}">
                                {% if resource.cost == 0.0 %}FREE{% else %}${{ "%.2f"|format(resource.cost) }}{% endif %}
                            </div>
                        </div>
                        {% endfor %}
                    </div>
                    {% endif %}
                    {% endfor %}
                </div>
                {% endif %}
                
                {% if provider_data.get('notes') %}
                <div class="info">{{ provider_data.notes }}</div>
                {% endif %}
            </div>
            {% endfor %}
        </section>
        
        <!-- Pivot Tables -->
        <div class="pivot-table">
            <!-- Cost by Provider -->
            <div class="pivot-section">
                <h3>Cost by Provider</h3>
                <table>
                    <thead>
                        <tr>
                            <th>Provider</th>
                            <th>Cost (USD)</th>
                            <th>% of Total</th>
                            <th>Distribution</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for provider_name, provider_data in summary.providers.items() %}
                        <tr>
                            <td>{{ provider_data.provider }}</td>
                            <td class="cost">${{ "%.2f"|format(provider_data.total_cost) }}</td>
                            <td>{{ "%.1f"|format((provider_data.total_cost / summary.total_cost * 100) if summary.total_cost > 0 else 0) }}%</td>
                            <td>
                                <div class="bar-container">
                                    <div class="provider-bar" style="width: {{ (provider_data.total_cost / summary.total_cost * 100) if summary.total_cost > 0 else 0 }}%"></div>
                                </div>
                            </td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
            
            <!-- Cost by Resource Category -->
            <div class="pivot-section">
                <h3>Cost by Resource Category</h3>
                <table>
                    <thead>
                        <tr>
                            <th>Category</th>
                            <th>Cost (USD)</th>
                            <th>% of Total</th>
                            <th>Distribution</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for category, cost in summary.resource_totals.items() %}
                        <tr>
                            <td class="resource-category">{{ category.title() }}</td>
                            <td class="cost">${{ "%.2f"|format(cost) }}</td>
                            <td>{{ "%.1f"|format((cost / summary.total_cost * 100) if summary.total_cost > 0 else 0) }}%</td>
                            <td>
                                <div class="bar-container">
                                    <div class="bar" style="width: {{ (cost / summary.total_cost * 100) if summary.total_cost > 0 else 0 }}%"></div>
                                </div>
                            </td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>
        
        <!-- Free Tier Status -->
        <section class="section">
            <h2>Free Tier Status</h2>
            <div class="resource-grid">
                {% for provider_name, status in summary.free_tier_status.items() %}
                <div class="resource-category-card">
                    <h4>{{ provider_name.title() }}</h4>
                    <div class="resource-item">
                        <div class="resource-name">Status</div>
                        <div class="{% if status == 'Free Tier' or 'Within limits' in status %}free-resource{% else %}resource-cost{% endif %}">
                            {{ status }}
                        </div>
                    </div>
                </div>
                {% endfor %}
            </div>
        </section>
        
        <!-- AWS Detailed Breakdown (if costs exist) -->
        {% if summary.providers.aws.total_cost > 0 %}
        <section class="section">
            <h2>AWS Detailed Cost Breakdown</h2>
            {% if summary.providers.aws.services %}
            <table>
                <thead>
                    <tr>
                        <th>Service</th>
                        <th>Usage Type</th>
                        <th>Cost (USD)</th>
                        <th>% of AWS Total</th>
                    </tr>
                </thead>
                <tbody>
                    {% for service in summary.providers.aws.services[:20] %}
                    <tr>
                        <td>{{ service.service }}</td>
                        <td>{{ service.usage_type }}</td>
                        <td class="cost">${{ "%.2f"|format(service.cost) }}</td>
                        <td>{{ "%.1f"|format((service.cost / summary.providers.aws.total_cost * 100) if summary.providers.aws.total_cost > 0 else 0) }}%</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
            {% else %}
            <div class="no-data">No detailed AWS cost data available.</div>
            {% endif %}
        </section>
        {% endif %}
        
        <footer>
            <p>Generated by Multi-Cloud Infrastructure Reporting Tool</p>
            <p>Data sources: AWS Cost Explorer API, Cloud Provider Free Tier Documentation</p>
        </footer>
    </div>
</body>
</html>
"""


class MultiCloudReportGenerator:
    """Generator for comprehensive multi-cloud cost reports."""

    def __init__(self, output_dir: str = "reports"):
        """
        Initialize multi-cloud report generator.

        Args:
            output_dir: Directory to save generated reports
        """
        self.output_dir = output_dir
        import os
        os.makedirs(output_dir, exist_ok=True)

    def generate_multicloud_report(
        self,
        title: str,
        summary: Dict[str, Any],
        days_back: int,
    ) -> str:
        """
        Generate comprehensive multi-cloud HTML report.

        Args:
            title: Report title
            summary: Multi-cloud cost summary data
            days_back: Number of days the report covers

        Returns:
            Path to generated HTML file
        """
        template = Template(MULTICLOUD_HTML_TEMPLATE)

        # Calculate additional summary metrics
        summary["free_tier_providers"] = sum(1 for status in summary["free_tier_status"].values() 
                                           if "Free Tier" in status or "Within limits" in status)
        summary["total_providers"] = len(summary["free_tier_status"])

        html_content = template.render(
            title=title,
            generated_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC"),
            days_back=days_back,
            summary=summary,
        )

        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"multicloud_cost_report_{timestamp}.html"
        filepath = os.path.join(self.output_dir, filename)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(html_content)

        logger.info(f"Generated multi-cloud report: {filepath}")

        # Also create index.html for GitHub Pages
        index_path = os.path.join(self.output_dir, "index.html")
        with open(index_path, "w", encoding="utf-8") as f:
            f.write(html_content)

        logger.info(f"Created index.html: {index_path}")

        return filepath
