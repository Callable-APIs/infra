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
        
        # Multi-region support
        self.regions: Dict[str, Dict[str, List[Dict[str, Any]]]] = {}
        
        # Load discovered resources from all regions
        self.discovered_resources = self._load_all_discovered_resources()

    def ensure_output_directory(self):
        """Ensure output directory exists with proper structure."""
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(f"{self.output_dir}/modules", exist_ok=True)
        os.makedirs(f"{self.output_dir}/environments", exist_ok=True)

    def _load_all_discovered_resources(self) -> Dict[str, List[Dict[str, Any]]]:
        """Load discovery results from all regions and organize by region."""
        # Look in terraform_output directory
        terraform_output_dir = "terraform_output"
        if not os.path.exists(terraform_output_dir):
            logger.error("terraform_output directory not found. Run terraform-discover first.")
            return {}
        
        discovery_files = [f for f in os.listdir(terraform_output_dir) if f.startswith("discovered_resources_") and f.endswith(".json")]
        
        if not discovery_files:
            logger.error("No discovery results found. Run terraform-discover first.")
            return {}
        
        # Load all discovery files and organize by region
        all_resources = {}
        region_mapping = {}
        
        for file in discovery_files:
            filepath = os.path.join(terraform_output_dir, file)
            with open(filepath, 'r') as f:
                resources = json.load(f)
                
                # Determine region from the resources (look for region-specific identifiers)
                region = self._determine_region_from_resources(resources)
                region_mapping[file] = region
                
                if region not in self.regions:
                    self.regions[region] = {}
                
                # Merge resources by type
                for resource_type, resource_list in resources.items():
                    if resource_type not in all_resources:
                        all_resources[resource_type] = []
                    if resource_type not in self.regions[region]:
                        self.regions[region][resource_type] = []
                    
                    # Add region information to each resource
                    for resource in resource_list:
                        resource['region'] = region
                        all_resources[resource_type].append(resource)
                        self.regions[region][resource_type].append(resource)
        
        logger.info(f"Loaded resources from regions: {list(self.regions.keys())}")
        return all_resources
    
    def _determine_region_from_resources(self, resources: Dict[str, List[Dict[str, Any]]]) -> str:
        """Determine the region from resource data."""
        # Check EC2 instances for region clues
        if 'ec2_instances' in resources and resources['ec2_instances']:
            instance = resources['ec2_instances'][0]
            if 'data' in instance and 'Placement' in instance['data']:
                az = instance['data']['Placement'].get('AvailabilityZone', '')
                if az.startswith('us-east-1'):
                    return 'us-east-1'
                elif az.startswith('us-east-2'):
                    return 'us-east-2'
                elif az.startswith('us-west-2'):
                    return 'us-west-2'
        
        # Check VPCs for region clues
        if 'vpcs' in resources and resources['vpcs']:
            vpc = resources['vpcs'][0]
            if 'data' in vpc and 'VpcId' in vpc['data']:
                vpc_id = vpc['data']['VpcId']
                # VPC IDs have region-specific patterns
                if vpc_id.startswith('vpc-') and len(vpc_id) > 4:
                    # This is a simplified approach - in practice, you'd need to query AWS
                    # For now, we'll use a default region
                    pass
        
        # Default to us-east-1 if we can't determine
        return 'us-east-1'

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
        
        # Generate region-specific configurations
        self.generate_region_configurations()
        
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
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')
        content = f"""# Main Terraform configuration
# Generated on {timestamp}
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
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')
        content = f"""# Output definitions
# Generated on {timestamp}

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
                block = self._generate_resource_block(resource, "us_east_1")
                if block:
                    resource_blocks.append(block)
        
        return '\n'.join(resource_blocks)

    def _generate_resource_block(self, resource: Dict[str, Any], provider_alias: str = "us_east_1") -> str:
        """Generate a single resource block."""
        resource_type = resource['type']
        resource_data = resource['data']
        resource_id = resource['id']
        
        # Get a safe resource name
        resource_name = self._get_resource_name(resource, resource_type)
        
        # Add provider alias to all resource blocks
        provider_line = f"  provider = aws.{provider_alias}\n"
        
        if resource_type == 'aws_instance':
            return self._generate_ec2_instance_block(resource_name, resource_data, provider_line)
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

    def _generate_ec2_instance_block(self, name: str, data: Dict[str, Any], provider_line: str = "") -> str:
        """Generate EC2 instance resource block."""
        tags = self._format_tags(data.get('Tags', []))
        
        return f"""
resource "aws_instance" "{name}" {{
{provider_line}  ami           = "{data.get('ImageId', '')}"
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

    def generate_providers_tf(self):
        """Generate multi-region provider configuration."""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')
        content = f"""# Multi-region AWS provider configuration
# Generated on {timestamp}

# Default provider (us-east-1)
provider "aws" {{
  region = "us-east-1"
  alias  = "us_east_1"
  
  default_tags {{
    tags = {{
      ManagedBy = "terraform"
      Generated = "true"
      Project   = var.project_name
      Region    = "us-east-1"
    }}
  }}
}}

# us-east-2 provider
provider "aws" {{
  region = "us-east-2"
  alias  = "us_east_2"
  
  default_tags {{
    tags = {{
      ManagedBy = "terraform"
      Generated = "true"
      Project   = var.project_name
      Region    = "us-east-2"
    }}
  }}
}}

# us-west-2 provider (for future migration)
provider "aws" {{
  region = "us-west-2"
  alias  = "us_west_2"
  
  default_tags {{
    tags = {{
      ManagedBy = "terraform"
      Generated = "true"
      Project   = var.project_name
      Region    = "us-west-2"
    }}
  }}
}}
"""
        
        with open(f"{self.output_dir}/providers.tf", 'w') as f:
            f.write(content)

    def generate_region_configurations(self):
        """Generate region-specific Terraform configurations."""
        for region, resources in self.regions.items():
            self._generate_region_file(region, resources)

    def _generate_region_file(self, region: str, resources: Dict[str, List[Dict[str, Any]]]):
        """Generate a Terraform file for a specific region."""
        region_alias = region.replace('-', '_')
        
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')
        content = f"""# {region.upper()} Region Configuration
# Generated on {timestamp}
# 
# This file contains resources specific to the {region} region.
# All resources in this file use the aws.{region_alias} provider.

"""
        
        # Add import blocks for this region
        import_blocks = []
        resource_blocks = []
        
        for resource_type, resource_list in resources.items():
            for resource in resource_list:
                if resource.get('region') == region:
                    # Generate import block
                    import_block = self._generate_import_block(resource)
                    if import_block:
                        import_blocks.append(import_block)
                    
                    # Generate resource block
                    resource_block = self._generate_resource_block(resource, region_alias)
                    if resource_block:
                        resource_blocks.append(resource_block)
        
        # Add import blocks
        if import_blocks:
            content += "# Import blocks for existing resources\n"
            for import_block in import_blocks:
                content += import_block + "\n"
            content += "\n"
        
        # Add resource blocks
        if resource_blocks:
            content += "# Resource definitions\n"
            for resource_block in resource_blocks:
                content += resource_block + "\n"
        
        # Write region-specific file
        filename = f"{self.output_dir}/{region_alias}.tf"
        with open(filename, 'w') as f:
            f.write(content)
        
        logger.info(f"Generated {region} configuration: {filename}")

    def _generate_import_block(self, resource: Dict[str, Any]) -> str:
        """Generate an import block for a resource."""
        resource_type = resource.get('type', '')
        resource_id = resource.get('id', '')
        
        if not resource_type or not resource_id:
            return ""
        
        # Generate a safe resource name
        safe_name = self._generate_safe_resource_name(resource_type, resource_id)
        
        return f"""import {{
  to = {resource_type}.{safe_name}
  id = "{resource_id}"
}}"""

    def _generate_resource_block(self, resource: Dict[str, Any], provider_alias: str) -> str:
        """Generate a resource block for a resource."""
        resource_type = resource.get('type', '')
        resource_id = resource.get('id', '')
        resource_data = resource.get('data', {})
        
        if not resource_type or not resource_id:
            return ""
        
        # Generate a safe resource name
        safe_name = self._generate_safe_resource_name(resource_type, resource_id)
        
        # Add provider alias
        provider_line = f"  provider = aws.{provider_alias}\n"
        
        # Generate basic resource block (this is a simplified version)
        # In a full implementation, you'd generate the complete resource configuration
        block = f"""resource "{resource_type}" "{safe_name}" {{
{provider_line}  # Resource configuration would be generated here
  # This is a placeholder - full configuration needs to be implemented
}}"""
        
        return block

    def _generate_safe_resource_name(self, resource_type: str, resource_id: str) -> str:
        """Generate a safe Terraform resource name."""
        # Remove common prefixes and make it Terraform-safe
        safe_id = resource_id.replace('-', '_').replace('.', '_')
        
        # Add resource type prefix if needed
        if resource_type.startswith('aws_'):
            type_prefix = resource_type.replace('aws_', '')
        else:
            type_prefix = resource_type
        
        return f"{type_prefix}_{safe_id}"


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
