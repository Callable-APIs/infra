# Project Instruction

## Use of Docker

For isolating command line dependencies and execution of commands you will use a Docker container.  If one does not yet exist, create a Dockerfile and as dependencies or command line tools / libraries are needed add them to the docker container.   All execution of local command should happen in the Docker container where the project directory is shared as a volume.

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

