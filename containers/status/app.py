import os
import json
import logging
import asyncio
import aiohttp
from datetime import datetime
from flask import Flask, jsonify, render_template_string, request

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Node configuration (from Ansible inventory or environment variables)
# In a real scenario, this would be dynamically discovered or managed by a service mesh
NODES = [
    {"id": "onode1", "display_name": "Oracle Cloud Node 1", "ip": "192.9.154.97", "provider": "Oracle Cloud", "role": "Primary"},
    {"id": "onode2", "display_name": "Oracle Cloud Node 2", "ip": "192.9.134.169", "provider": "Oracle Cloud", "role": "Secondary"},
    {"id": "gnode1", "display_name": "Google Cloud Node 1", "ip": "35.233.161.8", "provider": "Google Cloud", "role": "Monitoring"},
    {"id": "inode1", "display_name": "IBM Cloud Node 1", "ip": "52.116.135.43", "provider": "IBM Cloud", "role": "Services"},
]

CONTAINER_VERSION = os.environ.get('CONTAINER_VERSION', 'unknown')
START_TIME = datetime.now()

async def fetch_node_status(session, node):
    """Fetches health and status from a single node."""
    node_ip = node['ip']
    node_id = node['id']
    health_url = f"http://{node_ip}:8080/health"
    status_url = f"http://{node_ip}:8080/api/status"
    
    health_status = "unknown"
    api_status = "unknown"
    version = "unknown"
    uptime = "unknown"
    error_message = None
    response_time = None
    last_check = datetime.now().isoformat()

    try:
        start_time = asyncio.get_event_loop().time()
        async with session.get(health_url, timeout=5) as response:
            response.raise_for_status()
            health_data = await response.json()
            health_status = health_data.get("status", "unhealthy")
            version = health_data.get("version", "unknown")
        
        async with session.get(status_url, timeout=5) as response:
            response.raise_for_status()
            status_data = await response.json()
            api_status = status_data.get("status", "unhealthy")
            uptime = status_data.get("uptime", "unknown")
        end_time = asyncio.get_event_loop().time()
        response_time = round(end_time - start_time, 6)

    except aiohttp.ClientError as e:
        error_message = f"Client error: {e}"
        health_status = "unreachable"
        api_status = "unreachable"
    except asyncio.TimeoutError:
        error_message = "Timeout"
        health_status = "timeout"
        api_status = "timeout"
    except json.JSONDecodeError:
        error_message = "Invalid JSON response"
        health_status = "invalid_response"
        api_status = "invalid_response"
    except Exception as e:
        error_message = f"Unexpected error: {e}"
        health_status = "error"
        api_status = "error"
    
    return {
        "node_id": node_id,
        "display_name": node['display_name'],
        "ip": node_ip,
        "provider": node['provider'],
        "role": node['role'],
        "health_status": health_status,
        "api_status": api_status,
        "version": version,
        "uptime": uptime,
        "error_message": error_message,
        "response_time": response_time,
        "last_check": last_check
    }

async def get_all_nodes_status():
    """Aggregates status from all configured nodes concurrently."""
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_node_status(session, node) for node in NODES]
        return await asyncio.gather(*tasks)

@app.route('/')
def root():
    """Root endpoint - redirect to dashboard."""
    from flask import redirect, url_for
    return redirect('/dashboard')

@app.route('/health')
def health():
    """Health check endpoint for the status dashboard itself."""
    return jsonify({
        "service": "status-dashboard",
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/status')
def api_status():
    """API endpoint to get aggregated status of all nodes."""
    # Run the async function in a new event loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        nodes_status = loop.run_until_complete(get_all_nodes_status())
    finally:
        loop.close()
    
    overall_status = "healthy"
    healthy_nodes = 0
    for node in nodes_status:
        if node["health_status"] != "healthy" or node["api_status"] != "running":
            overall_status = "degraded"
        else:
            healthy_nodes += 1
    
    return jsonify({
        "service": "CallableAPIs Status Dashboard",
        "version": CONTAINER_VERSION,
        "overall_status": overall_status,
        "total_nodes": len(NODES),
        "healthy_nodes": healthy_nodes,
        "last_updated": datetime.now().isoformat(),
        "nodes": nodes_status
    })

@app.route('/dashboard')
def dashboard():
    """Web dashboard to display aggregated status of all nodes in a table format."""
    # Run the async function in a new event loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        nodes_status = loop.run_until_complete(get_all_nodes_status())
    finally:
        loop.close()
    
    # Calculate overall status
    healthy_nodes = sum(1 for node in nodes_status if node["health_status"] == "healthy")
    total_nodes = len(nodes_status)
    overall_status = "healthy" if healthy_nodes == total_nodes else "degraded" if healthy_nodes > 0 else "down"
    
    # Status color mapping
    status_colors = {
        "healthy": "#10B981",  # green
        "degraded": "#F59E0B",  # yellow
        "down": "#EF4444",     # red
        "error": "#6B7280",    # gray
        "timeout": "#F59E0B",  # yellow
        "unknown": "#6B7280",   # gray
        "unreachable": "#EF4444",  # red
        "invalid_response": "#F59E0B"  # yellow
    }
    
    # Provider color mapping
    provider_colors = {
        "Oracle Cloud": "provider-oracle",
        "Google Cloud": "provider-google", 
        "IBM Cloud": "provider-ibm"
    }
    
    overall_color = status_colors.get(overall_status, "#6B7280")
    
    # Generate table rows
    table_rows = ""
    for node in nodes_status:
        health_color = status_colors.get(node['health_status'], "#6B7280")
        provider_class = provider_colors.get(node['provider'], "")
        
        # Format response time
        response_time_str = f"{node['response_time']:.3f}s" if node['response_time'] else "N/A"
        
        # Format last check time
        try:
            last_check_dt = datetime.fromisoformat(node['last_check'].replace('Z', '+00:00'))
            last_check_str = last_check_dt.strftime('%H:%M:%S')
        except:
            last_check_str = "Unknown"
        
        # Error message if any
        error_cell = ""
        if node['error_message']:
            error_cell = f'<br><span class="error-message">Error: {node["error_message"]}</span>'
        
        table_rows += f"""
                    <tr>
                        <td>
                            <span class="status-indicator status-{node['health_status']}"></span>
                            {node['health_status'].upper()}
                        </td>
                        <td class="node-name">{node['display_name']}</td>
                        <td><span class="provider-badge {provider_class}">{node['provider']}</span></td>
                        <td>{node['role']}</td>
                        <td>{node['ip']}</td>
                        <td>{node['version']}</td>
                        <td>{node['uptime']}</td>
                        <td class="response-time">{response_time_str}</td>
                        <td>{last_check_str}{error_cell}</td>
                    </tr>
        """
    
    html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CallableAPIs Infrastructure Status</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f8fafc;
            color: #1f2937;
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
        }}
        .header {{
            text-align: center;
            margin-bottom: 30px;
        }}
        .header h1 {{
            font-size: 2.5em;
            margin: 0;
            color: #2d3748;
        }}
        .status-badge {{
            display: inline-block;
            padding: 8px 16px;
            border-radius: 20px;
            font-weight: bold;
            font-size: 0.9em;
            margin: 10px 0;
            background-color: {overall_color};
            color: white;
        }}
        .refresh-info {{
            background: #f3f4f6;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
            text-align: center;
        }}
        .status-table {{
            background: white;
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            overflow: hidden;
        }}
        .table-header {{
            background: #f8fafc;
            padding: 20px;
            border-bottom: 1px solid #e2e8f0;
        }}
        .table-header h2 {{
            margin: 0;
            color: #2d3748;
            font-size: 1.5em;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
        }}
        th, td {{
            padding: 12px 16px;
            text-align: left;
            border-bottom: 1px solid #e2e8f0;
        }}
        th {{
            background: #f8fafc;
            font-weight: 600;
            color: #374151;
            font-size: 0.9em;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}
        tr:hover {{
            background: #f9fafb;
        }}
        .status-indicator {{
            display: inline-block;
            width: 8px;
            height: 8px;
            border-radius: 50%;
            margin-right: 8px;
        }}
        .status-healthy {{ background-color: #10B981; }}
        .status-degraded {{ background-color: #F59E0B; }}
        .status-down {{ background-color: #EF4444; }}
        .status-error {{ background-color: #6B7280; }}
        .status-timeout {{ background-color: #F59E0B; }}
        .status-unknown {{ background-color: #6B7280; }}
        .status-unreachable {{ background-color: #EF4444; }}
        .status-invalid_response {{ background-color: #F59E0B; }}
        .node-name {{
            font-weight: 600;
            color: #2d3748;
        }}
        .provider-badge {{
            display: inline-block;
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 0.8em;
            font-weight: 500;
        }}
        .provider-oracle {{ background-color: #FF6B35; color: white; }}
        .provider-google {{ background-color: #4285F4; color: white; }}
        .provider-ibm {{ background-color: #0066CC; color: white; }}
        .response-time {{
            font-family: monospace;
            font-size: 0.9em;
        }}
        .error-message {{
            color: #ef4444;
            font-style: italic;
            font-size: 0.9em;
        }}
        .footer {{
            text-align: center;
            color: #6b7280;
            font-size: 0.9em;
            margin-top: 30px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>CallableAPIs Infrastructure Status</h1>
            <div class="status-badge">{overall_status.upper()}</div>
            <p>{healthy_nodes} of {total_nodes} nodes healthy</p>
        </div>
        
        <div class="refresh-info">
            <p>Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
            <p>This page refreshes automatically every 30 seconds</p>
        </div>
        
        <div class="status-table">
            <div class="table-header">
                <h2>Node Status Overview</h2>
            </div>
            <table>
                <thead>
                    <tr>
                        <th>Status</th>
                        <th>Node</th>
                        <th>Provider</th>
                        <th>Role</th>
                        <th>IP Address</th>
                        <th>Version</th>
                        <th>Uptime</th>
                        <th>Response Time</th>
                        <th>Last Check</th>
                    </tr>
                </thead>
                <tbody>
                    {table_rows}
                </tbody>
            </table>
        </div>
        
        <div class="footer">
            <p>CallableAPIs Multi-Cloud Infrastructure Status Dashboard</p>
            <p>Powered by Flask and aiohttp</p>
        </div>
    </div>
    
    <script>
        // Auto-refresh every 30 seconds
        setTimeout(function() {{
            location.reload();
        }}, 30000);
    </script>
</body>
</html>
"""
    
    return html

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    logger.info(f"Starting CallableAPIs Status Dashboard on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)