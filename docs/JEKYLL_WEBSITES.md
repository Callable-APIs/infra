# Jekyll Websites Documentation

This document explains how to deploy Jekyll-based blogs for all GoDaddy domains using Cloudflare Pages.

## Overview

We manage multiple Jekyll sites from a single repository, with each site configured to build independently for Cloudflare Pages.

## Repository Structure

```
docs/jekyll-multisite/
├── sites/
│   ├── cocoonspamini/      # Individual sites
│   ├── glassbubble/
│   ├── iheartdinos/
│   └── ...
├── shared/
│   └── _layouts/           # Shared layouts
├── Gemfile                 # Ruby dependencies
└── build.sh                # Build script
```

## Setup Steps

### 1. Create GitHub Repository

Create a new repository for the Jekyll multisite:
- Name: `jekyll-websites` (or similar)
- Public or Private
- Don't initialize with README

### 2. Copy Files

Copy `docs/jekyll-multisite/` to your new repository:

```bash
# From this infra repo
cp -r docs/jekyll-multisite/* ~/jekyll-websites/
cd ~/jekyll-websites
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR_USERNAME/jekyll-websites.git
git push -u origin main
```

### 3. Configure Cloudflare Pages (Dashboard Only)

**Note**: Terraform created the Pages projects, but Git integration must be configured in the dashboard.

For each of the 9 Pages projects:

1. Go to [Cloudflare Dashboard → Pages](https://dash.cloudflare.com/)
2. Click on a project (e.g., "cocoonspamini")
3. Click **"Connect to Git"**
4. Authorize GitHub
5. Select your `jekyll-websites` repository
6. Configure build settings:
   - **Build command**: `bundle install && cd sites/cocoonspamini && bundle exec jekyll build`
   - **Build output**: `../../_site/cocoonspamini`
   - **Root directory**: (empty)

### 4. Deploy

Push changes to trigger automatic deployment:

```bash
git add .
git commit -m "Update content"
git push origin main
```

Cloudflare Pages will build and deploy automatically.

## Why Not Terraform for Git Integration?

Cloudflare Pages' Git integration requires OAuth with GitHub, which is:
- Interactive by nature (requires browser authentication)
- Difficult to automate with Terraform
- Safer to do manually in the dashboard

**What Terraform does**:
- ✅ Creates Pages permissions projects
- ✅ Configures custom domains
- ✅ Sets up DNS records
- ❌ Cannot connect GitHub (requires manual setup)

**What the Dashboard does**:
- ✅ Connects GitHub via OAuth
- ✅ Configures build settings
- ✅ Manages deployments

## Adding Content

1. Edit files in `sites/DOMAIN_NAME/`
2. Commit and push
3. Cloudflare Pages builds and deploys automatically
4. Site goes live within 1-2 minutes

## Custom Domains

Already configured via Terraform! Each domain points to its Pages project:
- cocoonspamini.com ↔ cocoonspamini Pages project
- glassbubble.net ↔ glassbubble Pages project
- etc.

## Troubleshooting

### Build Fails
- Check build logs in Cloudflare Dashboard
- Verify Gemfile has correct dependencies
- Ensure build command paths are correct

### Domain Not Resolving
- Check DNS records in Cloudflare dashboard
- Verify Pages project has custom domain configured
- May take up to 24 hours for DNS propagation

## Resources

- [Jekyll Documentation](https://jekyllrb.com/docs/)
- [Cloudflare Pages Documentation](https://developers.cloudflare.com/pages/)
- [Terraform Cloudflare Provider](https://registry.terraform.io/providers/cloudflare/cloudflare/latest/docs/resources/pages_project)

