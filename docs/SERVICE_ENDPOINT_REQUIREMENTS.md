# Service Endpoint Requirements for Status Dashboard

This document outlines the minimum required fields for container health and status endpoints to work with the CallableAPIs status dashboard.

## Required Endpoints

All containers deployed to nodes must provide these two endpoints:

1. **`/health`** - Basic health check
2. **`/api/status`** - Detailed status information

## `/health` Endpoint

**URL**: `http://NODE_IP:8080/health`

**Required Fields**:
```json
{
  "status": "UP" | "DOWN" | "UP" (string),
  "version": "1.0.0" | "git-sha" | "unknown" (string)
}
```

**Optional Fields**:
- Any additional fields are permitted (tomcat_version, java_version, service name, etc.)

**Example**:
```json
{
  "status": "UP",
  "version": "1.0.0",
  "container": "rl337/callableapis:services",
  "tomcat_version": "10.1.18",
  "service": "Callable APIs Services",
  "java_version": "21.0.6",
  "timestamp": "2025-10-27T15:53:29.168517082Z"
}
```

**Status Dashboard Logic** (from `containers/status/app.py:47`):
```python
health_status = health_data.get("status", "unhealthy")
```

If `status` field is missing or not "UP", the dashboard shows the node as unhealthy.

## `/api/status` Endpoint

**URL**: `http://NODE_IP:8080/api/status`

**Required Fields**:
```json
{
  "status": "running" | "healthy" | "available" | "UP" (string),
  "uptime": "4 days, 7:40:06" | "1 day, 12:22:53" | "unknown" (string)
}
```

**Optional Fields**:
- Any additional fields are permitted (memory stats, endpoints, etc.)

**Example**:
```json
{
  "status": "running",
  "uptime": "1 day, 12:22:53",
  "container": "rl337/callableapis:services",
  "memory": {
    "heap_max_mb": 1986,
    "heap_used_mb": 46
  },
  "available_endpoints": {
    "health": "/api/health",
    "status": "/api/status"
  }
}
```

**Status Dashboard Logic** (from `containers/status/app.py:53-54`):
```python
api_status = status_data.get("status", "unhealthy")
uptime = status_data.get("uptime", "unknown")
```

If `status` field is missing, the dashboard defaults to "unhealthy".

## Summary of Required Fields

### `/health` endpoint:
- ✅ **`"status"`** (string): Must be "UP" or "DOWN"
- ✅ **`"version"`** (string): Version information

### `/api/status` endpoint:
- ✅ **`"status"`** (string): Must be present (any value acceptable)
- ✅ **`"uptime"`** (string): Uptime information

## Current Issue

The services container is returning:
```json
{
  "status": "error"  // ❌ This causes the dashboard to show "unhealthy"
}
```

Instead of:
```json
{
  "status": "running"  // ✅ Correct value
}
```

## Implementation Notes

1. Both endpoints must return **JSON**
2. Both endpoints must return **HTTP 200** status code
3. The `status` field is **case-sensitive** and should match expected values
4. Missing fields default to "unhealthy" in the dashboard
5. Any additional fields are accepted and displayed in the dashboard

## Testing

You can test endpoints directly:
```bash
# Test /health
curl http://localhost:8080/health

# Test /api/status
curl http://localhost:8080/api/status
```

Or via Ansible:
```bash
ansible inode1 -i ansible/inventory/production -m shell -a "curl -s http://localhost:8080/health" --become
```

