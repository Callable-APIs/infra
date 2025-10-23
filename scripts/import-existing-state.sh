#!/bin/bash
# Script to import existing infrastructure from cloud provider state files
# This imports the ACTUAL state, not what we think should be there

set -e

echo "Importing existing infrastructure from cloud provider state files..."
echo "=================================================================="

cd /Users/rlee/dev/infra/terraform

# Function to extract resource IDs from state file
extract_resource_id() {
    local state_file=$1
    local resource_name=$2
    
    # Extract the resource ID from the state file
    docker run --rm -v $(pwd):/app -w /app callableapis:infra terraform state show -state="$state_file" "$resource_name" 2>/dev/null | grep -E "^\s*id\s*=" | head -1 | sed 's/.*= *"\(.*\)".*/\1/' || echo ""
}

# Function to import resources from a state file
import_from_state() {
    local provider=$1
    local state_file=$2
    
    echo "Importing $provider infrastructure from $state_file..."
    
    if [ ! -f "$state_file" ]; then
        echo "State file $state_file not found, skipping $provider"
        return
    fi
    
    # Get all resource addresses from the state file
    resources=$(docker run --rm -v $(pwd):/app -w /app callableapis:infra terraform state list -state="$state_file" 2>/dev/null || echo "")
    
    if [ -z "$resources" ]; then
        echo "No resources found in $provider state file"
        return
    fi
    
    echo "Found resources in $provider:"
    echo "$resources"
    echo ""
    
    # Import each resource
    while IFS= read -r resource; do
        if [ -n "$resource" ]; then
            echo "Importing $resource..."
            
            # Get the resource ID
            resource_id=$(extract_resource_id "$state_file" "$resource")
            
            if [ -n "$resource_id" ]; then
                echo "  Resource ID: $resource_id"
                
                # Try to import the resource
                if docker run --rm -v $(pwd):/app -w /app \
                  -e AWS_ACCESS_KEY_ID="$AWS_ACCESS_KEY_ID" \
                  -e AWS_SECRET_ACCESS_KEY="$AWS_SECRET_ACCESS_KEY" \
                  callableapis:infra terraform import "$resource" "$resource_id" 2>/dev/null; then
                    echo "  ✅ Successfully imported $resource"
                else
                    echo "  ❌ Failed to import $resource (may not exist in main config yet)"
                fi
            else
                echo "  ❌ Could not determine resource ID for $resource"
            fi
        fi
    done <<< "$resources"
    
    echo ""
}

# Step 1: Import Google Cloud infrastructure
echo "Step 1: Importing Google Cloud infrastructure..."
import_from_state "Google Cloud" "google/terraform.tfstate"

# Step 2: Import Oracle Cloud infrastructure  
echo "Step 2: Importing Oracle Cloud infrastructure..."
import_from_state "Oracle Cloud" "oracle/terraform.tfstate"

# Step 3: Import IBM Cloud infrastructure
echo "Step 3: Importing IBM Cloud infrastructure..."
import_from_state "IBM Cloud" "ibm/terraform.tfstate"

# Step 4: Import SSH keys infrastructure
echo "Step 4: Importing SSH keys infrastructure..."
import_from_state "SSH Keys" "ssh_keys/terraform.tfstate"

echo "Import process completed!"
echo ""
echo "Next steps:"
echo "1. Review imported resources: docker run --rm -v \$(pwd):/app -w /app callableapis:infra terraform state list"
echo "2. Plan changes to see what needs to be updated: docker run --rm -v \$(pwd):/app -w /app callableapis:infra terraform plan"
echo "3. Update configuration files to match reality"
echo "4. Apply firewall rules: docker run --rm -v \$(pwd):/app -w /app callableapis:infra terraform apply"
