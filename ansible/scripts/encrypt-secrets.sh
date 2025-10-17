#!/bin/bash

# CallableAPIs Secrets Management Script
# This script helps manage encrypted secrets for the infrastructure

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ANSIBLE_DIR="$(dirname "$SCRIPT_DIR")"
SECRETS_FILE="$ANSIBLE_DIR/group_vars/secrets.yml"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if ansible-vault is available
if ! command -v ansible-vault &> /dev/null; then
    echo -e "${RED}Error: ansible-vault is not installed${NC}"
    echo "Install with: pip install ansible"
    exit 1
fi

# Function to show usage
show_usage() {
    echo "CallableAPIs Secrets Management"
    echo "==============================="
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  create     - Create encrypted secrets file from template"
    echo "  edit       - Edit encrypted secrets file"
    echo "  view       - View encrypted secrets file"
    echo "  decrypt    - Decrypt secrets file (for backup)"
    echo "  encrypt    - Encrypt secrets file"
    echo "  rotate     - Rotate vault password"
    echo "  backup     - Create encrypted backup of secrets"
    echo ""
    echo "Examples:"
    echo "  $0 create    # First time setup"
    echo "  $0 edit      # Edit secrets"
    echo "  $0 view      # View current secrets"
    echo "  $0 backup    # Create backup"
}

# Function to create secrets file
create_secrets() {
    if [ -f "$SECRETS_FILE" ]; then
        echo -e "${YELLOW}Warning: Secrets file already exists${NC}"
        read -p "Do you want to overwrite it? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            echo "Aborted"
            exit 1
        fi
    fi

    echo "Creating encrypted secrets file..."
    echo "You will be prompted to enter the vault password and secret values."
    echo ""
    
    # Create a temporary file with the template
    TEMP_FILE=$(mktemp)
    cat > "$TEMP_FILE" << 'EOF'
# CallableAPIs Infrastructure Secrets
# This file contains sensitive configuration data
# DO NOT commit this file to version control

# GitHub OIDC Configuration
vault_github_client_id: "your_github_client_id_here"
vault_github_client_secret: "your_github_client_secret_here"
vault_github_redirect_uri: "https://api.callableapis.com/api/auth/callback"

# AWS Configuration
vault_aws_access_key_id: "your_aws_access_key_id_here"
vault_aws_secret_access_key: "your_aws_secret_access_key_here"
vault_aws_region: "us-west-2"

# Cloudflare Configuration
vault_cloudflare_api_token: "your_cloudflare_api_token_here"
vault_cloudflare_zone_id: "your_cloudflare_zone_id_here"

# Oracle Cloud Configuration
vault_oci_tenancy_ocid: "your_oci_tenancy_ocid_here"
vault_oci_user_ocid: "your_oci_user_ocid_here"
vault_oci_fingerprint: "your_oci_fingerprint_here"
vault_oci_private_key_path: "/path/to/oci/private/key.pem"
vault_oci_compartment_id: "your_oci_compartment_id_here"

# Google Cloud Configuration
vault_google_project_id: "your_google_project_id_here"
vault_google_application_credentials: "/path/to/google/credentials.json"

# IBM Cloud Configuration
vault_ibmcloud_api_key: "your_ibmcloud_api_key_here"
vault_ibmcloud_resource_group_id: "your_ibmcloud_resource_group_id_here"
vault_ibmcloud_region: "us-south"

# Database Configuration (for future use)
vault_database_url: "your_database_url_here"
vault_database_username: "your_database_username_here"
vault_database_password: "your_database_password_here"

# API Keys (for future use)
vault_external_service_1_key: "your_external_service_1_key_here"
vault_external_service_2_key: "your_external_service_2_key_here"
EOF

    # Encrypt the file
    ansible-vault encrypt "$TEMP_FILE" --output "$SECRETS_FILE"
    rm "$TEMP_FILE"
    
    echo -e "${GREEN}Secrets file created: $SECRETS_FILE${NC}"
    echo "Remember to:"
    echo "1. Update the values with your actual secrets"
    echo "2. Store the vault password securely"
    echo "3. Add secrets.yml to .gitignore"
}

# Function to edit secrets
edit_secrets() {
    if [ ! -f "$SECRETS_FILE" ]; then
        echo -e "${RED}Error: Secrets file not found${NC}"
        echo "Run '$0 create' first"
        exit 1
    fi
    
    echo "Opening secrets file for editing..."
    ansible-vault edit "$SECRETS_FILE"
}

# Function to view secrets
view_secrets() {
    if [ ! -f "$SECRETS_FILE" ]; then
        echo -e "${RED}Error: Secrets file not found${NC}"
        echo "Run '$0 create' first"
        exit 1
    fi
    
    echo "Viewing secrets file..."
    ansible-vault view "$SECRETS_FILE"
}

# Function to decrypt secrets
decrypt_secrets() {
    if [ ! -f "$SECRETS_FILE" ]; then
        echo -e "${RED}Error: Secrets file not found${NC}"
        exit 1
    fi
    
    echo "Decrypting secrets file..."
    ansible-vault decrypt "$SECRETS_FILE"
    echo -e "${YELLOW}Warning: Secrets file is now unencrypted!${NC}"
    echo "Remember to encrypt it again with: $0 encrypt"
}

# Function to encrypt secrets
encrypt_secrets() {
    if [ ! -f "$SECRETS_FILE" ]; then
        echo -e "${RED}Error: Secrets file not found${NC}"
        exit 1
    fi
    
    echo "Encrypting secrets file..."
    ansible-vault encrypt "$SECRETS_FILE"
    echo -e "${GREEN}Secrets file encrypted${NC}"
}

# Function to create backup
backup_secrets() {
    if [ ! -f "$SECRETS_FILE" ]; then
        echo -e "${RED}Error: Secrets file not found${NC}"
        exit 1
    fi
    
    BACKUP_FILE="$SECRETS_FILE.backup.$(date +%Y%m%d_%H%M%S)"
    echo "Creating backup: $BACKUP_FILE"
    cp "$SECRETS_FILE" "$BACKUP_FILE"
    echo -e "${GREEN}Backup created: $BACKUP_FILE${NC}"
}

# Main script logic
case "${1:-}" in
    create)
        create_secrets
        ;;
    edit)
        edit_secrets
        ;;
    view)
        view_secrets
        ;;
    decrypt)
        decrypt_secrets
        ;;
    encrypt)
        encrypt_secrets
        ;;
    backup)
        backup_secrets
        ;;
    *)
        show_usage
        exit 1
        ;;
esac
