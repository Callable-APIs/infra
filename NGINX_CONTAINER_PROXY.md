# Nginx Container Proxy Setup

## 🎯 **Overview**

This setup provides nginx-based HTTP proxy for exposing container endpoints on port 80 across all containerd nodes. It enables unified access to health checks, status information, and API endpoints regardless of which containers are running.

## 🏗️ **Architecture**

```
Internet/Client
    ↓
Port 80 (nginx)
    ↓
Container Services (port 8080-8084)
    ↓
Health Monitoring (systemd timer)
```

## 📋 **Features**

### **Exposed Endpoints**
- `GET /health` - Health check (unversioned)
- `GET /api/status` - Detailed status (unversioned)  
- `GET /api/health` - API health check (unversioned)
- `GET /api/v1/*` - Version 1 API endpoints
- `GET /api/v2/*` - Version 2 API endpoints
- `GET /` - Node information

### **Health Monitoring**
- **Automatic container discovery** on ports 8080-8084
- **Dynamic upstream configuration** based on healthy containers
- **30-second health check interval** via systemd timer
- **Automatic nginx reload** when container status changes

### **Security Features**
- **Rate limiting** (10 req/s for API, 30 req/s for health)
- **Security headers** (X-Frame-Options, X-Content-Type-Options, etc.)
- **Firewall configuration** (ports 80, 443)
- **JSON error responses** for consistent API behavior

## 🚀 **Deployment**

### **Automatic Deployment (Recommended)**
The nginx proxy is automatically deployed when running the containerd setup:

```bash
# Deploy containerd + nginx on all nodes
ansible-playbook -i inventory/production playbooks/containerd-setup.yml

# Deploy only nginx on existing containerd nodes
ansible-playbook -i inventory/production playbooks/deploy-nginx-proxy.yml
```

### **Manual Deployment**
```bash
# Deploy to specific cloud provider
ansible-playbook -i inventory/production playbooks/deploy-nginx-proxy.yml --limit oracle_cloud
ansible-playbook -i inventory/production playbooks/deploy-nginx-proxy.yml --limit google_cloud
ansible-playbook -i inventory/production playbooks/deploy-nginx-proxy.yml --limit ibm_cloud
```

## 🧪 **Testing**

### **Test All Endpoints**
```bash
# Test localhost
./ansible/scripts/test-nginx-endpoints.sh

# Test specific node
./ansible/scripts/test-nginx-endpoints.sh 192.168.1.100

# Test with custom port
./ansible/scripts/test-nginx-endpoints.sh 192.168.1.100 8080
```

### **Manual Testing**
```bash
# Health check
curl http://node-ip/health

# Status information
curl http://node-ip/api/status

# Node information
curl http://node-ip/

# API endpoints (when containers are running)
curl http://node-ip/api/v1/calendar
curl http://node-ip/api/v2/astronomy
```

## 📊 **Monitoring**

### **Check nginx Status**
```bash
sudo systemctl status nginx
sudo nginx -t  # Test configuration
```

### **Check Container Health Monitor**
```bash
sudo systemctl status container-health-monitor.timer
sudo journalctl -u container-health-monitor.service -f
```

### **View Health Check Logs**
```bash
sudo tail -f /var/log/container-health-check.log
```

### **Check Active Upstreams**
```bash
sudo cat /etc/nginx/conf.d/container-upstream.conf
```

## 🔧 **Configuration**

### **Nginx Configuration Files**
- `/etc/nginx/nginx.conf` - Main nginx configuration
- `/etc/nginx/conf.d/container-proxy.conf` - Container proxy configuration
- `/etc/nginx/conf.d/container-upstream.conf` - Auto-generated upstream config

### **Health Check Script**
- `/usr/local/bin/container-health-check.sh` - Health monitoring script
- `/var/log/container-health-check.log` - Health check logs

### **Systemd Services**
- `nginx.service` - Main nginx service
- `container-health-monitor.service` - Health check service
- `container-health-monitor.timer` - Health check timer (30s interval)

## 🌐 **Container Integration**

### **For Base Container (`rl337/callableapis:base`)**
The base container endpoints are automatically exposed:
- `GET /health` → Container health check
- `GET /api/status` → Container status information

### **For Services Container (`rl337/callableapis:services`)**
The services container endpoints are automatically exposed:
- `GET /health` → Services health check
- `GET /api/status` → Services status information
- `GET /api/v1/calendar` → Calendar service v1
- `GET /api/v2/astronomy` → Astronomy service v2

### **Port Assignment**
- **Port 80**: nginx proxy (external access)
- **Port 8080**: Primary container (base or services)
- **Port 8081-8084**: Additional containers (if needed)

## 🔍 **Troubleshooting**

### **Common Issues**

#### **Nginx not starting**
```bash
sudo nginx -t  # Check configuration syntax
sudo journalctl -u nginx -f  # Check nginx logs
```

#### **Containers not being detected**
```bash
# Check if containers are running on expected ports
sudo netstat -tln | grep -E ":(8080|8081|8082|8083|8084) "

# Check health check script
sudo /usr/local/bin/container-health-check.sh
```

#### **Health checks failing**
```bash
# Check container health directly
curl http://127.0.0.1:8080/health

# Check nginx upstream configuration
sudo cat /etc/nginx/conf.d/container-upstream.conf
```

### **Log Locations**
- **Nginx access logs**: `/var/log/nginx/access.log`
- **Nginx error logs**: `/var/log/nginx/error.log`
- **Health check logs**: `/var/log/container-health-check.log`
- **Systemd logs**: `journalctl -u container-health-monitor.service`

## 📈 **Performance**

### **Rate Limits**
- **API endpoints**: 10 requests/second (burst: 50)
- **Health endpoints**: 30 requests/second (burst: 20)

### **Upstream Configuration**
- **Load balancing**: least_conn
- **Health checks**: 3 max failures, 30s timeout
- **Connection timeouts**: 5s connect, 10-30s read/send

### **Resource Usage**
- **Memory**: ~50MB for nginx
- **CPU**: Minimal (health checks every 30s)
- **Disk**: ~10MB for logs and configs

## 🔒 **Security**

### **Firewall Rules**
- **Port 80**: HTTP access (allowed)
- **Port 443**: HTTPS access (allowed)
- **Port 8080-8084**: Container ports (local only)

### **Security Headers**
- `X-Frame-Options: SAMEORIGIN`
- `X-Content-Type-Options: nosniff`
- `X-XSS-Protection: 1; mode=block`
- `Referrer-Policy: strict-origin-when-cross-origin`

### **Rate Limiting**
- Prevents abuse of API endpoints
- Separate limits for health vs API endpoints
- Automatic blocking of excessive requests

## 🚀 **Next Steps**

1. **Deploy containers** using the base container
2. **Monitor health** via the exposed endpoints
3. **Scale services** by adding more containers on different ports
4. **Add SSL/TLS** for HTTPS support (future enhancement)
5. **Implement load balancing** across multiple nodes (future enhancement)

