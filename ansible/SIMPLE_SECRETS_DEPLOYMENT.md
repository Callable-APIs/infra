# 🔐 Simple Secrets Deployment

## **New Approach: Local Build + SCP**

Much simpler and more secure than the previous approach:

1. **Build secrets locally** (vault file + password file)
2. **Store in artifacts directory** 
3. **SCP to hosts** with checksum verification
4. **Start with just GitHub OIDC** credentials

## 🚀 **Quick Start**

### **1. Build Secrets Locally**
```bash
# Build secrets with GitHub OIDC credentials
ansible/scripts/build-secrets.sh
```

This will:
- Prompt for GitHub OIDC credentials
- Generate vault password
- Create encrypted secrets file
- Store in `ansible/artifacts/` directory
- Generate checksums for verification

### **2. Deploy Everything**
```bash
# Deploy secrets and container
ansible/scripts/deploy-api.sh
```

This will:
- Deploy secrets to all hosts (`/etc/vault-secrets/`)
- Verify checksums
- Deploy base container with secrets mounted
- Test endpoints

## 📁 **File Structure**

```
ansible/
├── artifacts/                    # Local secrets (gitignored)
│   ├── vault-password           # Vault password file
│   ├── secrets.yml              # Encrypted secrets
│   ├── vault-password.sha256    # Checksum
│   └── secrets.yml.sha256       # Checksum
├── scripts/
│   ├── build-secrets.sh         # Build secrets locally
│   └── deploy-api.sh            # Deploy everything
└── playbooks/
    ├── deploy-secrets-simple.yml # Deploy secrets to hosts
    └── api-deploy-simple.yml     # Deploy container
```

## 🔧 **What Gets Deployed**

### **Secrets (GitHub OIDC Only)**
```yaml
# /etc/vault-secrets/secrets.yml (encrypted)
vault_github_client_id: "your_client_id"
vault_github_client_secret: "your_client_secret"
vault_github_redirect_uri: "https://api.callableapis.com/api/auth/callback"

# Note: All other credentials (AWS, Cloudflare, Oracle, Google, IBM) 
# are managed locally in env.sh and not deployed to containers
```

### **Container Mounts**
```bash
# Container runs with secrets mounted
-v /etc/vault-secrets/vault-password:/app/vault-password:ro
-v /etc/vault-secrets/secrets.yml:/app/secrets/all-secrets.env:ro
```

## 🛡️ **Security Features**

- ✅ **Local build only** - no credentials in git
- ✅ **Checksum verification** - ensures file integrity
- ✅ **Minimal secrets** - only GitHub OIDC deployed to containers
- ✅ **Read-only mounts** - container can't modify secrets
- ✅ **Proper permissions** - 600 on secrets, 700 on directory

## 🔄 **Adding More Secrets**

To add more secrets later:

1. **Edit build script** (`ansible/scripts/build-secrets.sh`)
2. **Add new prompts** for additional credentials
3. **Update secrets file** template
4. **Rebuild and redeploy**

## 🧪 **Testing**

### **Check Secrets Status**
```bash
# Test container status endpoint
curl http://onode1.callableapis.com:8080/api/status
```

### **Verify Secrets Deployment**
```bash
# Check files on host
ssh ansible@onode1 "ls -la /etc/vault-secrets/"

# Test vault decryption
ssh ansible@onode1 "cd /etc/vault-secrets && ansible-vault view secrets.yml --vault-password-file vault-password"
```

## 💡 **Benefits**

- **Simple**: No complex Ansible vault management
- **Secure**: Credentials never in git or Ansible files
- **Fast**: Local build, SCP deployment
- **Verifiable**: Checksums ensure integrity
- **Minimal**: Only GitHub OIDC deployed to containers
- **Clean separation**: Infrastructure credentials stay in env.sh

Perfect for getting started quickly while maintaining security!
