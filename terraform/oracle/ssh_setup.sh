#!/bin/bash

# SSH Setup Script for Oracle Cloud ARM Instances
# This script can be run after instance creation to configure SSH access

set -e

INSTANCE_NAME=${1:-"unknown"}
PUBLIC_IP=${2:-"unknown"}

echo "Setting up SSH access for $INSTANCE_NAME ($PUBLIC_IP)"

# Create SSH config entry
cat >> ~/.ssh/config << EOF

# Oracle Cloud ARM Instance - $INSTANCE_NAME
Host $INSTANCE_NAME
    HostName $PUBLIC_IP
    User ubuntu
    IdentityFile ~/.ssh/callableapis_private_key
    StrictHostKeyChecking no
    UserKnownHostsFile /dev/null
    ServerAliveInterval 60
    ServerAliveCountMax 3

# Cursor Agent Access - $INSTANCE_NAME
Host $INSTANCE_NAME-agent
    HostName $PUBLIC_IP
    User cursor-agent
    IdentityFile ~/.ssh/callableapis_private_key
    StrictHostKeyChecking no
    UserKnownHostsFile /dev/null
    ServerAliveInterval 60
    ServerAliveCountMax 3
EOF

echo "SSH configuration added for $INSTANCE_NAME"
echo "You can now connect using:"
echo "  ssh $INSTANCE_NAME"
echo "  ssh $INSTANCE_NAME-agent"
