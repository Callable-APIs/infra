# Cloudflare Pages Setup - Next Steps

## ✅ What's Done
- Created 9 Cloudflare Pages projects
- Configured custom domains for each domain
- Created DNS records pointing to Pages

## 📝 Next Steps

### 1. Create GitHub Repositories
For each domain, create a new repository and copy the Jekyll template:

```bash
# For each domain (e.g., cocoonspamini, glassbubble, etc.)
# Create a new GitHub repository
# Copy pages-jekyll-template/ to that repository
# Customize _config.yml with domain-specific information
```

### 2. Connect to Cloudflare Pages
For each Pages project:
1. Go to Cloudflare Dashboard → Pages
2. Select the project (e.g., "cocoonspamini")
3. Click "Connect to Git"
4. Select your GitHub repository
5. Configure build settings:
   - Build command: `bundle exec jekyll build`
   - Build output directory: `_site`
   - Root directory: `/`

### 3. Customize Each Site
For each domain:
- Edit `_config.yml`:
  - Update `title`, `description`, `url`
  - Update `author` information
- Customize layouts and styling as needed
- Add blog posts to `_posts/`

### 4. Access Your Sites
Once deployed:
- Production: https://yourdomain.com (via custom domain)
- Production preview: https://yourproject.pages.dev
- Branch previews: Available for each branch/PR

## 📚 Domains and Projects

| Domain | Pages Project | .pages.dev URL |
|--------|--------------|----------------|
| cocoonspamini.com | cocoonspamini | https://cocoonspamini.pages.dev |
| glassbubble.net | glassbubble | https://glassbubble.pages.dev |
| iheartdinos.com | iheartdinos | https://iheartdinos.pages.dev |
| jughunt.com | jughunt | https://jughunt.pages.dev |
| lipbalmjunkie.com | lipbalmjunkie | https://lipbalmjunkie.pages.dev |
| ohsorad.com | ohsorad | https://ohsorad.pages.dev |
| rosamimosa.com | rosamimosa | https://rosamimosa.pages.dev |
| taicho.com | taicho | https://taicho.pages.dev |
| tokyo3.com | tokyo3 | https://tokyo3.pages.dev |

## 🔧 Build Configuration
- **Build Command**: `bundle exec jekyll build`
- **Output Directory**: `_site`
- **Environment Variables**: None required for basic setup

## 📦 Dependencies
The `Gemfile` includes:
- jekyll (~> 4.3)
- jekyll-feed (RSS feed)
- jekyll-sitemap (SEO)
- jekyll-seo-tag (SEO)

