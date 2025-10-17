#!/bin/bash

# CallableAPIs Secrets Builder
# Builds encrypted secrets locally and stores in artifacts directory

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ANSIBLE_DIR="$(dirname "$SCRIPT_DIR")"
ARTIFACTS_DIR="$ANSIBLE_DIR/artifacts"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if ansible-vault is available
if ! command -v ansible-vault &> /dev/null; then
    echo -e "${RED}Error: ansible-vault is not installed${NC}"
    echo "Install with: pip install ansible"
    exit 1
fi

# Create artifacts directory
mkdir -p "$ARTIFACTS_DIR"

echo -e "${BLUE}CallableAPIs Secrets Builder${NC}"
echo "==============================="

# Prompt for GitHub OIDC credentials only
echo -e "${YELLOW}Enter GitHub OIDC credentials (only secrets deployed to containers):${NC}"
read -p "GitHub Client ID: " GITHUB_CLIENT_ID
read -p "GitHub Client Secret: " GITHUB_CLIENT_SECRET
read -p "GitHub Redirect URI [https://api.callableapis.com/api/auth/callback]: " GITHUB_REDIRECT_URI
GITHUB_REDIRECT_URI=${GITHUB_REDIRECT_URI:-"https://api.callableapis.com/api/auth/callback"}

echo -e "${BLUE}Note: All other credentials (AWS, Cloudflare, Oracle, Google, IBM) are managed locally in env.sh${NC}"

# Generate vault password
echo -e "${BLUE}Generating vault password...${NC}"
VAULT_PASSWORD=$(openssl rand -base64 32)
echo "$VAULT_PASSWORD" > "$ARTIFACTS_DIR/vault-password"

# Create secrets file
echo -e "${BLUE}Creating secrets file...${NC}"
cat > "$ARTIFACTS_DIR/secrets.yml" << EOF
# CallableAPIs Infrastructure Secrets
# Generated on $(date)
# Only GitHub OIDC secrets are deployed to containers
# All other credentials are managed locally in env.sh

# GitHub OIDC Configuration
vault_github_client_id: "$GITHUB_CLIENT_ID"
vault_github_client_secret: "$GITHUB_CLIENT_SECRET"
vault_github_redirect_uri: "$GITHUB_REDIRECT_URI"
EOF

# Encrypt secrets file
echo -e "${BLUE}Encrypting secrets file...${NC}"
ansible-vault encrypt "$ARTIFACTS_DIR/secrets.yml" --vault-password-file "$ARTIFACTS_DIR/vault-password"

# Generate checksums
echo -e "${BLUE}Generating checksums...${NC}"
cd "$ARTIFACTS_DIR"
sha256sum vault-password > vault-password.sha256
sha256sum secrets.yml > secrets.yml.sha256

# Display summary
echo -e "${GREEN}Secrets built successfully!${NC}"
echo ""
echo "Files created in $ARTIFACTS_DIR:"
echo "  - vault-password (vault password file)"
echo "  - secrets.yml (encrypted secrets)"
echo "  - vault-password.sha256 (checksum)"
echo "  - secrets.yml.sha256 (checksum)"
echo ""
echo "Next steps:"
echo "  1. Deploy secrets: ansible-playbook -i inventory/production playbooks/deploy-secrets.yml"
echo "  2. Deploy container: ansible-playbook -i inventory/production playbooks/api-deploy.yml"
