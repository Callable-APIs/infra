# GoDaddy to Cloudflare Migration Guide

## Overview

This guide will help you migrate your 9 domains from GoDaddy DNS to Cloudflare DNS, enabling Terraform management.

## Your Domains

1. cocoonspamini.com
2. glassbubble.net
3. iheartdinos.com
4. jughunt.com
5. lipbalmjunkie.com
6. ohsorad.com
7. rosamimosa.com
8. taicho.com
9. tokyo3.com

## Migration Steps

### Step 1: Add Domains to Cloudflare

Each domain needs to be added to your Cloudflare account first.

**Option A: Via Cloudflare Web Console (Easiest)**
1. Go to https://dash.cloudflare.com
2. Click "Add a Site"
3. Enter domain name
4. Cloudflare will detect DNS records automatically
5. Choose Free plan
6. Update nameservers shown

**Option B: Via Terraform (Automated)**
```bash
cd terraform
source ../env.sh
docker run --rm -v $(pwd):/app -w /app \
  -e AWS_ACCESS_KEY_ID="$AWS_ACCESS_KEY_ID" \
  -e AWS_SECRET_ACCESS_KEY="$AWS_SECRET_ACCESS_KEY" \
  -e CLOUDFLARE_API_TOKEN="$CLOUDFLARE_API_TOKEN" \
  -e CLOUDFLARE_ACCOUNT_ID="$CLOUDFLARE_ACCOUNT_ID" \
  callableapis:infra terraform apply -target=cloudflare_zone.godaddy_domains
```

### Step 2: Get Current DNS Records from GoDaddy

For each domain, get the current DNS records:

1. Log into GoDaddy
2. Go to DNS Management for each domain
3. Note all DNS records (A, AAAA, CNAME, MX, TXT, etc.)
4. Save them or we can help create Terraform configs for them

### Step 3: Update Nameservers in GoDaddy

After adding domains to Cloudflare, you'll get nameservers like:
- `alice.ns.cloudflare.com`
- `bob.ns.cloudflare.com`

For each domain:
1. In GoDaddy, go to DNS Management
2. Click "Change" next to Nameservers
3. Select "Custom" 
4. Enter the Cloudflare nameservers
5. Save

### Step 4: Import/Create DNS Records in Terraform

Once nameservers are updated in GoDaddy, DNS queries will go to Cloudflare. Then:

1. Add DNS records to Terraform configuration
2. Run `terraform apply` to create them in Cloudflare
3. Or use `terraform import` to import existing records

### Step 5: Verify DNS Propagation

After updating nameservers:
```bash
# Check that DNS is pointing to Cloudflare
dig cocoonspamini.com NS

# Should show Cloudflare nameservers
# Expected output contains "cloudflare.com"
```

## Terraform Configuration

The file `terraform/cloudflare-godaddy-domains.tf` creates:
- Cloudflare zones for all 9 domains
- Outputs the nameservers for each domain

After running `terraform apply`, you'll get the nameservers to configure in GoDaddy.

## Next Steps

1. **Do you want to migrate all domains or start with a few?**
2. **Do you have DNS records for each domain, or should I help you retrieve them?**
3. **Are any domains critical for business?** (We should migrate those carefully)

## Benefits After Migration

- ✅ Manage DNS via Terraform (Infrastructure as Code)
- ✅ Free SSL certificates
- ✅ Better DNS performance
- ✅ Automated DNS management
- ✅ No more GoDaddy API issues

## Important Notes

- **DNS propagation**: Can take 24-48 hours (usually much faster)
- **Downtime**: Minimal - DNS records stay the same, only nameservers change
- **SSL**: Cloudflare will auto-generate SSL certificates
- **Email**: Update MX records if using custom email

## Need Help?

Let me know:
1. Which domains to start with
2. If you need help getting current DNS records
3. Any specific requirements for each domain

