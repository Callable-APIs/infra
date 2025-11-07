# CallableAPIs Multi-Cloud Infrastructure

A comprehensive multi-cloud infrastructure management platform using Terraform, Ansible, and Docker to deploy and manage services across AWS, Google Cloud, Oracle Cloud, and IBM Cloud using free-tier resources.

## 🎯 Overview

This repository contains infrastructure-as-code for deploying and managing a multi-cloud infrastructure that maximizes free-tier resources while maintaining zero cost for compute instances. The platform includes:

- **Multi-cloud deployment** across AWS, Google Cloud, Oracle Cloud, and IBM Cloud
- **Containerized services** using Docker
- **Unified CLI tool** (`clint`) for infrastructure management
- **Automated billing reporting** with multi-cloud cost analysis
- **Infrastructure as Code** with Terraform
- **Configuration management** with Ansible

## 📊 Current Infrastructure

### Free Tier Compliant Nodes

| Provider | Node | Instance Type | vCPUs | RAM | Container | Status |
|----------|------|---------------|-------|-----|-----------|--------|
| AWS | anode1 | t2.micro | 1 | 1GB | Services | ✅ Active |
| Google Cloud | gnode1 | e2-micro | 1 | 1GB | Status | ✅ Active |

**Total Monthly Cost**: $0.00 (100% free tier compliant)

### Container Services

- **Base Container**: Provides standard API endpoints (`/`, `/health`, `/api/health`, `/api/status`)
- **Status Container**: Infrastructure monitoring dashboard at `https://status.callableapis.com`
- **Services Container**: Application services and APIs

## 🚀 Quick Start

### Prerequisites

- Docker (for running infrastructure tools)
- Python 3.10+ (for local development)
- Poetry (for Python dependency management)
- Terraform (via Docker container)
- Ansible (for configuration management)

### Initial Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Callable-APIs/infra.git
   cd infra
   ```

2. **Configure environment:**
   ```bash
   cp env.sh.in env.sh
   # Edit env.sh with your cloud provider credentials
   source env.sh
   ```

3. **Build the infrastructure Docker image:**
   ```bash
   docker build -t callableapis:infra .
   ```

4. **Deploy infrastructure:**
   ```bash
   cd terraform
   docker run --rm -v $(pwd):/app -w /app \
     -e AWS_ACCESS_KEY_ID="$AWS_ACCESS_KEY_ID" \
     -e AWS_SECRET_ACCESS_KEY="$AWS_SECRET_ACCESS_KEY" \
     # ... other env vars ...
     callableapis:infra terraform init
     callableapis:infra terraform plan
     callableapis:infra terraform apply
   ```

5. **Deploy containers:**
   ```bash
   ansible-playbook -i ansible/inventory/production \
     ansible/playbooks/containers/deploy-containers.yml
   ```

## 🛠️ CLINT - Command Line Infrastructure Tool

All Python-based infrastructure tools are centralized in the `clint` module and accessible via a unified CLI.

### Installation

The `clint` module is automatically installed when you build the Docker image or install Poetry dependencies:

```bash
# Via Docker (recommended)
docker run --rm -v $(pwd):/app -w /app callableapis:infra python -m clint --help

# Via Poetry (local development)
poetry install
poetry run python -m clint --help
```

### Available Commands

#### Billing and Cost Reporting

```bash
# Daily cost breakdown with month-over-month comparison
python -m clint billing --daily --compare

# Daily costs only
python -m clint billing --daily

# Month-over-month comparison only
python -m clint billing --compare

# Specific providers
python -m clint billing --daily --providers aws oracle

# Custom date range
python -m clint billing --daily --start 2024-01-01 --end 2024-01-31
```

#### Oracle Cloud Utilities

```bash
# Check ARM instance capacity across regions
python -m clint oracle check-capacity
```

#### Terraform Tools

```bash
# Discover existing infrastructure
python -m clint terraform discover

# Generate Terraform configuration
python -m clint terraform generate
```

#### Container Management

```bash
# Run base container application
python -m clint container base

# Run status container application
python -m clint container status
```

### Convenience Scripts

Several shell scripts wrap `clint` commands for easier execution:

```bash
# Billing reports
./scripts/run-billing-report.sh --daily --compare

# Oracle Cloud capacity search
./scripts/find-oracle-arm-capacity.sh
```

## 📁 Project Structure

```
infra/
├── clint/                    # Unified CLI tool (all Python code)
│   ├── __main__.py          # Main CLI entry point
│   ├── billing/             # Billing adapters (AWS, OCI, IBM)
│   ├── container/           # Container applications (base, status)
│   └── secrets/             # Secrets management strategies
├── ansible/                  # Ansible playbooks and configuration
│   ├── inventory/          # Host inventory
│   ├── playbooks/          # Deployment playbooks
│   └── artifacts/          # Secrets and artifacts (gitignored)
├── terraform/               # Terraform infrastructure definitions
│   ├── main.tf             # Main multi-cloud configuration
│   ├── providers.tf        # Cloud provider configurations
│   └── variables.tf        # Variable definitions
├── containers/              # Container definitions
│   ├── base/               # Base container Dockerfile
│   └── status/             # Status container Dockerfile
├── scripts/                 # Utility shell scripts
├── .github/workflows/      # CI/CD pipelines
├── Dockerfile              # Main infrastructure tools image
├── pyproject.toml          # Python dependencies (Poetry)
└── README.md               # This file
```

## 🔧 Infrastructure Management

### Terraform

All infrastructure is managed through Terraform with S3-backed state:

- **State Backend**: S3 bucket `callableapis-terraform-state` in `us-west-2`
- **Locking**: DynamoDB table `callableapis-terraform-locks`
- **Multi-Cloud**: Single state file for all providers

**Important**: Always use the Docker container for Terraform operations:

```bash
docker run --rm -v $(pwd):/app -w /app \
  -e AWS_ACCESS_KEY_ID="$AWS_ACCESS_KEY_ID" \
  # ... other env vars ...
  callableapis:infra terraform [command]
```

### Ansible

Configuration management and container deployment:

```bash
# Update SSH keys
ansible-playbook -i ansible/inventory/production \
  ansible/playbooks/update-ssh-keys.yml

# Deploy containers
ansible-playbook -i ansible/inventory/production \
  ansible/playbooks/containers/deploy-containers.yml

# Verify endpoints
ansible-playbook -i ansible/inventory/production \
  ansible/playbooks/verify-container-endpoints.yml
```

### Container Deployment

Containers are built via GitHub Actions and pushed to Docker Hub:

- **Base Container**: `rl337/callableapis:base`
- **Status Container**: `rl337/callableapis:status`
- **Services Container**: `rl337/callableapis:services`

All containers support multi-platform builds (amd64 and arm64) for Oracle Cloud ARM instances.

## 🔐 Secrets Management

Secrets are managed using a strategy pattern with Ansible Vault as the default:

- **Storage**: Encrypted files in `ansible/artifacts/` (gitignored)
- **Strategy**: Ansible Vault (extensible to HashiCorp Vault)
- **Distribution**: Deployed to nodes via Ansible playbooks
- **Runtime**: Mounted into containers at runtime

**Never commit secrets to git!** Use `env.sh.in` as a template and keep actual credentials in `env.sh` (gitignored).

## 📊 Billing and Cost Management

### Multi-Cloud Billing Reports

Generate comprehensive billing reports across all cloud providers:

```bash
# Full report (daily + month-over-month)
./scripts/run-billing-report.sh

# Daily breakdown only
./scripts/run-billing-report.sh --daily-only

# Specific providers
./scripts/run-billing-report.sh --providers aws oracle
```

### Free Tier Compliance

All active infrastructure is free tier compliant:

- **AWS**: t2.micro (always free tier eligible)
- **Google Cloud**: e2-micro (always free tier)
- **Oracle Cloud**: VM.Standard.A1.Flex ARM instances (always free tier)
- **IBM Cloud**: cx2-2x4 (free tier eligible)

## 🧪 Testing and Validation

### Run All Checks

```bash
./run_checks.sh
```

This runs:
- Code formatting (Black, isort)
- Type checking (mypy)
- Security scanning (bandit)
- Unit tests (pytest)
- Docker build validation

### Test Container Endpoints

```bash
./test-container-endpoints.sh
```

Tests all required endpoints (`/`, `/health`, `/api/health`, `/api/status`) across all nodes.

## 📚 Documentation

- **AGENTS.md**: Comprehensive development guidelines and design principles
- **terraform/README.md**: Terraform-specific documentation
- **ansible/SETUP_GUIDE.md**: Ansible setup and usage guide

## 🔄 Development Workflow

### Task Management

All work should be tracked via GitHub Issues:

1. Create a GitHub Issue for the task
2. Create a branch: `00001-task-description` (5-digit issue ID + snake_case title)
3. Make changes and commit frequently
4. Run `./run_checks.sh` before committing
5. Create a PR with "Closes #<issue_number>"
6. Wait for GitHub Actions to pass
7. Update the issue with completion status

### Code Organization

**CRITICAL**: All Python code must be in the `clint/` module:

- ✅ **Good**: `clint/billing/aws_adapter.py`
- ❌ **Bad**: `src/billing.py` or `scripts/billing.py`

See `AGENTS.md` for detailed guidelines.

## 🚨 Troubleshooting

### Terraform State Issues

If Terraform reports "No changes" but resources are missing:

1. Check for commented-out resources in `terraform/main.tf`
2. Compare state with actual cloud resources
3. Uncomment and apply missing resources

### Container Endpoint Issues

If containers aren't responding:

1. Check container status: `ansible all -i ansible/inventory/production -m shell -a "docker ps"`
2. Verify inventory groups match container assignments
3. Test endpoints: `./test-container-endpoints.sh`

### Billing API Issues

If billing reports fail:

1. Verify credentials in `env.sh`
2. Check API permissions for each provider
3. Review error messages in the report output

## 📝 License

MIT License - See LICENSE file for details

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (following task workflow above)
3. Make your changes
4. Run `./run_checks.sh` to validate
5. Submit a pull request

## 🔗 Links

- **Status Dashboard**: https://status.callableapis.com
- **GitHub Repository**: https://github.com/Callable-APIs/infra
- **Issue Tracker**: https://github.com/Callable-APIs/infra/issues

---

**Note**: This infrastructure is designed to operate entirely within free-tier limits. All active nodes are free tier compliant, resulting in $0.00 monthly compute costs.
