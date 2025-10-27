# Jekyll Multisite Repository

This repository contains multiple Jekyll sites for different domains, all managed in one place.

## Directory Structure

```
jekyll-multisite/
├── sites/           # Individual site directories
│   ├── cocoonspamini/
│   ├── glassbubble/
│   ├── iheartdinos/
│   └── ...
├── shared/          # Shared layouts and assets
│   └── _layouts/
├── Gemfile         # Ruby dependencies
├── build.sh        # Build script for all sites
└── README.md       # This file
```

## Setup

```bash
# Install dependencies
bundle install

# Build all sites
./build.sh
```

## Adding a New Site

1. Create a new directory in `sites/` with your domain name
2. Create a `_config.yml` file with site-specific settings
3. Set the `destination` to `../_site/yourdomain/` 
4. Copy layouts from `shared/_layouts/` if needed
5. Add content (posts, pages, etc.)

## Site Configuration

Each site has its own `_config.yml` with:
- Site title, description, URL
- Author information
- Build destination (output directory)
- Jekyll plugins

## Build Output

All sites build to the `_site/` directory:
- `_site/cocoonspamini/`
- `_site/glassbubble/`
- `_site/iheartdinos/`
- etc.

## Cloudflare Pages Setup

In Cloudflare Pages, configure each project with:
- **Build command**: `cd sites/yourdomain && bundle exec jekyll build`
- **Build output**: `../_site/yourdomain/`
- **Root directory**: Leave empty or set to repository root

Alternatively, use the build script:
- **Build command**: `./build.sh`
- **Build output**: `sites/yourdomain/_site/` (update accordingly)

## Local Development

To test a specific site locally:

```bash
cd sites/cocoonspamini
bundle exec jekyll serve
# Visit http://localhost:4000
```

## Shared Assets

Common layouts and assets are in the `shared/` directory and can be copied to individual sites as needed.

