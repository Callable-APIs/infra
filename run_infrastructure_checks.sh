#!/bin/bash

# Infrastructure Validation Script
# This script runs all automated tests, static checks, and validation for the infrastructure project
# as required by the project instructions in AGENTS.md

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to run command with timeout
run_check() {
    local check_name="$1"
    local command="$2"
    local timeout="${3:-30}"
    
    print_status "Running $check_name..."
    
    if timeout "$timeout" bash -c "$command"; then
        print_success "$check_name passed"
        return 0
    else
        print_error "$check_name failed"
        return 1
    fi
}

# Check if we're in the right directory
if [ ! -f "AGENTS.md" ]; then
    print_error "This script must be run from the project root directory (where AGENTS.md is located)"
    exit 1
fi

print_status "Starting infrastructure validation checks..."
print_status "Project: CallableAPIs Infrastructure"
print_status "Timestamp: $(date)"
echo ""

# Track overall success
overall_success=true

# 1. Terraform Validation
echo "=========================================="
print_status "1. TERRAFORM VALIDATION"
echo "=========================================="

if command_exists terraform; then
    # Check if we're in terraform directory or can find it
    if [ -d "terraform" ]; then
        cd terraform
        
        # Validate Terraform configuration
        if ! run_check "Terraform configuration validation" "terraform validate" 60; then
            overall_success=false
        fi
        
        # Check Terraform formatting
        if ! run_check "Terraform formatting check" "terraform fmt -check -diff" 30; then
            print_warning "Terraform files need formatting. Run 'terraform fmt' to fix."
            overall_success=false
        fi
        
        cd ..
    else
        print_warning "No terraform directory found"
        overall_success=false
    fi
else
    print_warning "Terraform not installed, skipping Terraform validation"
fi

echo ""

# 2. Ansible Validation
echo "=========================================="
print_status "2. ANSIBLE VALIDATION"
echo "=========================================="

if command_exists ansible-playbook; then
    # Check Ansible syntax for all playbooks
    print_status "Checking Ansible playbook syntax..."
    
    if [ -d "ansible/playbooks" ]; then
        for playbook in ansible/playbooks/*.yml; do
            if [ -f "$playbook" ]; then
                playbook_name=$(basename "$playbook")
                if ! run_check "Ansible syntax check: $playbook_name" "ansible-playbook --syntax-check '$playbook'" 30; then
                    overall_success=false
                fi
            fi
        done
    else
        print_warning "No ansible/playbooks directory found"
        overall_success=false
    fi
    
    # Check Ansible inventory syntax
    if [ -f "ansible/inventory/production" ]; then
        if ! run_check "Ansible inventory syntax check" "ansible-inventory --list -i ansible/inventory/production" 30; then
            overall_success=false
        fi
    else
        print_warning "No ansible inventory found"
        overall_success=false
    fi
else
    print_warning "Ansible not installed, skipping Ansible validation"
fi

echo ""

# 3. Docker Validation
echo "=========================================="
print_status "3. DOCKER VALIDATION"
echo "=========================================="

if command_exists docker; then
    # Check if Dockerfile exists
    if [ -f "Dockerfile" ]; then
        print_success "Dockerfile exists"
        
        # Test Docker build
        if ! run_check "Docker build test" "docker build -t callableapis-infra-test ." 300; then
            overall_success=false
        else
            # Clean up test image
            docker rmi callableapis-infra-test >/dev/null 2>&1 || true
        fi
    else
        print_warning "No Dockerfile found"
        overall_success=false
    fi
    
    # Check if callableapis:infra image exists
    if docker image inspect callableapis:infra >/dev/null 2>&1; then
        print_success "callableapis:infra Docker image exists"
    else
        print_warning "callableapis:infra Docker image not found. Run 'docker build -t callableapis:infra .' to create it."
        overall_success=false
    fi
else
    print_warning "Docker not installed, skipping Docker validation"
fi

echo ""

# 4. SSL Certificate Validation
echo "=========================================="
print_status "4. SSL CERTIFICATE VALIDATION"
echo "=========================================="

# Check if SSL artifacts exist
if [ -d "ansible/artifacts/ssl" ]; then
    print_success "SSL artifacts directory exists"
    
    # Check for required certificate files
    required_files=("privkey.pem" "cert.pem" "fullchain.pem" "chain.pem")
    for file in "${required_files[@]}"; do
        if [ -f "ansible/artifacts/ssl/$file" ]; then
            print_success "SSL file exists: $file"
            
            # Validate certificate if it's a cert file
            if [[ "$file" == "cert.pem" || "$file" == "fullchain.pem" ]]; then
                if command_exists openssl; then
                    if openssl x509 -in "ansible/artifacts/ssl/$file" -text -noout >/dev/null 2>&1; then
                        print_success "SSL certificate $file is valid"
                    else
                        print_error "SSL certificate $file is invalid"
                        overall_success=false
                    fi
                fi
            fi
        else
            print_warning "SSL file missing: $file"
            overall_success=false
        fi
    done
    
    # Check if certificate and private key match
    if [ -f "ansible/artifacts/ssl/cert.pem" ] && [ -f "ansible/artifacts/ssl/privkey.pem" ]; then
        if command_exists openssl; then
            cert_modulus=$(openssl x509 -noout -modulus -in ansible/artifacts/ssl/cert.pem | openssl md5)
            key_modulus=$(openssl rsa -noout -modulus -in ansible/artifacts/ssl/privkey.pem | openssl md5)
            
            if [ "$cert_modulus" = "$key_modulus" ]; then
                print_success "Certificate and private key match"
            else
                print_error "Certificate and private key do not match"
                overall_success=false
            fi
        fi
    fi
else
    print_warning "SSL artifacts directory not found. Run 'ansible-playbook generate-cloudflare-origin-certificates.yml' to create certificates."
    overall_success=false
fi

echo ""

# 5. Configuration File Validation
echo "=========================================="
print_status "5. CONFIGURATION FILE VALIDATION"
echo "=========================================="

# Check for required configuration files
required_configs=("env.sh.in" "terraform/terraform.tfvars.in")
for config in "${required_configs[@]}"; do
    if [ -f "$config" ]; then
        print_success "Configuration template exists: $config"
    else
        print_warning "Configuration template missing: $config"
        overall_success=false
    fi
done

# Check for actual configuration files (should exist but not be committed)
actual_configs=("env.sh" "terraform/terraform.tfvars")
for config in "${actual_configs[@]}"; do
    if [ -f "$config" ]; then
        print_success "Configuration file exists: $config"
    else
        print_warning "Configuration file missing: $config (copy from .in template)"
        overall_success=false
    fi
done

echo ""

# 6. Network Connectivity Tests
echo "=========================================="
print_status "6. NETWORK CONNECTIVITY TESTS"
echo "=========================================="

# Test external connectivity with timeouts
if command_exists curl; then
    # Test Cloudflare DNS resolution
    if timeout 10 curl -s -o /dev/null -w "%{http_code}" https://callableapis.com >/dev/null 2>&1; then
        print_success "Cloudflare DNS resolution working"
    else
        print_warning "Cloudflare DNS resolution may have issues"
        overall_success=false
    fi
    
    # Test status endpoint (if available)
    if timeout 10 curl -s -o /dev/null -w "%{http_code}" https://status.callableapis.com/api/status >/dev/null 2>&1; then
        print_success "Status endpoint accessible"
    else
        print_warning "Status endpoint not accessible (may be expected if not deployed)"
    fi
else
    print_warning "curl not available, skipping network tests"
fi

echo ""

# 7. Security Checks
echo "=========================================="
print_status "7. SECURITY CHECKS"
echo "=========================================="

# Check for sensitive files that shouldn't be committed
# Only check if files are actually committed, not just if they exist locally
sensitive_files=("env.sh" "terraform/terraform.tfvars")
for file in "${sensitive_files[@]}"; do
    if git ls-files --error-unmatch "$file" >/dev/null 2>&1; then
        print_error "Sensitive file is committed to git: $file"
        print_warning "Remove from git and ensure it's in .gitignore"
        overall_success=false
    else
        print_success "Sensitive file not committed: $file"
    fi
done

# Check for committed PEM/key/crt files (excluding artifacts directory)
committed_certs=$(git ls-files "*.pem" "*.key" "*.crt" | grep -v "ansible/artifacts/" | grep -v "terraform/ssh_keys/" || true)
if [ -n "$committed_certs" ]; then
    print_error "Sensitive certificate files are committed to git:"
    echo "$committed_certs" | while read -r cert_file; do
        print_warning "  - $cert_file"
    done
    print_warning "Remove from git and ensure *.pem, *.key, *.crt are in .gitignore"
    overall_success=false
else
    print_success "No certificate files committed to git"
fi

# Check .gitignore for sensitive patterns
if [ -f ".gitignore" ]; then
    print_success ".gitignore exists"
    
    # Check if sensitive patterns are in .gitignore
    sensitive_patterns=("*.pem" "*.key" "env.sh" "terraform.tfvars")
    for pattern in "${sensitive_patterns[@]}"; do
        if grep -q "$pattern" .gitignore; then
            print_success "Sensitive pattern in .gitignore: $pattern"
        else
            print_warning "Sensitive pattern missing from .gitignore: $pattern"
            overall_success=false
        fi
    done
else
    print_warning ".gitignore not found"
    overall_success=false
fi

echo ""

# 8. Documentation Checks
echo "=========================================="
print_status "8. DOCUMENTATION CHECKS"
echo "=========================================="

# Check for required documentation files
required_docs=("AGENTS.md" "README.md")
for doc in "${required_docs[@]}"; do
    if [ -f "$doc" ] && [ -s "$doc" ]; then
        print_success "Documentation exists: $doc"
    else
        print_warning "Documentation missing or empty: $doc"
        overall_success=false
    fi
done

echo ""

# 9. Final Summary
echo "=========================================="
print_status "INFRASTRUCTURE VALIDATION SUMMARY"
echo "=========================================="

if [ "$overall_success" = true ]; then
    print_success "All infrastructure checks passed! Repository is compliant with project requirements."
    echo ""
    print_status "Infrastructure is ready for deployment!"
    print_status "Next steps:"
    echo "  - Deploy certificates: ansible-playbook setup-cloudflare-ssl.yml"
    echo "  - Deploy containers: ansible-playbook deploy-all-containers.yml"
    echo "  - Test endpoints: ./test-container-endpoints.sh"
    exit 0
else
    print_error "Some infrastructure checks failed. Please review the output above and fix the issues."
    echo ""
    print_status "Common fixes:"
    echo "  - Generate certificates: ansible-playbook generate-cloudflare-origin-certificates.yml"
    echo "  - Fix Terraform: terraform fmt && terraform validate"
    echo "  - Fix Ansible: ansible-playbook --syntax-check playbooks/*.yml"
    echo "  - Build Docker: docker build -t callableapis:infra ."
    echo "  - Update .gitignore: Add sensitive file patterns"
    exit 1
fi
