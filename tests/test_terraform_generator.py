"""Tests for the TerraformGenerator module."""

import json
import os
import sys
import tempfile
from unittest.mock import Mock, mock_open, patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import pytest

from src.terraform_generator import TerraformGenerator


class TestTerraformGenerator:
    """Test cases for TerraformGenerator."""

    def test_init_default_output_dir(self):
        """Test TerraformGenerator initialization with default output directory."""
        with patch("os.makedirs") as mock_makedirs:
            with patch.object(
                TerraformGenerator, "_load_all_discovered_resources", return_value={}
            ):
                generator = TerraformGenerator()

                assert generator.output_dir == "terraform"
                assert generator.resource_names == {}
                assert generator.regions == {}
                mock_makedirs.assert_any_call("terraform", exist_ok=True)
                mock_makedirs.assert_any_call("terraform/modules", exist_ok=True)
                mock_makedirs.assert_any_call("terraform/environments", exist_ok=True)

    def test_init_custom_output_dir(self):
        """Test TerraformGenerator initialization with custom output directory."""
        with patch("os.makedirs") as mock_makedirs:
            with patch.object(
                TerraformGenerator, "_load_all_discovered_resources", return_value={}
            ):
                generator = TerraformGenerator("custom_terraform")

                assert generator.output_dir == "custom_terraform"
                mock_makedirs.assert_any_call("custom_terraform", exist_ok=True)

    def test_load_all_discovered_resources_no_directory(self):
        """Test loading discovered resources when directory doesn't exist."""
        with patch("os.path.exists", return_value=False):
            generator = TerraformGenerator()
            result = generator._load_all_discovered_resources()

            assert result == {}

    def test_load_all_discovered_resources_no_files(self):
        """Test loading discovered resources when no discovery files exist."""
        with patch("os.path.exists", return_value=True):
            with patch("os.listdir", return_value=["other_file.txt"]):
                generator = TerraformGenerator()
                result = generator._load_all_discovered_resources()

                assert result == {}

    def test_load_all_discovered_resources_success(self):
        """Test successful loading of discovered resources."""
        with patch("os.path.exists", return_value=True):
            with patch(
                "os.listdir", return_value=["discovered_resources_20230101_120000.json"]
            ):
                mock_resources = {
                    "ec2_instances": [
                        {
                            "type": "aws_instance",
                            "id": "i-1234567890abcdef0",
                            "data": {
                                "InstanceId": "i-1234567890abcdef0",
                                "Placement": {"AvailabilityZone": "us-east-1a"},
                            },
                            "tags": {"Name": "test-instance"},
                        }
                    ]
                }

                with patch(
                    "builtins.open", mock_open(read_data=json.dumps(mock_resources))
                ):
                    generator = TerraformGenerator()
                    result = generator._load_all_discovered_resources()

                    assert "ec2_instances" in result
                    assert len(result["ec2_instances"]) == 1
                    assert result["ec2_instances"][0]["region"] == "us-east-1"

    def test_determine_region_from_resources(self):
        """Test region determination from resource data."""
        generator = TerraformGenerator()

        # Test with EC2 instances
        resources_with_ec2 = {
            "ec2_instances": [
                {"data": {"Placement": {"AvailabilityZone": "us-west-2a"}}}
            ]
        }
        region = generator._determine_region_from_resources(resources_with_ec2)
        assert region == "us-west-2"

        # Test with VPCs (fallback)
        resources_with_vpc = {"vpcs": [{"data": {"VpcId": "vpc-12345678"}}]}
        region = generator._determine_region_from_resources(resources_with_vpc)
        assert region == "us-east-1"  # Default fallback

    def test_generate_main_tf(self):
        """Test main.tf file generation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch.object(
                TerraformGenerator, "_load_all_discovered_resources", return_value={}
            ):
                generator = TerraformGenerator(temp_dir)

                with patch.object(
                    generator, "_generate_import_blocks", return_value="# Import blocks"
                ):
                    with patch.object(
                        generator,
                        "_generate_resource_blocks",
                        return_value="# Resource blocks",
                    ):
                        generator.generate_main_tf()

                        main_tf_path = os.path.join(temp_dir, "main.tf")
                        assert os.path.exists(main_tf_path)

                        with open(main_tf_path, "r") as f:
                            content = f.read()
                            assert "terraform {" in content
                            assert "required_version" in content
                            assert "required_providers" in content
                            assert "# Import blocks" in content
                            assert "# Resource blocks" in content

    def test_generate_providers_tf(self):
        """Test providers.tf file generation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch.object(
                TerraformGenerator, "_load_all_discovered_resources", return_value={}
            ):
                generator = TerraformGenerator(temp_dir)
                generator.generate_providers_tf()

                providers_tf_path = os.path.join(temp_dir, "providers.tf")
                assert os.path.exists(providers_tf_path)

                with open(providers_tf_path, "r") as f:
                    content = f.read()
                    assert 'provider "aws"' in content
                    assert 'region = var.aws_region' in content

    def test_generate_variables_tf(self):
        """Test variables.tf file generation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch.object(
                TerraformGenerator, "_load_all_discovered_resources", return_value={}
            ):
                generator = TerraformGenerator(temp_dir)
                generator.generate_variables_tf()

                variables_tf_path = os.path.join(temp_dir, "variables.tf")
                assert os.path.exists(variables_tf_path)

                with open(variables_tf_path, "r") as f:
                    content = f.read()
                    assert 'variable "aws_region"' in content
                    assert 'variable "project_name"' in content
                    assert 'variable "environment"' in content

    def test_generate_outputs_tf(self):
        """Test outputs.tf file generation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch.object(
                TerraformGenerator, "_load_all_discovered_resources", return_value={}
            ):
                generator = TerraformGenerator(temp_dir)

                with patch.object(
                    generator, "_generate_output_blocks", return_value="# Output blocks"
                ):
                    generator.generate_outputs_tf()

                    outputs_tf_path = os.path.join(temp_dir, "outputs.tf")
                    assert os.path.exists(outputs_tf_path)

                    with open(outputs_tf_path, "r") as f:
                        content = f.read()
                        assert "# Output definitions" in content
                        assert "# Output blocks" in content

    def test_generate_import_block_ec2_instance(self):
        """Test import block generation for EC2 instance."""
        with patch.object(
            TerraformGenerator, "_load_all_discovered_resources", return_value={}
        ):
            generator = TerraformGenerator()

            resource = {
                "type": "aws_instance",
                "id": "i-1234567890abcdef0",
                "data": {"InstanceId": "i-1234567890abcdef0"},
            }

            with patch.object(
                generator, "_get_resource_name", return_value="test_instance"
            ):
                result = generator._generate_import_block(resource)

                assert "import {" in result
                assert "to = aws_instance.test_instance" in result
                assert 'id = "i-1234567890abcdef0"' in result

    def test_generate_import_block_vpc(self):
        """Test import block generation for VPC."""
        with patch.object(
            TerraformGenerator, "_load_all_discovered_resources", return_value={}
        ):
            generator = TerraformGenerator()

            resource = {
                "type": "aws_vpc",
                "id": "vpc-12345678",
                "data": {"VpcId": "vpc-12345678"},
            }

            with patch.object(generator, "_get_resource_name", return_value="test_vpc"):
                result = generator._generate_import_block(resource)

                assert "import {" in result
                assert "to = aws_vpc.test_vpc" in result
                assert 'id = "vpc-12345678"' in result

    def test_generate_import_block_route53_record(self):
        """Test import block generation for Route53 record."""
        with patch.object(
            TerraformGenerator, "_load_all_discovered_resources", return_value={}
        ):
            generator = TerraformGenerator()

            resource = {
                "type": "aws_route53_record",
                "id": "Z1234567890_www.example.com._A",
                "data": {"Name": "www.example.com.", "Type": "A"},
                "zone_id": "/hostedzone/Z1234567890",
            }

            with patch.object(
                generator, "_get_resource_name", return_value="test_record"
            ):
                result = generator._generate_import_block(resource)

                assert "import {" in result
                assert "to = aws_route53_record.test_record" in result
                assert 'id = "Z1234567890_www.example.com._A"' in result

    def test_generate_resource_block_ec2_instance(self):
        """Test resource block generation for EC2 instance."""
        with patch.object(
            TerraformGenerator, "_load_all_discovered_resources", return_value={}
        ):
            generator = TerraformGenerator()

            resource = {
                "type": "aws_instance",
                "id": "i-1234567890abcdef0",
                "data": {
                    "InstanceId": "i-1234567890abcdef0",
                    "ImageId": "ami-12345678",
                    "InstanceType": "t3.micro",
                    "SubnetId": "subnet-12345678",
                    "SecurityGroups": [{"GroupId": "sg-12345678"}],
                    "Tags": [{"Key": "Name", "Value": "test-instance"}],
                },
            }

            with patch.object(
                generator, "_get_resource_name", return_value="test_instance"
            ):
                result = generator._generate_resource_block(resource, "us_east_1")

                assert 'resource "aws_instance" "test_instance"' in result
                assert "provider = aws.us_east_1" in result
                assert 'ami           = "ami-12345678"' in result
                assert 'instance_type = "t3.micro"' in result

    def test_generate_resource_block_vpc(self):
        """Test resource block generation for VPC."""
        with patch.object(
            TerraformGenerator, "_load_all_discovered_resources", return_value={}
        ):
            generator = TerraformGenerator()

            resource = {
                "type": "aws_vpc",
                "id": "vpc-12345678",
                "data": {
                    "VpcId": "vpc-12345678",
                    "CidrBlock": "10.0.0.0/16",
                    "EnableDnsHostnames": True,
                    "EnableDnsSupport": True,
                    "Tags": [{"Key": "Name", "Value": "test-vpc"}],
                },
            }

            with patch.object(generator, "_get_resource_name", return_value="test_vpc"):
                result = generator._generate_resource_block(resource, "us_east_1")

                assert 'resource "aws_vpc" "test_vpc"' in result
                assert 'cidr_block           = "10.0.0.0/16"' in result
                assert "enable_dns_hostnames = true" in result
                assert "enable_dns_support   = true" in result

    def test_get_resource_name_from_tags(self):
        """Test resource name generation from tags."""
        with patch.object(
            TerraformGenerator, "_load_all_discovered_resources", return_value={}
        ):
            generator = TerraformGenerator()

            resource = {"tags": {"Name": "test-resource"}, "id": "i-1234567890abcdef0"}

            with patch.object(
                generator, "_sanitize_name", return_value="test_resource"
            ):
                result = generator._get_resource_name(resource, "aws_instance")

                assert result == "test_resource"

    def test_get_resource_name_from_id(self):
        """Test resource name generation from ID when no tags."""
        with patch.object(
            TerraformGenerator, "_load_all_discovered_resources", return_value={}
        ):
            generator = TerraformGenerator()

            resource = {"tags": {}, "id": "i-1234567890abcdef0"}

            with patch.object(
                generator, "_sanitize_name", return_value="i_1234567890abcdef0"
            ):
                result = generator._get_resource_name(resource, "aws_instance")

                assert result == "i_1234567890abcdef0"

    def test_sanitize_name(self):
        """Test name sanitization for Terraform."""
        with patch.object(
            TerraformGenerator, "_load_all_discovered_resources", return_value={}
        ):
            generator = TerraformGenerator()

            # Test various name sanitizations
            assert generator._sanitize_name("test-resource") == "test-resource"
            assert generator._sanitize_name("test.resource") == "test_resource"
            assert generator._sanitize_name("123resource") == "resource_123resource"
            assert generator._sanitize_name("Test Resource") == "test_resource"
            assert generator._sanitize_name("") == ""

    def test_format_tags(self):
        """Test tag formatting for Terraform."""
        with patch.object(
            TerraformGenerator, "_load_all_discovered_resources", return_value={}
        ):
            generator = TerraformGenerator()

            tags = [
                {"Key": "Name", "Value": "test-instance"},
                {"Key": "Environment", "Value": "production"},
                {"Key": "Project:Name", "Value": "test-project"},
            ]

            result = generator._format_tags(tags)

            assert 'Name = "test-instance"' in result
            assert 'Environment = "production"' in result
            assert '"Project:Name" = "test-project"' in result

    def test_format_list(self):
        """Test list formatting for Terraform."""
        with patch.object(
            TerraformGenerator, "_load_all_discovered_resources", return_value={}
        ):
            generator = TerraformGenerator()

            # Test with items
            items = ["item1", "item2", "item3"]
            result = generator._format_list(items)
            assert result == '["item1", "item2", "item3"]'

            # Test with empty list
            result = generator._format_list([])
            assert result == "[]"

            # Test with None
            result = generator._format_list(None)
            assert result == "[]"

    def test_generate_all_configurations(self):
        """Test generating all configurations."""
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch.object(
                TerraformGenerator, "_load_all_discovered_resources", return_value={}
            ):
                generator = TerraformGenerator(temp_dir)

                with patch.object(generator, "generate_main_tf"):
                    with patch.object(generator, "generate_variables_tf"):
                        with patch.object(generator, "generate_outputs_tf"):
                            with patch.object(generator, "generate_providers_tf"):
                                with patch.object(
                                    generator, "generate_region_configurations"
                                ):
                                    with patch.object(
                                        generator, "generate_ec2_resources"
                                    ):
                                        with patch.object(
                                            generator, "generate_vpc_resources"
                                        ):
                                            with patch.object(
                                                generator, "generate_route53_resources"
                                            ):
                                                with patch.object(
                                                    generator, "generate_s3_resources"
                                                ):
                                                    with patch.object(
                                                        generator,
                                                        "generate_iam_resources",
                                                    ):
                                                        with patch.object(
                                                            generator,
                                                            "generate_modules",
                                                        ):
                                                            generator.generate_all_configurations()

                                                            # All methods should have been called
                                                            generator.generate_main_tf.assert_called_once()
                                                            generator.generate_variables_tf.assert_called_once()
                                                            generator.generate_outputs_tf.assert_called_once()
                                                            generator.generate_providers_tf.assert_called_once()

    def test_generate_modules(self):
        """Test module generation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch.object(
                TerraformGenerator, "_load_all_discovered_resources", return_value={}
            ):
                generator = TerraformGenerator(temp_dir)
                generator.generate_modules()

                module_file = os.path.join(temp_dir, "modules", "example.tf")
                assert os.path.exists(module_file)

                with open(module_file, "r") as f:
                    content = f.read()
                    assert 'variable "environment"' in content
                    assert 'variable "project_name"' in content
                    assert 'output "module_output"' in content


if __name__ == "__main__":
    pytest.main([__file__])
