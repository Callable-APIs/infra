#!/usr/bin/env python3
"""
CallableAPIs Status Container
Aggregates health and status information from all infrastructure nodes
"""

import os
import json
import logging
import requests
import asyncio
import aiohttp
from datetime import datetime, timedelta
from flask import Flask, jsonify, render_template_string
from typing import Dict, List, Optional, Tuple

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)

# Node configuration - mapping hostnames to IPs and display names
NODES = {
    "onode1": {
        "ip": "192.9.154.97",
        "display_name": "Oracle Cloud Node 1",
        "provider": "Oracle Cloud",
        "role": "Primary"
    },
    "onode2": {
        "ip": "192.9.134.169", 
        "display_name": "Oracle Cloud Node 2",
        "provider": "Oracle Cloud",
        "role": "Secondary"
    },
    "gnode1": {
        "ip": "35.233.161.8",
        "display_name": "Google Cloud Node 1", 
        "provider": "Google Cloud",
        "role": "Monitoring"
    },
    "inode1": {
        "ip": "52.116.135.43",
        "display_name": "IBM Cloud Node 1",
        "provider": "IBM Cloud", 
        "role": "Services"
    }
}

# Timeout for health checks
HEALTH_CHECK_TIMEOUT = 5

class NodeStatus:
    """Represents the status of a single node"""
    
    def __init__(self, node_id: str, config: dict):
        self.node_id = node_id
        self.config = config
        self.health_status = "unknown"
        self.api_status = "unknown"
        self.last_check = None
        self.uptime = None
        self.version = None
        self.error_message = None
        self.response_time = None

    async def check_health(self, session: aiohttp.ClientSession) -> None:
        """Check the health and status of this node"""
        start_time = datetime.now()
        
        try:
            # Check health endpoint
            health_url = f"http://{self.config['ip']}:8080/health"
            async with session.get(health_url, timeout=aiohttp.ClientTimeout(total=HEALTH_CHECK_TIMEOUT)) as response:
                if response.status == 200:
                    health_data = await response.json()
                    self.health_status = health_data.get('status', 'unknown')
                    self.version = health_data.get('version', 'unknown')
                else:
                    self.health_status = 'error'
                    self.error_message = f"Health check returned {response.status}"
            
            # Check API status endpoint
            status_url = f"http://{self.config['ip']}:8080/api/status"
            async with session.get(status_url, timeout=aiohttp.ClientTimeout(total=HEALTH_CHECK_TIMEOUT)) as response:
                if response.status == 200:
                    status_data = await response.json()
                    self.api_status = status_data.get('status', 'unknown')
                    self.uptime = status_data.get('uptime', 'unknown')
                else:
                    self.api_status = 'error'
                    if not self.error_message:
                        self.error_message = f"Status check returned {response.status}"
            
            self.response_time = (datetime.now() - start_time).total_seconds()
            self.last_check = datetime.now()
            
        except asyncio.TimeoutError:
            self.health_status = 'timeout'
            self.api_status = 'timeout'
            self.error_message = "Request timeout"
            self.last_check = datetime.now()
        except Exception as e:
            self.health_status = 'error'
            self.api_status = 'error'
            self.error_message = str(e)
            self.last_check = datetime.now()

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization"""
        return {
            "node_id": self.node_id,
            "display_name": self.config["display_name"],
            "provider": self.config["provider"],
            "role": self.config["role"],
            "ip": self.config["ip"],
            "health_status": self.health_status,
            "api_status": self.api_status,
            "uptime": self.uptime,
            "version": self.version,
            "last_check": self.last_check.isoformat() if self.last_check else None,
            "response_time": self.response_time,
            "error_message": self.error_message
        }

async def check_all_nodes() -> List[NodeStatus]:
    """Check the status of all nodes concurrently"""
    nodes = [NodeStatus(node_id, config) for node_id, config in NODES.items()]
    
    async with aiohttp.ClientSession() as session:
        tasks = [node.check_health(session) for node in nodes]
        await asyncio.gather(*tasks, return_exceptions=True)
    
    return nodes

@app.route('/')
def home():
    """Main status page"""
    return jsonify({
        "service": "CallableAPIs Status Dashboard",
        "version": os.environ.get('CONTAINER_VERSION', 'unknown'),
        "description": "Multi-cloud infrastructure status aggregation",
        "endpoints": {
            "status": "/api/status",
            "health": "/health",
            "nodes": "/api/nodes"
        },
        "timestamp": datetime.now().isoformat()
    })

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "status-dashboard"
    })

@app.route('/api/status')
def status():
    """Detailed status of all nodes"""
    try:
        # Run async health checks
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        nodes = loop.run_until_complete(check_all_nodes())
        loop.close()
        
        # Calculate overall status
        healthy_nodes = sum(1 for node in nodes if node.health_status == 'healthy')
        total_nodes = len(nodes)
        overall_status = "healthy" if healthy_nodes == total_nodes else "degraded" if healthy_nodes > 0 else "down"
        
        return jsonify({
            "service": "CallableAPIs Status Dashboard",
            "version": os.environ.get('CONTAINER_VERSION', 'unknown'),
            "overall_status": overall_status,
            "healthy_nodes": healthy_nodes,
            "total_nodes": total_nodes,
            "last_updated": datetime.now().isoformat(),
            "nodes": [node.to_dict() for node in nodes]
        })
        
    except Exception as e:
        logger.error(f"Error checking node status: {e}")
        return jsonify({
            "service": "CallableAPIs Status Dashboard",
            "version": os.environ.get('CONTAINER_VERSION', 'unknown'),
            "overall_status": "error",
            "error": str(e),
            "last_updated": datetime.now().isoformat(),
            "nodes": []
        }), 500

@app.route('/api/nodes')
def nodes():
    """Get individual node status"""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        nodes = loop.run_until_complete(check_all_nodes())
        loop.close()
        
        return jsonify({
            "nodes": [node.to_dict() for node in nodes],
            "last_updated": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error checking nodes: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/dashboard')
def dashboard():
    """HTML dashboard for status.callableapis.com"""
    try:
        # Get status data
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        nodes = loop.run_until_complete(check_all_nodes())
        loop.close()
        
        # Calculate overall status
        healthy_nodes = sum(1 for node in nodes if node.health_status == 'healthy')
        total_nodes = len(nodes)
        overall_status = "healthy" if healthy_nodes == total_nodes else "degraded" if healthy_nodes > 0 else "down"
        
        # Status color mapping
        status_colors = {
            "healthy": "#10B981",  # green
            "degraded": "#F59E0B",  # yellow
            "down": "#EF4444",     # red
            "error": "#6B7280",    # gray
            "timeout": "#F59E0B",  # yellow
            "unknown": "#6B7280"   # gray
        }
        
        overall_color = status_colors.get(overall_status, "#6B7280")
        
        # Generate HTML
        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CallableAPIs Status Dashboard</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f8fafc;
            color: #1f2937;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        .header {{
            text-align: center;
            margin-bottom: 30px;
        }}
        .status-badge {{
            display: inline-block;
            padding: 8px 16px;
            border-radius: 20px;
            font-weight: 600;
            color: white;
            background-color: {overall_color};
        }}
        .nodes-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .node-card {{
            background: white;
            border-radius: 8px;
            padding: 20px;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
            border-left: 4px solid {status_colors.get('healthy', '#6B7280')};
        }}
        .node-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }}
        .node-name {{
            font-weight: 600;
            font-size: 1.1em;
        }}
        .node-status {{
            padding: 4px 8px;
            border-radius: 12px;
            font-size: 0.8em;
            font-weight: 500;
        }}
        .node-details {{
            font-size: 0.9em;
            color: #6b7280;
        }}
        .node-details div {{
            margin-bottom: 5px;
        }}
        .error-message {{
            color: #ef4444;
            font-style: italic;
            margin-top: 10px;
        }}
        .footer {{
            text-align: center;
            color: #6b7280;
            font-size: 0.9em;
        }}
        .refresh-info {{
            background: #f3f4f6;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
            text-align: center;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>CallableAPIs Infrastructure Status</h1>
            <div class="status-badge">{overall_status.upper()}</div>
            <p>{{healthy_nodes}} of {total_nodes} nodes healthy</p>
        </div>
        
        <div class="refresh-info">
            <p>Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
            <p>This page refreshes automatically every 30 seconds</p>
        </div>
        
        <div class="nodes-grid">
"""
        
        # Add node cards
        for node in nodes:
            health_color = status_colors.get(node.health_status, "#6B7280")
            node_html = f"""
            <div class="node-card" style="border-left-color: {health_color};">
                <div class="node-header">
                    <div class="node-name">{node.config['display_name']}</div>
                    <div class="node-status" style="background-color: {health_color}; color: white;">
                        {node.health_status.upper()}
                    </div>
                </div>
                <div class="node-details">
                    <div><strong>Provider:</strong> {node.config['provider']}</div>
                    <div><strong>Role:</strong> {node.config['role']}</div>
                    <div><strong>IP:</strong> {node.config['ip']}</div>
                    <div><strong>Version:</strong> {node.version or 'Unknown'}</div>
                    <div><strong>Uptime:</strong> {node.uptime or 'Unknown'}</div>
                    <div><strong>Response Time:</strong> {f"{node.response_time:.2f}s" if node.response_time else 'N/A'}</div>
                    <div><strong>Last Check:</strong> {node.last_check.strftime('%H:%M:%S') if node.last_check else 'Never'}</div>
                </div>
"""
            if node.error_message:
                node_html += f'<div class="error-message">Error: {node.error_message}</div>'
            
            node_html += "</div>"
            html += node_html
        
        html += """
        </div>
        
        <div class="footer">
            <p>CallableAPIs Multi-Cloud Infrastructure Status Dashboard</p>
            <p>Powered by Flask and aiohttp</p>
        </div>
    </div>
    
    <script>
        // Auto-refresh every 30 seconds
        setTimeout(function() {
            location.reload();
        }, 30000);
    </script>
</body>
</html>
"""
        
        return html
        
    except Exception as e:
        logger.error(f"Error generating dashboard: {e}")
        return f"""
        <html>
        <body>
            <h1>Error</h1>
            <p>Failed to load status dashboard: {str(e)}</p>
        </body>
        </html>
        """, 500

@app.errorhandler(404)
def not_found(error):
    """404 error handler"""
    return jsonify({
        "error": "Not Found",
        "message": "The requested resource was not found",
        "status": 404
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """500 error handler"""
    logger.error(f"Internal server error: {error}")
    return jsonify({
        "error": "Internal Server Error",
        "message": "An internal server error occurred",
        "status": 500
    }), 500

if __name__ == '__main__':
    # Get port from environment or default to 8080
    port = int(os.environ.get('PORT', 8080))
    
    # Run the application
    logger.info(f"Starting CallableAPIs Status Dashboard on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)
