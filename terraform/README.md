# Multi-Cloud Infrastructure with Terraform

This directory contains Terraform configurations for managing infrastructure across multiple cloud providers.

## 📁 Directory Structure

```
terraform/
├── main.tf              # Main configuration with Cloudflare DNS
├── variables.tf         # Global variables
├── outputs.tf          # Global outputs
├── providers.tf        # Provider configurations
├── aws/                # AWS-specific resources
│   ├── main.tf         # AWS infrastructure
│   ├── variables.tf    # AWS variables
│   ├── outputs.tf      # AWS outputs
│   └── user_data/      # User data scripts
├── oracle/             # Oracle Cloud resources
│   ├── main.tf         # Oracle infrastructure
│   ├── variables.tf    # Oracle variables
│   ├── outputs.tf      # Oracle outputs
│   └── user_data.sh    # User data script
├── google/             # Google Cloud resources
├── ibm/                # IBM Cloud resources
└── ssh_keys/           # SSH key management
    ├── main.tf         # SSH key generation
    ├── variables.tf    # SSH key variables
    └── inventory       # Ansible inventory
```

## 🚀 Usage

### Deploy All Infrastructure
```bash
# Initialize and apply all resources
terraform init
terraform plan
terraform apply
```

### Deploy Specific Provider
```bash
# Deploy only AWS resources
cd aws
terraform init
terraform apply

# Deploy only Oracle Cloud resources
cd oracle
terraform init
terraform apply
```

### SSH Key Management
```bash
# Generate SSH keys for all providers
cd ssh_keys
terraform init
terraform apply
```

## 🔧 Environment Variables

Set these environment variables before running Terraform:

```bash
# AWS
export AWS_ACCESS_KEY_ID="your-access-key"
export AWS_SECRET_ACCESS_KEY="your-secret-key"
export AWS_DEFAULT_REGION="us-west-2"

# Cloudflare
export CLOUDFLARE_API_TOKEN="your-api-token"
export CLOUDFLARE_ZONE_ID="your-zone-id"

# Oracle Cloud
export OCI_TENANCY_OCID="your-tenancy-ocid"
export OCI_USER_OCID="your-user-ocid"
export OCI_FINGERPRINT="your-fingerprint"
export OCI_PRIVATE_KEY_PATH="path/to/private-key.pem"
export OCI_COMPARTMENT_ID="your-compartment-id"
export OCI_REGION="us-sanjose-1"

# GitHub OAuth
export GITHUB_CLIENT_ID="your-client-id"
export GITHUB_CLIENT_SECRET="your-client-secret"
```

## 📊 Resources by Provider

### AWS (us-west-2)
- **Elastic Beanstalk**: Java API application
- **S3 Bucket**: Static website hosting
- **Route53**: DNS management (handled by Cloudflare)
- **IAM**: Users and policies

### Oracle Cloud (us-sanjose-1)
- **2x ARM Instances**: 2 OCPUs, 12GB RAM each (Always Free)
- **VCN**: Virtual Cloud Network
- **Security Groups**: SSH, HTTP, HTTPS access

### Google Cloud
- **1x e2-micro**: 1 vCPU, 1GB RAM (Always Free)

### IBM Cloud
- **1x VSI**: Virtual Server Instance (Always Free)

## 🔐 SSH Access

After deployment, you can access instances using:

```bash
# Oracle Cloud instances
ssh ubuntu@<oracle-arm-1-ip>
ssh ubuntu@<oracle-arm-2-ip>

# AWS Elastic Beanstalk
ssh ec2-user@<eb-instance-ip>
```

## 📈 Cost Optimization

- **AWS**: Using t4g.micro (free tier eligible)
- **Oracle Cloud**: Always Free tier (4 OCPUs, 24GB RAM total)
- **Google Cloud**: Always Free tier (e2-micro)
- **IBM Cloud**: Always Free tier (VSI)

**Total Monthly Cost**: $0.00 for compute resources