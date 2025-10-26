# Free Tier Resources Analysis

## Current Free Tier Usage

### Oracle Cloud (Always Free Tier)
- ✅ **2x ARM Instances** (VM.Standard.A1.Flex): Currently fully utilized
  - `oci_core_instance.callableapis_arm_1` - 4 OCPU, 24GB RAM
  - `oci_core_instance.callableapis_arm_2` - 4 OCPU, 24GB RAM
- ✅ **Networking**: VCN, subnet, internet gateway (all free)
- ⚠️ **Data Transfer**: 10TB/month free
- 📊 **Status**: Fully optimized for free tier

### Google Cloud (Always Free Tier)
- ✅ **1x e2-micro instance** (1 vCPU, 1GB RAM): Currently utilized
  - `google_compute_instance.callableapis_e2_micro`
- ⚠️ **f1-micro availability**: Should switch from e2 to f1-micro to maximize free tier
  - e2-micro has limitations (would incur small charges)
  - f1-micro is fully within free tier with sustained usage discount
- 📊 **Status**: Should migrate to f1-micro instance

### IBM Cloud (Lite Tier)
- ✅ **1x Virtual Server Instance** (1 vCPU, 2GB RAM): Currently utilized
  - `ibm_is_instance.callableapis_vsi`
- ⚠️ **Always Free tier**: Should verify if we qualify
  - VSI instances may incur minimal charges
  - Consider VPC vs Classic infrastructure
- 📊 **Status**: Should verify free tier eligibility

### AWS (Currently Free Tier)
- ❌ **No compute instances** currently
- ✅ **S3 buckets**: Public website hosting (free tier)
- ⚠️ **Elastic Beanstalk**: Could deploy static sites for free
- 📊 **Status**: Underutilized - could add more resources

## Recommended Free Tier Optimizations

### 1. Google Cloud - Migrate to f1-micro
**Current**: e2-micro instance
**Recommended**: f1-micro instance
- Fully within free tier
- Better for non-compute-intensive workloads
- Sustained use discount makes it effectively free

### 2. AWS - Add More Resources
**Current**: S3 buckets only
**Recommended**:
- CloudFront distributions (free tier)
- Lambda functions (1M requests/month free)
- API Gateway (1M API calls/month free)
- Could host static websites via S3 + CloudFront

### 3. IBM Cloud - Verify Free Tier
**Current**: VSI instance
**Recommended**:
- Check if we qualify for Lite tier (always free)
- Verify resource usage against free tier limits
- Consider using Lite tier resource quotas

### 4. GoDaddy Domains - Cloudflare Pages Migration
**Current**: Domains managed in GoDaddy
**Recommended**: Migrate to Cloudflare Pages
- Cloudflare Pages: Free tier (unlimited sites)
- Cloudflare DNS: Free with all domains
- Cloudflare SSL: Free automatic SSL
- No hosting costs for static sites

## Cloudflare Pages Migration Strategy

### Benefits of Cloudflare Pages
1. **Free Tier**: Unlimited sites, unlimited bandwidth
2. **Static Site Hosting**: Perfect for GoDaddy websites
3. **Git Integration**: Automatic deployments from Git
4. **Global CDN**: Built-in performance optimization
5. **Automatic SSL**: Free SSL certificates
6. **Custom Domains**: Easy DNS management

### Migration Process
1. **Connect GitHub Repository**: Link GoDaddy site repos to Cloudflare Pages
2. **Update DNS**: Point GoDaddy domains to Cloudflare Pages
3. **Deploy Sites**: Automatic deployments on git push
4. **Custom Domain Setup**: Use Cloudflare for DNS management

### Implementation with Terraform
```hcl
# Cloudflare Pages project
resource "cloudflare_pages_project" "godaddy_site" {
  account_id = var.cloudflare_account_id
  name       = "godaddy-site"
  
  build_config {
    build_command  = "npm run build"
    destination_dir = "dist"
  }
  
  source {
    type = "github"
    config {
      owner      = "Callable-APIs"
      repo_name  = "godaddy-site"
      branch     = "main"
    }
  }
}

# Cloudflare DNS record pointing to Pages
resource "cloudflare_record" "godaddy_site" {
  zone_id = data.cloudflare_zone.example.id
  name    = "www"
  type    = "CNAME"
  content = cloudflare_pages_project.godaddy_site.subdomain
  proxied = true
}
```

## Next Steps

1. **Review current instance types** in Google Cloud and switch to f1-micro
2. **Verify IBM Cloud free tier eligibility** and optimize resource usage
3. **Set up Cloudflare Pages** for GoDaddy domain migration
4. **Implement Terraform resources** for Cloudflare Pages projects
5. **Update GoDaddy DNS** to point to Cloudflare Pages

## Free Tier Limits Summary

| Cloud Provider | Service | Free Tier Limit | Current Usage |
|---------------|---------|-----------------|---------------|
| Oracle Cloud | ARM Instances | 2x (4 OCPU, 24GB each) | ✅ Fully utilized |
| Google Cloud | f1-micro | 1 instance | ⚠️ Using e2-micro (should switch) |
| IBM Cloud | VSI | Varies by tier | ⚠️ Need to verify |
| AWS | Lambda | 1M requests/month | ❌ Not utilized |
| AWS | API Gateway | 1M calls/month | ❌ Not utilized |
| Cloudflare | Pages | Unlimited | ❌ Not utilized |
| Cloudflare | Workers | 100k requests/day | ❌ Not utilized |

## Cost Optimization

### Current Monthly Costs (Approximate)
- Oracle Cloud: $0 (always free tier)
- Google Cloud: $0-5 (e2-micro might have minimal charges)
- IBM Cloud: $0-10 (should be free but verify)
- AWS: $0 (S3 static hosting free tier)
- Cloudflare: $0 (free tier)

### Potential Savings
- Migrating GoDaddy sites to Cloudflare Pages: Save hosting costs
- Switching to f1-micro in GCP: Ensure full free tier compliance
- Adding Lambda/API Gateway: No cost if within free tier limits
- Utilizing Cloudflare Workers: Free for low-volume traffic

