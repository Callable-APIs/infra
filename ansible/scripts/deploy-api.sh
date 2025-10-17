#!/bin/bash

# CallableAPIs API Deployment Script
# Simple deployment using local artifacts

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ANSIBLE_DIR="$(dirname "$SCRIPT_DIR")"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if ansible-playbook is available
if ! command -v ansible-playbook &> /dev/null; then
    echo -e "${RED}Error: ansible-playbook is not installed${NC}"
    echo "Install with: pip install ansible"
    exit 1
fi

# Check if production inventory exists
if [ ! -f "$ANSIBLE_DIR/inventory/production" ]; then
    echo -e "${RED}Error: Production inventory not found${NC}"
    echo "Run: ansible/scripts/setup-inventory.sh first"
    exit 1
fi

# Check if artifacts exist
if [ ! -f "$ANSIBLE_DIR/artifacts/vault-password" ] || [ ! -f "$ANSIBLE_DIR/artifacts/secrets.yml" ]; then
    echo -e "${RED}Error: Secrets artifacts not found${NC}"
    echo "Run: ansible/scripts/build-secrets.sh first"
    exit 1
fi

echo -e "${BLUE}CallableAPIs API Deployment${NC}"
echo "============================="

# Deploy secrets
echo -e "${YELLOW}Deploying secrets...${NC}"
ansible-playbook -i inventory/production playbooks/deploy-secrets-simple.yml

# Deploy container
echo -e "${YELLOW}Deploying container...${NC}"
ansible-playbook -i inventory/production playbooks/api-deploy-simple.yml

echo -e "${GREEN}Deployment complete!${NC}"
echo ""
echo "Test endpoints:"
echo "  - Health: http://onode1.callableapis.com:8080/health"
echo "  - Status: http://onode1.callableapis.com:8080/api/status"
