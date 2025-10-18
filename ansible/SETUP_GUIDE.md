# 🚀 CallableAPIs Setup Guide

## **Quick Start**

### **1. Setup Inventory**
```bash
# Create production inventory from template
ansible/scripts/setup-inventory.sh

# Edit the inventory with your actual IPs
nano ansible/inventory/production
```

### **2. Build Secrets**
```bash
# Build GitHub OIDC secrets locally
ansible/scripts/build-secrets.sh
```

### **3. Deploy Everything**
```bash
# Deploy secrets and base container
ansible/scripts/deploy-api.sh
```

## 📁 **File Structure**

```
ansible/
├── inventory/
│   ├── production.in          # Template (in git)
│   └── production             # Your actual inventory (gitignored)
├── artifacts/                 # Local secrets (gitignored)
│   ├── vault-password
│   ├── secrets.yml
│   └── *.sha256
├── scripts/
│   ├── setup-inventory.sh     # Create inventory from template
│   ├── build-secrets.sh       # Build secrets locally
│   └── deploy-api.sh          # Deploy everything
└── playbooks/
    ├── deploy-secrets-simple.yml
    └── api-deploy-simple.yml
```

## 🔧 **Detailed Setup**

### **Step 1: Create Inventory**

The template (`production.in`) contains placeholders:

```ini
[oracle_cloud]
oracle_node1 ansible_host=YOUR_ORACLE_IP ansible_user=ansible provider=oracle role=primary

[google_cloud]
google_node1 ansible_host=YOUR_GOOGLE_IP ansible_user=ansible provider=google role=monitoring

[ibm_cloud]
ibm_node1 ansible_host=YOUR_IBM_IP ansible_user=ansible provider=ibm role=services

[api_servers]
oracle_node1 ansible_host=YOUR_ORACLE_IP ansible_user=ansible provider=oracle role=api_server
```

Replace with your actual values:
- `YOUR_ORACLE_IP` → Your Oracle Cloud IP
- `YOUR_GOOGLE_IP` → Your Google Cloud IP
- `YOUR_IBM_IP` → Your IBM Cloud IP
- `yourdomain.com` → Your actual domain
- `your_private_key` → Your SSH private key filename

### **Step 2: Build Secrets**

The script will prompt for:
- GitHub Client ID
- GitHub Client Secret
- GitHub Redirect URI (defaults to `https://api.callableapis.com/api/auth/callback`)

### **Step 3: Deploy**

The deployment script will:
1. Deploy secrets to all hosts (`/etc/vault-secrets/`)
2. Verify checksums
3. Deploy base container with secrets mounted
4. Test endpoints

## 🛡️ **Security Features**

- ✅ **No sensitive data in git** - inventory and secrets are gitignored
- ✅ **Local secrets build** - credentials never leave your machine
- ✅ **Checksum verification** - ensures file integrity
- ✅ **Minimal secrets** - only GitHub OIDC deployed to containers
- ✅ **Template-based** - easy to recreate inventory

## 🧪 **Testing**

### **Test Inventory**
```bash
# Test connection to all hosts
ansible all -i inventory/production -m ping

# Test specific group
ansible api_servers -i inventory/production -m ping
```

### **Test Container**
```bash
# Check health endpoint
curl http://oracle_node1.yourdomain.com:8080/health

# Check status endpoint (shows secrets info)
curl http://oracle_node1.yourdomain.com:8080/api/status
```

### **Test Secrets**
```bash
# Verify secrets on host
ssh ansible@oracle_node1 "ls -la /etc/vault-secrets/"

# Test vault decryption
ssh ansible@oracle_node1 "cd /etc/vault-secrets && ansible-vault view secrets.yml --vault-password-file vault-password"
```

## 🔄 **Adding New Hosts**

1. **Edit inventory** (`ansible/inventory/production`)
2. **Add new host** to appropriate group
3. **Test connection**: `ansible new_host -i inventory/production -m ping`
4. **Deploy**: `ansible/scripts/deploy-api.sh`

## 🚨 **Troubleshooting**

### **Inventory Issues**
- Check IP addresses are correct
- Verify SSH key is in `ansible/keys/callableapis_private_key`
- Test SSH manually: `ssh ansible@your_host`

### **Secrets Issues**
- Rebuild secrets: `ansible/scripts/build-secrets.sh`
- Check artifacts exist: `ls -la ansible/artifacts/`
- Verify checksums: `cd ansible/artifacts && sha256sum -c *.sha256`

### **Container Issues**
- Check containerd is running: `nerdctl ps`
- Check container logs: `nerdctl logs callableapis-base`
- Test endpoints: `curl http://localhost:8080/health`

## 💡 **Best Practices**

1. **Keep inventory updated** - IPs can change
2. **Rebuild secrets** when credentials change
3. **Test connections** before deploying
4. **Monitor container logs** for issues
5. **Use version control** for your production inventory (private repo)

Perfect for keeping sensitive data out of the public repo while maintaining easy setup!
