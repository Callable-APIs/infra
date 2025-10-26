# GoDaddy Test Key Setup Guide

## GoDaddy API Testing Workflow

According to GoDaddy's instructions, you need to:

1. **Create a TEST/Development key first** (in the sandbox environment)
2. **Verify that things work** with the test key
3. **Then create a PRODUCTION key** for actual use

## Current Status

❌ **Your current key appears to be for Production**, but you may need to start with a Test key first.

## Steps to Create Test Key

### 1. Create Development/Sandbox Key

1. Go to https://developer.godaddy.com/keys/
2. Create a new API key with:
   - **Environment**: Development (or Sandbox)
   - **Name**: `terraform-test`
3. Copy the Key and Secret (they'll look similar to your current ones)

### 2. Test the Sandbox Environment

The sandbox uses different endpoints:

**Development/Sandbox API:**
```bash
curl -X GET "https://api.ote-godaddy.com/v1/domains" \
  -H "Authorization: sso-key YOUR_TEST_KEY:YOUR_TEST_SECRET" \
  -H "Accept: application/json"
```

**Production API (what we've been using):**
```bash
curl -X GET "https://api.godaddy.com/v1/domains" \
  -H "Authorization: sso-key YOUR_PROD_KEY:YOUR_PROD_SECRET" \
  -H "Accept: application/json"
```

### 3. Update Terraform Configuration for Test Environment

Update the provider to use the sandbox endpoint:

```hcl
provider "godaddy" {
  key      = var.godaddy_api_key
  secret   = var.godaddy_api_secret
  shopper_id = ""  # May need for production
}
```

The provider may need to know which environment to use.

### 4. After Test Works, Create Production Key

Once verified with test key:
1. Create a Production key in the GoDaddy Developer Portal
2. Update env.sh with Production credentials
3. Update Terraform configuration for production environment

## Troubleshooting Test vs Production

**Common Issues:**

1. **Test key works, Production doesn't**:
   - Production requires 10+ domains (as documented)
   - Use test/sandbox for development

2. **Neither key works**:
   - Check for typos in credentials
   - Verify environment selection
   - Wait a few minutes for propagation

3. **Provider doesn't support environment switching**:
   - May need different provider or manual configuration
   - Consider skipping GoDaddy API and using Cloudflare instead

## Next Steps

1. **Create Test Key**: GoDaddy Developer Portal → New API Key → Development/Sandbox
2. **Update env.sh** with test credentials
3. **Test API access** with curl commands
4. **If test works**, try importing domains into Terraform
5. **If test doesn't work**, fall back to Cloudflare migration approach

## Alternative: Skip GoDaddy API Entirely

If the API continues to cause issues, consider:
- **Direct Cloudflare migration** (no GoDaddy API needed)
- **Manual DNS configuration** in Cloudflare
- **Terraform management via Cloudflare** (much better API)

This may be simpler than dealing with GoDaddy's API restrictions.

