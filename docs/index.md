# AWS Infrastructure Cost Reports

This repository automatically generates and publishes AWS cost reports to GitHub Pages.

## 📊 About the Reports

The reports are generated daily at 2 AM UTC and contain:

- **Total AWS costs** for the specified period
- **Service breakdown** showing which AWS services are consuming the most resources
- **Cost trends** and analysis
- **Sanitized data** - account IDs are masked for privacy

## 🔄 Automated Updates

Reports are automatically updated:
- **Daily at 2 AM UTC** via GitHub Actions
- **On manual trigger** via the Actions tab
- **On code changes** (optional)

## 🛡️ Privacy & Security

All reports are sanitized to protect sensitive information:
- ✅ Account IDs are masked (e.g., `****-****-1234`)
- ✅ Only public service names are displayed
- ✅ No resource identifiers or ARNs are included
- ✅ Safe for public sharing

## 📈 Report Types

### Public Reports (GitHub Pages)
- High-level cost overview
- Service-level breakdown
- Beautiful HTML format
- Safe for public sharing

### Internal Reports (Command Line)
- Detailed resource-level costs
- Full account information
- Granular usage type breakdown
- Text format for analysis

## 🚀 Getting Started

To set up your own automated cost reports:

1. **Fork this repository**
2. **Add your AWS credentials** as GitHub secrets
3. **Enable GitHub Pages** in repository settings
4. **Configure the workflow** for your needs

See the [README.md](../README.md) for detailed setup instructions.

## 📞 Support

For issues and questions:
- Open an issue on GitHub
- Check the workflow logs in the Actions tab
- Review the AWS Cost Explorer documentation

---

*Last updated: {{ "now" | date: "%Y-%m-%d %H:%M:%S UTC" }}*
