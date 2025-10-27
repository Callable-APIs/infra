# Cloudflare Pages Multisite Setup

This document explains how to configure Cloudflare Pages to build individual sites from a monorepo.

## Repository Structure

```
jekyll-multisite/
├── sites/
│   ├── cocoonspamini/      # Site 1
│   ├── glassbubble/        # Site 2
│   ├── iheartdinos/        # Site 3
│   └── ...
├── shared/                 # Shared layouts
└── Gemfile                 # Ruby dependencies
```

## Cloudflare Pages Configuration

### Option 1: Per-Site Builds (Recommended)

For each domain's Pages project, configure:

**Build Settings**:
- **Build command**: `bundle install && cd sites/DOMAIN_NAME && bundle exec jekyll build`
- **Build output directory**: `../../_site/DOMAIN_NAME`
- **Root directory**: (leave empty)

Replace `DOMAIN_NAME` with the actual domain name (e.g., `cocoonspamini`, `glassbubble`)

### Option 2: Build Script

Alternatively, use the build script:

**Build Settings**:
- **Build command**: `bundle install && ./build.sh`
- **Build output directory**: `sites/DOMAIN_NAME/_site` (adjust based on actual output)
- **Root directory**: (leave empty)

## Example Configurations

### cocoonspamini.com
- Build command: `bundle install && cd sites/cocoonspamini && bundle exec jekyll build`
- Build output: `../../_site/cocoonspamini`

### glassbubble.net
- Build command: `bundle install && cd sites/glassbubble && bundle exec jekyll build`
- Build output: `../../_site/glassbubble`

### Repeat for all 9 domains

## Environment Variables

No special environment variables are required for the basic Jekyll setup.

## Deployment Process

1. Connect your GitHub repository to each Pages project
2. Configure the build settings as above
3. Push to the `main` branch to trigger deployments
4. Each site will deploy independently

## Custom Domains

Each Pages project already has its custom domain configured via Terraform:
- cocoonspamini.pages.dev → cocoonspamini.com
- glassbubble.pages.dev → glassbubble.net
- etc.

## Adding a New Site

1. Create new directory in `sites/yourdomain/`
2. Add `_config.yml` with site-specific settings
3. Add content (posts, pages)
4. Create or update Cloudflare Pages project
5. Configure build settings pointing to your domain's subdirectory

