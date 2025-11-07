#!/bin/bash

# Docker entrypoint script for AWS Infrastructure Reporting Tool

set -e

# Function to display help
show_help() {
    echo "AWS Infrastructure Reporting Tool with Terraform"
    echo "================================================"
    echo ""
    echo "Usage: docker run [OPTIONS] aws-infra-report [COMMAND] [ARGS]"
    echo ""
    echo "Commands:"
    echo "  cost-report [OPTIONS]     Generate AWS cost reports"
    echo "  multicloud-report [OPTIONS] Generate multi-cloud cost reports"
    echo "  billing [OPTIONS]         Unified multi-cloud billing reports"
    echo "  terraform-discover        Discover current AWS infrastructure"
    echo "  terraform-generate        Generate Terraform configuration"
    echo "  terraform-plan            Run terraform plan on generated config"
    echo "  full-analysis             Run complete analysis (cost + terraform)"
    echo "  help                      Show this help message"
    echo ""
    echo "  Or use 'python -m clint <command>' for direct CLI access"
    echo ""
    echo "Cost Report Options:"
    echo "  --internal                Generate internal detailed report"
    echo "  --console-only            Print summary to console only"
    echo "  --days N                  Number of days to look back (default: 30)"
    echo "  --output DIR              Output directory (default: reports)"
    echo ""
    echo "Environment Variables:"
    echo "  AWS_ACCESS_KEY_ID         AWS access key"
    echo "  AWS_SECRET_ACCESS_KEY     AWS secret key"
    echo "  AWS_DEFAULT_REGION        AWS region (default: us-east-1)"
    echo ""
    echo "Volume Mounts:"
    echo "  -v \$(pwd)/reports:/app/reports"
    echo "  -v \$(pwd)/internal_reports:/app/internal_reports"
    echo "  -v \$(pwd)/terraform_output:/app/terraform_output"
    echo ""
    echo "Examples:"
    echo "  # Generate public cost report"
    echo "  docker run -v \$(pwd)/reports:/app/reports aws-infra-report cost-report"
    echo ""
    echo "  # Generate internal cost report"
    echo "  docker run -v \$(pwd)/internal_reports:/app/internal_reports aws-infra-report cost-report --internal"
    echo ""
    echo "  # Discover infrastructure and generate Terraform"
    echo "  docker run -v \$(pwd)/terraform_output:/app/terraform_output aws-infra-report full-analysis"
}

# Function to check AWS credentials
check_aws_credentials() {
    if [ -z "$AWS_ACCESS_KEY_ID" ] || [ -z "$AWS_SECRET_ACCESS_KEY" ]; then
        echo "❌ Error: AWS credentials not found"
        echo "Please set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY environment variables"
        exit 1
    fi
    
    echo "✅ AWS credentials found"
    aws sts get-caller-identity --output table
}

# Function to generate cost reports
generate_cost_report() {
    echo "📊 Generating cost reports..."
    python -m clint cost-report "$@"
}

# Function to generate multi-cloud cost reports
generate_multicloud_report() {
    echo "🌐 Generating multi-cloud cost reports..."
    python -m clint multicloud-report "$@"
}

# Function to discover AWS infrastructure
discover_infrastructure() {
    echo "🔍 Discovering AWS infrastructure..."
    python -m clint terraform discover
}

# Function to generate Terraform configuration
generate_terraform() {
    echo "🏗️  Generating Terraform configuration..."
    python -m clint terraform generate
}

# Function to run terraform plan
terraform_plan() {
    echo "📋 Running Terraform plan..."
    cd terraform
    terraform init
    terraform plan
    echo ""
    echo "✅ Terraform plan completed!"
    echo "If the plan shows 'No changes', then the configuration accurately represents your current infrastructure."
}

# Function to run full analysis
full_analysis() {
    echo "🚀 Running full infrastructure analysis..."
    python -m clint full-analysis
}

# Main script logic
case "${1:-help}" in
    "cost-report")
        check_aws_credentials
        shift
        generate_cost_report "$@"
        ;;
    "multicloud-report")
        check_aws_credentials
        shift
        generate_multicloud_report "$@"
        ;;
    "billing")
        shift
        python -m clint billing "$@"
        ;;
    "terraform-discover")
        check_aws_credentials
        discover_infrastructure
        ;;
    "terraform-generate")
        generate_terraform
        ;;
    "terraform-plan")
        terraform_plan
        ;;
    "full-analysis")
        check_aws_credentials
        full_analysis
        ;;
    "clint")
        shift
        python -m clint "$@"
        ;;
    "help"|"--help"|"-h")
        show_help
        ;;
    *)
        # If command not recognized, try passing to clint
        python -m clint "$@" 2>/dev/null || {
            echo "❌ Unknown command: $1"
            echo ""
            show_help
            exit 1
        }
        ;;
esac
