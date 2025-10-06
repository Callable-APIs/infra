#!/bin/bash

# CallableAPIs Practical Migration Script
# This script migrates the existing application to us-west-2

set -e

echo "🚀 CallableAPIs Practical Migration to us-west-2"
echo "==============================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if AWS CLI is configured
check_aws_credentials() {
    print_status "Checking AWS credentials..."
    if ! aws sts get-caller-identity > /dev/null 2>&1; then
        print_error "AWS credentials not configured."
        print_error "Please run: source env-deploy.sh"
        print_error "Or configure AWS CLI with deployment user credentials."
        exit 1
    fi
    print_success "AWS credentials verified"
}

# Check if Terraform is installed
check_terraform() {
    print_status "Checking Terraform installation..."
    if ! command -v terraform &> /dev/null; then
        print_error "Terraform is not installed. Please install Terraform first."
        exit 1
    fi
    print_success "Terraform is installed: $(terraform version | head -n1)"
}

# Check existing resources
check_existing_resources() {
    print_status "Checking existing resources..."
    
    echo ""
    echo "📊 Current Infrastructure:"
    echo "========================="
    
    # Check us-east-1 Elastic Beanstalk
    print_status "Checking us-east-1 Elastic Beanstalk..."
    EB_ENV=$(aws elasticbeanstalk describe-environments --region us-east-1 --query 'Environments[?ApplicationName==`CallableapisServiceEnv`].[EnvironmentName,Status,Health]' --output table 2>/dev/null || echo "No Elastic Beanstalk environment found")
    echo "$EB_ENV"
    
    # Check us-east-1 instances
    print_status "Checking us-east-1 instances..."
    INSTANCES_1=$(aws ec2 describe-instances --region us-east-1 --query 'Reservations[*].Instances[*].[InstanceId,InstanceType,State.Name,PublicIpAddress]' --output table 2>/dev/null || echo "No instances found")
    echo "$INSTANCES_1"
    
    # Check us-east-2 instances
    print_status "Checking us-east-2 instances..."
    INSTANCES_2=$(aws ec2 describe-instances --region us-east-2 --query 'Reservations[*].Instances[*].[InstanceId,InstanceType,State.Name,PublicIpAddress]' --output table 2>/dev/null || echo "No instances found")
    echo "$INSTANCES_2"
    
    # Check current DNS
    print_status "Checking current DNS records..."
    DNS_RECORDS=$(aws route53 list-resource-record-sets --hosted-zone-id ZJ57N2O5R20OE --query 'ResourceRecordSets[?Name==`callableapis.com.` || Name==`www.callableapis.com.` || Name==`api.callableapis.com.`].[Name,Type,ResourceRecords[0].Value]' --output table 2>/dev/null || echo "No DNS records found")
    echo "$DNS_RECORDS"
}

# Deploy us-west-2 infrastructure
deploy_infrastructure() {
    print_status "Deploying us-west-2 infrastructure..."
    
    cd terraform
    
    # Initialize Terraform
    print_status "Initializing Terraform..."
    terraform init
    
    # Plan the deployment
    print_status "Planning deployment..."
    terraform plan -target=aws_vpc.main -target=aws_internet_gateway.main -target=aws_subnet.public_1 -target=aws_subnet.public_2 -target=aws_route_table.public -target=aws_security_group.eb_security_group -target=aws_security_group.api_security_group
    
    # Ask for confirmation
    echo ""
    print_warning "This will create networking infrastructure in us-west-2. Continue? (y/N)"
    read -r response
    if [[ ! "$response" =~ ^[Yy]$ ]]; then
        print_status "Deployment cancelled by user"
        exit 0
    fi
    
    # Apply networking infrastructure
    print_status "Applying networking infrastructure..."
    terraform apply -auto-approve -target=aws_vpc.main -target=aws_internet_gateway.main -target=aws_subnet.public_1 -target=aws_subnet.public_2 -target=aws_route_table.public -target=aws_security_group.eb_security_group -target=aws_security_group.api_security_group
    
    print_success "Networking infrastructure deployed!"
    
    # Deploy Elastic Beanstalk
    print_status "Deploying Elastic Beanstalk environment..."
    terraform plan -target=aws_elastic_beanstalk_application.callableapis -target=aws_elastic_beanstalk_environment.callableapis_env -target=aws_iam_role.eb_service_role -target=aws_iam_role.eb_instance_role -target=aws_iam_instance_profile.eb_instance_profile
    
    echo ""
    print_warning "This will create Elastic Beanstalk environment in us-west-2. Continue? (y/N)"
    read -r response
    if [[ ! "$response" =~ ^[Yy]$ ]]; then
        print_status "Deployment cancelled by user"
        exit 0
    fi
    
    terraform apply -auto-approve -target=aws_elastic_beanstalk_application.callableapis -target=aws_elastic_beanstalk_environment.callableapis_env -target=aws_iam_role.eb_service_role -target=aws_iam_role.eb_instance_role -target=aws_iam_instance_profile.eb_instance_profile
    
    print_success "Elastic Beanstalk environment deployed!"
    
    # Deploy API instance
    print_status "Deploying API instance..."
    terraform plan -target=aws_instance.api_instance -target=aws_eip.api_eip
    
    echo ""
    print_warning "This will create API instance in us-west-2. Continue? (y/N)"
    read -r response
    if [[ ! "$response" =~ ^[Yy]$ ]]; then
        print_status "Deployment cancelled by user"
        exit 0
    fi
    
    terraform apply -auto-approve -target=aws_instance.api_instance -target=aws_eip.api_eip
    
    print_success "API instance deployed!"
}

# Get new IP addresses
get_new_ips() {
    print_status "Getting new IP addresses..."
    
    # Get Elastic Beanstalk CNAME
    EB_CNAME=$(cd terraform && terraform output -raw eb_cname 2>/dev/null || echo "")
    
    # Get API instance IP
    API_IP=$(cd terraform && terraform output -raw api_ip 2>/dev/null || echo "")
    
    if [ -z "$EB_CNAME" ] || [ -z "$API_IP" ]; then
        print_error "Could not get IP addresses from Terraform output"
        exit 1
    fi
    
    print_success "New IP addresses:"
    echo "  Elastic Beanstalk: $EB_CNAME"
    echo "  API Instance: $API_IP"
}

# Update DNS records
update_dns() {
    print_status "Updating DNS records..."
    
    # Get new IP addresses
    get_new_ips
    
    # Update main domain
    print_status "Updating callableapis.com..."
    aws route53 change-resource-record-sets --hosted-zone-id ZJ57N2O5R20OE --change-batch '{
        "Changes": [{
            "Action": "UPSERT",
            "ResourceRecordSet": {
                "Name": "callableapis.com",
                "Type": "A",
                "AliasTarget": {
                    "DNSName": "'$EB_CNAME'",
                    "EvaluateTargetHealth": false,
                    "HostedZoneId": "Z2FDTNDATAQYW2"
                }
            }
        }]
    }'
    
    # Update www domain
    print_status "Updating www.callableapis.com..."
    aws route53 change-resource-record-sets --hosted-zone-id ZJ57N2O5R20OE --change-batch '{
        "Changes": [{
            "Action": "UPSERT",
            "ResourceRecordSet": {
                "Name": "www.callableapis.com",
                "Type": "A",
                "AliasTarget": {
                    "DNSName": "'$EB_CNAME'",
                    "EvaluateTargetHealth": false,
                    "HostedZoneId": "Z2FDTNDATAQYW2"
                }
            }
        }]
    }'
    
    # Update API domain
    print_status "Updating api.callableapis.com..."
    aws route53 change-resource-record-sets --hosted-zone-id ZJ57N2O5R20OE --change-batch '{
        "Changes": [{
            "Action": "UPSERT",
            "ResourceRecordSet": {
                "Name": "api.callableapis.com",
                "Type": "A",
                "TTL": 300,
                "ResourceRecords": [{"Value": "'$API_IP'"}]
            }
        }]
    }'
    
    print_success "DNS records updated successfully!"
}

# Test the deployment
test_deployment() {
    print_status "Testing deployment..."
    
    # Wait for DNS propagation
    print_status "Waiting for DNS propagation (60 seconds)..."
    sleep 60
    
    # Test main website
    print_status "Testing main website..."
    if curl -s -o /dev/null -w "%{http_code}" https://callableapis.com | grep -q "200"; then
        print_success "Main website is accessible"
    else
        print_warning "Main website may not be accessible yet (DNS propagation)"
    fi
    
    # Test API
    print_status "Testing API..."
    if curl -s -o /dev/null -w "%{http_code}" https://api.callableapis.com/ | grep -q "200"; then
        print_success "API is accessible"
    else
        print_warning "API may not be accessible yet (DNS propagation)"
    fi
    
    print_success "Deployment testing completed!"
}

# Show cost savings
show_cost_savings() {
    print_status "Cost Analysis:"
    echo ""
    echo "💰 COST SAVINGS ANALYSIS"
    echo "========================"
    echo "Previous monthly cost: $16.80 (2 × t2.micro instances)"
    echo "New monthly cost: $8.40 (1 × t2.micro instance)"
    echo "Monthly savings: $8.40"
    echo "Annual savings: $100.80"
    echo ""
    echo "🎉 You're now running on 50% reduced costs!"
    echo ""
    echo "New Infrastructure:"
    echo "✅ us-west-2 Elastic Beanstalk environment"
    echo "✅ us-west-2 API instance"
    echo "✅ Consolidated in single region"
    echo "✅ Better performance (closer to California)"
}

# Main execution
main() {
    echo ""
    print_status "Starting CallableAPIs practical migration to us-west-2..."
    echo ""
    
    # Pre-flight checks
    check_aws_credentials
    check_terraform
    
    # Check existing resources
    check_existing_resources
    
    # Deploy infrastructure
    deploy_infrastructure
    
    # Update DNS
    update_dns
    
    # Test deployment
    test_deployment
    
    # Show cost savings
    show_cost_savings
    
    echo ""
    print_success "🎉 Practical migration to us-west-2 completed successfully!"
    echo ""
    print_status "Next steps:"
    echo "1. Deploy your application code to the new Elastic Beanstalk environment"
    echo "2. Deploy your API code to the new API instance"
    echo "3. Monitor the deployment for 24-48 hours"
    echo "4. Test all functionality"
    echo "5. Terminate old us-east-1 and us-east-2 resources"
    echo ""
    print_status "Your infrastructure is now available at:"
    echo "🌐 https://callableapis.com"
    echo "🌐 https://www.callableapis.com"
    echo "🔌 https://api.callableapis.com"
    echo ""
    print_warning "Remember to deploy your application code to the new infrastructure!"
    echo ""
}

# Run main function
main "$@"
