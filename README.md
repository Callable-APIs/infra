# AWS Infrastructure Reporting Tool

A comprehensive AWS-based infrastructure reporting and management tool that uses boto3 and AWS Cost Explorer to generate detailed cost and usage reports. Reports are automatically published to GitHub Pages with careful attention to data sanitization and privacy.

## Features

- 📊 **Cost Analysis**: Retrieve and analyze AWS costs using Cost Explorer API
- 🔒 **Privacy-First**: Automatically masks sensitive information (account IDs, ARNs)
- 📈 **Visual Reports**: Beautiful HTML reports with charts and summaries
- 🤖 **Automated**: GitHub Actions workflow for daily report generation
- 🌐 **GitHub Pages**: Automatic deployment to GitHub Pages
- ⚙️ **Configurable**: YAML-based configuration for customization

## Prerequisites

- Python 3.11 or higher
- AWS account with Cost Explorer enabled
- AWS credentials with appropriate permissions
- GitHub repository with Pages enabled

## Required AWS Permissions

The AWS credentials need the following permissions:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ce:GetCostAndUsage",
        "ce:GetCostForecast",
        "sts:GetCallerIdentity"
      ],
      "Resource": "*"
    }
  ]
}
```

## Installation

1. Clone the repository:
```bash
git clone https://github.com/Callable-APIs/infra.git
cd infra
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Create configuration file:
```bash
cp config.yaml.example config.yaml
```

4. Edit `config.yaml` with your settings:
```yaml
aws:
  region: us-east-1
  profile: null  # or your AWS profile name

cost_explorer:
  days_back: 30
  granularity: DAILY
  metrics:
    - UnblendedCost
    - UsageQuantity

report:
  title: "AWS Cost and Usage Report"
  output_dir: "reports"
  mask_account_ids: true
  include_service_breakdown: true
```

## Usage

### Quick Demo (No AWS Required)

Run the example script to see how the tool works without AWS credentials:

```bash
python example.py
```

This generates a demo report with mock data in the `demo_reports/` directory.

### Local Execution

Generate a report locally:

```bash
cd src
python main.py
```

With custom options:

```bash
python main.py --days 60 --output ../my-reports
```

Command-line options:
- `--config PATH`: Path to configuration file (default: config.yaml)
- `--days N`: Number of days to look back (overrides config)
- `--output DIR`: Output directory for reports (overrides config)
- `--no-mask`: Do not mask account IDs (use with caution)

### GitHub Actions Automation

1. Add AWS credentials as GitHub secrets:
   - Go to repository Settings → Secrets and variables → Actions
   - Add `AWS_ACCESS_KEY_ID`
   - Add `AWS_SECRET_ACCESS_KEY`

2. Enable GitHub Pages:
   - Go to Settings → Pages
   - Set Source to "Deploy from a branch"
   - Select `gh-pages` branch

3. The workflow runs:
   - Daily at 00:00 UTC (scheduled)
   - On manual trigger via Actions tab
   - On push to main branch (optional)

## Security & Privacy

This tool implements multiple security measures:

- ✅ **Account ID Masking**: AWS account IDs are masked (e.g., `****-****-1234`)
- ✅ **ARN Sanitization**: ARNs are sanitized to remove sensitive details
- ✅ **Metadata Filtering**: Request IDs and metadata are removed from reports
- ✅ **No Raw Data**: Only aggregated, sanitized data is included in reports
- ✅ **Public Service Names**: Only standard AWS service names (public info) are displayed

### What's Safe to Share

- ✅ AWS service names (e.g., "Amazon EC2", "Amazon S3")
- ✅ Cost amounts and percentages
- ✅ Usage quantities
- ✅ Time periods and dates

### What's Protected

- 🔒 Full AWS account IDs (only last 4 digits shown)
- 🔒 ARNs and resource identifiers
- 🔒 Request IDs and API metadata
- 🔒 Custom tags (if enabled in config)

## Project Structure

```
infra/
├── .github/
│   └── workflows/
│       └── generate-report.yml    # GitHub Actions workflow
├── src/
│   ├── main.py                    # Main entry point
│   ├── cost_explorer.py           # AWS Cost Explorer client
│   ├── sanitizer.py               # Data sanitization utilities
│   └── report_generator.py        # HTML report generator
├── reports/                       # Generated reports (gitignored)
├── config.yaml.example            # Example configuration
├── config.yaml                    # Your configuration (gitignored)
├── requirements.txt               # Python dependencies
├── .gitignore                     # Git ignore rules
└── README.md                      # This file
```

## Example Report

The generated HTML reports include:

- **Summary Cards**: Total cost, active services, reporting period
- **Top Services Table**: Services ranked by cost with visual bars
- **Complete Service List**: All services with detailed costs
- **Privacy Notice**: Clear indication that data is sanitized

## Development

### Running Tests

(Add test framework as needed)

```bash
pytest tests/
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## Troubleshooting

### "Unable to locate credentials"

Make sure AWS credentials are configured:
- For local: Use `aws configure` or set environment variables
- For GitHub Actions: Add secrets `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY`

### "Cost Explorer is not enabled"

Enable Cost Explorer in your AWS account:
1. Go to AWS Cost Management Console
2. Enable Cost Explorer (may take 24 hours to activate)

### Empty reports

- Ensure you have costs in the specified time period
- Check that your AWS credentials have the required permissions
- Verify Cost Explorer is enabled and has data

## License

MIT License - See LICENSE file for details

## Support

For issues and questions:
- Open an issue on GitHub
- Check existing issues for solutions
- Review AWS Cost Explorer documentation

## Acknowledgments

- Built with [boto3](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html)
- Templating by [Jinja2](https://jinja.palletsprojects.com/)
- Automated with [GitHub Actions](https://github.com/features/actions)