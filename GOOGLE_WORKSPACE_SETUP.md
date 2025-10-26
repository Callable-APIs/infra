# Google Workspace Email Setup for All Domains

## Current Status

✅ **DNS records created** for all 9 domains via Terraform
- MX records pointing to Google Workspace
- SPF records for email authentication
- DMARC records for email security

## What You Need to Do in Google Workspace

### Step 1: Add Domains to Google Workspace

1. Log into Google Workspace Admin Console: https://admin.google.com
2. Go to **Domains** in the left menu
3. Click **Add a domain**
4. For each of your 9 domains:
   - Enter the domain name
   - Select **Add a domain alias of** (if you already have a primary domain)
   - Or **Add another domain** if you want to set up separate email
5. Follow the verification process

### Step 2: Verify Domain Ownership

Google will ask you to verify domain ownership. You have DNS records already in place, so verification should work. Google will check for specific verification TXT records.

**Option A: Add Verification TXT Record via Terraform** (Recommended)
Once you have the verification string from Google, tell me and I'll add it to the Terraform configuration.

**Option B: Add Manually via Cloudflare**
1. Go to Cloudflare dashboard
2. Select your domain
3. Go to DNS > Records
4. Add a TXT record with Google's verification string

### Step 3: After Domain Verification

Once Google verifies the domain, you can:

1. **Create email addresses** for each domain (e.g., admin@domain.com)
2. **Set up routing** to forward to your primary Google account
3. **Enable "catch-all"** to accept any email@domain.com

## Catch-All Email Setup

To accept arbitrary emails like `anything@domain.com`:

1. In Google Workspace Admin Console
2. Go to **Apps > Google Workspace > Gmail > Routing**
3. Under **Routing**, click **Add Another Rule**
4. Set up a catch-all rule that forwards to your primary email

## Required DNS Records (Already in Place)

All domains now have:
- ✅ MX records (5 priorities) pointing to Google
- ✅ SPF record for authentication
- ✅ DMARC record for security

## What Works Automatically

Once domains are verified in Google Workspace, you can:
- Send email FROM any of the domains
- Receive email TO any address at those domains
- Set up custom routing and forwarding
- Use catch-all to accept all emails

## Important Notes

1. **Primary vs Alias**: Decide if these are aliases of an existing domain or separate domains
2. **Business Email**: If you need business features, you may need paid Google Workspace
3. **Free Gmail**: You can use a personal Gmail account if you don't need business features
4. **Email Limits**: Free accounts have lower limits than paid Workspace

## Next Steps

1. Add domains to Google Workspace (web console)
2. Get verification TXT record from Google
3. I'll add the verification record via Terraform
4. Complete verification in Google Workspace
5. Set up email addresses and routing as needed

The DNS records are ready - you just need to verify ownership with Google Workspace!

