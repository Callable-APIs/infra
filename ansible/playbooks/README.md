# Ansible Playbook Structure

This directory contains a hierarchical playbook structure designed for maintainability and separation of concerns.

## Top-Level Playbooks (Orchestration)

These playbooks orchestrate the subdirectory playbooks and contain minimal logic:

- `setup-infrastructure.yml` - Complete infrastructure setup
- `deploy-applications.yml` - Deploy applications based on inventory
- `manage-ssl.yml` - SSL certificate and firewall management
- `manage-secrets.yml` - Secrets management
- `maintenance.yml` - Infrastructure maintenance tasks

## Subdirectory Playbooks (Implementation)

### `ssl/` - SSL Certificate Management
- `manage-certificates.yml` - Generate and deploy SSL certificates
- `generate-csr-tasks.yml` - Generate Certificate Signing Request
- `create-cloudflare-cert-tasks.yml` - Create Cloudflare Origin Certificate
- `retrieve-cloudflare-cert-tasks.yml` - Retrieve certificate from Terraform
- `verify-ssl-artifacts-tasks.yml` - Verify SSL artifact integrity
- `deploy-ssl-to-nodes-tasks.yml` - Deploy certificates to nodes
- `verify-ssl-deployment-tasks.yml` - Verify SSL deployment

### `containers/` - Container Management
- `deploy-containers.yml` - Deploy containers based on inventory groups
- `deploy-base-container-tasks.yml` - Deploy base container
- `deploy-status-container-tasks.yml` - Deploy status container
- `deploy-services-container-tasks.yml` - Deploy services container

### `nginx/` - Nginx Configuration
- `setup-nginx.yml` - Setup Nginx with SSL
- `configure-routing-tasks.yml` - Configure dynamic routing

### `firewall/` - Firewall Management
- `ensure-firewall-rules.yml` - Ensure firewall rules for all cloud providers

### `testing/` - Endpoint Testing
- `test-endpoints.yml` - Test all endpoints
- `test-https-endpoints.yml` - Test HTTPS endpoints
- `test-container-endpoints.yml` - Test container endpoints

### `secrets/` - Secrets Management
- `build-secrets.yml` - Build secrets locally
- `deploy-secrets-simple.yml` - Deploy secrets to nodes

## Utility Playbooks (Root Level)
- `update-ssh-keys.yml` - Update SSH keys on all nodes
- `validate-facts.yml` - Validate and update host facts
- `verify-container-endpoints.yml` - Verify container endpoints

## Design Principles

1. **Separation of Concerns**: Top-level playbooks orchestrate, subdirectory playbooks implement
2. **Idempotency**: All playbooks are safe to run multiple times
3. **Self-Healing**: Playbooks automatically detect and fix issues
4. **Minimal Logic**: Top-level playbooks contain minimal logic, complexity is in subdirectories
5. **Aggressive Consolidation**: Related functionality is combined into single playbooks

## Usage Examples

```bash
# Complete infrastructure setup
ansible-playbook -i ansible/inventory/production ansible/playbooks/setup-infrastructure.yml

# Deploy applications only
ansible-playbook -i ansible/inventory/production ansible/playbooks/deploy-applications.yml

# Manage SSL certificates
ansible-playbook -i ansible/inventory/production ansible/playbooks/manage-ssl.yml

# Run maintenance tasks
ansible-playbook -i ansible/inventory/production ansible/playbooks/maintenance.yml
```
