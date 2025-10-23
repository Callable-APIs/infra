#!/bin/bash
# Script to visualize Terraform state and infrastructure

set -e

echo "Terraform Infrastructure Visualization"
echo "===================================="

cd /Users/rlee/dev/infra/terraform

# Check if we have a state file
if [ ! -f ".terraform/terraform.tfstate" ] && [ ! -f "terraform.tfstate" ]; then
    echo "No Terraform state found. Initializing..."
    echo "yes" | docker run --rm -i -v $(pwd):/app -w /app \
      -e AWS_ACCESS_KEY_ID="$AWS_ACCESS_KEY_ID" \
      -e AWS_SECRET_ACCESS_KEY="$AWS_SECRET_ACCESS_KEY" \
      callableapis:infra terraform init
fi

echo ""
echo "1. Current Terraform State:"
echo "=========================="
docker run --rm -v $(pwd):/app -w /app \
  -e AWS_ACCESS_KEY_ID="$AWS_ACCESS_KEY_ID" \
  -e AWS_SECRET_ACCESS_KEY="$AWS_SECRET_ACCESS_KEY" \
  callableapis:infra terraform state list

echo ""
echo "2. Generating Infrastructure Graph..."
echo "==================================="

# Generate DOT graph
docker run --rm -v $(pwd):/app -w /app \
  -e AWS_ACCESS_KEY_ID="$AWS_ACCESS_KEY_ID" \
  -e AWS_SECRET_ACCESS_KEY="$AWS_SECRET_ACCESS_KEY" \
  callableapis:infra terraform graph > infrastructure.dot

echo "Graph saved to infrastructure.dot"

# Generate PNG image using Graphviz
if command -v dot >/dev/null 2>&1; then
    echo "Generating PNG image..."
    docker run --rm -v $(pwd):/app -w /app callableapis:infra dot -Tpng infrastructure.dot -o infrastructure.png
    echo "PNG image saved to infrastructure.png"
else
    echo "Graphviz not available, skipping PNG generation"
fi

echo ""
echo "3. Infrastructure Summary:"
echo "========================="

# Count resources by provider
echo "Resources by provider:"
docker run --rm -v $(pwd):/app -w /app \
  -e AWS_ACCESS_KEY_ID="$AWS_ACCESS_KEY_ID" \
  -e AWS_SECRET_ACCESS_KEY="$AWS_SECRET_ACCESS_KEY" \
  callableapis:infra terraform state list | cut -d'.' -f1 | sort | uniq -c | sort -nr

echo ""
echo "4. Resource Details:"
echo "==================="

# Show detailed resource information
docker run --rm -v $(pwd):/app -w /app \
  -e AWS_ACCESS_KEY_ID="$AWS_ACCESS_KEY_ID" \
  -e AWS_SECRET_ACCESS_KEY="$AWS_SECRET_ACCESS_KEY" \
  callableapis:infra terraform state list | while read resource; do
    echo "Resource: $resource"
    docker run --rm -v $(pwd):/app -w /app \
      -e AWS_ACCESS_KEY_ID="$AWS_ACCESS_KEY_ID" \
      -e AWS_SECRET_ACCESS_KEY="$AWS_SECRET_ACCESS_KEY" \
      callableapis:infra terraform state show "$resource" | head -5
    echo "---"
done

echo ""
echo "Visualization complete!"
echo "Files generated:"
echo "- infrastructure.dot (Graphviz DOT format)"
if [ -f "infrastructure.png" ]; then
    echo "- infrastructure.png (PNG image)"
fi
echo ""
echo "To view the graph:"
echo "- Open infrastructure.dot in a Graphviz viewer"
echo "- Or convert to other formats: dot -Tsvg infrastructure.dot -o infrastructure.svg"
