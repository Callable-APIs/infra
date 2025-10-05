"""AWS Infrastructure Discovery for Terraform Generation."""

import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)


class TerraformDiscovery:
    """Discovers AWS infrastructure and prepares data for Terraform generation."""

    def __init__(self, region: str = "us-east-1"):
        """
        Initialize Terraform discovery client.

        Args:
            region: AWS region to discover resources in
        """
        self.region = region
        self.session = boto3.Session()
        self.discovered_resources: Dict[str, List[Dict[str, Any]]] = {}
        
        # Initialize AWS service clients
        self.clients = {
            'ec2': boto3.client('ec2', region_name=region),
            'r53': boto3.client('route53', region_name=region),
            's3': boto3.client('s3', region_name=region),
            'vpc': boto3.client('ec2', region_name=region),  # VPC is part of EC2
            'iam': boto3.client('iam', region_name=region),
            'cloudwatch': boto3.client('cloudwatch', region_name=region),
        }

    def discover_all_resources(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Discover all AWS resources in the account.

        Returns:
            Dictionary of discovered resources by service
        """
        logger.info("Starting AWS infrastructure discovery...")
        
        # Discover resources by service
        self.discover_ec2_instances()
        self.discover_vpcs()
        self.discover_subnets()
        self.discover_security_groups()
        self.discover_route_tables()
        self.discover_internet_gateways()
        self.discover_nat_gateways()
        self.discover_elastic_ips()
        self.discover_volumes()
        self.discover_snapshots()
        self.discover_route53_zones()
        self.discover_route53_records()
        self.discover_s3_buckets()
        self.discover_iam_roles()
        self.discover_iam_policies()
        
        # Save discovery results
        self._save_discovery_results()
        
        logger.info(f"Discovery complete. Found {sum(len(resources) for resources in self.discovered_resources.values())} resources")
        return self.discovered_resources

    def discover_ec2_instances(self):
        """Discover EC2 instances."""
        try:
            response = self.clients['ec2'].describe_instances()
            instances = []
            
            for reservation in response.get('Reservations', []):
                for instance in reservation.get('Instances', []):
                    if instance['State']['Name'] not in ['terminated', 'shutting-down']:
                        instances.append({
                            'type': 'aws_instance',
                            'id': instance['InstanceId'],
                            'data': instance,
                            'tags': {tag['Key']: tag['Value'] for tag in instance.get('Tags', [])}
                        })
            
            self.discovered_resources['ec2_instances'] = instances
            logger.info(f"Discovered {len(instances)} EC2 instances")
            
        except ClientError as e:
            logger.error(f"Error discovering EC2 instances: {e}")

    def discover_vpcs(self):
        """Discover VPCs."""
        try:
            response = self.clients['vpc'].describe_vpcs()
            vpcs = []
            
            for vpc in response.get('Vpcs', []):
                vpcs.append({
                    'type': 'aws_vpc',
                    'id': vpc['VpcId'],
                    'data': vpc,
                    'tags': {tag['Key']: tag['Value'] for tag in vpc.get('Tags', [])}
                })
            
            self.discovered_resources['vpcs'] = vpcs
            logger.info(f"Discovered {len(vpcs)} VPCs")
            
        except ClientError as e:
            logger.error(f"Error discovering VPCs: {e}")

    def discover_subnets(self):
        """Discover subnets."""
        try:
            response = self.clients['vpc'].describe_subnets()
            subnets = []
            
            for subnet in response.get('Subnets', []):
                subnets.append({
                    'type': 'aws_subnet',
                    'id': subnet['SubnetId'],
                    'data': subnet,
                    'tags': {tag['Key']: tag['Value'] for tag in subnet.get('Tags', [])}
                })
            
            self.discovered_resources['subnets'] = subnets
            logger.info(f"Discovered {len(subnets)} subnets")
            
        except ClientError as e:
            logger.error(f"Error discovering subnets: {e}")

    def discover_security_groups(self):
        """Discover security groups."""
        try:
            response = self.clients['vpc'].describe_security_groups()
            security_groups = []
            
            for sg in response.get('SecurityGroups', []):
                security_groups.append({
                    'type': 'aws_security_group',
                    'id': sg['GroupId'],
                    'data': sg,
                    'tags': {tag['Key']: tag['Value'] for tag in sg.get('Tags', [])}
                })
            
            self.discovered_resources['security_groups'] = security_groups
            logger.info(f"Discovered {len(security_groups)} security groups")
            
        except ClientError as e:
            logger.error(f"Error discovering security groups: {e}")

    def discover_route_tables(self):
        """Discover route tables."""
        try:
            response = self.clients['vpc'].describe_route_tables()
            route_tables = []
            
            for rt in response.get('RouteTables', []):
                route_tables.append({
                    'type': 'aws_route_table',
                    'id': rt['RouteTableId'],
                    'data': rt,
                    'tags': {tag['Key']: tag['Value'] for tag in rt.get('Tags', [])}
                })
            
            self.discovered_resources['route_tables'] = route_tables
            logger.info(f"Discovered {len(route_tables)} route tables")
            
        except ClientError as e:
            logger.error(f"Error discovering route tables: {e}")

    def discover_internet_gateways(self):
        """Discover internet gateways."""
        try:
            response = self.clients['vpc'].describe_internet_gateways()
            igws = []
            
            for igw in response.get('InternetGateways', []):
                igws.append({
                    'type': 'aws_internet_gateway',
                    'id': igw['InternetGatewayId'],
                    'data': igw,
                    'tags': {tag['Key']: tag['Value'] for tag in igw.get('Tags', [])}
                })
            
            self.discovered_resources['internet_gateways'] = igws
            logger.info(f"Discovered {len(igws)} internet gateways")
            
        except ClientError as e:
            logger.error(f"Error discovering internet gateways: {e}")

    def discover_nat_gateways(self):
        """Discover NAT gateways."""
        try:
            response = self.clients['vpc'].describe_nat_gateways()
            nat_gateways = []
            
            for ngw in response.get('NatGateways', []):
                if ngw['State'] not in ['deleted', 'deleting']:
                    nat_gateways.append({
                        'type': 'aws_nat_gateway',
                        'id': ngw['NatGatewayId'],
                        'data': ngw,
                        'tags': {tag['Key']: tag['Value'] for tag in ngw.get('Tags', [])}
                    })
            
            self.discovered_resources['nat_gateways'] = nat_gateways
            logger.info(f"Discovered {len(nat_gateways)} NAT gateways")
            
        except ClientError as e:
            logger.error(f"Error discovering NAT gateways: {e}")

    def discover_elastic_ips(self):
        """Discover Elastic IPs."""
        try:
            response = self.clients['vpc'].describe_addresses()
            eips = []
            
            for eip in response.get('Addresses', []):
                eips.append({
                    'type': 'aws_eip',
                    'id': eip['AllocationId'] if 'AllocationId' in eip else eip['PublicIp'],
                    'data': eip,
                    'tags': {tag['Key']: tag['Value'] for tag in eip.get('Tags', [])}
                })
            
            self.discovered_resources['elastic_ips'] = eips
            logger.info(f"Discovered {len(eips)} Elastic IPs")
            
        except ClientError as e:
            logger.error(f"Error discovering Elastic IPs: {e}")

    def discover_volumes(self):
        """Discover EBS volumes."""
        try:
            response = self.clients['ec2'].describe_volumes()
            volumes = []
            
            for volume in response.get('Volumes', []):
                if volume['State'] not in ['deleted', 'deleting']:
                    volumes.append({
                        'type': 'aws_ebs_volume',
                        'id': volume['VolumeId'],
                        'data': volume,
                        'tags': {tag['Key']: tag['Value'] for tag in volume.get('Tags', [])}
                    })
            
            self.discovered_resources['volumes'] = volumes
            logger.info(f"Discovered {len(volumes)} EBS volumes")
            
        except ClientError as e:
            logger.error(f"Error discovering EBS volumes: {e}")

    def discover_snapshots(self):
        """Discover EBS snapshots."""
        try:
            # Only get snapshots owned by the current account
            response = self.clients['ec2'].describe_snapshots(OwnerIds=['self'])
            snapshots = []
            
            for snapshot in response.get('Snapshots', []):
                if snapshot['State'] not in ['deleted', 'deleting']:
                    snapshots.append({
                        'type': 'aws_ebs_snapshot',
                        'id': snapshot['SnapshotId'],
                        'data': snapshot,
                        'tags': {tag['Key']: tag['Value'] for tag in snapshot.get('Tags', [])}
                    })
            
            self.discovered_resources['snapshots'] = snapshots
            logger.info(f"Discovered {len(snapshots)} EBS snapshots")
            
        except ClientError as e:
            logger.error(f"Error discovering EBS snapshots: {e}")

    def discover_route53_zones(self):
        """Discover Route 53 hosted zones."""
        try:
            response = self.clients['r53'].list_hosted_zones()
            zones = []
            
            for zone in response.get('HostedZones', []):
                zones.append({
                    'type': 'aws_route53_zone',
                    'id': zone['Id'].split('/')[-1],  # Remove /hostedzone/ prefix
                    'data': zone,
                    'tags': {}  # Route53 zones don't have tags in list response
                })
            
            self.discovered_resources['route53_zones'] = zones
            logger.info(f"Discovered {len(zones)} Route 53 hosted zones")
            
        except ClientError as e:
            logger.error(f"Error discovering Route 53 zones: {e}")

    def discover_route53_records(self):
        """Discover Route 53 records."""
        try:
            records = []
            
            # Get records for each hosted zone
            for zone in self.discovered_resources.get('route53_zones', []):
                zone_id = zone['data']['Id']
                response = self.clients['r53'].list_resource_record_sets(HostedZoneId=zone_id)
                
                for record in response.get('ResourceRecordSets', []):
                    # Skip NS and SOA records as they're managed by the zone
                    if record['Type'] not in ['NS', 'SOA']:
                        records.append({
                            'type': 'aws_route53_record',
                            'id': f"{zone['id']}_{record['Name']}_{record['Type']}",
                            'data': record,
                            'zone_id': zone_id,
                            'tags': {}
                        })
            
            self.discovered_resources['route53_records'] = records
            logger.info(f"Discovered {len(records)} Route 53 records")
            
        except ClientError as e:
            logger.error(f"Error discovering Route 53 records: {e}")

    def discover_s3_buckets(self):
        """Discover S3 buckets."""
        try:
            response = self.clients['s3'].list_buckets()
            buckets = []
            
            for bucket in response.get('Buckets', []):
                buckets.append({
                    'type': 'aws_s3_bucket',
                    'id': bucket['Name'],
                    'data': bucket,
                    'tags': {}  # Tags need separate API call
                })
            
            self.discovered_resources['s3_buckets'] = buckets
            logger.info(f"Discovered {len(buckets)} S3 buckets")
            
        except ClientError as e:
            logger.error(f"Error discovering S3 buckets: {e}")

    def discover_iam_roles(self):
        """Discover IAM roles."""
        try:
            response = self.clients['iam'].list_roles()
            roles = []
            
            for role in response.get('Roles', []):
                roles.append({
                    'type': 'aws_iam_role',
                    'id': role['RoleName'],
                    'data': role,
                    'tags': {tag['Key']: tag['Value'] for tag in role.get('Tags', [])}
                })
            
            self.discovered_resources['iam_roles'] = roles
            logger.info(f"Discovered {len(roles)} IAM roles")
            
        except ClientError as e:
            logger.error(f"Error discovering IAM roles: {e}")

    def discover_iam_policies(self):
        """Discover IAM policies."""
        try:
            response = self.clients['iam'].list_policies(Scope='Local')
            policies = []
            
            for policy in response.get('Policies', []):
                policies.append({
                    'type': 'aws_iam_policy',
                    'id': policy['PolicyName'],
                    'data': policy,
                    'tags': {tag['Key']: tag['Value'] for tag in policy.get('Tags', [])}
                })
            
            self.discovered_resources['iam_policies'] = policies
            logger.info(f"Discovered {len(policies)} IAM policies")
            
        except ClientError as e:
            logger.error(f"Error discovering IAM policies: {e}")

    def _save_discovery_results(self):
        """Save discovery results to JSON file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"terraform_output/discovered_resources_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(self.discovered_resources, f, indent=2, default=str)
        
        logger.info(f"Discovery results saved to {filename}")


def main():
    """Main function for Terraform discovery."""
    logging.basicConfig(level=logging.INFO)
    
    discovery = TerraformDiscovery()
    resources = discovery.discover_all_resources()
    
    # Print summary
    print("\n" + "="*60)
    print("AWS INFRASTRUCTURE DISCOVERY SUMMARY")
    print("="*60)
    
    total_resources = 0
    for resource_type, resources_list in resources.items():
        count = len(resources_list)
        total_resources += count
        print(f"{resource_type.replace('_', ' ').title():<30} {count:>6}")
    
    print("-"*60)
    print(f"{'Total Resources':<30} {total_resources:>6}")
    print("="*60)


if __name__ == "__main__":
    main()
