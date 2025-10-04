"""HTML report generator for AWS cost and usage data."""
import os
from datetime import datetime
from jinja2 import Template
from typing import Dict, List, Any
import logging

logger = logging.getLogger(__name__)


# HTML template for the report
HTML_TEMPLATE = """
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
            max-width: 1200px;
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
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
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
        
        footer {
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #eee;
            text-align: center;
            color: #666;
            font-size: 0.9em;
        }
        
        .no-data {
            text-align: center;
            padding: 40px;
            color: #999;
            font-style: italic;
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
                {% if account_id %}
                <strong>Account:</strong> {{ account_id }}
                {% endif %}
            </div>
        </header>
        
        <div class="alert">
            <strong>⚠️ Privacy Notice:</strong> This report contains sanitized cost information. 
            Account IDs and sensitive data have been masked to protect privacy.
        </div>
        
        <div class="summary">
            <div class="summary-card">
                <h3>Total Cost</h3>
                <div class="value">${{ "%.2f"|format(summary.total_cost) }}</div>
            </div>
            <div class="summary-card">
                <h3>Active Services</h3>
                <div class="value">{{ summary.service_count }}</div>
            </div>
            <div class="summary-card">
                <h3>Reporting Period</h3>
                <div class="value">{{ days_back }} days</div>
            </div>
        </div>
        
        {% if summary.top_services %}
        <section class="section">
            <h2>Top Services by Cost</h2>
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
                    {% for service in summary.top_services %}
                    <tr>
                        <td>{{ service.service }}</td>
                        <td class="cost">${{ "%.2f"|format(service.cost) }}</td>
                        <td>{{ "%.1f"|format(service.percentage) }}%</td>
                        <td>
                            <div class="bar-container">
                                <div class="bar" style="width: {{ service.percentage }}%"></div>
                            </div>
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </section>
        {% endif %}
        
        {% if services %}
        <section class="section">
            <h2>All Services</h2>
            {% if services|length > 0 %}
            <table>
                <thead>
                    <tr>
                        <th>Service</th>
                        <th>Cost (USD)</th>
                    </tr>
                </thead>
                <tbody>
                    {% for service in services %}
                    <tr>
                        <td>{{ service.service }}</td>
                        <td class="cost">${{ "%.2f"|format(service.cost) }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
            {% else %}
            <div class="no-data">No service data available for the selected period.</div>
            {% endif %}
        </section>
        {% endif %}
        
        <footer>
            <p>Generated by AWS Infrastructure Reporting Tool</p>
            <p>Data source: AWS Cost Explorer API</p>
        </footer>
    </div>
</body>
</html>
"""


class ReportGenerator:
    """Generator for HTML reports from AWS cost data."""
    
    def __init__(self, output_dir: str = "reports"):
        """
        Initialize report generator.
        
        Args:
            output_dir: Directory to save generated reports
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
    def generate_html_report(
        self,
        title: str,
        summary: Dict[str, Any],
        services: List[Dict],
        days_back: int,
        account_id: str = None
    ) -> str:
        """
        Generate HTML report from cost data.
        
        Args:
            title: Report title
            summary: Summary statistics
            services: List of services with costs
            days_back: Number of days the report covers
            account_id: AWS account ID (masked if provided)
            
        Returns:
            Path to generated HTML file
        """
        template = Template(HTML_TEMPLATE)
        
        html_content = template.render(
            title=title,
            generated_at=datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC'),
            days_back=days_back,
            account_id=account_id,
            summary=summary,
            services=services
        )
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"aws_cost_report_{timestamp}.html"
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        logger.info(f"Generated report: {filepath}")
        
        # Also create index.html for GitHub Pages
        index_path = os.path.join(self.output_dir, "index.html")
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        logger.info(f"Created index.html: {index_path}")
        
        return filepath
