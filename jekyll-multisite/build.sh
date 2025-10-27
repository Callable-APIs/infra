#!/bin/bash

# Build all Jekyll sites in the multisite setup

set -e

SITES_DIR="sites"
SHARED_DIR="shared"

echo "Building all Jekyll sites..."

# Build each site
for site_dir in ${SITES_DIR}/*/; do
    if [ -f "${site_dir}_config.yml" ]; then
        site_name=$(basename "${site_dir}")
        echo "Building ${site_name}..."
        
        # Copy shared layouts to site
        mkdir -p "${site_dir}_layouts"
        cp -r "${SHARED_DIR}/_layouts/"* "${site_dir}_layouts/" 2>/dev/null || true
        
        # Build the site
        cd "${site_dir}"
        bundle exec jekyll build
        cd - > /dev/null
    fi
done

echo "All sites built successfully!"

