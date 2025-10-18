# Container Setup Guide

## 🐳 **Docker Hub Configuration**

### **Why Docker Hub?**
- **Unlimited public repos** (perfect for open source services)
- **No storage limits** for public images
- **Better for decentralized architecture** (multiple 256MB containers)
- **Keeps sensitive infra config private** while services are open source
- **Function-based tagging** for organized container management

### **Setup Steps:**

#### **1. Use Your Personal Docker Hub Account**
- Use your existing Docker Hub account
- No need to create a new account

#### **2. Create Repository**
1. Go to [hub.docker.com](https://hub.docker.com)
2. Click "Create Repository"
3. **Repository name**: `callableapis`
4. **Visibility**: **Public** (for open source)
5. **Description**: "CallableAPIs Multi-Cloud Infrastructure Services"
6. Click "Create"

#### **3. Create Access Token**
1. Go to Account Settings → Security
2. Create new access token: `github-actions`
3. Copy the token (you'll need it for GitHub secrets)

#### **4. Configure GitHub Secrets**
Add these secrets to your GitHub repository:
- `DOCKERHUB_USERNAME`: `your-dockerhub-username`
- `DOCKERHUB_TOKEN`: `your-access-token`

## 🏗️ **Architecture Overview**

### **Repository Structure:**
```
infra/ (PRIVATE)
├── ansible/           # Infrastructure management
├── terraform/         # Cloud configurations
├── containers/        # Open source services
│   └── api/          # API container (public)
└── .github/workflows/ # CI/CD pipelines
```

### **Container Registry:**
- **Registry**: `docker.io`
- **Namespace**: `your-dockerhub-username`
- **Images**: `your-dockerhub-username/callableapis:api`

### **Security Model:**
- **Infra repo**: Private (contains IPs, regions, cloud configs)
- **Container images**: Public (open source services)
- **Sensitive data**: Stored in GitHub secrets, not in code

## 🚀 **Deployment Flow**

### **1. Build & Push (GitHub Actions)**
```yaml
# Triggers on changes to containers/api/
# Builds: your-dockerhub-username/callableapis:api
# Pushes to: docker.io/your-dockerhub-username/callableapis
```

### **2. Deploy (Ansible)**
```bash
# Pulls: your-dockerhub-username/callableapis:api
# Deploys to: onode1.callableapis.com
# Exposes via: nginx reverse proxy
```

## 📊 **Resource Usage**

### **Per Container:**
- **Size**: ~256MB (Alpine Linux base)
- **Memory**: 256MB limit
- **CPU**: 0.5 cores
- **Storage**: Minimal (Alpine base)

### **Docker Hub Usage:**
- **Storage**: Unlimited (public repos)
- **Bandwidth**: Unlimited (public repos)
- **Rate limits**: 100 pulls/6 hours (free tier)

## 🔧 **Next Steps**

1. **Set up Docker Hub account** and repository
2. **Configure GitHub secrets** for authentication
3. **Test container build** via GitHub Actions
4. **Deploy to onode1** using Ansible
5. **Update DNS** to point to containerized API

## 🛡️ **Security Considerations**

### **What's Private:**
- Infrastructure configurations
- IP addresses and regions
- Cloud provider credentials
- Ansible playbooks and inventory

### **What's Public:**
- Container images (services)
- Application code
- Dockerfiles and requirements

### **Best Practices:**
- Use GitHub secrets for sensitive data
- Keep infra repo private
- Use least-privilege access tokens
- Regular security audits
