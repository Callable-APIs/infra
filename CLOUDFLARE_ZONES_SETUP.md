# Cloudflare Zones Setup for GoDaddy Domains

## Current Status

❌ **Cannot create zones via Terraform** - API token lacks zone creation permissions
✅ **Solution**: Add domains via Cloudflare web console, then import into Terraform

## Required Manual Steps

### Step 1: Add Each Domain to Cloudflare

Go to https://dash.cloudflare.com and add each domain:

1. Click "Add a Site"
2. Enter domain name (e.g., `cocoonspamini.com`)
3. Choose "Free" plan
4. Continue through setup
5. Accept that DNS records need to be configured

**Do this for all 9 domains:**
1. cocoonspamini.com
2. glassbubble.net
3. iheartdinos.com
4. jughunt.com
5. lipbalmjunkie.com
6. ohsorad.com
7. rosamimosa.com
8. taicho.com
9. tokyo3.com

### Step 2: Note the Nameservers

For each domain, Cloudflare will show you nameservers like:
- `alice.ns.cloudflare.com`
- `bob.ns.cloudflare.com`

**Save these for each domain** - you'll need to update them in GoDaddy.

### Step 3: Import Zones into Terraform

Once domains are added via web console, import them into Terraform:

```bash
cd /Users/rlee/dev/infra/terraform

# For each domain, run:
terraform import cloudflare_zone.godaddy_domains["cocoonspamini"] cocoonspamini.com
terraform import cloudflare_zone.godaddy_domains["glassbubble"] glassbubble.net
terraform import cloudflare_zone.godaddy_domains["iheartdinos"] iheartdinos.com
terraform import cloudflare_zone.godaddy_domains["jughunt"] jughunt.com
terraform import cloudflare_zone.godaddy_domains["lipbalmjunkie"] lipbalmjunkie.com
terraform import cloudflare_zone.godaddy_domains["ohsorad"] ohsorad.com
terraform import cloudflare_zone.godaddy_domains["rosamimosa"] rosamimosa.com
terraform import cloudflare_zone.godaddy_domains["taicho"] taicho.com
terraform import cloudflare_zone.godaddy_domains["tokyo3"] tokyo3.com
```

### Step 4: After Import, Run Terraform Apply

After importing, run:

```bash
docker run --rm -v $(pwd):/app -w /app \
  -e AWS_ACCESS_KEY_ID="$AWS_ACCESS_KEY_ID" \
  -e AWS_SECRET_ACCESS_KEY="$AWS_SECRET_ACCESS_KEY" \
  -e CLOUDFLARE_API_TOKEN="$CLOUDFLARE_API_TOKEN" \
  -e CLOUDFLARE_ACCOUNT_ID="$CLOUDFLARE_ACCOUNT_ID" \
  callableapis:infra terraform apply
```

This will sync Terraform state with the existing zones.

## Alternative: Update Cloudflare API Token Permissions

If you have admin access to Cloudflare account:

1. Go to https://dash.cloudflare.com/profile/api-tokens
2. Find your API token
3. Add permission: `Zone:Zone:Edit` and `Zone:Zone:Read`
4. Add permission: `Account:Account Settings:Read`
5. Save and retry Terraform apply

## Next Steps After Zones Are Created

1. **Get current DNS records** from GoDaddy for each domain
2. **Create Terraform configs** for the DNS records
3. **Import DNS records** into Terraform
4. **Update nameservers** in GoDaddy to point to Cloudflare

## Summary

- ✅ Terraform configuration is ready
- ❌ API token needs zone creation permission OR use web console
- ✅ After adding domains via web console, import works perfectly
- ✅ Then everything can be managed via Terraform

