# Jekyll Blog Template for Cloudflare Pages

This is a template Jekyll blog that can be deployed to Cloudflare Pages.

## Features

- Clean, modern blog layout
- RSS feed support
- SEO tags
- Sitemap generation
- Mobile responsive design
- Markdown support for posts

## Setup Instructions

1. **Copy this template** to create a repository for your domain
2. **Customize the configuration**:
   - Edit `_config.yml` with your site information
   - Customize layouts in `_layouts/`
   - Add your own posts to `_posts/`

3. **Deploy to Cloudflare Pages**:
   - Connect your GitHub repository to Cloudflare Pages
   - Set build command: `bundle exec jekyll build`
   - Set output directory: `_site`
   - Configure custom domain in Cloudflare dashboard

## Local Development

```bash
# Install dependencies
bundle install

# Start local server
bundle exec jekyll serve

# Visit http://localhost:4000
```

## Configuration

Update these files for your domain:
- `_config.yml` - Site configuration, title, description, URL
- `_layouts/default.html` - Customize the site layout
- `_posts/*` - Add your blog posts

## Adding Posts

Create new files in `_posts/` with the format:
```
YYYY-MM-DD-post-title.md
```

Example front matter:
```yaml
---
layout: post
title: "My Post Title"
date: 2025-10-27
---
```

## Deployment

Once connected to Cloudflare Pages, your site will automatically deploy on:
- Push to main branch (production)
- Pull requests (preview deployments)

