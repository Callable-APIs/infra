"""Terraform Configuration Generator from Discovered AWS Resources."""

import json
import logging
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class TerraformGenerator:
    """Generates Terraform configurations from discovered AWS resources."""

    def __init__(self, output_dir: str = "terraform"):
        """
        Initialize Terraform generator.

        Args:
            output_dir: Directory to output Terraform files
        """
        self.output_dir = output_dir
        self.ensure_output_directory()
        
        # Resource name mappings to avoid conflicts
        self.resource_names: Dict[str, int] = {}
        
        # Load discovered resources
        self.discovered_resources = self._load_discovered_resources()

    def ensure_output_directory(self):
        """Ensure output directory exists with proper structure."""
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(f"{self.output_dir}/modules", exist_ok=True)
        os.makedirs(f"{self.output_dir}/environments", exist_ok=True)

    def _load_discovered_resources(self) -> Dict[str, List[Dict[str, Any]]]:
        """Load the most recent discovery results."""
        # Look in terraform_output directory
        terraform_output_dir = "terraform_output"
        if not os.path.exists(terraform_output_dir):
            logger.error("terraform_output directory not found. Run terraform-discover first.")
            return {}
        
        discovery_files = [f for f in os.listdir(terraform_output_dir) if f.startswith("discovered_resources_") and f.endswith(".json")]
        
        if not discovery_files:
            logger.error("No discovery results found. Run terraform-discover first.")
            return {}
        
        # Get the most recent file by modification time
        latest_file = max(discovery_files, key=lambda x: os.path.getmtime(os.path.join(terraform_output_dir, x)))
        filepath = os.path.join(terraform_output_dir, latest_file)
        
        with open(filepath, 'r') as f:
            return json.load(f)

    def generate_all_configurations(self):
        """Generate all Terraform configurations."""
        logger.info("Generating Terraform configurations...")
        
        # Generate main configuration
        self.generate_main_tf()
        
        # Generate variables
        self.generate_variables_tf()
        
        # Generate outputs
        self.generate_outputs_tf()
        
        # Generate provider configuration
        self.generate_providers_tf()
        
        # Generate resource configurations
        self.generate_ec2_resources()
        self.generate_vpc_resources()
        self.generate_route53_resources()
        self.generate_s3_resources()
        self.generate_iam_resources()
        
        # Generate modules
        self.generate_modules()
        
        logger.info(f"Terraform configurations generated in {self.output_dir}/")

    def generate_main_tf(self):
        """Generate main.tf file."""
        content = f"""# Main Terraform configuration
# Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}
# 
# This file contains the main infrastructure configuration
# generated from your current AWS deployment.
# 
# IMPORTANT: This configuration uses import blocks to import existing resources.
# Run 'terraform plan' to verify the configuration matches your current infrastructure.

terraform {{
  required_version = ">= 1.5"
  required_providers {{
    aws = {{
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }}
  }}
}}

# Import blocks for existing resources
{self._generate_import_blocks()}

# Resource configurations
{self._generate_resource_blocks()}
"""
        
        with open(f"{self.output_dir}/main.tf", 'w') as f:
            f.write(content)

    def generate_providers_tf(self):
        """Generate providers.tf file."""
        content = """# Provider configuration
provider "aws" {
  region = var.aws_region
  
  default_tags {
    tags = {
      ManagedBy = "terraform"
      Generated = "true"
      Project   = var.project_name
    }
  }
}

# Configure multiple AWS providers for different regions if needed
# provider "aws" {
#   alias  = "us-west-2"
#   region = "us-west-2"
# }
"""
        
        with open(f"{self.output_dir}/providers.tf", 'w') as f:
            f.write(content)

    def generate_variables_tf(self):
        """Generate variables.tf file."""
        content = """# Variable definitions
variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Name of the project"
  type        = string
  default     = "aws-infrastructure"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "production"
}

# Add more variables as needed
variable "common_tags" {
  description = "Common tags to apply to all resources"
  type        = map(string)
  default = {
    Environment = "production"
    Project     = "aws-infrastructure"
    ManagedBy   = "terraform"
  }
}
"""
        
        with open(f"{self.output_dir}/variables.tf", 'w') as f:
            f.write(content)

    def generate_outputs_tf(self):
        """Generate outputs.tf file."""
        content = f"""# Output definitions
# Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}

{self._generate_output_blocks()}
"""
        
        with open(f"{self.output_dir}/outputs.tf", 'w') as f:
            f.write(content)

    def _generate_import_blocks(self) -> str:
        """Generate import blocks for existing resources."""
        import_blocks = []
        
        for resource_type, resources in self.discovered_resources.items():
            for resource in resources:
                import_block = self._generate_import_block(resource)
                if import_block:
                    import_blocks.append(import_block)
        
        return '\n'.join(import_blocks)

    def _generate_import_block(self, resource: Dict[str, Any]) -> str:
        """Generate a single import block."""
        resource_type = resource['type']
        resource_data = resource['data']
        resource_id = resource['id']
        
        # Get a safe resource name
        resource_name = self._get_resource_name(resource, resource_type)
        
        if resource_type == 'aws_instance':
            return f"""import {{
  to = aws_instance.{resource_name}
  id = "{resource_id}"
}}"""
        elif resource_type == 'aws_vpc':
            return f"""import {{
  to = aws_vpc.{resource_name}
  id = "{resource_id}"
}}"""
        elif resource_type == 'aws_subnet':
            return f"""import {{
  to = aws_subnet.{resource_name}
  id = "{resource_id}"
}}"""
        elif resource_type == 'aws_security_group':
            return f"""import {{
  to = aws_security_group.{resource_name}
  id = "{resource_id}"
}}"""
        elif resource_type == 'aws_route53_zone':
            return f"""import {{
  to = aws_route53_zone.{resource_name}
  id = "{resource_id}"
}}"""
        elif resource_type == 'aws_route53_record':
            # Route53 records need special handling for the ID format
            zone_id = resource.get('zone_id', '').split('/')[-1]  # Remove /hostedzone/ prefix
            record_name = resource_data.get('Name', '')
            record_type = resource_data.get('Type', '')
            record_id = f"{zone_id}_{record_name}_{record_type}"
            return f"""import {{
  to = aws_route53_record.{resource_name}
  id = "{record_id}"
}}"""
        elif resource_type == 'aws_s3_bucket':
            return f"""import {{
  to = aws_s3_bucket.{resource_name}
  id = "{resource_id}"
}}"""
        elif resource_type == 'aws_iam_role':
            return f"""import {{
  to = aws_iam_role.{resource_name}
  id = "{resource_id}"
}}"""
        elif resource_type == 'aws_iam_policy':
            return f"""import {{
  to = aws_iam_policy.{resource_name}
  id = "{resource_id}"
}}"""
        elif resource_type == 'aws_ebs_volume':
            return f"""import {{
  to = aws_ebs_volume.{resource_name}
  id = "{resource_id}"
}}"""
        elif resource_type == 'aws_internet_gateway':
            return f"""import {{
  to = aws_internet_gateway.{resource_name}
  id = "{resource_id}"
}}"""
        elif resource_type == 'aws_nat_gateway':
            return f"""import {{
  to = aws_nat_gateway.{resource_name}
  id = "{resource_id}"
}}"""
        elif resource_type == 'aws_eip':
            return f"""import {{
  to = aws_eip.{resource_name}
  id = "{resource_id}"
}}"""
        elif resource_type == 'aws_route_table':
            return f"""import {{
  to = aws_route_table.{resource_name}
  id = "{resource_id}"
}}"""
        
        return ""

    def _generate_resource_blocks(self) -> str:
        """Generate resource blocks for all discovered resources."""
        resource_blocks = []
        
        for resource_type, resources in self.discovered_resources.items():
            for resource in resources:
                block = self._generate_resource_block(resource)
                if block:
                    resource_blocks.append(block)
        
        return '\n'.join(resource_blocks)

    def _generate_resource_block(self, resource: Dict[str, Any]) -> str:
        """Generate a single resource block."""
        resource_type = resource['type']
        resource_data = resource['data']
        resource_id = resource['id']
        
        # Get a safe resource name
        resource_name = self._get_resource_name(resource, resource_type)
        
        if resource_type == 'aws_instance':
            return self._generate_ec2_instance_block(resource_name, resource_data)
        elif resource_type == 'aws_vpc':
            return self._generate_vpc_block(resource_name, resource_data)
        elif resource_type == 'aws_subnet':
            return self._generate_subnet_block(resource_name, resource_data)
        elif resource_type == 'aws_security_group':
            return self._generate_security_group_block(resource_name, resource_data)
        elif resource_type == 'aws_route53_zone':
            return self._generate_route53_zone_block(resource_name, resource_data)
        elif resource_type == 'aws_route53_record':
            # Pass the full resource data including zone_id
            return self._generate_route53_record_block(resource_name, resource)
        elif resource_type == 'aws_s3_bucket':
            return self._generate_s3_bucket_block(resource_name, resource_data)
        elif resource_type == 'aws_iam_role':
            return self._generate_iam_role_block(resource_name, resource_data)
        elif resource_type == 'aws_iam_policy':
            return self._generate_iam_policy_block(resource_name, resource_data)
        elif resource_type == 'aws_ebs_volume':
            return self._generate_ebs_volume_block(resource_name, resource_data)
        elif resource_type == 'aws_internet_gateway':
            return self._generate_internet_gateway_block(resource_name, resource_data)
        elif resource_type == 'aws_nat_gateway':
            return self._generate_nat_gateway_block(resource_name, resource_data)
        elif resource_type == 'aws_eip':
            return self._generate_eip_block(resource_name, resource_data)
        elif resource_type == 'aws_route_table':
            return self._generate_route_table_block(resource_name, resource_data)
        
        return ""

    def _generate_ec2_instance_block(self, name: str, data: Dict[str, Any]) -> str:
        """Generate EC2 instance resource block."""
        tags = self._format_tags(data.get('Tags', []))
        
        return f"""
resource "aws_instance" "{name}" {{
  ami           = "{data.get('ImageId', '')}"
  instance_type = "{data.get('InstanceType', '')}"
  subnet_id     = "{data.get('SubnetId', '')}"
  
  vpc_security_group_ids = {self._format_list([sg['GroupId'] for sg in data.get('SecurityGroups', [])])}
  
  # Add key_name if available
  # key_name = "your-key-pair"
  
  # Add user_data if available
  # user_data = base64encode(file("user_data.sh"))
  
  tags = {{
    Name = "{data.get('InstanceId', name)}"
    {tags}
  }}
}}
"""

    def _generate_vpc_block(self, name: str, data: Dict[str, Any]) -> str:
        """Generate VPC resource block."""
        tags = self._format_tags(data.get('Tags', []))
        
        return f"""
resource "aws_vpc" "{name}" {{
  cidr_block           = "{data.get('CidrBlock', '10.0.0.0/16')}"
  enable_dns_hostnames = {str(data.get('EnableDnsHostnames', True)).lower()}
  enable_dns_support   = {str(data.get('EnableDnsSupport', True)).lower()}
  
  tags = {{
    Name = "{data.get('VpcId', name)}"
    {tags}
  }}
}}
"""

    def _generate_subnet_block(self, name: str, data: Dict[str, Any]) -> str:
        """Generate subnet resource block."""
        tags = self._format_tags(data.get('Tags', []))
        
        return f"""
resource "aws_subnet" "{name}" {{
  vpc_id            = "{data.get('VpcId', '')}"
  cidr_block        = "{data.get('CidrBlock', '')}"
  availability_zone = "{data.get('AvailabilityZone', '')}"
  
  map_public_ip_on_launch = {str(data.get('MapPublicIpOnLaunch', False)).lower()}
  
  tags = {{
    Name = "{data.get('SubnetId', name)}"
    {tags}
  }}
}}
"""

    def _generate_security_group_block(self, name: str, data: Dict[str, Any]) -> str:
        """Generate security group resource block."""
        tags = self._format_tags(data.get('Tags', []))
        
        # Generate ingress rules
        ingress_rules = []
        for rule in data.get('IpPermissions', []):
            for ip_range in rule.get('IpRanges', []):
                ingress_rules.append(f"""
  ingress {{
    from_port   = {rule.get('FromPort', 0)}
    to_port     = {rule.get('ToPort', 0)}
    protocol    = "{rule.get('IpProtocol', 'tcp')}"
    cidr_blocks = ["{ip_range.get('CidrIp', '0.0.0.0/0')}"]
    description = "{ip_range.get('Description', '')}"
  }}""")
        
        # Generate egress rules
        egress_rules = []
        for rule in data.get('IpPermissionsEgress', []):
            for ip_range in rule.get('IpRanges', []):
                egress_rules.append(f"""
  egress {{
    from_port   = {rule.get('FromPort', 0)}
    to_port     = {rule.get('ToPort', 0)}
    protocol    = "{rule.get('IpProtocol', 'tcp')}"
    cidr_blocks = ["{ip_range.get('CidrIp', '0.0.0.0/0')}"]
    description = "{ip_range.get('Description', '')}"
  }}""")
        
        return f"""
resource "aws_security_group" "{name}" {{
  name        = "{data.get('GroupName', name)}"
  description = "{data.get('Description', '')}"
  vpc_id      = "{data.get('VpcId', '')}"
  
  {''.join(ingress_rules)}
  {''.join(egress_rules)}
  
  tags = {{
    Name = "{data.get('GroupName', name)}"
    {tags}
  }}
}}
"""

    def _generate_route53_zone_block(self, name: str, data: Dict[str, Any]) -> str:
        """Generate Route53 zone resource block."""
        return f"""
resource "aws_route53_zone" "{name}" {{
  name = "{data.get('Name', '')}"
  
  tags = {{
    Name = "{data.get('Name', name)}"
  }}
}}
"""

    def _generate_route53_record_block(self, name: str, resource: Dict[str, Any]) -> str:
        """Generate Route53 record resource block."""
        # Get zone_id from the resource data
        zone_id = resource.get('zone_id', '')
        if zone_id.startswith('/hostedzone/'):
            zone_id = zone_id.split('/')[-1]  # Remove /hostedzone/ prefix
        
        # Get the actual record data
        record_data = resource.get('data', {})
        records = [record.get('Value', '') for record in record_data.get('ResourceRecords', [])]
        
        # Handle alias records differently
        if 'AliasTarget' in record_data:
            alias_target = record_data['AliasTarget']
            return f"""
resource "aws_route53_record" "{name}" {{
  zone_id = "{zone_id}"
  name    = "{record_data.get('Name', '')}"
  type    = "{record_data.get('Type', '')}"
  
  alias {{
    name                   = "{alias_target.get('DNSName', '')}"
    zone_id                = "{alias_target.get('HostedZoneId', '')}"
    evaluate_target_health = {str(alias_target.get('EvaluateTargetHealth', False)).lower()}
  }}
}}
"""
        else:
            return f"""
resource "aws_route53_record" "{name}" {{
  zone_id = "{zone_id}"
  name    = "{record_data.get('Name', '')}"
  type    = "{record_data.get('Type', '')}"
  ttl     = {record_data.get('TTL', 300)}
  
  records = {self._format_list(records)}
}}
"""

    def _generate_s3_bucket_block(self, name: str, data: Dict[str, Any]) -> str:
        """Generate S3 bucket resource block."""
        return f"""
resource "aws_s3_bucket" "{name}" {{
  bucket = "{data.get('Name', name)}"
  
  tags = {{
    Name = "{data.get('Name', name)}"
  }}
}}

resource "aws_s3_bucket_versioning" "{name}" {{
  bucket = aws_s3_bucket.{name}.id
  versioning_configuration {{
    status = "Enabled"
  }}
}}

resource "aws_s3_bucket_server_side_encryption_configuration" "{name}" {{
  bucket = aws_s3_bucket.{name}.id
  
  rule {{
    apply_server_side_encryption_by_default {{
      sse_algorithm = "AES256"
    }}
  }}
}}
"""

    def _generate_iam_role_block(self, name: str, data: Dict[str, Any]) -> str:
        """Generate IAM role resource block."""
        tags = self._format_tags(data.get('Tags', []))
        
        return f"""
resource "aws_iam_role" "{name}" {{
  name = "{data.get('RoleName', name)}"
  
  assume_role_policy = jsonencode({{
    Version = "2012-10-17"
    Statement = [
      {{
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {{
          Service = "ec2.amazonaws.com"
        }}
      }}
    ]
  }})
  
  tags = {{
    Name = "{data.get('RoleName', name)}"
    {tags}
  }}
}}

resource "aws_iam_instance_profile" "{name}" {{
  name = "{data.get('RoleName', name)}-profile"
  role = aws_iam_role.{name}.name
}}
"""

    def _generate_iam_policy_block(self, name: str, data: Dict[str, Any]) -> str:
        """Generate IAM policy resource block."""
        tags = self._format_tags(data.get('Tags', []))
        
        return f"""
resource "aws_iam_policy" "{name}" {{
  name        = "{data.get('PolicyName', name)}"
  description = "{data.get('Description', '')}"
  
  policy = jsonencode({{
    Version = "2012-10-17"
    Statement = [
      {{
        Effect = "Allow"
        Action = "*"
        Resource = "*"
      }}
    ]
  }})
  
  tags = {{
    Name = "{data.get('PolicyName', name)}"
    {tags}
  }}
}}
"""

    def _generate_ebs_volume_block(self, name: str, data: Dict[str, Any]) -> str:
        """Generate EBS volume resource block."""
        tags = self._format_tags(data.get('Tags', []))
        
        return f"""
resource "aws_ebs_volume" "{name}" {{
  availability_zone = "{data.get('AvailabilityZone', '')}"
  size              = {data.get('Size', 8)}
  type              = "{data.get('VolumeType', 'gp2')}"
  encrypted         = {str(data.get('Encrypted', False)).lower()}
  
  tags = {{
    Name = "{data.get('VolumeId', name)}"
    {tags}
  }}
}}
"""

    def _generate_internet_gateway_block(self, name: str, data: Dict[str, Any]) -> str:
        """Generate internet gateway resource block."""
        tags = self._format_tags(data.get('Tags', []))
        
        return f"""
resource "aws_internet_gateway" "{name}" {{
  vpc_id = "{data.get('VpcId', '')}"
  
  tags = {{
    Name = "{data.get('InternetGatewayId', name)}"
    {tags}
  }}
}}
"""

    def _generate_nat_gateway_block(self, name: str, data: Dict[str, Any]) -> str:
        """Generate NAT gateway resource block."""
        tags = self._format_tags(data.get('Tags', []))
        
        return f"""
resource "aws_nat_gateway" "{name}" {{
  allocation_id = "{data.get('NatGatewayAddresses', [{}])[0].get('AllocationId', '')}"
  subnet_id     = "{data.get('SubnetId', '')}"
  
  tags = {{
    Name = "{data.get('NatGatewayId', name)}"
    {tags}
  }}
}}
"""

    def _generate_eip_block(self, name: str, data: Dict[str, Any]) -> str:
        """Generate Elastic IP resource block."""
        tags = self._format_tags(data.get('Tags', []))
        
        return f"""
resource "aws_eip" "{name}" {{
  domain = "vpc"
  
  tags = {{
    Name = "{data.get('PublicIp', name)}"
    {tags}
  }}
}}
"""

    def _generate_route_table_block(self, name: str, data: Dict[str, Any]) -> str:
        """Generate route table resource block."""
        tags = self._format_tags(data.get('Tags', []))
        
        return f"""
resource "aws_route_table" "{name}" {{
  vpc_id = "{data.get('VpcId', '')}"
  
  tags = {{
    Name = "{data.get('RouteTableId', name)}"
    {tags}
  }}
}}
"""

    def _generate_output_blocks(self) -> str:
        """Generate output blocks."""
        outputs = []
        
        # Add outputs for key resources that actually exist
        for resource_type, resources in self.discovered_resources.items():
            if resource_type == 'aws_vpc' and resources:
                for resource in resources:
                    name = self._get_resource_name(resource, 'aws_vpc')
                    outputs.append(f"""
output "{name}_id" {{
  description = "ID of the VPC"
  value       = aws_vpc.{name}.id
}}

output "{name}_cidr_block" {{
  description = "CIDR block of the VPC"
  value       = aws_vpc.{name}.cidr_block
}}
""")
        
        return '\n'.join(outputs)

    def _get_resource_name(self, resource: Dict[str, Any], resource_type: str) -> str:
        """Get a safe resource name for Terraform."""
        # Try to get name from tags first
        tags = resource.get('tags', {})
        if 'Name' in tags:
            name = self._sanitize_name(tags['Name'])
        else:
            # Use resource ID as fallback
            name = self._sanitize_name(resource.get('id', f"{resource_type}_{len(self.resource_names)}"))
        
        # Ensure uniqueness
        if name in self.resource_names:
            self.resource_names[name] += 1
            name = f"{name}_{self.resource_names[name]}"
        else:
            self.resource_names[name] = 0
        
        return name

    def _sanitize_name(self, name: str) -> str:
        """Sanitize name for Terraform resource naming."""
        # Replace invalid characters with underscores
        import re
        sanitized = re.sub(r'[^a-zA-Z0-9_-]', '_', name)
        # Ensure it starts with a letter
        if sanitized and not sanitized[0].isalpha():
            sanitized = f"resource_{sanitized}"
        return sanitized.lower()

    def _format_tags(self, tags: List[Dict[str, str]]) -> str:
        """Format tags for Terraform."""
        if not tags:
            return ""
        
        tag_lines = []
        for tag in tags:
            key = tag.get('Key', '')
            value = tag.get('Value', '')
            if key and value:
                # Quote keys that contain special characters
                if ':' in key or '-' in key or ' ' in key:
                    quoted_key = f'"{key}"'
                else:
                    quoted_key = key
                # Escape quotes in values
                escaped_value = str(value).replace('"', '\\"')
                tag_lines.append(f'    {quoted_key} = "{escaped_value}"')
        
        return '\n'.join(tag_lines)

    def _format_list(self, items: List[str]) -> str:
        """Format a list for Terraform."""
        if not items:
            return "[]"
        
        formatted_items = [f'"{item}"' for item in items if item]
        return f'[{", ".join(formatted_items)}]'

    def generate_ec2_resources(self):
        """Generate EC2-specific resource files."""
        # This could be expanded to create separate files for different resource types
        pass

    def generate_vpc_resources(self):
        """Generate VPC-specific resource files."""
        # This could be expanded to create separate files for different resource types
        pass

    def generate_route53_resources(self):
        """Generate Route53-specific resource files."""
        # This could be expanded to create separate files for different resource types
        pass

    def generate_s3_resources(self):
        """Generate S3-specific resource files."""
        # This could be expanded to create separate files for different resource types
        pass

    def generate_iam_resources(self):
        """Generate IAM-specific resource files."""
        # This could be expanded to create separate files for different resource types
        pass

    def generate_modules(self):
        """Generate Terraform modules."""
        # Create a basic module structure
        module_content = """# Example module for reusable components
# This is a placeholder for future module development

variable "environment" {
  description = "Environment name"
  type        = string
}

variable "project_name" {
  description = "Project name"
  type        = string
}

output "module_output" {
  description = "Example module output"
  value       = "Hello from module"
}
"""
        
        with open(f"{self.output_dir}/modules/example.tf", 'w') as f:
            f.write(module_content)


def main():
    """Main function for Terraform generation."""
    logging.basicConfig(level=logging.INFO)
    
    generator = TerraformGenerator()
    generator.generate_all_configurations()
    
    print("\n" + "="*60)
    print("TERRAFORM CONFIGURATION GENERATION COMPLETE")
    print("="*60)
    print(f"Generated files in: {generator.output_dir}/")
    print("\nNext steps:")
    print("1. Review the generated Terraform files")
    print("2. Run 'terraform init' in the terraform/ directory")
    print("3. Run 'terraform plan' to see what would change")
    print("4. Run 'terraform apply' to apply the configuration")
    print("="*60)


if __name__ == "__main__":
    main()
