#!/bin/bash

# Docker run script for AWS Infrastructure Reporting Tool with Terraform
# This script runs the container with proper volume mounts for reports and terraform configs

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
IMAGE_NAME="aws-infra-report"
CONTAINER_NAME="aws-infra-report-container"

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

# Function to show help
show_help() {
    echo "AWS Infrastructure Reporting Tool - Docker Runner"
    echo "================================================="
    echo ""
    echo "Usage: $0 [COMMAND] [OPTIONS]"
    echo ""
    echo "Commands:"
    echo "  build                     Build the Docker image"
    echo "  cost-report [OPTIONS]     Generate cost reports"
    echo "  terraform-discover        Discover current AWS infrastructure"
    echo "  terraform-generate        Generate Terraform configuration"
    echo "  terraform-plan            Run terraform plan on generated config"
    echo "  full-analysis             Run complete analysis (cost + terraform)"
    echo "  shell                     Open shell in container"
    echo "  clean                     Clean up containers and images"
    echo "  help                      Show this help message"
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
    echo "Examples:"
    echo "  # Build the image"
    echo "  $0 build"
    echo ""
    echo "  # Generate public cost report"
    echo "  $0 cost-report"
    echo ""
    echo "  # Generate internal cost report"
    echo "  $0 cost-report --internal"
    echo ""
    echo "  # Discover infrastructure and generate Terraform"
    echo "  $0 full-analysis"
    echo ""
    echo "  # Open shell in container"
    echo "  $0 shell"
}

# Function to check if Docker is running
check_docker() {
    if ! docker info >/dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker and try again."
        exit 1
    fi
}

# Function to check AWS credentials
check_aws_credentials() {
    if [ -z "$AWS_ACCESS_KEY_ID" ] || [ -z "$AWS_SECRET_ACCESS_KEY" ]; then
        print_error "AWS credentials not found!"
        echo ""
        echo "Please set the following environment variables:"
        echo "  export AWS_ACCESS_KEY_ID=your_access_key"
        echo "  export AWS_SECRET_ACCESS_KEY=your_secret_key"
        echo "  export AWS_DEFAULT_REGION=us-east-1  # optional"
        echo ""
        echo "Or create a .env file with:"
        echo "  AWS_ACCESS_KEY_ID=your_access_key"
        echo "  AWS_SECRET_ACCESS_KEY=your_secret_key"
        echo "  AWS_DEFAULT_REGION=us-east-1"
        exit 1
    fi
}

# Function to create necessary directories
create_directories() {
    print_status "Creating necessary directories..."
    mkdir -p reports
    mkdir -p internal_reports
    mkdir -p terraform
    mkdir -p terraform_output
    print_success "Directories created"
}

# Function to build Docker image
build_image() {
    print_status "Building Docker image..."
    docker build -t $IMAGE_NAME .
    print_success "Docker image built successfully"
}

# Function to run container with common options
run_container() {
    local command="$1"
    shift
    
    # Check if image exists
    if ! docker image inspect $IMAGE_NAME >/dev/null 2>&1; then
        print_warning "Docker image not found. Building..."
        build_image
    fi
    
    # Create directories
    create_directories
    
    # Load environment variables from .env file if it exists
    if [ -f .env ]; then
        print_status "Loading environment variables from .env file"
        export $(cat .env | grep -v '^#' | xargs)
    fi
    
    # Check AWS credentials
    check_aws_credentials
    
    # Run container
    print_status "Running container with command: $command"
    docker run --rm \
        -v "$(pwd)/reports:/app/reports" \
        -v "$(pwd)/internal_reports:/app/internal_reports" \
        -v "$(pwd)/terraform:/app/terraform" \
        -v "$(pwd)/terraform_output:/app/terraform_output" \
        -e AWS_ACCESS_KEY_ID \
        -e AWS_SECRET_ACCESS_KEY \
        -e AWS_DEFAULT_REGION \
        -e AWS_SESSION_TOKEN \
        --name $CONTAINER_NAME \
        $IMAGE_NAME \
        $command "$@"
}

# Function to open shell in container
open_shell() {
    # Check if image exists
    if ! docker image inspect $IMAGE_NAME >/dev/null 2>&1; then
        print_warning "Docker image not found. Building..."
        build_image
    fi
    
    # Create directories
    create_directories
    
    # Load environment variables from .env file if it exists
    if [ -f .env ]; then
        print_status "Loading environment variables from .env file"
        export $(cat .env | grep -v '^#' | xargs)
    fi
    
    print_status "Opening shell in container..."
    docker run --rm -it \
        -v "$(pwd)/reports:/app/reports" \
        -v "$(pwd)/internal_reports:/app/internal_reports" \
        -v "$(pwd)/terraform:/app/terraform" \
        -v "$(pwd)/terraform_output:/app/terraform_output" \
        -e AWS_ACCESS_KEY_ID \
        -e AWS_SECRET_ACCESS_KEY \
        -e AWS_DEFAULT_REGION \
        -e AWS_SESSION_TOKEN \
        --name $CONTAINER_NAME \
        $IMAGE_NAME \
        /bin/bash
}

# Function to clean up
cleanup() {
    print_status "Cleaning up containers and images..."
    
    # Stop and remove container if running
    if docker ps -q -f name=$CONTAINER_NAME | grep -q .; then
        docker stop $CONTAINER_NAME
        print_success "Stopped container"
    fi
    
    # Remove container if exists
    if docker ps -aq -f name=$CONTAINER_NAME | grep -q .; then
        docker rm $CONTAINER_NAME
        print_success "Removed container"
    fi
    
    # Remove image if exists
    if docker image inspect $IMAGE_NAME >/dev/null 2>&1; then
        docker rmi $IMAGE_NAME
        print_success "Removed image"
    fi
    
    print_success "Cleanup complete"
}

# Main script logic
check_docker

case "${1:-help}" in
    "build")
        build_image
        ;;
    "cost-report")
        shift
        run_container "cost-report" "$@"
        ;;
    "terraform-discover")
        run_container "terraform-discover"
        ;;
    "terraform-generate")
        run_container "terraform-generate"
        ;;
    "terraform-plan")
        run_container "terraform-plan"
        ;;
    "full-analysis")
        run_container "full-analysis"
        ;;
    "shell")
        open_shell
        ;;
    "clean")
        cleanup
        ;;
    "help"|"--help"|"-h")
        show_help
        ;;
    *)
        print_error "Unknown command: $1"
        echo ""
        show_help
        exit 1
        ;;
esac
