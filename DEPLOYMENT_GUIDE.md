# Complete Deployment Guide: Jekyll Multisite to Cloudflare Pages

## Overview

Cloudflare Pages **automatically builds and publishes** your Jekyll sites. You don't need to manually build or publish - just push to GitHub and Pages handles the rest.

## Step-by-Step Process

### 1. Create the GitHub Repository

```bash
# Option A: Create new repo manually on GitHub
# - Go to https://github.com/new
# - Name it: jekyll-multisite (or any name you prefer)
# - Make it public or private
# - Don't initialize with README

# Option B: Using GitHub CLI
gh repo create jekyll-multisite --public
```

### 2. Copy Jekyll Multisite Code to New Repo

```bash
# Clone the infra repo (if not already)
cd /tmp
git clone https://github.com/Callable-APIs/infra.git

# Copy the jekyll-multisite directory contents
cd infra
cp -r jekyll-multisite/* /path/to/new/jekyll-multisite-repo/

# Or create a new directory and copy
mkdir ~/jekyll-multisite
cp -r jekyll-multisite/* ~/jekyll-multisite/
cd ~/jekyll-multisite

# Initialize git
git init
git add .
git commit -m "Initial commit: Jekyll multisite structure"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/jekyll-multisite.git
git push -u origin main
```

### 3. Connect Cloudflare Pages to GitHub Repository

For **each** of the 9 Pages projects we created:

1. Go to Cloudflare Dashboard → Pages
2. Click on a project (e.g., "cocoonspamini")
3. Click **"Connect to Git"** button
4. Select **GitHub** and authorize Cloudflare
5. Select your `jekyll-multisite` repository
6. Configure build settings (see below)

### 4. Configure Build Settings for Each Site

For **cocoonspamini**:
- **Build command**: `bundle install && cd sites/cocoonspamini && bundle exec jekyll build`
- **Build output directory**: `../../_site/cocoonspamini`
- **Root directory**: (leave empty)

For **glassbubble**:
- **Build command**: `bundle install && cd sites/glassbubble && bundle exec jekyll build`
- **Build output directory**: `../../_site/glassbubble`
- **Root directory**: (leave empty)

Repeat for all 9 domains with their respective directory names.

### 5. Push and Deploy

```bash
# Make changes to your sites
cd ~/jekyll-multisite
echo "New content" >> sites/cocoonspamini/index.html

# Commit and push
git add .
git commit -m "Update content"
git push origin main
```

**That's it!** Cloudflare Pages will:
1. Detect the push to `main` branch
2. Run the build command
3. Build the Jekyll site
4. Publish it to the custom domain (e.g., cocoonspamini.com)
5. Make it live automatically

## How Publishing Works

Cloudflare Pages handles everything automatically:

```
You Push to GitHub
    ↓
Cloudflare Pages detects the push
    ↓
Runs your build command (bundle install && jekyll build)
    ↓
Generates static HTML in _site/
    ↓
Deploys to Cloudflare CDN
    ↓
Site is live at yourdomain.com
```

## No Manual Publishing Needed!

- ✅ **No `jekyll build` needed locally** - Cloudflare builds it
- ✅ **No upload needed** - Cloudflare handles deployment
- ✅ **Automatic deployments** - Every push to main triggers a new deploy
- ✅ **Preview deployments** - PRs get preview URLs automatically
- ✅ **Instant CDN** - Sites are served from Cloudflare's global network

## Agent Workflow

When you have an agent help build the sites:

1. Agent creates content in `sites/DOMAIN_NAME/`
2. Agent commits and pushes to GitHub
3. Cloudflare Pages automatically builds and publishes
4. Site goes live within 1-2 minutes

The agent only needs to create the content - Cloudflare handles the rest.

## Verification

After pushing, check:
- Build status: Cloudflare Dashboard → Pages → Your Project → Deployments
- Live site: Visit your custom domain (e.g., https://cocoonspamini.com)
- Preview URL: https://cocoonspamini.pages.dev

## Custom Domains

Already configured! Each domain automatically points to its Pages project:
- cocoonspamini.com → cocoonspamini Pages project
- glassbubble.net → glassbubble Pages project
- etc.

You don't need to configure DNS - we already did that with Terraform.

## Summary

**Old way (what you thought)**:
1. Build locally ✅
2. Upload files ❌
3. Configure server ❌

**New way (Cloudflare Pages)**:
1. Push to GitHub ✅
2. That's it! 🎉

Cloudflare Pages = GitHub Actions + Static Site Hosting + CDN, all in one service.

