# GoDaddy to Cloudflare Migration - Current Status

## Summary

✅ **Terraform configuration ready** for 9 domains
❌ **API token lacks zone creation permissions**
✅ **Solution**: Add domains via Cloudflare web console, then import

## Your 9 Domains

1. cocoonspamini.com
2. glassbubble.net
3. iheartdinos.com
4. jughunt.com
5. lipbalmjunkie.com
6. ohsorad.com
7. rosamimosa.com
8. taicho.com
9. tokyo3.com

## What I've Prepared

### 1. Terraform Configuration
- `terraform/cloudflare-godaddy-domains.tf` - Zone creation config
- Variables with default empty values (no GoDaddy API needed)
- Import script ready

### 2. Documentation
- `CLOUDFLARE_ZONES_SETUP.md` - Step-by-step setup guide
- `GODADDY_TO_CLOUDFLARE_MIGRATION.md` - Full migration process
- `import_cloudflare_zones.sh` - Automated import script

### 3. Import Script
- Ready to run after you add domains via web console
- Will import all 9 domains into Terraform state

## What You Need to Do

### Step 1: Add Domains to Cloudflare (5 minutes)
1. Go to https://dash.cloudflare.com
2. For each of the 9 domains:
   - Click "Add a Site"
   - Enter domain name
   - Choose "Free" plan
   - Continue through setup
3. Note the nameservers for each domain

### Step 2: Run Import Script
```bash
cd /Users/rlee/dev/infra
./import_cloudflare_zones.sh
```

This will import all domains into Terraform.

### Step 3: Apply Configuration
```bash
cd terraform
source ../env.sh
docker run --rm -v $(pwd):/app -w /app \
  -e AWS_ACCESS_KEY_ID="$AWS_ACCESS_KEY_ID" \
  -e AWS_SECRET_ACCESS_KEY="$AWS_SECRET_ACCESS_KEY" \
  -e CLOUDFLARE_API_TOKEN="$CLOUDFLARE_API_TOKEN" \
  -e CLOUDFLARE_ACCOUNT_ID="$CLOUDFLARE_ACCOUNT_ID" \
  callableapis:infra terraform apply
```

### Step 4: Update Nameservers in GoDaddy
For each domain, update nameservers in GoDaddy to point to Cloudflare.

### Step 5: Add DNS Records
Once domains are in Cloudflare and nameservers are updated:
1. Get current DNS records from GoDaddy
2. I'll help create Terraform configs for the DNS records
3. Add them via Terraform

## Alternative: Update API Token

If you can update Cloudflare API token permissions:
1. Go to https://dash.cloudflare.com/profile/api-tokens
2. Edit your token
3. Add permissions: `Zone:Zone:Edit`, `Zone:Zone:Read`, `Account:Account Settings:Read`
4. Then we can create zones directly via Terraform

## Benefits After Migration

- ✅ All DNS managed via Terraform
- ✅ Infrastructure as Code for DNS records
- ✅ Free SSL certificates
- ✅ Better DNS performance
- ✅ Can use Cloudflare Pages for free hosting
- ✅ No more GoDaddy API issues

## Current Status

| Task | Status | Notes |
|------|--------|-------|
| Parse domains | ✅ Done | All 9 domains extracted |
| Terraform config | ✅ Done | Zones and imports ready |
| API zone creation | ❌ Blocked | Need web console or token update |
| Import script | ✅ Done | Ready to run |
| Documentation | ✅ Done | All guides created |

## Next Action

**Add the 9 domains to Cloudflare via web console**, then we can run the import script and proceed with DNS setup.

