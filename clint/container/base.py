#!/usr/bin/env python3
"""
CallableAPIs Base Container
A minimal base container for multi-cloud infrastructure services
"""
import os
import logging
import subprocess
import sys
from datetime import datetime
from flask import Flask, jsonify

# Import secrets manager from clint
try:
    from clint.secrets.manager import SecretsManager
    SECRETS_AVAILABLE = True
except ImportError:
    SECRETS_AVAILABLE = False
    logging.warning("Secrets manager not available")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)

# Load container version
def load_container_version():
    """Load container version from /etc/CONTAINER_VERSION"""
    try:
        with open('/etc/CONTAINER_VERSION', 'r') as f:
            return f.read().strip()
    except FileNotFoundError:
        return "unknown"

CONTAINER_VERSION = load_container_version()
START_TIME = datetime.now()

@app.route('/')
def home():
    """Root endpoint"""
    return jsonify({
        "service": "CallableAPIs Base Container",
        "version": CONTAINER_VERSION,
        "status": "running",
        "uptime": str(datetime.now() - START_TIME),
        "timestamp": datetime.now().isoformat()
    })

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": CONTAINER_VERSION
    })

@app.route('/api/health')
def api_health():
    """API health check endpoint (for compatibility)"""
    return jsonify({
        "status": "ok",
        "timestamp": datetime.now().isoformat(),
        "version": CONTAINER_VERSION
    })

@app.route('/api/status')
def status():
    """Detailed status endpoint - instantiates secrets manager to pick up rotated secrets"""
    # Get memory info
    try:
        with open('/proc/meminfo', 'r') as f:
            meminfo = f.read()
    except FileNotFoundError:
        meminfo = "unavailable"
    
    # Get uptime
    try:
        uptime_result = subprocess.run(['uptime'], capture_output=True, text=True)
        uptime = uptime_result.stdout.strip() if uptime_result.returncode == 0 else "unavailable"
    except Exception:
        uptime = "unavailable"
    
    # Get secrets info (instantiate manager here to pick up rotated secrets)
    secret_keys = []
    vault_password_hash = "unavailable"
    secrets_file_hash = "unavailable"
    
    if SECRETS_AVAILABLE:
        try:
            secrets_manager = SecretsManager()  # Defaults to Ansible Vault strategy
            secret_keys = secrets_manager.get_secret_keys()
            vault_password_hash = secrets_manager.get_vault_password_hash()
            secrets_file_hash = secrets_manager.get_secrets_file_hash()
        except Exception as e:
            logger.warning(f"Secrets error in status endpoint: {e}")
            vault_password_hash = "error"
            secrets_file_hash = "error"
    
    return jsonify({
        "service": "CallableAPIs Base Container",
        "version": CONTAINER_VERSION,
        "status": "running",
        "uptime": str(datetime.now() - START_TIME),
        "timestamp": datetime.now().isoformat(),
        "environment": {
            "python_version": os.sys.version,
            "container": True,
            "memory_info": meminfo,
            "system_uptime": uptime
        },
        "secrets": {
            "keys": secret_keys,
            "vault_password_hash": vault_password_hash,
            "secrets_file_hash": secrets_file_hash
        }
    })


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


def main():
    """Main entry point for base container."""
    # Get port from environment or default to 8080
    port = int(os.environ.get('PORT', 8080))
    
    # Run the application
    logger.info(f"Starting CallableAPIs Base Container on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)


if __name__ == '__main__':
    main()

