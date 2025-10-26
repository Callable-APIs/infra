# SSL Certificate Management System

This document describes the comprehensive SSL certificate management system for CallableAPIs infrastructure using Cloudflare Origin Certificates.

## Overview

The system provides automated generation, deployment, and management of SSL certificates for end-to-end encryption between Cloudflare and our infrastructure nodes.

## Architecture

```
Cloudflare (Strict SSL) ↔ Oracle/Google/IBM Nodes (Cloudflare Origin Certificates) ↔ Nginx ↔ Containers
```

## Certificate Lifecycle

### 1. Initial Setup

```bash
# Generate CSR and private key
ansible-playbook generate-cloudflare-origin-certificates.yml

# Create Cloudflare Origin Certificate via Terraform
cd terraform && source ../env.sh
docker run --rm -v $(pwd):/app -w /app -e [ENV_VARS] \
  callableapis:infra terraform apply -var-file=cloudflare-csr.tfvars \
  -target=cloudflare_origin_ca_certificate.callableapis_origin_cert -auto-approve

# Retrieve certificate from Terraform
ansible-playbook retrieve-cloudflare-certificate.yml

# Deploy to all nodes
ansible-playbook deploy-ssl-certificates.yml

# Restart Nginx
ansible-playbook restart-nginx.yml
```

### 2. Complete Automated Setup

```bash
# One-command setup (recommended)
ansible-playbook setup-cloudflare-ssl.yml
```

### 3. Adding New Nodes

```bash
# Add new node to existing certificate
ansible-playbook add-node-to-certificate.yml \
  -e "node_hostname=new-node.callableapis.com" \
  -e "node_ip=1.2.3.4"
```

## Playbooks

### Core Playbooks

| Playbook | Purpose | When to Use |
|----------|---------|-------------|
| `generate-cloudflare-origin-certificates.yml` | Generate CSR and private key | Initial setup or certificate rotation |
| `retrieve-cloudflare-certificate.yml` | Get certificate from Terraform | After Terraform creates certificate |
| `deploy-ssl-certificates.yml` | Deploy certificates to nodes | After certificate generation/update |
| `setup-cloudflare-ssl.yml` | Complete automated setup | Initial setup or full refresh |
| `restart-nginx.yml` | Restart Nginx services | After certificate deployment |

### Utility Playbooks

| Playbook | Purpose | When to Use |
|----------|---------|-------------|
| `add-node-to-certificate.yml` | Add new node to certificate | When adding new infrastructure nodes |

## File Structure

```
ansible/
├── artifacts/
│   └── ssl/
│       ├── privkey.pem          # Private key (2048-bit RSA)
│       ├── cert.pem             # Cloudflare Origin Certificate
│       ├── fullchain.pem        # Same as cert.pem (no intermediates)
│       ├── chain.pem            # Empty file (no intermediates)
│       ├── cert.csr             # Certificate Signing Request
│       ├── cert_single_line.csr # CSR in single line format for Terraform
│       └── san.conf             # SAN configuration file
├── playbooks/
│   ├── generate-cloudflare-origin-certificates.yml
│   ├── retrieve-cloudflare-certificate.yml
│   ├── deploy-ssl-certificates.yml
│   ├── setup-cloudflare-ssl.yml
│   ├── restart-nginx.yml
│   └── add-node-to-certificate.yml
└── inventory/
    └── production               # Node inventory

terraform/
├── cloudflare-csr.tfvars       # CSR for Terraform
├── cloudflare-origin-cert.tf   # Terraform certificate resource
└── main.tf                     # Main Terraform configuration
```

## Certificate Details

### Cloudflare Origin Certificates

- **Type**: RSA 2048-bit
- **Validity**: 15 years
- **Issuer**: Cloudflare Origin CA
- **Hostnames**: All infrastructure nodes
- **No Intermediate Certificates**: Cloudflare Origin Certificates are self-contained

### Supported Hostnames

- `callableapis.com`
- `*.callableapis.com`
- `onode1.callableapis.com`
- `onode2.callableapis.com`
- `gnode1.callableapis.com`
- `inode1.callableapis.com`

## Security Considerations

### File Permissions

- **Private Key**: `0600` (root:root)
- **Certificates**: `0644` (root:root)
- **Nginx SSL Directory**: `0755` (root:root)

### Backup Strategy

- All certificate files are backed up before deployment
- Private keys are stored securely in `ansible/artifacts/ssl/`
- Certificates are retrieved from Terraform state (source of truth)

## Troubleshooting

### Common Issues

1. **Certificate and Private Key Mismatch**
   ```bash
   # Verify modulus match
   openssl x509 -noout -modulus -in cert.pem | openssl md5
   openssl rsa -noout -modulus -in privkey.pem | openssl md5
   ```

2. **Nginx SSL Errors**
   ```bash
   # Check Nginx error logs
   sudo journalctl -xeu nginx.service
   
   # Verify certificate validity
   openssl x509 -in cert.pem -text -noout
   ```

3. **Cloudflare API Token Issues**
   - Ensure token has "SSL and Certificates:Edit" permission
   - Verify token is not expired
   - Check token scope includes the correct zone

### Validation Commands

```bash
# Run comprehensive infrastructure validation
./run_infrastructure_checks.sh

# Test certificate deployment
ansible-playbook deploy-ssl-certificates.yml --check

# Verify certificate on node
ansible onode1 -i ansible/inventory/production -m shell -a "openssl x509 -in /etc/ssl/callableapis/cert.pem -text -noout"
```

## Maintenance

### Certificate Rotation

1. Generate new CSR and private key
2. Create new Cloudflare Origin Certificate
3. Deploy to all nodes
4. Restart Nginx services

### Adding New Nodes

1. Add node to inventory
2. Update certificate to include new hostname
3. Deploy updated certificate
4. Configure Nginx on new node

### Monitoring

- Certificate expiration: 15 years (very long-lived)
- Monitor Cloudflare Origin Certificate status
- Check Nginx SSL configuration regularly

## Integration with CI/CD

The certificate management system integrates with:

- **Terraform**: Infrastructure as Code
- **Ansible**: Configuration Management
- **Docker**: Containerized Terraform execution
- **GitHub Actions**: Automated validation

## Best Practices

1. **Always use timeouts** for external commands
2. **Backup certificates** before deployment
3. **Validate certificate-key matching** before deployment
4. **Test locally** before external deployment
5. **Use infrastructure validation script** for comprehensive checks
6. **Document all certificate changes** in commit messages

## Support

For issues with the certificate management system:

1. Check the troubleshooting section above
2. Run `./run_infrastructure_checks.sh` for comprehensive validation
3. Review Ansible playbook logs for detailed error information
4. Verify Cloudflare API token permissions and Terraform state
