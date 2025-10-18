# 🔐 Secrets Management Guide

## **The Problem You Identified**

> "How does the servlet get the secret to unlock the vault without that secret itself being part of a build and therefore exposed?"

**Answer: The vault password is never stored in the container image!**

## 🎯 **How It Works**

### **1. Vault Password Storage**
```
Host (onode1, gnode1, etc.)          Container
├── /opt/callableapis/               ├── /app/vault-password (mounted)
│   └── vault-password               ├── /app/secrets/ (mounted)
└── /opt/callableapis/secrets/       └── secrets_manager.py
    └── all-secrets.env (encrypted)
```

### **2. Container Startup Process**
```python
# 1. Container starts
# 2. Reads vault password from mounted file
# 3. Uses password to decrypt secrets
# 4. Loads secrets into environment variables
# 5. API runs with access to secrets
```

## 🔧 **Implementation Details**

### **Step 1: Setup Vault Password on Host**
```bash
# On each node (onode1, gnode1, inode1)
echo "your-vault-password" > /opt/callableapis/vault-password
chmod 600 /opt/callableapis/vault-password
```

### **Step 2: Deploy Encrypted Secrets**
```bash
# Deploy secrets to all nodes
ansible-playbook -i inventory/production playbooks/deploy-secrets.yml --ask-vault-pass
```

### **Step 3: Run Container with Mounted Secrets**
```bash
# Container mounts both password file and secrets
docker run -d \
  --name callableapis-api \
  -v /opt/callableapis/vault-password:/app/vault-password:ro \
  -v /opt/callableapis/secrets:/app/secrets:ro \
  callableapis/api:latest
```

### **Step 4: API Loads Secrets at Runtime**
```python
# In your API code
secrets_manager = SecretsManager()
secrets_manager.setup_environment()  # Loads all secrets into os.environ
```

## 🛡️ **Security Model**

### **What's Secure:**
- ✅ Vault password never in container image
- ✅ Secrets encrypted at rest
- ✅ Password file has 600 permissions (owner only)
- ✅ Container runs as non-root user
- ✅ Secrets only decrypted in memory

### **What's Not Secure:**
- ❌ Vault password visible in process list (but only on host)
- ❌ Secrets visible in container environment variables
- ❌ Anyone with host access can read vault password

## 🔄 **Alternative Approaches**

### **Option 1: Cloud Provider Secrets (Most Secure)**
```python
# Fetch vault password from cloud provider
def get_vault_password():
    if os.getenv('AWS_REGION'):
        # AWS Secrets Manager
        client = boto3.client('secretsmanager')
        response = client.get_secret_value(SecretId='callableapis/vault-password')
        return response['SecretString']
    # ... other clouds
```

### **Option 2: Environment Variables (Simplest)**
```bash
# Set vault password as environment variable
export ANSIBLE_VAULT_PASSWORD="your-password"
docker run -e ANSIBLE_VAULT_PASSWORD="$ANSIBLE_VAULT_PASSWORD" callableapis/api
```

### **Option 3: HashiCorp Vault (Enterprise)**
```python
# Fetch secrets directly from Vault
import hvac
client = hvac.Client(url='https://vault.example.com')
client.token = os.getenv('VAULT_TOKEN')
secrets = client.secrets.kv.v2.read_secret_version(path='callableapis/secrets')
```

## 🚀 **Quick Start**

### **1. Create Vault Password File**
```bash
# On each node
ansible-playbook -i inventory/production playbooks/setup-vault-password.yml
```

### **2. Create Encrypted Secrets**
```bash
# Create secrets file
ansible/scripts/encrypt-secrets.sh create

# Edit secrets
ansible/scripts/encrypt-secrets.sh edit
```

### **3. Deploy Secrets**
```bash
# Deploy to all nodes
ansible-playbook -i inventory/production playbooks/deploy-secrets.yml --ask-vault-pass
```

### **4. Test Container**
```bash
# Test secrets loading
docker run --rm \
  -v /opt/callableapis/vault-password:/app/vault-password:ro \
  -v /opt/callableapis/secrets:/app/secrets:ro \
  callableapis/api:latest \
  python3 -c "from src.secrets_manager import SecretsManager; print(SecretsManager().load_secrets())"
```

## 🔍 **Troubleshooting**

### **Check Secrets Status**
```bash
# Via API endpoint
curl https://api.callableapis.com/api/secrets/status

# Direct container check
docker exec callableapis-api python3 -c "from src.secrets_manager import SecretsManager; print(SecretsManager().load_secrets())"
```

### **Common Issues**
1. **Vault password file not found**: Check file exists and has correct permissions
2. **Secrets file not found**: Run deploy-secrets playbook
3. **Decryption failed**: Check vault password is correct
4. **Permission denied**: Check file ownership and permissions

## 📊 **Security Comparison**

| Method | Security | Complexity | Cloud Agnostic | Cost |
|--------|----------|------------|----------------|------|
| **Vault Password File** | ⭐⭐⭐ | ⭐⭐ | ✅ | Free |
| **Environment Variables** | ⭐⭐ | ⭐ | ✅ | Free |
| **Cloud Provider Secrets** | ⭐⭐⭐⭐ | ⭐⭐⭐ | ❌ | $ |
| **HashiCorp Vault** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ✅ | $$ |

## 💡 **Recommendation**

For your multi-cloud setup, **Vault Password File** is the sweet spot:
- ✅ Works across all cloud providers
- ✅ No additional infrastructure
- ✅ Good security for your use case
- ✅ Simple to implement and maintain

The vault password is only stored on the host (not in the container), and secrets are only decrypted in memory when needed.
