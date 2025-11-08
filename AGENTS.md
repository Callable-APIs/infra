# Project Instruction

## Use of Docker

**CRITICAL: Always use the Docker container for all operations. Never install dependencies locally.**

### Docker Container Requirements

For isolating command line dependencies and execution of commands you will use a Docker container. If one does not yet exist, create a Dockerfile and as dependencies or command line tools / libraries are needed add them to the docker container. All execution of local commands should happen in the Docker container where the project directory is shared as a volume.

### Dependency Management Rules

1. **All Python dependencies MUST be installed in the Docker container**, not locally
2. **When adding new dependencies**, update the Dockerfile (and `pyproject.toml` for Poetry), then rebuild the container
3. **Never run `poetry install` or `pip install` locally** - these should only happen in the Docker container
4. **All commands should run through the Docker container** using `docker run --rm -v $(pwd):/app -w /app callableapis:infra <command>`

### Prohibited Actions
- ❌ Installing Python packages locally using `poetry install`, `pip install`, or `poetry add`
- ❌ Running Python commands directly (e.g., `python -m clint billing`)
- ❌ Installing system dependencies locally
- ❌ Modifying local Python environments

### Required Actions
- ✅ Always use the Docker container: `docker run --rm -v $(pwd):/app -w /app callableapis:infra <command>`
- ✅ Add dependencies to `pyproject.toml` and update the Dockerfile if needed
- ✅ Rebuild the Docker container after adding dependencies: `docker build -t callableapis:infra -f Dockerfile .`
- ✅ Run all Python commands through the container: `docker run --rm -v $(pwd):/app -w /app callableapis:infra python -m clint <command>`
- ✅ Run all Terraform commands through the container: `docker run --rm -v $(pwd):/app -w /app/terraform -e [ENV_VARS] callableapis:infra terraform <command>`

### Docker Container Usage Examples

```bash
# Run Python CLI commands
docker run --rm -v $(pwd):/app -w /app callableapis:infra python -m clint billing --daily

# Run Terraform commands
docker run --rm -v $(pwd):/app -w /app/terraform \
  -e AWS_ACCESS_KEY_ID="$AWS_ACCESS_KEY_ID" \
  -e AWS_SECRET_ACCESS_KEY="$AWS_SECRET_ACCESS_KEY" \
  callableapis:infra terraform plan

# Run cloud CLI commands
docker run --rm -v $(pwd):/app -w /app callableapis:infra aws s3 ls
docker run --rm -v $(pwd):/app -w /app callableapis:infra oci compute instance list
docker run --rm -v $(pwd):/app -w /app callableapis:infra ibmcloud account list

# Rebuild container after dependency changes
docker build -t callableapis:infra -f Dockerfile .
```

### Adding New Dependencies

When adding new Python dependencies:

1. **Add to `pyproject.toml`** (for Poetry-managed dependencies):
   ```toml
   [tool.poetry.dependencies]
   new-dependency = "^1.0.0"
   ```

2. **Update Dockerfile if needed** (for system packages or special installation):
   ```dockerfile
   # Install special dependency
   RUN pip install special-package || echo "Warning: installation failed"
   ```

3. **Rebuild the Docker container**:
   ```bash
   docker build -t callableapis:infra -f Dockerfile .
   ```

4. **Test in the container**:
   ```bash
   docker run --rm -v $(pwd):/app -w /app callableapis:infra python -m clint <command>
   ```

### Container Image

The primary Docker container is:
- **Image name**: `callableapis:infra`
- **Dockerfile**: `Dockerfile` (root of repository)
- **Purpose**: Infrastructure management, Terraform, cloud CLIs, Python tools

## Ansible Playbook Design Principles

**CRITICAL: Design playbooks to be idempotent and self-healing**

### Playbook Design Requirements
1. **Idempotent Operations**: Playbooks should be safe to run multiple times
2. **Self-Healing**: Automatically detect and fix blocking situations
3. **Conditional Logic**: Only perform actions when needed
4. **Comprehensive Coverage**: Handle all related tasks in a single playbook
5. **No Manual Intervention**: Never require manual shell commands to fix issues

### Prohibited Actions
- ❌ Using `ansible shell` commands to solve problems
- ❌ Creating multiple fragmented playbooks for related tasks
- ❌ Manual cleanup between playbook runs
- ❌ Playbooks that fail if run multiple times

### Required Actions
- ✅ Consolidate related functionality into single playbooks
- ✅ Use conditional logic (`when`, `failed_when: false`, `ignore_errors`)
- ✅ Check current state before making changes
- ✅ Automatically clean up blocking situations
- ✅ Design for "run anywhere, anytime" behavior

### Example: SSL Certificate Management
Instead of separate playbooks for:
- Generate CSR
- Create Cloudflare certificate
- Deploy certificates
- Verify certificates

Create ONE playbook that:
- Checks if valid certificate exists as artifact
- Creates new certificate only if needed
- Deploys to all nodes with proper permissions
- Verifies and corrects any issues
- Does nothing if everything is correct

## Playbook Structure Guidelines

**CRITICAL: Use hierarchical playbook structure for maintainability**

### Top-Level Playbooks (Orchestration)
- **Minimal Logic**: Top-level playbooks should only orchestrate subdirectory playbooks
- **No Implementation**: Top-level playbooks contain no complex logic or implementation details
- **Clear Purpose**: Each top-level playbook has a single, clear purpose
- **Aggressive Consolidation**: Combine related top-level playbooks whenever possible

### Subdirectory Playbooks (Implementation)
- **Specialized Logic**: Subdirectory playbooks contain specialized, self-healing, idempotent logic
- **Task Per Subdirectory**: Organize playbooks by functional area (ssl/, containers/, nginx/, etc.)
- **Minimal Count**: Keep subdirectory playbooks to a minimum
- **Self-Contained**: Each subdirectory playbook should be self-contained and testable

### Directory Structure
```
ansible/playbooks/
├── setup-infrastructure.yml          # Top-level orchestration
├── deploy-applications.yml            # Top-level orchestration
├── manage-ssl.yml                     # Top-level orchestration
├── ssl/                               # SSL implementation
│   ├── manage-certificates.yml
│   ├── generate-csr-tasks.yml
│   └── deploy-ssl-to-nodes-tasks.yml
├── containers/                        # Container implementation
│   ├── deploy-containers.yml
│   ├── deploy-base-container-tasks.yml
│   └── deploy-services-container-tasks.yml
├── nginx/                            # Nginx implementation
│   ├── setup-nginx.yml
│   └── configure-routing-tasks.yml
├── firewall/                         # Firewall implementation
│   └── ensure-firewall-rules.yml
├── testing/                          # Testing implementation
│   ├── test-endpoints.yml
│   └── test-https-endpoints.yml
└── secrets/                          # Secrets implementation
    ├── build-secrets.yml
    └── deploy-secrets-simple.yml
```

### Prohibited Actions
- ❌ Creating top-level playbooks with complex implementation logic
- ❌ Having too many top-level playbooks (aim for < 10)
- ❌ Duplicating logic across subdirectory playbooks
- ❌ Creating subdirectory playbooks that are too granular

### Required Actions
- ✅ Use top-level playbooks for orchestration only
- ✅ Implement complex logic in subdirectory playbooks
- ✅ Organize subdirectory playbooks by functional area
- ✅ Keep subdirectory playbooks self-contained and testable
- ✅ Maintain clear separation between orchestration and implementation

## Command Execution and Timeouts

**CRITICAL: Always use timeouts for external commands to prevent hanging**

### Timeout Requirements
1. **All external commands MUST have timeouts** to prevent indefinite hanging
2. **Use appropriate timeout values** based on command type:
   - Network requests: 5-10 seconds
   - File operations: 30 seconds
   - System commands: 60 seconds
   - Long-running processes: 300+ seconds

### Timeout Implementation
```bash
# curl commands - use both connect and max timeouts
curl --connect-timeout 5 --max-time 10 -s -o /dev/null -w "%{http_code}" https://example.com

# ansible commands - use timeout parameter
ansible-playbook -i inventory playbook.yml --timeout=30

# docker commands - use timeout wrapper
timeout 60 docker run --rm image:tag command

# system commands - use timeout wrapper
timeout 30 systemctl status service

# ssh commands - use ConnectTimeout
ssh -o ConnectTimeout=10 user@host command
```

### Prohibited Actions
- ❌ Running commands without timeouts
- ❌ Using indefinite waits in scripts
- ❌ Blocking operations without timeout controls
- ❌ Network requests without connection timeouts

### Required Actions
- ✅ Always specify timeouts for external commands
- ✅ Use appropriate timeout values for command type
- ✅ Test timeout behavior in development
- ✅ Document timeout values in scripts

## Python Code Organization

**CRITICAL: All Python code must be centralized in the clint module**

### CLINT Module Requirements

All Python code in this repository must be:
1. **Located in the `clint/` module** - No scattered Python scripts
2. **Accessible via CLI** - All functionality must be accessible through `python -m clint <command>`
3. **Managed via Poetry** - Dependencies and package structure defined in `pyproject.toml`
4. **Well-organized** - Use submodules for logical grouping (billing/, container/, secrets/, etc.)

### Prohibited Actions
- ❌ Creating standalone Python scripts in `src/` or root directory
- ❌ Creating Python code in container directories (`containers/*/app.py`)
- ❌ Duplicating functionality across multiple files
- ❌ Creating Python tools that aren't accessible via `clint` CLI
- ❌ Adding Python dependencies outside of `pyproject.toml`

### Required Actions
- ✅ All new Python functionality goes in `clint/` module
- ✅ Add CLI commands to `clint/__main__.py` for new functionality
- ✅ Use submodules for organization (e.g., `clint/billing/`, `clint/secrets/`)
- ✅ Add dependencies to `pyproject.toml` using Poetry
- ✅ Use strategy patterns for extensible functionality (e.g., secrets management)
- ✅ Update Dockerfiles to copy `clint/` module, not individual scripts

### CLINT Module Structure

```
clint/
├── __init__.py              # Module initialization
├── __main__.py              # Main CLI entry point
├── billing/                 # Billing adapters (AWS, OCI, IBM)
│   ├── __init__.py
│   ├── base_adapter.py
│   ├── aws_adapter.py
│   ├── oci_adapter.py
│   ├── ibm_adapter.py
│   └── manager.py
├── container/               # Container applications
│   ├── __init__.py
│   ├── base.py             # Base container Flask app
│   └── status.py           # Status container Flask app
└── secrets/                 # Secrets management strategies
    ├── __init__.py
    ├── base.py             # Base strategy interface
    ├── ansible_vault.py    # Ansible Vault strategy
    ├── hashicorp_vault.py  # HashiCorp Vault strategy
    └── manager.py          # Strategy factory
```

### Adding New Functionality

When adding new Python functionality:

1. **Create appropriate submodule** in `clint/` (e.g., `clint/new_feature/`)
2. **Add CLI command** to `clint/__main__.py`:
   ```python
   new_feature_parser = subparsers.add_parser("new-feature", ...)
   ```
3. **Add dependencies** to `pyproject.toml`:
   ```toml
   [tool.poetry.dependencies]
   new-dependency = "^1.0.0"
   ```
4. **Update Dockerfile** if the dependency needs special installation (see "Use of Docker" section)
5. **Rebuild Docker container**: `docker build -t callableapis:infra -f Dockerfile .`
6. **Test via CLI in container**: `docker run --rm -v $(pwd):/app -w /app callableapis:infra python -m clint new-feature --help`

### Migration from Scattered Code

If you find Python code outside of `clint/`:
1. Move it to appropriate `clint/` submodule
2. Add CLI command to expose functionality
3. Update any references to use `clint` CLI
4. Remove old files
5. Update Dockerfiles/scripts to use `clint` commands

### Examples

**Good**: All functionality in clint
```bash
python -m clint billing --daily
python -m clint container base
python -m clint terraform discover
```

**Bad**: Scattered scripts
```bash
python src/unified_billing_app.py  # ❌ Should be: clint billing
python containers/base/app.py      # ❌ Should be: clint container base
python scripts/some_tool.py        # ❌ Should be: clint some-tool
```

## Testing and Coverage

When adding or removing code it is essential that every functional edit to the codebase have corresponding tests. These tests, when possible should use the testing frameworks of the platform, for example in python it should be pytest.  

## Validation Script

There should be a run_checks.sh that runs all automated tests, static checks, style linting, test coverage or automation that run in the github actions.  If the repository contains multiple languages or platforms ALL of their checks must be run from this validation script.

## Validation of PRs
There should be at least 1 github action designed to validate Pull Requests which run a relevant subset of 
checks found in run_checks.sh.  Ideally it will be all but there may be checks that cannot run headlessly or in a github actions context.  

## Terraform State Management

**CRITICAL: All infrastructure changes MUST go through S3-backed Terraform state**

### State Management Rules
1. **S3 Backend Only**: All infrastructure is managed through the S3-backed Terraform state located at:
   - Bucket: `callableapis-terraform-state`
   - Key: `terraform.tfstate`
   - Region: `us-west-2`
   - Locking: DynamoDB table `callableapis-terraform-locks`

2. **No Local State**: Never create or modify local `terraform.tfstate` files. All state operations must use the S3 backend.

3. **Import Before Modify**: When adding new infrastructure:
   - First import existing resources into S3-backed state
   - Then modify the Terraform configuration
   - Finally apply changes through `terraform apply`

4. **Multi-Cloud Coverage**: All cloud providers (AWS, Google Cloud, Oracle Cloud, IBM Cloud) must be managed through the single S3-backed state.

### Terraform Workflow
1. **Always use Docker container**: `callableapis:infra` for all Terraform operations
2. **Load environment variables**: Source `env.sh` before running Terraform commands
3. **Verify state**: Run `terraform plan` before any changes to ensure state consistency
4. **Apply changes**: Use `terraform apply` for all infrastructure modifications
5. **Use relative paths**: All commands should be run from repository root

### Prohibited Actions
- ❌ Creating local `terraform.tfstate` files
- ❌ Using cloud provider CLIs/consoles for infrastructure changes
- ❌ Manual firewall rule modifications outside Terraform
- ❌ Creating resources directly in cloud consoles
- ❌ Using separate Terraform configurations for different cloud providers

### Required Actions
- ✅ All infrastructure changes through `terraform apply`
- ✅ Import existing resources before managing them
- ✅ Use `terraform plan` to verify changes before applying
- ✅ Test infrastructure changes in development before production
- ✅ Document all infrastructure changes in commit messages

### Node Management Principles
**CRITICAL: Avoid destroying nodes to prevent outages and data loss**

#### Node Update Strategy
1. **Use Ansible for configuration changes** - SSH keys, user accounts, software updates
2. **Use Terraform for infrastructure changes** - firewall rules, networking, storage
3. **Never destroy nodes for configuration changes** - Always patch in-place
4. **Test changes in development** before applying to production nodes

#### Configuration Management Hierarchy
1. **Ansible**: Node configuration, SSH keys, users, software, services
2. **Terraform**: Infrastructure, networking, firewall rules, storage
3. **Docker/Containers**: Application deployment and management

#### Prohibited Actions
- ❌ Destroying nodes for SSH key updates
- ❌ Recreating instances for configuration changes
- ❌ Using Terraform for user account management
- ❌ Manual configuration changes outside Ansible

#### Required Actions
- ✅ Use Ansible for all node configuration changes
- ✅ Use Terraform only for infrastructure changes
- ✅ Test configuration changes in development first
- ✅ Maintain node availability during updates
- ✅ Document all configuration changes

### Ansible Playbook Structure
**Current playbooks after Docker standardization cleanup:**

#### Core Docker Playbooks
- `install-docker-standard.yml` - Standardize nodes with Docker Engine
- `deploy-docker-container.yml` - Deploy containers using Docker

#### Utility Playbooks  
- `update-ssh-keys.yml` - Update SSH keys on all nodes
- `verify-container-endpoints.yml` - Verify container endpoints
- `validate-facts.yml` - Validate and update standardization facts

#### Service Playbooks
- `deploy-nginx-proxy.yml` - Deploy nginx proxy for containers
- `deploy-api.yml` - Deploy API services

#### Secrets Playbooks
- `build-secrets.yml` - Build secrets locally
- `deploy-secrets-simple.yml` - Deploy secrets to nodes

**Removed playbooks:** All containerd/ctr-based playbooks have been removed as we now use Docker exclusively.

### Node Standardization Process
**CRITICAL: New nodes must be standardized before container deployment**

#### Standardization Requirements
All new nodes must be standardized using our Ansible playbooks to ensure:
- **Container Runtime**: Docker Engine with Docker CLI
- **Python Version**: Python 3.10+ for Ansible compatibility
- **System Packages**: Essential tools and dependencies
- **User Configuration**: ansible user with proper permissions
- **Service Configuration**: Docker service enabled and running

#### Standardization Commands
```bash
# Standardize new Oracle Cloud nodes
ansible-playbook -i ansible/inventory/production ansible/playbooks/install-docker-standard.yml --limit oracle_cloud

# Standardize new Google Cloud nodes  
ansible-playbook -i ansible/inventory/production ansible/playbooks/install-docker-standard.yml --limit google_cloud

# Standardize new IBM Cloud nodes
ansible-playbook -i ansible/inventory/production ansible/playbooks/install-docker-standard.yml --limit ibm_cloud

# Standardize all new nodes at once
ansible-playbook -i ansible/inventory/production ansible/playbooks/install-docker-standard.yml

# Note: Migration playbook removed - all nodes now standardized on Docker
```

#### Post-Standardization Deployment
After standardization, deploy containers using:
```bash
# Deploy containers to standardized nodes
ansible-playbook -i ansible/inventory/production ansible/playbooks/deploy-docker-container.yml

# Or use the nginx proxy setup with Docker
ansible-playbook -i ansible/inventory/production ansible/playbooks/containerd-setup.yml
```

#### Standardization Verification
```bash
# Check if nodes are standardized
ansible all -i ansible/inventory/production -m shell -a "cat /home/ansible/.ansible/facts/standardization_complete 2>/dev/null || echo 'Not standardized'"

# Verify container runtime availability
ansible all -i ansible/inventory/production -m shell -a "docker --version || echo 'No container runtime'"

# Check container runtime type
ansible all -i ansible/inventory/production -m shell -a "cat /home/ansible/.ansible/facts/container_runtime 2>/dev/null || echo 'Unknown'"
```

### Environment Configuration Management
**CRITICAL: Keep template files in sync with actual configuration**

#### Template Files (Safe to Commit)
- `env.sh.in` - Environment variables template
- `terraform/terraform.tfvars.in` - Terraform variables template

#### Actual Files (Never Commit)
- `env.sh` - Contains actual credentials (gitignored)
- `terraform/terraform.tfvars` - Contains actual values (gitignored)

#### Template File Maintenance Rules
1. **Always update templates first** when adding new variables
2. **Keep templates in sync** with actual configuration files
3. **Use descriptive placeholder values** in templates
4. **Test template files** by copying to actual files and verifying

#### Adding New Variables
When adding new environment variables or Terraform variables:
1. Add to `env.sh.in` with placeholder value
2. Add to `terraform/terraform.tfvars.in` with placeholder value
3. Test by copying templates to actual files
4. Verify all required variables are documented


## Credential and Artifact Management (Do NOT store secrets in env.sh)

To prevent on-disk check-ins of sensitive data, all runtime credentials and SSH keys must be managed as Ansible artifacts, not committed files:

- Storage location (gitignored): `ansible/artifacts/`
- Builders (idempotent): playbooks in `ansible/playbooks/secrets/`
  - `secrets/build-ssh-key-artifact.yml` creates rotated SSH keypairs under `ansible/artifacts/ssh/`
  - Add additional builders for cloud/API tokens as needed (write files under `ansible/artifacts/secrets/`)
- Distribution: reference artifacts from playbooks (e.g., `update-ssh-keys.yml` uses the rotated public key artifact)
- Never commit real credentials to `env.sh`; keep only non-secret toggles there. Put example values in `env.sh.in`
- `.gitignore` must include `ansible/artifacts/` and any private key patterns

Credential rotation workflow:
1) Generate/rotate locally: run the builder (e.g., `ansible-playbook ansible/playbooks/secrets/build-ssh-key-artifact.yml`)
2) Distribute to hosts: run the appropriate rotation playbook (e.g., `ansible/playbooks/update-ssh-keys.yml`)
3) Update Terraform to consume artifact-based public keys (e.g., `aws_key_pair` reads from `ansible/artifacts/..._public_key`)
4) Verify access (SSH/connectivity) and remove deprecated keys


### Current Infrastructure State
**Get the current infrastructure state from Terraform (single source of truth):**

```bash
# Check current Terraform state
docker run --rm -v $(pwd):/app -w /app -e AWS_ACCESS_KEY_ID="$AWS_ACCESS_KEY_ID" -e AWS_SECRET_ACCESS_KEY="$AWS_SECRET_ACCESS_KEY" callableapis:infra terraform state list

# Get detailed resource information
docker run --rm -v $(pwd):/app -w /app -e AWS_ACCESS_KEY_ID="$AWS_ACCESS_KEY_ID" -e AWS_SECRET_ACCESS_KEY="$AWS_SECRET_ACCESS_KEY" callableapis:infra terraform state list | while read -r resource; do
  echo "Resource: $resource"
  docker run --rm -v $(pwd):/app -w /app -e AWS_ACCESS_KEY_ID="$AWS_ACCESS_KEY_ID" -e AWS_SECRET_ACCESS_KEY="$AWS_SECRET_ACCESS_KEY" callableapis:infra terraform state show "$resource"
  echo "---"
done

# Get infrastructure summary by provider
docker run --rm -v $(pwd):/app -w /app -e AWS_ACCESS_KEY_ID="$AWS_ACCESS_KEY_ID" -e AWS_SECRET_ACCESS_KEY="$AWS_SECRET_ACCESS_KEY" callableapis:infra terraform state list | awk -F'.' '{print $1"."$2}' | sort | uniq -c | sort -nr
```

## Terraform State vs Configuration Mismatches

**CRITICAL: When Terraform says "No changes" but the cloud resource is missing, check for commented-out sections**

### Common Issue: Commented-Out Resources
Terraform may report "No changes. Your infrastructure matches the configuration" even when:
- Resources are missing in the cloud
- Configuration exists but is commented out
- State and configuration appear aligned, but the actual resource doesn't exist

### Troubleshooting Steps
When encountering state/config mismatches:

1. **Check for Commented-Out Sections**
   ```bash
   # Search for commented resources in main Terraform config
   grep -n "# resource" terraform/main.tf
   grep -n "# resource" terraform/*/main.tf
   
   # Look for specific resource types that might be commented
   grep -A 10 "#.*443\|#.*https\|#.*firewall" terraform/main.tf
   ```

2. **Compare State with Actual Cloud Resources**
   ```bash
   # Check what's actually in the cloud (security group example)
   # vs what Terraform state says exists
   
   # Oracle Cloud
   docker run --rm -v $(pwd):/app -w /app -e OCI_... callableapis:infra terraform state show oci_core_security_list.callableapis_sl
   
   # IBM Cloud
   docker run --rm -v $(pwd):/app -w /app -e IBMCLOUD_... callableapis:infra terraform state show ibm_is_security_group.callableapis_sg
   ```

3. **Uncomment and Apply**
   If you find commented-out resources:
   ```bash
   # Uncomment the section in terraform/main.tf
   # Then apply the resource
   docker run --rm -v $(pwd):/app -w /app -e [ENV_VARS] callableapis:infra \
     terraform apply -target=resource.type.resource_name -auto-approve
   ```

4. **Verify Changes Propagated**
   ```bash
   # Test that the resource is now accessible
   curl --connect-timeout 5 --max-time 10 -k https://[IP]:[PORT]/
   
   # Check Terraform state shows the resource
   docker run --rm -v $(pwd):/app -w /app -e [ENV_VARS] callableapis:infra \
     terraform state show resource.type.resource_name
   ```

### Signs You May Have Commented-Out Resources
- ❌ `terraform plan` shows no changes
- ❌ Resource exists in Terraform config but missing in cloud
- ❌ Resources show "disabled" or "SSL terminated at Cloudflare" in comments
- ❌ Multiple Terraform config files (e.g., `main.tf` vs `cloud/main.tf`) with conflicting definitions

### Real-World Example
**Problem**: IBM Cloud security group missing port 443 inbound rule
- **Symptom**: HTTPS timing out externally despite internal service working
- **Root Cause**: `ibm_is_security_group_rule.callableapis_https` was commented out in `terraform/main.tf` with note "HTTPS disabled - SSL terminated at Cloudflare"
- **Solution**: Uncommented the rule, ran `terraform apply -target=ibm_is_security_group_rule.callableapis_https`, verified connectivity
- **Result**: All 4 nodes now fully operational with end-to-end HTTPS encryption

### Required Actions
- ✅ Search for commented `# resource` blocks when changes don't apply
- ✅ Check for conflicting definitions across multiple config files
- ✅ Uncomment and apply commented resources
- ✅ Verify changes propagated to actual cloud infrastructure
- ✅ Document why resources were previously commented out

### Node and Container Status Commands
**Get current node connectivity and container status:**

```bash
# Test SSH connectivity to all nodes
ansible all -i ansible/inventory/production -m ping

# Check container status on all nodes
ansible all -i ansible/inventory/production -m shell -a "docker ps -a"

# Test external access to container endpoints
./test-container-endpoints.sh

# Check specific node status
ansible onode1 -i ansible/inventory/production -m shell -a "curl -s http://localhost:8080/health"
ansible gnode1 -i ansible/inventory/production -m shell -a "curl -s http://localhost:8080/health"  
ansible inode1 -i ansible/inventory/production -m shell -a "curl -s http://localhost:8080/health"
```

### Quick Reference Commands
```bash
# Load environment and navigate to terraform directory
# Note: Run from repository root, ensure env.sh contains all required credentials
cd $(pwd) && source env.sh && cd terraform

# Plan changes (load all environment variables from env.sh)
docker run --rm -v $(pwd):/app -w /app \
  -e AWS_ACCESS_KEY_ID="$AWS_ACCESS_KEY_ID" \
  -e AWS_SECRET_ACCESS_KEY="$AWS_SECRET_ACCESS_KEY" \
  -e GOOGLE_APPLICATION_CREDENTIALS="/app/google-credentials.json" \
  -e OCI_TENANCY_OCID="$OCI_TENANCY_OCID" \
  -e OCI_USER_OCID="$OCI_USER_OCID" \
  -e OCI_FINGERPRINT="$OCI_FINGERPRINT" \
  -e OCI_PRIVATE_KEY_PATH="/app/oci-private-key.pem" \
  -e OCI_COMPARTMENT_ID="$OCI_COMPARTMENT_ID" \
  -e OCI_REGION="$OCI_REGION" \
  -e IBMCLOUD_API_KEY="$IBMCLOUD_API_KEY" \
  -e IBMCLOUD_REGION="$IBMCLOUD_REGION" \
  callableapis:infra terraform plan

# Apply changes (load all environment variables from env.sh)
docker run --rm -v $(pwd):/app -w /app \
  -e AWS_ACCESS_KEY_ID="$AWS_ACCESS_KEY_ID" \
  -e AWS_SECRET_ACCESS_KEY="$AWS_SECRET_ACCESS_KEY" \
  -e GOOGLE_APPLICATION_CREDENTIALS="/app/google-credentials.json" \
  -e OCI_TENANCY_OCID="$OCI_TENANCY_OCID" \
  -e OCI_USER_OCID="$OCI_USER_OCID" \
  -e OCI_FINGERPRINT="$OCI_FINGERPRINT" \
  -e OCI_PRIVATE_KEY_PATH="/app/oci-private-key.pem" \
  -e OCI_COMPARTMENT_ID="$OCI_COMPARTMENT_ID" \
  -e OCI_REGION="$OCI_REGION" \
  -e IBMCLOUD_API_KEY="$IBMCLOUD_API_KEY" \
  -e IBMCLOUD_REGION="$IBMCLOUD_REGION" \
  callableapis:infra terraform apply

# Import existing resource (use appropriate environment variables)
docker run --rm -v $(pwd):/app -w /app -e [ENV_VARS] callableapis:infra terraform import [RESOURCE_TYPE].[RESOURCE_NAME] [RESOURCE_ID]
```

### Ansible Node Management Commands
```bash
# Update SSH keys on all nodes (non-destructive)
ansible-playbook -i ansible/inventory/production ansible/playbooks/update-ssh-keys.yml

# Deploy containers to all nodes
ansible-playbook -i ansible/inventory/production ansible/playbooks/debug-and-deploy.yml

# Verify container endpoints
ansible-playbook -i ansible/inventory/production ansible/playbooks/verify-container-endpoints.yml

# Test external access to endpoints
./test-container-endpoints.sh
```

## Cloud Infrastructure Connectivity Testing

**CRITICAL: Never use ping for cloud infrastructure testing**

### Ping is Outdated for Cloud Infrastructure
- **ICMP is often blocked** by cloud providers by default
- **External networks** cannot reliably ping cloud instances
- **Ping results are misleading** and don't reflect actual service availability
- **Use proper connectivity tests** instead of ping

### Proper Connectivity Testing Methods

#### 1. SSH Connectivity (Primary Test)
```bash
# Test SSH connectivity to all nodes
ansible all -i ansible/inventory/production -m ping

# Test specific node
ansible onode1 -i ansible/inventory/production -m ping
```

#### 2. Service Port Testing
```bash
# Test if services are listening on expected ports
ansible all -i ansible/inventory/production -m shell -a "ss -tlnp | grep :443" --become

# Test specific service
ansible onode1 -i ansible/inventory/production -m shell -a "ss -tlnp | grep :8080" --become
```

#### 3. HTTP/HTTPS Endpoint Testing
```bash
# Test HTTP endpoints with proper timeouts
curl --connect-timeout 5 --max-time 10 -s -o /dev/null -w "%{http_code}" https://onode1.callableapis.com/

# Test with SSL verification disabled for troubleshooting
curl --connect-timeout 5 --max-time 10 -k -s -o /dev/null -w "%{http_code}" https://192.9.154.97:443/
```

#### 4. Internal Service Testing (via Ansible)
```bash
# Test services from inside the node
ansible onode1 -i ansible/inventory/production -m shell -a "curl -s http://localhost:8080/health" --become

# Test Nginx configuration
ansible onode1 -i ansible/inventory/production -m shell -a "nginx -t" --become
```

### Prohibited Actions
- ❌ Using `ping` to test cloud instance connectivity
- ❌ Relying on ICMP responses for troubleshooting
- ❌ Assuming ping failure means service is down

### Required Actions
- ✅ Use SSH connectivity tests via Ansible
- ✅ Test service ports and listening status
- ✅ Use HTTP/HTTPS endpoint testing with proper timeouts
- ✅ Test services from inside the node when external tests fail
- ✅ Use Ansible for internal connectivity verification

## Container Deployment Verification

**CRITICAL: Verify containers are running where expected based on inventory groups**

### Container Deployment Rules
Containers must run only on hosts assigned in inventory groups:
- **Base Container**: Only on hosts in `base_container_hosts` group
- **Status Container**: Only on hosts in `status_container_hosts` group
- **Services Container**: Only on hosts in `services_container_hosts` group
- **Mutual Exclusion**: A host should only run containers for which it's explicitly assigned

### Checking Current Container Status
```bash
# Verify container deployment matches inventory expectations
ansible-playbook -i ansible/inventory/production ansible/playbooks/verify-container-deployment.yml

# Check which containers are running on a specific host
ansible onode1 -i ansible/inventory/production -m shell -a "docker ps" --become

# Check container port assignments
ansible onode1 -i ansible/inventory/production -m shell -a "docker port $(docker ps -q)" --become
```

### Resolving Container Misconfigurations
When containers are running on wrong hosts:

1. **Stop Incorrect Containers**
   ```bash
   # Stop containers that shouldn't be running
   ansible onode1 -i ansible/inventory/production -m shell -a "docker stop callableapis-status" --become
   ```

2. **Start Expected Containers**
   ```bash
   # Use the deployment playbook to start correct containers
   ansible-playbook -i ansible/inventory/production ansible/playbooks/containers/deploy-containers.yml
   ```

3. **Verify After Deploy**
   ```bash
   # Re-run verification
   ansible-playbook -i ansible/inventory/production ansible/playbooks/verify-container-deployment.yml
   ```

### Inventory Group Definition
Current assignment (from `ansible/inventory/production`):
- **base_container_hosts**: onode1, onode2, gnode1
- **status_container_hosts**: gnode1
- **services_container_hosts**: inode1

### Signs of Container Misconfiguration
- ❌ Container running on node not in its inventory group
- ❌ Multiple container types running on same host when only one is assigned
- ❌ Expected container not running on assigned host
- ❌ Port conflicts between containers

### Required Actions
- ✅ Use verification playbook to check container deployment
- ✅ Ensure containers only run on explicitly assigned hosts
- ✅ Stop incorrectly placed containers
- ✅ Deploy containers based on inventory groups
- ✅ Verify DNS records point to correct hosts for their assigned containers

## Container Service Endpoint Compliance

**CRITICAL: All containers must provide base container endpoints plus their own**

When evaluating or creating a new service container, it MUST provide all the standard endpoints that the base container provides, in addition to any service-specific endpoints.

### Base Container Endpoints (Required for All Containers)

Every container in the infrastructure MUST implement these four standard endpoints:

1. **`GET /`** - Root endpoint
   - **Flexible format**: Can return HTML (for user-facing containers like status dashboard) or JSON (for API services)
   - **HTML format**: User-friendly interface (e.g., status dashboard, API documentation landing page)
   - **JSON format**: `{"service": "Container Name", "version": "...", "status": "running", "uptime": "...", "timestamp": "..."}`
   - **Note**: If root returns HTML, JSON service info must be available via `/api/status` endpoint
   - **Examples**:
     - Status container: Returns HTML dashboard (primary use case for browser access)
     - Base container: Returns JSON service info
     - Services container: Can return HTML landing page with API docs, or JSON service info

2. **`GET /health`** - Health check endpoint
   - **MUST return JSON** with health status
   - Format: `{"status": "healthy", "timestamp": "...", "version": "..."}`
   - Used by load balancers, monitoring, and Docker health checks
   - **Critical**: This endpoint is used by automated systems and must be JSON

3. **`GET /api/health`** - API health check endpoint
   - **MUST return JSON** with API status
   - Format: `{"status": "ok", "timestamp": "...", "version": "..."}`
   - Used for API-level health monitoring
   - **Critical**: This endpoint is used by automated systems and must be JSON

4. **`GET /api/status`** - Detailed status endpoint
   - **MUST return JSON** with comprehensive service status
   - Format: `{"service": "...", "version": "...", "status": "running", "uptime": "...", "timestamp": "...", ...}`
   - May include additional service-specific information
   - **Critical**: This endpoint provides JSON service info when root endpoint returns HTML

### Service-Specific Endpoints

Containers may add their own additional endpoints beyond the base requirements:
- Status container: `/dashboard` (HTML dashboard)
- Services container: `/api/v1/*`, `/api/v2/*` (versioned API endpoints)

### Compliance Checklist

When evaluating or creating a new service container:

- ✅ **Root endpoint** (`/`): Returns HTML (for user-facing) or JSON (for API services)
  - If HTML: Must provide JSON alternative via `/api/status`
  - If JSON: Should match base container format
- ✅ **Health endpoint** (`/health`): **MUST return JSON** with format `{"status": "healthy", "timestamp": "...", "version": "..."}`
- ✅ **API health endpoint** (`/api/health`): **MUST return JSON** with format `{"status": "ok", "timestamp": "...", "version": "..."}`
- ✅ **Status endpoint** (`/api/status`): **MUST return JSON** with detailed status matching base container format
- ✅ **Service-specific endpoints**: May add additional endpoints beyond base requirements
- ✅ **Response format**: `/health`, `/api/health`, and `/api/status` MUST return JSON (root endpoint can be HTML or JSON)

### Example: Base Container Implementation

Reference implementation in `clint/container/base.py`:
```python
@app.route('/')
def home():
    return jsonify({
        "service": "CallableAPIs Base Container",
        "version": CONTAINER_VERSION,
        "status": "running",
        "uptime": str(datetime.now() - START_TIME),
        "timestamp": datetime.now().isoformat()
    })

@app.route('/health')
def health():
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": CONTAINER_VERSION
    })

@app.route('/api/health')
def api_health():
    return jsonify({
        "status": "ok",
        "timestamp": datetime.now().isoformat(),
        "version": CONTAINER_VERSION
    })

@app.route('/api/status')
def status():
    # Returns detailed status with additional information
    ...
```

### Verification

Test all required endpoints after deployment:
```bash
# Test root endpoint
curl http://localhost:8080/

# Test health endpoint
curl http://localhost:8080/health

# Test API health endpoint
curl http://localhost:8080/api/health

# Test status endpoint
curl http://localhost:8080/api/status
```

All endpoints should return JSON responses with appropriate status codes (200 for healthy services).

### Non-Compliant Containers

If a container does not provide all base endpoints:
- ❌ It is non-compliant and must be fixed
- ❌ Do not deploy non-compliant containers
- ❌ Update container implementation to add missing endpoints
- ❌ Verify compliance before deploying

# Task Instruction
All work and changes to the repository should be part of a task.  A task has a distinct starting point and measurable end goal.  If you feel like you are not presently in a task, ask for more detailed instructions or clarity on any underdeveloped parts of the problem.  Once the problem is well understood and appropriately broken down it will be tracked in a Github Issue.

When Starting a distinct task that has a clear starting point and end goal, create an Issue in the github issue tracker via the github MCP (configured via Cursor MCPs) and start a branch named after a 5 digit issue's ID left padded with 0s and suffixed with a snake case identifier transformation of the issue title.  You should check into this branch often and check github action statuses on your checkins fixing any problems that arise with them.  When the task is complete, create a PR against main for me to review and merge.

Issue tracking should take the place of status markdowns in the repository.

# Automatic Task Instructions
Once a task is started and a Github Issue is created the following steps in the task should be performed
## Starting Steps
1. Create branch as described in Task Instruction
2. Evaluate existing checks in run_checks.sh and augment them as well as checks in github actions, updating them when they are out of date or superceded by other methodology.
3. If checks introduced in step 2 of starting steps fail, those failures become part of the scope of this task.
## Closing Steps
1. Verify changes are logically complete and consistent with the overall style of the project
2. Run all checks defined in the run_checks.sh
3. Clean up any artifacts that might have been created during development of the task.  Add relevant entries to .gitignore. Fix problems found with step 2.  If there were problems fixed, return to step 1.  
4. Check in all relevant changes and new files into the branch.  Push changes to to remote.
5. **Create a pull request against main that references the GitHub issue using "Closes #<issue_number>" in the PR title or description.**
6. Wait for verification github action to complete.  If the action fails, analyze failure treating that failure like a local test failure and return to step 3.
7. When previous closing steps are complete, update the GitHub issue with what was accomplished.

