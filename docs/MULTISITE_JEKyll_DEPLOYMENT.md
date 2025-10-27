# Multisite Jekyll Deployment from This Repo

This guide explains how to deploy the Jekyll multisite content from **this repository** to Cloudflare Pages.

## Current Setup

✅ **Terraform has already created**:
- 9 Cloudflare Pages projects (cocoonspamini, glassbubble, etc.)
- Custom domains configured
- DNS records set up

❌ **Still needed**:
- Connect this GitHub repo to the Pages projects
- Configure build settings for each site

## Why Manual Connection is Required

Wrangler CLI and Terraform **cannot** connect GitHub repositories to Pages projects because:
- It requires Cloudflare's OAuth authentication with GitHub
- OAuth requires browser-based user authentication
- This security step prevents automation

## Step-by-Step Deployment

### 1. Authenticate Cloudflare with GitHub (One-Time)

1. Go to [Cloudflare Dashboard → My Profile → Integrations](https://dash.cloudflare.com/profile/integrations)
2. Click **"Add"** next to GitHub
3. Authorize Cloudflare to access your repositories
4. Select the repositories Cloudflare can access

### 2. Connect This Repository to Each Pages Project

For each of the 9 Pages projects:

#### For cocoonspamini:
1. Go to [Cloudflare Dashboard → Pages](https://dash.cloudflare.com/)
2. Click on **"cocoonspamini"** project
3. Click **"Connect to Git"**
4. Select **GitHub** and authorize
5. Select repository: **Callable-APIs/infra**
6. Click **"Begin setup"**
7. Configure build settings:
   - **Framework preset**: Jekyll
   - **Root directory**: `docs/jekyll-multisite/sites/cocoonspamini`
   - **Build command**: (leave empty, Jekyll preset handles it)
   - **Build output directory**: `_site`
   - **Production branch**: `main`
8. Click **"Save and Deploy"**

#### Repeat for all 9 projects:
- glassb❷: `docs/jekyll-multisite/sites/glassbubble`
- iheartdinos: `docs/jekyll-multisite/sites/iheartdinos`
- jughunt: `docs/jekyll-multisite/sites/jughunt`
- lipbalmjunkie: `docs/jekyll-multisite/sites/lipbalmjunkie`
- ohsorad: `docs/jekyll-multisite/sites/ohsorad`
- rosamimosa: `docs/jekyll-multisite/sites/rosamimosa`
- taicho: `docs/jekyll-multisite/sites/taicho`
- tokyo3: `docs/jekyll-multisite/sites/tokyo3`

### 3. Build Settings

For each project, you need to configure:
- **Root directory** points to the site's subdirectory
- **Build output** is `_site` (Jekyll default)
- **Framework preset** is Jekyll

### 4. Deploy

Once connected:
1. Push changes to this repo
2. Each Pages project will detect the push
3. Cloudflare will build only the relevant subdirectory
4. Site deploys automatically within 1-2 minutes

## Adding More Sites

When you're ready to add content for each domain:

1. Create directory: `docs/jekyll-multisite/sites/DOMAIN_NAME/`
2. Add `_config.yml` (copy from cocoonspamini example)
3. Add content (posts, pages, etc.)
4. Commit and push
5. Site automatically builds and deploys

## Alternative: Manual Wrangler Deployment

If you don't want Git integration, you can deploy manually with Wrangler:

```bash
# Build the site
cd docs/jekyll-multisite/sites/cocoonspamini
bundle exec jekyll build

# Deploy to Pages
docker run --rm -v $(pwd):/app -w /app \
  -e CLOUDFLARE_API_TOKEN="$CLOUDFLARE_API_TOKEN" \
  callableapis:infra wrangler pages publish _site --project-name=cocoonspamini
```

But this requires manual deployments for every change.

## Summary

**Terraform** = Infrastructure (projects, domains, DNS)
**Dashboard** = Git connection (one-time manual setup)
**Git Push** = Automatic deployments (forever after)

This is the recommended approach and only requires ~10 minutes of manual setup once.

