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
- Poetry (for dependency management)
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

2. Install Poetry (if not already installed):
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

3. Install dependencies:
```bash
poetry install
```

4. Create configuration file:
```bash
cp config.yaml.example config.yaml
```

5. Edit `config.yaml` with your settings:
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
poetry run aws-infra-report
```

Or using the module directly:

```bash
poetry run python -m src.main
```

With custom options:

```bash
poetry run aws-infra-report --days 60 --output my-reports
```

### Report Types

The tool supports two different report types:

#### 1. Public Report (Default)
```bash
poetry run aws-infra-report --days 30
```
- **Sanitized data** (account ID masked)
- **HTML format** for web viewing
- **Safe for public sharing**
- **GitHub Pages ready**

#### 2. Internal Detailed Report
```bash
# Generate detailed internal report
poetry run aws-infra-report --internal --days 30

# Console-only summary
poetry run aws-infra-report --internal --console-only --days 7
```
- **Full account details** (unmasked)
- **Resource-level costs** (usage types, instance types)
- **Granular breakdown** by service and usage type
- **Text format** for analysis
- **Contains sensitive information**

### Command-line options:
- `--config PATH`: Path to configuration file (default: config.yaml)
- `--days N`: Number of days to look back (overrides config)
- `--output DIR`: Output directory for reports (overrides config)
- `--no-mask`: Do not mask account IDs (use with caution)
- `--internal`: Generate internal detailed report with resource-level costs
- `--console-only`: Print summary to console only (no file output)

### GitHub Actions Automation

The project includes automated GitHub Actions workflows for:

1. **CI/CD Pipeline** (`.github/workflows/ci.yml`):
   - Runs on every push and pull request
   - Tests code quality, security, and functionality

2. **Automated Report Publishing** (`.github/workflows/github-pages.yml`):
   - Runs daily at 2 AM UTC
   - Generates and publishes sanitized reports to GitHub Pages
   - Can be triggered manually with custom parameters

#### Setup Instructions:

1. **Add AWS credentials as GitHub secrets:**
   - Go to repository Settings → Secrets and variables → Actions
   - Add `AWS_ACCESS_KEY_ID`
   - Add `AWS_SECRET_ACCESS_KEY`

2. **Enable GitHub Pages:**
   - Go to Settings → Pages
   - Set Source to "GitHub Actions"
   - The workflow will automatically deploy to Pages

3. **Manual Report Generation:**
   - Go to Actions tab → "Deploy AWS Cost Report to GitHub Pages"
   - Click "Run workflow"
   - Optionally specify number of days to look back

4. **Access Your Reports:**
   - Public reports: `https://yourusername.github.io/infra`
   - Reports are automatically updated daily

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
│       └── ci.yml                 # GitHub Actions CI/CD workflow
├── .pre-commit-config.yaml        # Pre-commit hooks configuration
├── src/
│   ├── main.py                    # Main entry point
│   ├── cost_explorer.py           # AWS Cost Explorer client
│   ├── sanitizer.py               # Data sanitization utilities
│   └── report_generator.py        # HTML report generator
├── tests/
│   └── test_basic.py              # Test suite
├── reports/                       # Generated reports (gitignored)
├── config.yaml.example            # Example configuration
├── config.yaml                    # Your configuration (gitignored)
├── pyproject.toml                 # Poetry configuration and dependencies
├── poetry.lock                    # Poetry lock file (auto-generated)
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

### Setup Development Environment

1. Install development dependencies:
```bash
poetry install --with dev
```

2. Install pre-commit hooks:
```bash
poetry run pre-commit install
```

### Running Tests

```bash
# Run all tests
poetry run pytest

# Run tests with coverage
poetry run pytest --cov=src --cov-report=html

# Run specific test file
poetry run pytest tests/test_basic.py
```

### Code Quality

The project uses several tools to maintain code quality:

```bash
# Type checking
poetry run mypy src/

# Linting
poetry run pylint src/

# Code formatting
poetry run black src/ tests/
poetry run isort src/ tests/

# Security scanning
poetry run bandit -r src/
```

### Pre-commit Hooks

Pre-commit hooks are configured to run automatically on git commit:

- Black (code formatting)
- isort (import sorting)
- pylint (linting)
- mypy (type checking)
- bandit (security scanning)
- Various git hooks (trailing whitespace, large files, etc.)

### CI/CD Pipeline

The project includes a comprehensive GitHub Actions workflow that runs on every push and pull request:

**Test Job:**
- Runs on Python 3.11 and 3.12
- Installs dependencies with Poetry
- Runs mypy for type checking
- Runs pylint for code linting
- Runs black and isort for code formatting checks
- Runs pytest with coverage reporting
- Uploads coverage reports to Codecov

**Security Job:**
- Runs bandit for security vulnerability scanning
- Uploads security reports as artifacts

The pipeline ensures code quality and security before merging changes.

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