# CallableAPIs Services Container Implementation Guide

## 🎯 **Overview**

This guide provides instructions for implementing a services container that extends the `rl337/callableapis:base` container and overrides the Flask app with a Java webapp running on Tomcat.

## ⚠️ **CRITICAL: Health Endpoint**

The services container **MUST** implement `/health` (not `/api/health`). This is required for:
- Status monitoring dashboard
- Docker health checks
- Load balancer health checks
- Consistent monitoring across all containers

The current implementation incorrectly exposes `/api/health`. **This must be fixed to use `/health`**.

## 🏗️ **Container Architecture**

```
rl337/callableapis:base (Python Flask app on port 8080)
    ↓ OVERRIDDEN
rl337/callableapis:services (Java webapp on Tomcat port 8080)
```

## 📋 **Required Implementation Steps**

### **1. Container Override Strategy**

The services container **completely overrides** the base container's Flask app:

- ✅ **Port 8080**: Used by Tomcat instead of Flask
- ✅ **Health Checks**: Custom health checks for Tomcat
- ✅ **Endpoints**: Implements mixed pattern (unversioned health/status, versioned services)
- ✅ **Base Container Features**: Still available (secrets, Python tools)

### **2. API Endpoint Pattern**

Implement these endpoint patterns:

```
# Health & Status (Unversioned - matches base container)
GET  /health                 # Health check
GET  /api/status             # Detailed status

# Service Endpoints (Versioned)
GET  /api/v1/calendar        # Calendar service v1
GET  /api/v2/calendar        # Calendar service v2
GET  /api/v1/astronomy       # Astronomy service v1
GET  /api/v2/astronomy       # Astronomy service v2

# Service-Specific Endpoints
GET  /api/v1/calendar/events
POST /api/v1/calendar/events
GET  /api/v2/calendar/events
PUT  /api/v2/calendar/events/{id}
```

### **3. Dockerfile Requirements**

```dockerfile
FROM rl337/callableapis:base

# Install Java and Tomcat
RUN apk add --no-cache openjdk11-jre tomcat9

# Override health check for Tomcat
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Override the base container's CMD
CMD ["/usr/share/tomcat9/bin/catalina.sh", "run"]
```

### **4. Java Implementation Requirements**

#### **Health Controller**
- Implement `/health` endpoint (unversioned)
- Return service status, version, timestamp
- Check Tomcat health and base container features

#### **Status Controller**
- Implement `/api/status` endpoint (unversioned)
- Include base container info (secrets, Python availability)
- Include Tomcat info (version, memory usage)
- Include services info (enabled services, versions)

#### **Service Controllers**
- Implement versioned endpoints for each service
- Follow `/api/v#/apiname` pattern
- Include service-specific functionality

### **5. Key Considerations**

#### **Port Management**
- Services container uses port 8080 (same as base container)
- Base container's Flask app is completely overridden
- No port conflicts since only Tomcat runs

#### **Health Checks**
- Must provide custom health checks for Tomcat
- Should check both Tomcat and service availability
- Include base container feature checks

#### **Base Container Integration**
- Secrets management still available
- Python tools still accessible
- Logging should integrate with base container structure

#### **Versioning Strategy**
- Health/Status endpoints: Unversioned (matches base container)
- Service endpoints: Versioned with `/api/v#/` prefix
- Support multiple versions (v1, v2, etc.)

### **6. Testing Requirements**

#### **Health Check Tests**
```bash
curl http://localhost:8080/health
curl http://localhost:8080/api/status
```

#### **Service Endpoint Tests**
```bash
curl http://localhost:8080/api/v1/calendar
curl http://localhost:8080/api/v2/calendar
curl http://localhost:8080/api/v1/astronomy
curl http://localhost:8080/api/v2/astronomy
```

#### **Container Health Check**
```bash
docker run --rm -p 8080:8080 rl337/callableapis:services
# Should pass Docker health checks
```

### **7. Deployment Considerations**

#### **Container Registry**
- Publish as `rl337/callableapis:services`
- Tag with version numbers for releases
- Use `latest` tag for main branch

#### **Environment Variables**
- `TOMCAT_PORT=8080` (default)
- `JAVA_OPTS` for JVM configuration
- `SPRING_PROFILES_ACTIVE=production`

#### **Resource Requirements**
- Memory: Minimum 512MB, recommended 1GB
- CPU: 1 core minimum
- Storage: ~500MB for container image

### **8. Monitoring & Logging**

#### **Health Monitoring**
- Use `/health` for load balancer health checks
- Use `/api/status` for detailed monitoring
- Monitor Tomcat metrics and JVM stats

#### **Logging**
- Integrate with base container logging
- Use structured logging (JSON format)
- Include service version and request tracing

## 🚀 **Quick Start**

1. **Build the container**:
   ```bash
   docker build -t rl337/callableapis:services .
   ```

2. **Run the container**:
   ```bash
   docker run --rm -p 8080:8080 rl337/callableapis:services
   ```

3. **Test the endpoints**:
   ```bash
   curl http://localhost:8080/health
   curl http://localhost:8080/api/status
   curl http://localhost:8080/api/v1/calendar
   curl http://localhost:8080/api/v1/astronomy
   ```

4. **Push to registry**:
   ```bash
   docker push rl337/callableapis:services
   ```

## 📚 **Additional Resources**

- [Tomcat Configuration Guide](https://tomcat.apache.org/tomcat-9.0-doc/config/)
- [Spring Boot Health Checks](https://docs.spring.io/spring-boot/docs/current/reference/html/actuator.html)
- [Docker Health Checks](https://docs.docker.com/engine/reference/builder/#healthcheck)
