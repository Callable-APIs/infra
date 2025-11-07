"""Tests for the TerraformDiscovery module."""

import json
import os
import sys
import tempfile
from unittest.mock import MagicMock, Mock, patch

import pytest

from clint.terraform.discovery import TerraformDiscovery


class TestTerraformDiscovery:
    """Test cases for TerraformDiscovery."""

    def test_init_default_region(self):
        """Test TerraformDiscovery initialization with default region."""
        with patch("boto3.client") as mock_boto_client:
            mock_clients = {
                "ec2": Mock(),
                "r53": Mock(),
                "s3": Mock(),
                "vpc": Mock(),
                "iam": Mock(),
                "cloudwatch": Mock(),
            }

            def client_side_effect(service_name, region_name=None):
                return mock_clients.get(service_name, Mock())

            mock_boto_client.side_effect = client_side_effect

            discovery = TerraformDiscovery()

            assert discovery.region == "us-east-1"
            assert discovery.discovered_resources == {}
            assert "ec2" in discovery.clients
            assert "r53" in discovery.clients
            assert "s3" in discovery.clients

    def test_init_custom_region(self):
        """Test TerraformDiscovery initialization with custom region."""
        with patch("boto3.client") as mock_boto_client:
            mock_clients = {
                "ec2": Mock(),
                "r53": Mock(),
                "s3": Mock(),
                "vpc": Mock(),
                "iam": Mock(),
                "cloudwatch": Mock(),
            }

            def client_side_effect(service_name, region_name=None):
                return mock_clients.get(service_name, Mock())

            mock_boto_client.side_effect = client_side_effect

            discovery = TerraformDiscovery(region="us-west-2")

            assert discovery.region == "us-west-2"

    def test_discover_ec2_instances_success(self):
        """Test successful EC2 instances discovery."""
        with patch("boto3.client") as mock_boto_client:
            mock_ec2_client = Mock()
            mock_clients = {"ec2": mock_ec2_client}

            def client_side_effect(service_name, region_name=None):
                return mock_clients.get(service_name, Mock())

            mock_boto_client.side_effect = client_side_effect

            # Mock EC2 response
            mock_ec2_client.describe_instances.return_value = {
                "Reservations": [
                    {
                        "Instances": [
                            {
                                "InstanceId": "i-1234567890abcdef0",
                                "State": {"Name": "running"},
                                "ImageId": "ami-12345678",
                                "InstanceType": "t3.micro",
                                "Tags": [
                                    {"Key": "Name", "Value": "test-instance"},
                                    {"Key": "Environment", "Value": "test"},
                                ],
                            }
                        ]
                    }
                ]
            }

            discovery = TerraformDiscovery()
            discovery.discover_ec2_instances()

            assert "ec2_instances" in discovery.discovered_resources
            assert len(discovery.discovered_resources["ec2_instances"]) == 1

            instance = discovery.discovered_resources["ec2_instances"][0]
            assert instance["type"] == "aws_instance"
            assert instance["id"] == "i-1234567890abcdef0"
            assert instance["tags"]["Name"] == "test-instance"

    def test_discover_ec2_instances_filters_terminated(self):
        """Test EC2 instances discovery filters out terminated instances."""
        with patch("boto3.client") as mock_boto_client:
            mock_ec2_client = Mock()
            mock_clients = {"ec2": mock_ec2_client}

            def client_side_effect(service_name, region_name=None):
                return mock_clients.get(service_name, Mock())

            mock_boto_client.side_effect = client_side_effect

            # Mock EC2 response with terminated instance
            mock_ec2_client.describe_instances.return_value = {
                "Reservations": [
                    {
                        "Instances": [
                            {
                                "InstanceId": "i-running",
                                "State": {"Name": "running"},
                                "ImageId": "ami-12345678",
                                "InstanceType": "t3.micro",
                                "Tags": [],
                            },
                            {
                                "InstanceId": "i-terminated",
                                "State": {"Name": "terminated"},
                                "ImageId": "ami-12345678",
                                "InstanceType": "t3.micro",
                                "Tags": [],
                            },
                        ]
                    }
                ]
            }

            discovery = TerraformDiscovery()
            discovery.discover_ec2_instances()

            assert len(discovery.discovered_resources["ec2_instances"]) == 1
            assert discovery.discovered_resources["ec2_instances"][0]["id"] == "i-running"

    def test_discover_ec2_instances_error_handling(self):
        """Test EC2 instances discovery error handling."""
        with patch("boto3.client") as mock_boto_client:
            mock_ec2_client = Mock()
            mock_clients = {"ec2": mock_ec2_client}

            def client_side_effect(service_name, region_name=None):
                return mock_clients.get(service_name, Mock())

            mock_boto_client.side_effect = client_side_effect

            # Mock EC2 error
            from botocore.exceptions import ClientError

            mock_ec2_client.describe_instances.side_effect = ClientError(
                {"Error": {"Code": "UnauthorizedOperation"}}, "DescribeInstances"
            )

            discovery = TerraformDiscovery()
            discovery.discover_ec2_instances()

            # Should not raise exception, just log error
            assert "ec2_instances" not in discovery.discovered_resources

    def test_discover_vpcs_success(self):
        """Test successful VPCs discovery."""
        with patch("boto3.client") as mock_boto_client:
            mock_vpc_client = Mock()
            mock_clients = {"ec2": mock_vpc_client}  # VPC is part of EC2

            def client_side_effect(service_name, region_name=None):
                return mock_clients.get(service_name, Mock())

            mock_boto_client.side_effect = client_side_effect

            # Mock VPC response
            mock_vpc_client.describe_vpcs.return_value = {
                "Vpcs": [
                    {
                        "VpcId": "vpc-12345678",
                        "CidrBlock": "10.0.0.0/16",
                        "State": "available",
                        "Tags": [{"Key": "Name", "Value": "test-vpc"}],
                    }
                ]
            }

            discovery = TerraformDiscovery()
            discovery.discover_vpcs()

            assert "vpcs" in discovery.discovered_resources
            assert len(discovery.discovered_resources["vpcs"]) == 1

            vpc = discovery.discovered_resources["vpcs"][0]
            assert vpc["type"] == "aws_vpc"
            assert vpc["id"] == "vpc-12345678"
            assert vpc["data"]["CidrBlock"] == "10.0.0.0/16"

    def test_discover_s3_buckets_success(self):
        """Test successful S3 buckets discovery."""
        with patch("boto3.client") as mock_boto_client:
            mock_s3_client = Mock()
            mock_clients = {"s3": mock_s3_client}

            def client_side_effect(service_name, region_name=None):
                return mock_clients.get(service_name, Mock())

            mock_boto_client.side_effect = client_side_effect

            # Mock S3 response
            mock_s3_client.list_buckets.return_value = {
                "Buckets": [
                    {"Name": "test-bucket-1", "CreationDate": "2023-01-01T00:00:00Z"},
                    {"Name": "test-bucket-2", "CreationDate": "2023-01-02T00:00:00Z"},
                ]
            }

            discovery = TerraformDiscovery()
            discovery.discover_s3_buckets()

            assert "s3_buckets" in discovery.discovered_resources
            assert len(discovery.discovered_resources["s3_buckets"]) == 2

            bucket = discovery.discovered_resources["s3_buckets"][0]
            assert bucket["type"] == "aws_s3_bucket"
            assert bucket["id"] == "test-bucket-1"

    def test_discover_iam_roles_success(self):
        """Test successful IAM roles discovery."""
        with patch("boto3.client") as mock_boto_client:
            mock_iam_client = Mock()
            mock_clients = {"iam": mock_iam_client}

            def client_side_effect(service_name, region_name=None):
                return mock_clients.get(service_name, Mock())

            mock_boto_client.side_effect = client_side_effect

            # Mock IAM response
            mock_iam_client.list_roles.return_value = {
                "Roles": [
                    {
                        "RoleName": "test-role-1",
                        "Arn": "arn:aws:iam::123456789012:role/test-role-1",
                        "CreateDate": "2023-01-01T00:00:00Z",
                        "Tags": [{"Key": "Environment", "Value": "test"}],
                    }
                ]
            }

            discovery = TerraformDiscovery()
            discovery.discover_iam_roles()

            assert "iam_roles" in discovery.discovered_resources
            assert len(discovery.discovered_resources["iam_roles"]) == 1

            role = discovery.discovered_resources["iam_roles"][0]
            assert role["type"] == "aws_iam_role"
            assert role["id"] == "test-role-1"
            assert role["tags"]["Environment"] == "test"

    def test_discover_route53_zones_success(self):
        """Test successful Route53 zones discovery."""
        with patch("boto3.client") as mock_boto_client:
            mock_r53_client = Mock()
            mock_clients = {"route53": mock_r53_client}

            def client_side_effect(service_name, region_name=None):
                return mock_clients.get(service_name, Mock())

            mock_boto_client.side_effect = client_side_effect

            # Mock Route53 response
            mock_r53_client.list_hosted_zones.return_value = {
                "HostedZones": [
                    {
                        "Id": "/hostedzone/Z1234567890",
                        "Name": "example.com.",
                        "CallerReference": "test-ref",
                    }
                ]
            }

            discovery = TerraformDiscovery()
            discovery.discover_route53_zones()

            assert "route53_zones" in discovery.discovered_resources
            assert len(discovery.discovered_resources["route53_zones"]) == 1

            zone = discovery.discovered_resources["route53_zones"][0]
            assert zone["type"] == "aws_route53_zone"
            assert zone["id"] == "Z1234567890"  # Should remove /hostedzone/ prefix

    def test_discover_route53_records_success(self):
        """Test successful Route53 records discovery."""
        with patch("boto3.client") as mock_boto_client:
            mock_r53_client = Mock()
            mock_clients = {"route53": mock_r53_client}

            def client_side_effect(service_name, region_name=None):
                return mock_clients.get(service_name, Mock())

            mock_boto_client.side_effect = client_side_effect

            # First set up zones
            discovery = TerraformDiscovery()
            discovery.discovered_resources["route53_zones"] = [
                {"data": {"Id": "/hostedzone/Z1234567890"}, "id": "Z1234567890"}
            ]

            # Mock Route53 records response
            mock_r53_client.list_resource_record_sets.return_value = {
                "ResourceRecordSets": [
                    {
                        "Name": "www.example.com.",
                        "Type": "A",
                        "TTL": 300,
                        "ResourceRecords": [{"Value": "192.168.1.1"}],
                    },
                    {
                        "Name": "example.com.",
                        "Type": "NS",
                        "TTL": 172800,
                        "ResourceRecords": [{"Value": "ns-123.awsdns-12.com."}],
                    },
                ]
            }

            discovery.discover_route53_records()

            assert "route53_records" in discovery.discovered_resources
            assert len(discovery.discovered_resources["route53_records"]) == 1  # NS record should be skipped

            record = discovery.discovered_resources["route53_records"][0]
            assert record["type"] == "aws_route53_record"
            assert record["id"] == "Z1234567890_www.example.com._A"

    def test_save_discovery_results(self):
        """Test saving discovery results to JSON file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch("boto3.client") as mock_boto_client:
                mock_clients = {"ec2": Mock()}

                def client_side_effect(service_name, region_name=None):
                    return mock_clients.get(service_name, Mock())

                mock_boto_client.side_effect = client_side_effect

                discovery = TerraformDiscovery()
                discovery.discovered_resources = {
                    "ec2_instances": [
                        {
                            "type": "aws_instance",
                            "id": "i-1234567890abcdef0",
                            "data": {"InstanceId": "i-1234567890abcdef0"},
                            "tags": {"Name": "test-instance"},
                        }
                    ]
                }

                # Change to temp directory and create terraform_output
                original_cwd = os.getcwd()
                os.chdir(temp_dir)
                os.makedirs("terraform_output", exist_ok=True)

                try:
                    discovery._save_discovery_results()

                    # Check that file was created
                    output_files = [
                        f
                        for f in os.listdir("terraform_output")
                        if f.startswith("discovered_resources_") and f.endswith(".json")
                    ]
                    assert len(output_files) == 1
                finally:
                    os.chdir(original_cwd)

                # Check file content
                with open(os.path.join(temp_dir, "terraform_output", output_files[0]), "r") as f:
                    data = json.load(f)
                    assert "ec2_instances" in data
                    assert len(data["ec2_instances"]) == 1

    def test_discover_all_resources(self):
        """Test discovering all resources."""
        with patch("boto3.client") as mock_boto_client:
            mock_ec2_client = Mock()
            mock_clients = {
                "ec2": mock_ec2_client,
                "r53": Mock(),
                "s3": Mock(),
                "vpc": mock_ec2_client,  # VPC client is the same as EC2 client
                "iam": Mock(),
                "cloudwatch": Mock(),
            }

            def client_side_effect(service_name, region_name=None):
                # Map boto3 service names to our client keys
                service_mapping = {
                    "ec2": "ec2",
                    "route53": "r53",
                    "s3": "s3",
                    "iam": "iam",
                    "cloudwatch": "cloudwatch",
                }
                client_key = service_mapping.get(service_name, service_name)
                return mock_clients.get(client_key, Mock())

            mock_boto_client.side_effect = client_side_effect

            # Mock all responses
            mock_ec2_client.describe_instances.return_value = {"Reservations": []}
            mock_ec2_client.describe_vpcs.return_value = {"Vpcs": []}
            mock_ec2_client.describe_subnets.return_value = {"Subnets": []}
            mock_ec2_client.describe_security_groups.return_value = {"SecurityGroups": []}
            mock_ec2_client.describe_route_tables.return_value = {"RouteTables": []}
            mock_ec2_client.describe_internet_gateways.return_value = {"InternetGateways": []}
            mock_ec2_client.describe_nat_gateways.return_value = {"NatGateways": []}
            mock_ec2_client.describe_addresses.return_value = {"Addresses": []}
            mock_ec2_client.describe_volumes.return_value = {"Volumes": []}
            mock_ec2_client.describe_snapshots.return_value = {"Snapshots": []}
            mock_clients["r53"].list_hosted_zones.return_value = {"HostedZones": []}
            mock_clients["s3"].list_buckets.return_value = {"Buckets": []}
            mock_clients["iam"].list_roles.return_value = {"Roles": []}
            mock_clients["iam"].list_policies.return_value = {"Policies": []}

            discovery = TerraformDiscovery()

            with patch.object(discovery, "_save_discovery_results"):
                result = discovery.discover_all_resources()

                # Check that all resource types are present
                expected_types = [
                    "ec2_instances",
                    "vpcs",
                    "subnets",
                    "security_groups",
                    "route_tables",
                    "internet_gateways",
                    "nat_gateways",
                    "elastic_ips",
                    "volumes",
                    "snapshots",
                    "route53_zones",
                    "route53_records",
                    "s3_buckets",
                    "iam_roles",
                    "iam_policies",
                ]

                for resource_type in expected_types:
                    assert resource_type in result


if __name__ == "__main__":
    pytest.main([__file__])
