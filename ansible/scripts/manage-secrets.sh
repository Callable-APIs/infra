#!/bin/bash

# CallableAPIs Secrets Management Script
# Comprehensive secrets management with rotation and auditing

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

# Function to show usage
show_usage() {
    echo "CallableAPIs Secrets Management"
    echo "==============================="
    echo ""
    echo "Usage: $0 [COMMAND] [OPTIONS]"
    echo ""
    echo "Commands:"
    echo "  setup       - Initial secrets setup"
    echo "  rotate      - Rotate all secrets"
    echo "  audit       - Security audit of secrets"
    echo "  deploy      - Deploy secrets to containers"
    echo "  status      - Check secrets status"
    echo "  backup      - Create backup of current secrets"
    echo "  restore     - Restore from backup"
    echo ""
    echo "Options:"
    echo "  --hosts HOSTS    - Target specific hosts (default: all)"
    echo "  --check          - Dry run (check mode)"
    echo "  --verbose        - Verbose output"
    echo ""
    echo "Examples:"
    echo "  $0 setup                    # Initial setup"
    echo "  $0 rotate --hosts onode1    # Rotate secrets on Oracle node"
    echo "  $0 audit --check            # Security audit (dry run)"
    echo "  $0 status --verbose         # Check status with details"
}

# Function to run ansible playbook
run_playbook() {
    local playbook="$1"
    local hosts="${2:-all}"
    local check_mode="${3:-}"
    local verbose="${4:-}"
    
    local cmd="ansible-playbook -i inventory/production $playbook --limit $hosts"
    
    if [ "$check_mode" = "true" ]; then
        cmd="$cmd --check"
    fi
    
    if [ "$verbose" = "true" ]; then
        cmd="$cmd -v"
    fi
    
    echo -e "${BLUE}Running: $cmd${NC}"
    eval $cmd
}

# Function to setup initial secrets
setup_secrets() {
    echo -e "${GREEN}Setting up initial secrets...${NC}"
    
    # Create encrypted secrets file
    echo "Creating encrypted secrets file..."
    ansible/scripts/encrypt-secrets.sh create
    
    # Deploy secrets to all hosts
    echo "Deploying secrets to all hosts..."
    run_playbook "playbooks/deploy-secrets.yml" "$HOSTS" "$CHECK_MODE" "$VERBOSE"
    
    # Setup vault passwords
    echo "Setting up vault passwords..."
    run_playbook "playbooks/setup-vault-password.yml" "$HOSTS" "$CHECK_MODE" "$VERBOSE"
    
    echo -e "${GREEN}Initial secrets setup complete!${NC}"
}

# Function to rotate secrets
rotate_secrets() {
    echo -e "${YELLOW}Rotating secrets...${NC}"
    echo -e "${RED}WARNING: This will generate new secrets and restart containers!${NC}"
    
    if [ "$CHECK_MODE" != "true" ]; then
        read -p "Are you sure you want to continue? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            echo "Aborted"
            exit 1
        fi
    fi
    
    run_playbook "playbooks/secrets-rotation.yml" "$HOSTS" "$CHECK_MODE" "$VERBOSE"
    
    echo -e "${GREEN}Secrets rotation complete!${NC}"
    echo -e "${YELLOW}Remember to update cloud provider credentials with new values.${NC}"
}

# Function to audit secrets
audit_secrets() {
    echo -e "${BLUE}Running security audit...${NC}"
    
    run_playbook "playbooks/secrets-audit.yml" "$HOSTS" "$CHECK_MODE" "$VERBOSE"
    
    echo -e "${GREEN}Security audit complete!${NC}"
}

# Function to deploy secrets
deploy_secrets() {
    echo -e "${GREEN}Deploying secrets to containers...${NC}"
    
    run_playbook "playbooks/deploy-secrets.yml" "$HOSTS" "$CHECK_MODE" "$VERBOSE"
    
    echo -e "${GREEN}Secrets deployment complete!${NC}"
}

# Function to check status
check_status() {
    echo -e "${BLUE}Checking secrets status...${NC}"
    
    # Check local secrets file
    if [ -f "ansible/group_vars/secrets.yml" ]; then
        echo -e "${GREEN}✓ Local secrets file exists${NC}"
    else
        echo -e "${RED}✗ Local secrets file missing${NC}"
    fi
    
    # Check on each host
    for host in onode1 gnode1 inode1; do
        echo "Checking $host..."
        if ssh -o ConnectTimeout=5 -o StrictHostKeyChecking=no ansible@$host "test -f /opt/callableapis/vault-password && test -f /opt/callableapis/secrets/all-secrets.env" 2>/dev/null; then
            echo -e "${GREEN}✓ $host: Secrets deployed${NC}"
        else
            echo -e "${RED}✗ $host: Secrets missing${NC}"
        fi
    done
    
    # Check API status
    echo "Checking API secrets status..."
    if curl -s https://api.callableapis.com/api/secrets/status | grep -q '"status":"ok"'; then
        echo -e "${GREEN}✓ API: Secrets loaded successfully${NC}"
    else
        echo -e "${RED}✗ API: Secrets not loaded${NC}"
    fi
}

# Function to create backup
backup_secrets() {
    local backup_dir="secrets-backup-$(date +%Y%m%d_%H%M%S)"
    
    echo -e "${GREEN}Creating backup: $backup_dir${NC}"
    
    mkdir -p "$backup_dir"
    
    # Backup local secrets
    if [ -f "ansible/group_vars/secrets.yml" ]; then
        cp "ansible/group_vars/secrets.yml" "$backup_dir/"
        echo -e "${GREEN}✓ Local secrets backed up${NC}"
    fi
    
    # Backup from each host
    for host in onode1 gnode1 inode1; do
        echo "Backing up from $host..."
        if ssh -o ConnectTimeout=5 -o StrictHostKeyChecking=no ansible@$host "tar -czf - /opt/callableapis/secrets /opt/callableapis/vault-password" 2>/dev/null | cat > "$backup_dir/$host-secrets.tar.gz"; then
            echo -e "${GREEN}✓ $host: Secrets backed up${NC}"
        else
            echo -e "${RED}✗ $host: Backup failed${NC}"
        fi
    done
    
    echo -e "${GREEN}Backup complete: $backup_dir${NC}"
}

# Parse command line arguments
HOSTS="all"
CHECK_MODE="false"
VERBOSE="false"
COMMAND=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --hosts)
            HOSTS="$2"
            shift 2
            ;;
        --check)
            CHECK_MODE="true"
            shift
            ;;
        --verbose)
            VERBOSE="true"
            shift
            ;;
        setup|rotate|audit|deploy|status|backup|restore)
            COMMAND="$1"
            shift
            ;;
        -h|--help)
            show_usage
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            show_usage
            exit 1
            ;;
    esac
done

# Check if command was provided
if [ -z "$COMMAND" ]; then
    echo -e "${RED}Error: No command provided${NC}"
    show_usage
    exit 1
fi

# Change to ansible directory
cd "$ANSIBLE_DIR"

# Execute command
case $COMMAND in
    setup)
        setup_secrets
        ;;
    rotate)
        rotate_secrets
        ;;
    audit)
        audit_secrets
        ;;
    deploy)
        deploy_secrets
        ;;
    status)
        check_status
        ;;
    backup)
        backup_secrets
        ;;
    restore)
        echo -e "${RED}Restore functionality not implemented yet${NC}"
        exit 1
        ;;
    *)
        echo -e "${RED}Unknown command: $COMMAND${NC}"
        show_usage
        exit 1
        ;;
esac
