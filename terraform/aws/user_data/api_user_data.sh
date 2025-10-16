#!/bin/bash

# CallableAPIs API Instance User Data Script
# This script sets up the API instance in us-west-2

# Update system
yum update -y

# Install required packages
yum install -y python3 python3-pip nginx git

# Create application directory
mkdir -p /opt/callableapis
cd /opt/callableapis

# Clone or copy your existing application code
# TODO: Replace with your actual application deployment method
# This could be:
# 1. Git clone from your repository
# 2. S3 download of application package
# 3. Copy from existing instance

# Example: Git clone (replace with your actual repository)
# git clone https://github.com/yourusername/callableapis.git .

# Example: Download from S3 (replace with your actual bucket)
# aws s3 cp s3://your-bucket/callableapis-app.zip .
# unzip callableapis-app.zip

# Install Python dependencies
# pip3 install -r requirements.txt

# Configure Nginx
cat > /etc/nginx/conf.d/callableapis.conf << 'EOF'
server {
    listen 80;
    server_name api.callableapis.com;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF

# Start and enable Nginx
systemctl start nginx
systemctl enable nginx

# Create systemd service for your API application
cat > /etc/systemd/system/callableapis-api.service << 'EOF'
[Unit]
Description=CallableAPIs API Service
After=network.target

[Service]
Type=simple
User=ec2-user
WorkingDirectory=/opt/callableapis
Environment=PATH=/usr/bin:/usr/local/bin
ExecStart=/usr/bin/python3 app.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Don't start the service yet - we'll do it after creating the app file

# Configure log rotation
cat > /etc/logrotate.d/callableapis << 'EOF'
/opt/callableapis/logs/*.log {
    daily
    missingok
    rotate 7
    compress
    delaycompress
    notifempty
    create 644 ec2-user ec2-user
    postrotate
        systemctl reload callableapis-api
    endscript
}
EOF

# Set up monitoring script
cat > /opt/callableapis/monitor.sh << 'EOF'
#!/bin/bash

# Simple health check script
if ! systemctl is-active --quiet callableapis-api; then
    echo "$(date): API service is down, restarting..." >> /var/log/callableapis-monitor.log
    systemctl restart callableapis-api
fi

if ! systemctl is-active --quiet nginx; then
    echo "$(date): Nginx is down, restarting..." >> /var/log/callableapis-monitor.log
    systemctl restart nginx
fi
EOF

chmod +x /opt/callableapis/monitor.sh

# Add monitoring to crontab
echo "*/5 * * * * /opt/callableapis/monitor.sh" | crontab -

# Create a simple test endpoint
cat > /opt/callableapis/app.py << 'EOF'
#!/usr/bin/env python3

from flask import Flask, jsonify
import datetime

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({
        'message': 'CallableAPIs API',
        'version': '2.0',
        'region': 'us-west-2',
        'timestamp': datetime.datetime.utcnow().isoformat(),
        'status': 'healthy'
    })

@app.route('/health')
def health():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.datetime.utcnow().isoformat()
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=False)
EOF

# Install Flask for the test endpoint
pip3 install flask

# Start and enable the API service
systemctl daemon-reload
systemctl start callableapis-api
systemctl enable callableapis-api

# Log completion
echo "$(date): CallableAPIs API instance setup completed" >> /var/log/callableapis-setup.log
