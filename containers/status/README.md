# CallableAPIs Status Container

A status dashboard that aggregates health and status information from all infrastructure nodes across multiple cloud providers.

## Features

- **Real-time Health Monitoring**: Checks `/health` and `/api/status` endpoints on all nodes
- **Concurrent Health Checks**: Uses asyncio for fast, parallel health checking
- **HTML Dashboard**: Beautiful web interface at `/dashboard` for status.callableapis.com
- **JSON API**: RESTful endpoints for programmatic access
- **Node Identification**: Shows only CNAMEs (onode1, onode2, gnode1, inode1) for security

## Endpoints

- `/` - Service information
- `/health` - Health check endpoint
- `/api/status` - Detailed status of all nodes (JSON)
- `/api/nodes` - Individual node status (JSON)
- `/dashboard` - HTML status dashboard

## Monitored Nodes

- **onode1** (Oracle Cloud Node 1) - 192.9.154.97
- **onode2** (Oracle Cloud Node 2) - 192.9.134.169
- **gnode1** (Google Cloud Node 1) - 35.233.161.8
- **inode1** (IBM Cloud Node 1) - 52.116.135.43

## Status Levels

- **healthy**: Node responding correctly
- **degraded**: Some issues but still operational
- **down**: Node not responding
- **error**: Network or application error
- **timeout**: Request timed out
- **unknown**: Status not yet determined

## Deployment

The status container should be deployed to one of the infrastructure nodes and exposed via Cloudflare at `status.callableapis.com`.

## Security

- No authentication implemented yet
- Only displays node CNAMEs, not sensitive information
- All health checks are internal (port 8080)
