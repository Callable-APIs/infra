# 🏷️ Container Tagging Strategy

## **Repository Structure**

**Single Repository**: `your-dockerhub-username/callableapis`

**Function-Based Tags**:
- `:base` - Base container (current)
- `:agents` - AI agent containers (future)
- `:monitoring` - Monitoring services (future)
- `:workers` - Background workers (future)

## 🏗️ **Current Implementation**

### **Base Container**
```bash
# Image: your-dockerhub-username/callableapis:base
# Source: containers/base/
# Purpose: Base container for all CallableAPIs services
```

### **Future Services**
```bash
# AI Agents
your-dockerhub-username/callableapis:agents
# Source: containers/agents/
# Purpose: AI agent containers for various tasks

# Monitoring
your-dockerhub-username/callableapis:monitoring
# Source: containers/monitoring/
# Purpose: System monitoring and alerting

# Workers
your-dockerhub-username/callableapis:workers
# Source: containers/workers/
# Purpose: Background job processing
```

## 🔄 **Tagging Strategy**

### **Function Tags (Primary)**
- `:base` - Base container
- `:agents` - AI agents
- `:monitoring` - Monitoring
- `:workers` - Workers

### **Version Tags (Secondary)**
- `:base-v1.0.0` - Specific base version
- `:agents-v1.0.0` - Specific agents version
- `:latest` - Latest stable (points to base)

### **Environment Tags (Tertiary)**
- `:api-dev` - Development API
- `:api-staging` - Staging API
- `:api-prod` - Production API

## 📋 **Setup Checklist**

### **1. Docker Hub Repository**
- [ ] Create repository: `callableapis`
- [ ] Set visibility: **Public**
- [ ] Add description: "CallableAPIs Multi-Cloud Infrastructure Services"

### **2. GitHub Secrets**
- [ ] `DOCKERHUB_USERNAME`: `your-dockerhub-username`
- [ ] `DOCKERHUB_TOKEN`: `your-access-token`

### **3. Update Configuration**
- [ ] Replace `your-dockerhub-username` in all config files
- [ ] Test GitHub Actions workflow
- [ ] Verify container builds and pushes

## 🚀 **Deployment Examples**

### **Base Container**
```bash
# Deploy base container
docker run -d \
  --name callableapis-base \
  -p 8080:8080 \
  your-dockerhub-username/callableapis:base
```

### **Future: AI Agents**
```bash
# Deploy AI agent container
docker run -d \
  --name callableapis-agent \
  your-dockerhub-username/callableapis:agents
```

### **Future: Monitoring**
```bash
# Deploy monitoring container
docker run -d \
  --name callableapis-monitoring \
  -p 3000:3000 \
  your-dockerhub-username/callableapis:monitoring
```

## 🔧 **GitHub Actions Workflow**

### **Current: Base Container**
```yaml
# Triggers on: containers/base/** changes
# Builds: your-dockerhub-username/callableapis:base
# Pushes to: docker.io/your-dockerhub-username/callableapis
```

### **Future: Multiple Services**
```yaml
# Triggers on: containers/agents/** changes
# Builds: your-dockerhub-username/callableapis:agents

# Triggers on: containers/monitoring/** changes
# Builds: your-dockerhub-username/callableapis:monitoring
```

## 💡 **Benefits of This Approach**

### **1. Organization**
- Single repository for all CallableAPIs services
- Clear function-based tagging
- Easy to manage and discover

### **2. Efficiency**
- No need for multiple repositories
- Shared base images and layers
- Simplified CI/CD pipeline

### **3. Scalability**
- Easy to add new services
- Consistent naming convention
- Future-proof architecture

### **4. Cost Effective**
- Single Docker Hub repository
- No storage limits for public repos
- Efficient layer sharing

## 🎯 **Next Steps**

1. **Create Docker Hub repository** (`callableapis`)
2. **Update GitHub secrets** with your Docker Hub credentials
3. **Replace placeholder** `your-dockerhub-username` in config files
4. **Test container build** by pushing changes to `containers/base/`
5. **Deploy to onode1** using the new container image

Ready to proceed with the Docker Hub setup?
