#!/bin/bash

# Google Cloud e2-micro Instance Setup Script
# This script configures SSH access, users, and basic system setup

set -e  # Exit on any error

# Update system
apt-get update
apt-get upgrade -y

# Install essential packages
apt-get install -y \
    curl \
    wget \
    git \
    python3 \
    python3-pip \
    python3-venv \
    htop \
    iotop \
    nethogs \
    vim \
    nano \
    unzip \
    jq \
    fail2ban \
    ufw

# Create ansible user for unmanaged instance management
useradd -m -s /bin/bash ansible
usermod -aG sudo ansible

# Create .ssh directory for ansible user
mkdir -p /home/ansible/.ssh
chmod 700 /home/ansible/.ssh

# Copy SSH key from ubuntu user to ansible user
if [ -f /home/ubuntu/.ssh/authorized_keys ]; then
    cp /home/ubuntu/.ssh/authorized_keys /home/ansible/.ssh/authorized_keys
    chmod 600 /home/ansible/.ssh/authorized_keys
    chown -R ansible:ansible /home/ansible/.ssh
fi

# Configure SSH for ansible user
echo "ansible ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers.d/ansible
chmod 440 /etc/sudoers.d/ansible

# Install Ansible and common tools
pip3 install ansible requests pyyaml

# Set up ansible directory
mkdir -p /home/ansible/.ansible
chown -R ansible:ansible /home/ansible

# Configure SSH daemon
cat >> /etc/ssh/sshd_config << EOF

# CallableAPIs SSH Configuration
Port 22
Protocol 2
PermitRootLogin no
PasswordAuthentication no
PubkeyAuthentication yes
AuthorizedKeysFile .ssh/authorized_keys
X11Forwarding no
PrintMotd no
AcceptEnv LANG LC_*
EOF

# Restart SSH service
systemctl restart ssh

# Configure firewall
ufw --force enable
ufw allow ssh
ufw allow 80/tcp
ufw allow 443/tcp

# Configure fail2ban for SSH protection
cat > /etc/fail2ban/jail.local << EOF
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 3

[sshd]
enabled = true
port = ssh
logpath = /var/log/auth.log
maxretry = 3
EOF

systemctl enable fail2ban
systemctl start fail2ban

# Create setup completion marker
echo "Google Cloud e2-micro instance setup complete - $(date)" > /home/ubuntu/setup.log
echo "Google Cloud e2-micro instance setup complete - $(date)" > /home/ansible/setup.log

# Set proper permissions
chown ubuntu:ubuntu /home/ubuntu/setup.log
chown ansible:ansible /home/ansible/setup.log

echo "Setup completed successfully!"
