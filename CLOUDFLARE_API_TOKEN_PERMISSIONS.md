# Cloudflare API Token Permissions for Zone Creation

## Current Issue

Your Cloudflare API token has:
- ✅ `Zone:Zone:Read` (to read existing zones)
- ❌ Missing `Zone:Zone:Edit` or `Account:Zone:Create` (to create new zones)

## Required Permissions for Terraform Zone Creation

To create zones via Terraform, your API token needs one of these permission combinations:

### Option 1: Zone Edit Permission (Recommended)
**Permission Type**: Zone
**Operation**: Edit
**Zone Resources**: Include all zones (`*`)

This allows:
- Creating new zones
- Editing existing zones
- Managing DNS records
- Modifying zone settings

### Option 2: Account-Level Permissions
**Permission Type**: Account
**Operation**: Zone
**Permissions**: `Account.Zone.Zone:Edit`

This allows zone management at the account level.

## How to Update Your API Token

1. **Go to Cloudflare Dashboard**:
   https://dash.cloudflare.com/profile/api-tokens

2. **Find Your Current Token** (the one with value from `env.sh`):
   `$CLOUDFLARE_API_TOKEN`

3. **Click "Edit"** on the token

4. **Add Permission**:
   - **Permission Type**: Zone
   - **Operation**: Edit
   - **Zone Resources**: Include `*` (all zones)

5. **Or use Account Permissions**:
   - **Permission Type**: Account
   - **Permissions**: 
     - `Account.Zone.Zone:Edit`
     - `Account.Zone.Zone:Read`
     - `Account.Account Settings:Read`

6. **Save Changes**

## After Updating Permissions

Test the updated permissions:

```bash
cd /Users/rlee/dev/infra
source env.sh
cd terraform

docker run --rm -v $(pwd):/app -w /app \
  -e AWS_ACCESS_KEY_ID="$AWS_ACCESS_KEY_ID" \
  -e AWS_SECRET_ACCESS_KEY="$AWS_SECRET_ACCESS_KEY" \
  -e CLOUDFLARE_API_TOKEN="$CLOUDFLARE_API_TOKEN" \
  -e CLOUDFLARE_ACCOUNT_ID="$CLOUDFLARE_ACCOUNT_ID" \
  callableapis:infra terraform apply -target=cloudflare_zone.godaddy_domains
```

This should now be able to create the zones without errors.

## Alternative: Use Cloudflare API with API Key

If updating permissions is not possible, you could:
1. Generate a new token with full permissions
2. Update the token in `env.sh`
3. Retry the Terraform apply

## Recommended Permissions for Full DNS Management

For complete zone and DNS management via Terraform, use:

**Zone Permissions**:
- `Zone:Zone:Read` ✅ (you have this)
- `Zone:Zone:Edit` ❌ (add this)
- `Zone:DNS:Edit` (for DNS records)
- `Zone:Zone Settings:Edit` (for zone settings)

**Account Permissions** (Optional):
- `Account:Account Settings:Read`
- `Account.Account:Read`

This gives you full control over zones and DNS via Terraform.

