#!/bin/bash

# CallableAPIs Inventory Setup Script
# Creates production inventory from template

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ANSIBLE_DIR="$(dirname "$SCRIPT_DIR")"
INVENTORY_DIR="$ANSIBLE_DIR/inventory"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}CallableAPIs Inventory Setup${NC}"
echo "============================="

# Check if production inventory already exists
if [ -f "$INVENTORY_DIR/production" ]; then
    echo -e "${YELLOW}Production inventory already exists.${NC}"
    read -p "Do you want to overwrite it? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Aborted"
        exit 1
    fi
fi

# Copy template to production
echo -e "${BLUE}Creating production inventory from template...${NC}"
cp "$INVENTORY_DIR/production.in" "$INVENTORY_DIR/production"

echo -e "${GREEN}Production inventory created!${NC}"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "1. Edit ansible/inventory/production"
echo "2. Replace placeholder values with your actual IPs:"
echo "   - YOUR_ORACLE_IP"
echo "   - YOUR_GOOGLE_IP" 
echo "   - YOUR_IBM_IP"
echo "   - YOUR_AWS_IP"
echo ""
echo "3. Test connection:"
echo "   ansible all -i inventory/production -m ping"
echo ""
echo -e "${BLUE}Note: The production inventory file is gitignored for security.${NC}"
