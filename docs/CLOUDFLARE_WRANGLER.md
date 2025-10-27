# Cloudflare Wrangler CLI for Pages Deployment

Wrangler CLI is now available in the Docker container for managing Cloudflare Pages deployments.

## Installation

Wrangler is included in the `callableapis:infra` Docker image.

## Limitations

**Important**: Wrangler **cannot** fully automate the GitHub connection setup for Pages projects. This must be done manually via the dashboard for security reasons.

**What Wrangler CAN do**:
- ✅ Deploy sites manually (`wrangler pages publish`)
- ✅ List projects (`wrangler pages project list`)
- ✅ Create projects (`wrangler pages project create`)
- ❌ Connect GitHub repositories (requires OAuth in dashboard)

**What Wrangler CANNOT do**:
- ❌ Connect GitHub via CLI
- ❌ Configure Git-based deployments
- ❌ Set up build settings

## Usage in Docker

```bash
# Run Wrangler commands in the Docker container
docker run --rm -v $(pwd):/app -w /app callableapis:infra wrangler pages project list

# Authenticate (requires browser)
docker run --rm -it -v $(pwd):/app -w /app call pointer.inf

# Deploy a site
docker run --rm -v $(pwd):/app -w /app callableapis:infra wrangler pages publish _site --project-name=cocoonspamini
```

## Recommended Approach

1. **Terraform**: Create Pages projects and configure domains
2. **Dashboard**: Connect GitHub repositories (one-time manual step)
3. **Git Push**: Automatically triggers Cloudflare Pages builds

This hybrid approach gives you:
- Infrastructure as code (Terraform)
- Secure GitHub integration (Dashboard OAuth)
- Automatic deployments (Git push)

## Alternative: Manual Wrangler Deployments

If you want to deploy manually without Git integration:

```bash
# Build Jekyll site
cd docs/jekyll-multisite/sites/cocoonspamini
bundle exec jekyll build

# Deploy to Pages
wrangler pages publish _site --project-name=cocoonspamini
```

This bypasses Git integration but requires manual deployments for each change.

