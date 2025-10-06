#!/bin/bash

# Create IAM User for Infrastructure Deployment
# This script creates a new IAM user with the necessary permissions for Terraform deployment

set -e

echo "🔧 Creating IAM User for Infrastructure Deployment"
echo "================================================="

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
        print_error "AWS credentials not configured. Please run 'aws configure' first."
        exit 1
    fi
    print_success "AWS credentials verified"
}

# Create IAM user
create_iam_user() {
    print_status "Creating IAM user: callableapis-deployer"
    
    # Create user
    aws iam create-user --user-name callableapis-deployer --tags 'Key=Purpose,Value=Infrastructure Deployment' 'Key=Project,Value=CallableAPIs' 'Key=ManagedBy,Value=Terraform'
    
    print_success "IAM user created: callableapis-deployer"
}

# Create access key
create_access_key() {
    print_status "Creating access key for callableapis-deployer..."
    
    # Create access key
    ACCESS_KEY_OUTPUT=$(aws iam create-access-key --user-name callableapis-deployer)
    ACCESS_KEY_ID=$(echo $ACCESS_KEY_OUTPUT | jq -r '.AccessKey.AccessKeyId')
    SECRET_ACCESS_KEY=$(echo $ACCESS_KEY_OUTPUT | jq -r '.AccessKey.SecretAccessKey')
    
    print_success "Access key created"
    echo ""
    print_warning "IMPORTANT: Save these credentials securely!"
    echo "Access Key ID: $ACCESS_KEY_ID"
    echo "Secret Access Key: $SECRET_ACCESS_KEY"
    echo ""
}

# Create deployment policy
create_deployment_policy() {
    print_status "Creating deployment policy..."
    
    # Create the policy document
    cat > deployment-policy.json << 'EOF'
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "EC2FullAccess",
            "Effect": "Allow",
            "Action": [
                "ec2:*"
            ],
            "Resource": "*"
        },
        {
            "Sid": "ElasticBeanstalkFullAccess",
            "Effect": "Allow",
            "Action": [
                "elasticbeanstalk:*"
            ],
            "Resource": "*"
        },
        {
            "Sid": "Route53FullAccess",
            "Effect": "Allow",
            "Action": [
                "route53:*"
            ],
            "Resource": "*"
        },
        {
            "Sid": "IAMLimitedAccess",
            "Effect": "Allow",
            "Action": [
                "iam:CreateRole",
                "iam:DeleteRole",
                "iam:GetRole",
                "iam:PassRole",
                "iam:AttachRolePolicy",
                "iam:DetachRolePolicy",
                "iam:PutRolePolicy",
                "iam:DeleteRolePolicy",
                "iam:GetRolePolicy",
                "iam:CreateInstanceProfile",
                "iam:DeleteInstanceProfile",
                "iam:GetInstanceProfile",
                "iam:AddRoleToInstanceProfile",
                "iam:RemoveRoleFromInstanceProfile",
                "iam:ListInstanceProfilesForRole",
                "iam:ListAttachedRolePolicies",
                "iam:ListRolePolicies"
            ],
            "Resource": "*"
        },
        {
            "Sid": "DynamoDBFullAccess",
            "Effect": "Allow",
            "Action": [
                "dynamodb:*"
            ],
            "Resource": "*"
        },
        {
            "Sid": "S3FullAccess",
            "Effect": "Allow",
            "Action": [
                "s3:*"
            ],
            "Resource": "*"
        },
        {
            "Sid": "LambdaFullAccess",
            "Effect": "Allow",
            "Action": [
                "lambda:*"
            ],
            "Resource": "*"
        },
        {
            "Sid": "APIGatewayFullAccess",
            "Effect": "Allow",
            "Action": [
                "apigateway:*"
            ],
            "Resource": "*"
        },
        {
            "Sid": "CloudFrontFullAccess",
            "Effect": "Allow",
            "Action": [
                "cloudfront:*"
            ],
            "Resource": "*"
        },
        {
            "Sid": "CloudWatchFullAccess",
            "Effect": "Allow",
            "Action": [
                "cloudwatch:*",
                "logs:*"
            ],
            "Resource": "*"
        }
    ]
}
EOF

    # Create the policy
    aws iam create-policy \
        --policy-name CallableAPIsDeploymentPolicy \
        --policy-document file://deployment-policy.json \
        --description "Policy for CallableAPIs infrastructure deployment"
    
    # Attach policy to user
    aws iam attach-user-policy \
        --user-name callableapis-deployer \
        --policy-arn arn:aws:iam::$(aws sts get-caller-identity --query Account --output text):policy/CallableAPIsDeploymentPolicy
    
    # Clean up policy file
    rm deployment-policy.json
    
    print_success "Deployment policy created and attached"
}

# Create environment file
create_env_file() {
    print_status "Creating deployment environment file..."
    
    # Get account ID
    ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
    
    # Create deployment environment file
    cat > env-deploy.sh << EOF
#!/bin/bash
# CallableAPIs Deployment Environment
# Generated on $(date)

export AWS_ACCESS_KEY_ID="$ACCESS_KEY_ID"
export AWS_SECRET_ACCESS_KEY="$SECRET_ACCESS_KEY"
export AWS_DEFAULT_REGION="us-west-2"
export AWS_ACCOUNT_ID="$ACCOUNT_ID"

echo "Deployment environment loaded for CallableAPIs"
echo "Region: us-west-2"
echo "Account: $ACCOUNT_ID"
EOF

    chmod +x env-deploy.sh
    
    print_success "Environment file created: env-deploy.sh"
}

# Show next steps
show_next_steps() {
    print_status "Next Steps:"
    echo ""
    echo "1. 🔐 Save the credentials securely:"
    echo "   Access Key ID: $ACCESS_KEY_ID"
    echo "   Secret Access Key: $SECRET_ACCESS_KEY"
    echo ""
    echo "2. 🚀 Use the deployment environment:"
    echo "   source env-deploy.sh"
    echo ""
    echo "3. 🏗️  Deploy infrastructure:"
    echo "   ./deploy-practical-migration.sh"
    echo ""
    echo "4. 🧹 Clean up when done:"
    echo "   aws iam delete-access-key --user-name callableapis-deployer --access-key-id $ACCESS_KEY_ID"
    echo "   aws iam detach-user-policy --user-name callableapis-deployer --policy-arn arn:aws:iam::$ACCOUNT_ID:policy/CallableAPIsDeploymentPolicy"
    echo "   aws iam delete-user --user-name callableapis-deployer"
    echo ""
    print_warning "Keep the credentials secure and delete them when migration is complete!"
}

# Main execution
main() {
    echo ""
    print_status "Starting IAM user creation for infrastructure deployment..."
    echo ""
    
    # Pre-flight checks
    check_aws_credentials
    
    # Create IAM user
    create_iam_user
    
    # Create access key
    create_access_key
    
    # Create deployment policy
    create_deployment_policy
    
    # Create environment file
    create_env_file
    
    # Show next steps
    show_next_steps
    
    echo ""
    print_success "🎉 IAM user setup completed successfully!"
    echo ""
}

# Run main function
main "$@"
