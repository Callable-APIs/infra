# GitHub Pages Setup Guide

This guide will help you set up automated AWS cost report publishing to GitHub Pages.

## Step 1: Enable GitHub Pages

1. Go to your repository on GitHub
2. Click **Settings** → **Pages**
3. Under **Source**, select "Deploy from a branch"
4. Select `gh-pages` branch and `/ (root)` folder
5. Click **Save**

Note: The `gh-pages` branch will be automatically created when the workflow runs for the first time.

## Step 2: Add AWS Credentials as Secrets

1. Go to **Settings** → **Secrets and variables** → **Actions**
2. Click **New repository secret**
3. Add the following secrets:
   - Name: `AWS_ACCESS_KEY_ID`
     Value: Your AWS access key ID
   - Name: `AWS_SECRET_ACCESS_KEY`
     Value: Your AWS secret access key

### Creating AWS Credentials

It's recommended to create a dedicated IAM user for this tool with minimal permissions:

1. Go to AWS IAM Console
2. Create a new IAM user (e.g., `github-cost-reporter`)
3. Attach a policy with these permissions:

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

4. Create access keys for the user
5. Copy the access key ID and secret access key

**Important**: Never commit these credentials to your repository!

## Step 3: Configure the Tool

1. Create a `config.yaml` file in the root of your repository:

```yaml
aws:
  region: us-east-1
  profile: null

cost_explorer:
  days_back: 30
  granularity: DAILY
  metrics:
    - UnblendedCost
    - UsageQuantity

report:
  title: "My AWS Cost Report"
  output_dir: "reports"
  mask_account_ids: true
  include_service_breakdown: true
```

2. Commit and push the config file:

```bash
git add config.yaml
git commit -m "Add cost reporting configuration"
git push
```

## Step 4: Run the Workflow

### Manual Trigger

1. Go to **Actions** tab in your repository
2. Select "Generate AWS Cost Report" workflow
3. Click **Run workflow** → **Run workflow**

### Automatic Schedule

The workflow is configured to run daily at 00:00 UTC. You can modify the schedule in `.github/workflows/generate-report.yml`:

```yaml
on:
  schedule:
    - cron: '0 0 * * *'  # Daily at midnight UTC
```

## Step 5: View Your Reports

Once the workflow completes successfully:

1. Your reports will be available at: `https://[username].github.io/[repository-name]/`
2. For example: `https://callable-apis.github.io/infra/`

## Troubleshooting

### Workflow fails with "Unable to locate credentials"

- Make sure you've added `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` as repository secrets
- Check that the secret names are exactly as specified (case-sensitive)

### "Cost Explorer is not enabled"

- Enable Cost Explorer in your AWS account
- Note: It may take up to 24 hours after enabling before data is available

### Pages deployment fails

- Ensure GitHub Pages is enabled in repository settings
- Check that the workflow has write permissions (Settings → Actions → General → Workflow permissions)

### No data in reports

- Verify you have AWS costs in the specified time period
- Check that your IAM user has the required permissions
- Review the workflow logs in the Actions tab

## Security Best Practices

1. **Use IAM User with Minimal Permissions**: Only grant Cost Explorer read permissions
2. **Enable MFA**: Consider enabling MFA for the IAM user
3. **Rotate Credentials**: Regularly rotate AWS access keys
4. **Monitor Usage**: Set up CloudWatch alerts for unusual API calls
5. **Keep Masking Enabled**: Always mask account IDs in public reports (`mask_account_ids: true`)

## Updating the Tool

To get the latest features and bug fixes:

1. Pull the latest changes from the main repository
2. Review and merge into your fork
3. The workflow will automatically use the updated code

## Support

If you encounter issues:

1. Check the workflow logs in the Actions tab
2. Review the troubleshooting section above
3. Open an issue on GitHub with:
   - Error message from workflow logs
   - Your configuration (with sensitive data removed)
   - Steps to reproduce the issue
