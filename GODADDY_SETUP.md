# GoDaddy API Setup Guide

## Steps to Obtain GoDaddy API Credentials

### 1. Create API Key and Secret

1. Navigate to the [GoDaddy Developer Portal](https://developer.godaddy.com/keys/)
2. Log in with your GoDaddy account
3. Click **"Create New API Key"**
4. Fill in the form:
   - **Name**: `terraform-infrastructure` (or any descriptive name)
   - **Environment**: Select **Production**
   - **Description**: `For managing DNS records via Terraform`
5. Click **Create**
6. **IMPORTANT**: Copy both the **API Key** and **API Secret** immediately - they won't be shown again

### 2. Add Credentials to env.sh

Add the following to your `env.sh` file:

```bash
# GoDaddy Configuration
export GODADDY_API_KEY="your_api_key_here"
export GODADDY_API_SECRET="your_api_secret_here"
```

Replace `your_api_key_here` and `your_api_secret_here` with the actual values from step 1.

### 3. Source the Environment

```bash
source env.sh
```

### 4. Verify Credentials

Test the credentials with a simple API call:

```bash
curl -X GET "https://api.godaddy.com/v1/domains?limit=10" \
  -H "Authorization: sso-key $GODADDY_API_KEY:$GODADDY_API_SECRET"
```

You should see a list of your domains.

### 5. Update Terraform Variables

The credentials are automatically available to Terraform through the provider configuration. No additional tfvars changes needed.

## Terraform Provider Configuration

The GoDaddy provider is already configured in `terraform/main.tf`:

```hcl
provider "godaddy" {
  key    = var.godaddy_api_key
  secret = var.godaddy_api_secret
}
```

## Importing Existing DNS Records

### List Your Domains

First, get a list of all your domains:

```bash
curl -X GET "https://api.godaddy.com/v1/domains?limit=1000" \
  -H "Authorization: sso-key $GODADDY_API_KEY:$GODADDY_API_SECRET" \
  -H "Accept: application/json" | jq -r '.[].domain'
```

### Import DNS Records

For each domain, you'll need to import the DNS records. Example:

```bash
cd terraform

# Import all DNS records for a domain
terraform import godaddy_domain_record.example_www example.com www A

# Or use the godaddy_domain_record resource:
# This will be created after we design the Terraform configuration
```

## Security Best Practices

1. **Never commit env.sh** - It's already in `.gitignore`
2. **Rotate API keys regularly** - Update them every 90 days
3. **Use separate keys** - Create different API keys for different purposes
4. **Limit scope** - Use the minimum permissions needed
5. **Monitor usage** - Check GoDaddy logs for any unauthorized access

## API Rate Limits

GoDaddy API has rate limits:
- **60 requests per minute** for GET requests
- **120 requests per minute** for POST/PUT/DELETE requests

Plan bulk operations accordingly.

## Next Steps

1. Add credentials to `env.sh` as described above
2. Run `source env.sh` to load the environment
3. Test the credentials using the verification step above
4. We can then start importing your GoDaddy DNS records into Terraform
5. Migrate domains to Cloudflare Pages as documented in `FREE_TIER_RESOURCES.md`

