#!/bin/bash

# Script to update CallableAPIs URLs from HTTP to HTTPS after Cloudflare activation
# Run this script once Cloudflare zone is active and HTTPS is working

set -e

echo "🔒 Updating CallableAPIs URLs to HTTPS..."

# Load environment variables
source env.sh

# Function to check if HTTPS is working
check_https() {
    echo "🔍 Checking if HTTPS is working..."
    
    # Test main website
    if curl -s -I https://callableapis.com | grep -q "200 OK"; then
        echo "✅ https://callableapis.com is working"
    else
        echo "❌ https://callableapis.com is not working yet"
        echo "   Please wait for Cloudflare zone activation and try again"
        exit 1
    fi
    
    # Test API
    if curl -s -I https://api.callableapis.com | grep -q "200 OK"; then
        echo "✅ https://api.callableapis.com is working"
    else
        echo "❌ https://api.callableapis.com is not working yet"
        echo "   Please wait for Cloudflare zone activation and try again"
        exit 1
    fi
}

# Function to update Parameter Store
update_parameter_store() {
    echo "📝 Updating Parameter Store..."
    
    # Update redirect URI to HTTPS
    docker run --rm -v $(pwd):/workspace \
        -e AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID \
        -e AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY \
        -e AWS_DEFAULT_REGION=$AWS_DEFAULT_REGION \
        amazon/aws-cli:latest ssm put-parameter \
        --name "/callableapis/github/redirect-uri" \
        --value "https://api.callableapis.com/api/auth/callback" \
        --type "String" \
        --overwrite
    
    echo "✅ Updated redirect URI to HTTPS"
}

# Function to update Terraform configuration
update_terraform() {
    echo "🏗️  Updating Terraform configuration..."
    
    # Update parameter_store.tf
    sed -i.bak 's|http://api.callableapis.com/api/auth/callback|https://api.callableapis.com/api/auth/callback|g' terraform/parameter_store.tf
    
    echo "✅ Updated terraform/parameter_store.tf"
    echo "   Run 'cd terraform && terraform plan && terraform apply' to apply changes"
}

# Function to update Elastic Beanstalk environment
update_elastic_beanstalk() {
    echo "🚀 Updating Elastic Beanstalk environment..."
    
    # Update environment variables
    docker run --rm -v $(pwd):/workspace \
        -e AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID \
        -e AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY \
        -e AWS_DEFAULT_REGION=$AWS_DEFAULT_REGION \
        amazon/aws-cli:latest elasticbeanstalk update-environment \
        --environment-name callableapis-java-env \
        --option-settings file://<(echo '[{"Namespace":"aws:elasticbeanstalk:application:environment","OptionName":"GITHUB_REDIRECT_URI","Value":"https://api.callableapis.com/api/auth/callback"}]')
    
    echo "✅ Updated Elastic Beanstalk environment variables"
}

# Function to check GitHub OAuth app settings
check_github_oauth() {
    echo "🔧 GitHub OAuth App Configuration:"
    echo "   Please update your GitHub OAuth app settings:"
    echo "   1. Go to GitHub Settings > Developer settings > OAuth Apps"
    echo "   2. Find your CallableAPIs app"
    echo "   3. Update the following URLs:"
    echo "      - Authorization callback URL: https://api.callableapis.com/api/auth/callback"
    echo "      - Homepage URL: https://callableapis.com"
    echo "      - Application name: CallableAPIs (if needed)"
    echo ""
    echo "   Current redirect URI in Parameter Store:"
    docker run --rm -v $(pwd):/workspace \
        -e AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID \
        -e AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY \
        -e AWS_DEFAULT_REGION=$AWS_DEFAULT_REGION \
        amazon/aws-cli:latest ssm get-parameter \
        --name "/callableapis/github/redirect-uri" \
        --with-decryption \
        --query "Parameter.Value" \
        --output text
}

# Function to check website URLs
check_website_urls() {
    echo "🌐 Website URL Updates Needed:"
    echo "   Update any hardcoded HTTP URLs in your website/application to HTTPS:"
    echo "   - http://callableapis.com → https://callableapis.com"
    echo "   - http://api.callableapis.com → https://api.callableapis.com"
    echo "   - http://www.callableapis.com → https://www.callableapis.com"
    echo ""
    echo "   Check these files for hardcoded URLs:"
    echo "   - terraform/website/index.html"
    echo "   - Any application configuration files"
    echo "   - Any documentation or README files"
}

# Main execution
main() {
    echo "🚀 CallableAPIs HTTPS Migration Script"
    echo "======================================"
    echo ""
    
    # Check if HTTPS is working
    check_https
    
    echo ""
    echo "📋 The following updates will be made:"
    echo "   1. Update Parameter Store redirect URI to HTTPS"
    echo "   2. Update Terraform configuration"
    echo "   3. Update Elastic Beanstalk environment"
    echo "   4. Show GitHub OAuth app update instructions"
    echo "   5. Show website URL update checklist"
    echo ""
    
    read -p "Continue? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "❌ Cancelled"
        exit 1
    fi
    
    # Execute updates
    update_parameter_store
    update_terraform
    update_elastic_beanstalk
    
    echo ""
    echo "✅ Parameter Store and Elastic Beanstalk updated!"
    echo ""
    
    # Show remaining manual steps
    check_github_oauth
    echo ""
    check_website_urls
    
    echo ""
    echo "🎉 HTTPS migration complete!"
    echo "   Next steps:"
    echo "   1. Update GitHub OAuth app settings (see above)"
    echo "   2. Update any hardcoded URLs in your application"
    echo "   3. Run 'cd terraform && terraform plan && terraform apply'"
    echo "   4. Test the OIDC flow with HTTPS URLs"
}

# Run main function
main "$@"

