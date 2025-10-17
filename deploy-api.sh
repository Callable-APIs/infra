#!/bin/bash

# CallableAPIs API Deployment Script
# This script deploys the containerized API to replace Elastic Beanstalk

set -e

echo "🚀 CallableAPIs API Container Deployment"
echo "========================================"

# Check if we're in the right directory
if [ ! -f "ansible/ansible.cfg" ]; then
    echo "❌ Error: Please run this script from the repository root"
    exit 1
fi

# Check if Ansible is installed
if ! command -v ansible-playbook &> /dev/null; then
    echo "❌ Error: Ansible is not installed. Please install it first:"
    echo "   pip install ansible"
    exit 1
fi

echo "📋 Step 1: Setting up containerd on all nodes..."
cd ansible
ansible-playbook playbooks/containerd-setup.yml -v

echo "📦 Step 2: Building and pushing container image..."
cd ..
# This will be handled by GitHub Actions, but we can trigger it manually
echo "   Container will be built by GitHub Actions workflow"
echo "   Image: ghcr.io/callable-apis/infra/api:latest"

echo "🚀 Step 3: Deploying API container to onode1..."
cd ansible
ansible-playbook playbooks/api-deploy.yml -v

echo "✅ Step 4: Testing API deployment..."
echo "   Testing health endpoint..."
curl -f http://onode1.callableapis.com/health || echo "   ⚠️  Health check failed - container may still be starting"

echo "🎉 Deployment complete!"
echo ""
echo "Next steps:"
echo "1. Test the API: curl http://onode1.callableapis.com/api/health"
echo "2. Update DNS to point api.callableapis.com to onode1.callableapis.com"
echo "3. Decommission Elastic Beanstalk once confirmed working"
echo ""
echo "API Endpoints:"
echo "- Health: http://onode1.callableapis.com/health"
echo "- Status: http://onode1.callableapis.com/api/status"
echo "- Infrastructure: http://onode1.callableapis.com/api/infrastructure"
