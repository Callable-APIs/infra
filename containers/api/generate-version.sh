#!/bin/bash

# Generate container version file
# This script creates /etc/CONTAINER_VERSION with repo/githash format

set -e

# Get repository name from GitHub context
REPO_NAME="${GITHUB_REPOSITORY:-unknown/unknown}"

# Get git hash
GIT_HASH="${GITHUB_SHA:-unknown}"

# Create version string
VERSION="${REPO_NAME}/${GIT_HASH}"

# Write to container version file
echo "$VERSION" > /etc/CONTAINER_VERSION

echo "Container version: $VERSION"
