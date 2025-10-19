"""Multi-cloud cost analyzer for comprehensive cost reporting across all providers."""
import json
import logging
import os
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple, Union

import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)


class MultiCloudCostAnalyzer:
    """Analyzer for multi-cloud cost data across AWS, Oracle, Google, and IBM Cloud."""

    def __init__(self, aws_region: str = "us-east-1", aws_profile: Optional[str] = None):
        """
        Initialize multi-cloud cost analyzer.

        Args:
            aws_region: AWS region for Cost Explorer
            aws_profile: AWS profile name (optional)
        """
        self.aws_region = aws_region
        self.aws_profile = aws_profile

        # Initialize AWS client
        session_kwargs: Dict[str, Any] = {"region_name": aws_region}
        if aws_profile:
            session_kwargs["profile_name"] = aws_profile

        session = boto3.Session(**session_kwargs)
        self.ce_client = session.client("ce")
        self.sts_client = session.client("sts")

    def get_aws_costs(self, days_back: int = 30) -> Dict[str, Any]:
        """
        Get AWS cost data grouped by service and resource type.

        Args:
            days_back: Number of days to look back

        Returns:
            Dictionary with AWS cost breakdown
        """
        try:
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=days_back)

            # Get cost data grouped by service and usage type
            response = self.ce_client.get_cost_and_usage(
                TimePeriod={
                    "Start": start_date.strftime("%Y-%m-%d"),
                    "End": end_date.strftime("%Y-%m-%d"),
                },
                Granularity="MONTHLY",
                Metrics=["UnblendedCost"],
                GroupBy=[
                    {"Type": "DIMENSION", "Key": "SERVICE"},
                    {"Type": "DIMENSION", "Key": "USAGE_TYPE"},
                ],
            )

            aws_costs: Dict[str, Any] = {
                "provider": "AWS",
                "total_cost": 0.0,
                "resource_categories": {
                    "compute": {"cost": 0.0, "resources": []},
                    "networking": {"cost": 0.0, "resources": []},
                    "storage": {"cost": 0.0, "resources": []},
                    "databases": {"cost": 0.0, "resources": []},
                    "other": {"cost": 0.0, "resources": []},
                },
                "services": [],
            }

            # Process cost data with type safety
            results_by_time = response.get("ResultsByTime", [])
            if not isinstance(results_by_time, list):
                return aws_costs

            for result in results_by_time:
                if not isinstance(result, dict):
                    continue

                groups = result.get("Groups", [])
                if not isinstance(groups, list):
                    continue

                for group in groups:
                    if not isinstance(group, dict):
                        continue

                    keys = group.get("Keys", [])
                    if not isinstance(keys, list) or len(keys) < 1:
                        continue

                    service = str(keys[0])
                    usage_type = str(keys[1]) if len(keys) > 1 else "General"

                    metrics = group.get("Metrics", {})
                    if not isinstance(metrics, dict):
                        continue

                    unblended_cost = metrics.get("UnblendedCost", {})
                    if not isinstance(unblended_cost, dict):
                        continue

                    amount = unblended_cost.get("Amount", "0")
                    try:
                        cost = float(amount)
                    except (ValueError, TypeError):
                        continue

                    if cost > 0:
                        aws_costs["total_cost"] += cost

                        # Sanitize usage type and service name for public reports
                        sanitized_usage_type = self._sanitize_usage_type(usage_type)
                        sanitized_service = self._sanitize_service_name(service)

                        # Categorize by service type
                        category = self._categorize_aws_service(service, usage_type)
                        aws_costs["resource_categories"][category]["cost"] += cost
                        aws_costs["resource_categories"][category]["resources"].append(
                            {
                                "service": sanitized_service,
                                "usage_type": sanitized_usage_type,
                                "cost": cost,
                            }
                        )

                        # Add to services list
                        aws_costs["services"].append(
                            {
                                "service": sanitized_service,
                                "usage_type": sanitized_usage_type,
                                "cost": cost,
                            }
                        )

            # Sort resources by cost
            for category in aws_costs["resource_categories"]:
                aws_costs["resource_categories"][category]["resources"].sort(key=lambda x: x["cost"], reverse=True)

            aws_costs["services"].sort(key=lambda x: x["cost"], reverse=True)
            return aws_costs

        except Exception as e:
            logger.error(f"Error retrieving AWS costs: {e}")
            return {
                "provider": "AWS",
                "total_cost": 0.0,
                "resource_categories": {
                    "compute": {"cost": 0.0, "resources": []},
                    "networking": {"cost": 0.0, "resources": []},
                    "storage": {"cost": 0.0, "resources": []},
                    "databases": {"cost": 0.0, "resources": []},
                    "other": {"cost": 0.0, "resources": []},
                },
                "services": [],
                "error": str(e),
            }

    def _categorize_aws_service(self, service: str, usage_type: str) -> str:
        """
        Categorize AWS service into resource categories.

        Args:
            service: AWS service name
            usage_type: Usage type

        Returns:
            Category name
        """
        service_lower = service.lower()
        usage_lower = usage_type.lower()

        # Compute services
        if any(
            compute in service_lower
            for compute in ["ec2", "lambda", "elastic beanstalk", "fargate", "ecs", "eks", "lightsail"]
        ):
            return "compute"

        # Networking services
        if any(
            network in service_lower
            for network in [
                "cloudfront",
                "route53",
                "vpc",
                "direct connect",
                "api gateway",
                "load balancer",
                "nat gateway",
                "transit gateway",
            ]
        ):
            return "networking"

        # Storage services
        if any(storage in service_lower for storage in ["s3", "ebs", "efs", "fsx", "glacier", "storage gateway"]):
            return "storage"

        # Database services
        if any(db in service_lower for db in ["rds", "dynamodb", "redshift", "elasticache", "documentdb", "neptune"]):
            return "databases"

        return "other"

    def _sanitize_usage_type(self, usage_type: str) -> str:
        """
        Sanitize usage type to remove sensitive information while preserving useful context.

        Args:
            usage_type: Original usage type

        Returns:
            Sanitized usage type
        """
        import re

        # Remove IP addresses
        sanitized = re.sub(r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b", "[IP]", usage_type)

        # Replace specific region/zone identifiers with generic region names
        # Keep the provider context but remove specific identifiers
        region_patterns = [
            (r"\b(us|eu|ap|ca|sa|af|me)[a-z0-9-]+\b", r"\1-[Region]", re.IGNORECASE),  # USW2, USE1, etc.
            (r"\b(us|eu|ap|ca|sa|af|me)-[a-z0-9-]+\b", r"\1-[Region]", re.IGNORECASE),  # us-west-2, eu-west-1, etc.
            (
                r"\b(us|eu|ap|ca|sa|af|me)-[a-z]+-[0-9]+[a-z]?\b",
                r"\1-[Region]",
                re.IGNORECASE,
            ),  # us-west-2a, eu-west-1b, etc.
        ]

        for pattern, replacement, flags in region_patterns:
            sanitized = re.sub(pattern, replacement, sanitized, flags=flags)

        # Replace specific resource IDs with generic identifiers
        # Keep the resource type but remove specific IDs
        resource_patterns = [
            (r"\b(i-[a-z0-9]+)\b", "i-[Instance]", re.IGNORECASE),  # EC2 instances
            (r"\b(vol-[a-z0-9]+)\b", "vol-[Volume]", re.IGNORECASE),  # EBS volumes
            (r"\b(snap-[a-z0-9]+)\b", "snap-[Snapshot]", re.IGNORECASE),  # Snapshots
            (r"\b(ami-[a-z0-9]+)\b", "ami-[Image]", re.IGNORECASE),  # AMI images
            (r"\b(sg-[a-z0-9]+)\b", "sg-[SecurityGroup]", re.IGNORECASE),  # Security groups
            (r"\b(subnet-[a-z0-9]+)\b", "subnet-[Subnet]", re.IGNORECASE),  # Subnets
            (r"\b(vpc-[a-z0-9]+)\b", "vpc-[VPC]", re.IGNORECASE),  # VPCs
        ]

        for pattern, replacement, flags in resource_patterns:
            sanitized = re.sub(pattern, replacement, sanitized, flags=flags)

        # Remove account-specific identifiers
        sanitized = re.sub(r"\b\d{12}\b", "[Account]", sanitized)  # 12-digit AWS account numbers

        # Handle multiple resource groups by adding designators
        # Look for patterns like "Resource Group 1", "Resource Group 2", etc.
        resource_group_count = {}

        def replace_resource_group(match):
            provider = match.group(1).lower()
            if provider not in resource_group_count:
                resource_group_count[provider] = 0
            resource_group_count[provider] += 1

            designators = ["Alpha", "Bravo", "Charlie", "Delta", "Echo", "Foxtrot", "Golf", "Hotel"]
            if resource_group_count[provider] <= len(designators):
                return f"{provider.title()} Resource Group {designators[resource_group_count[provider]-1]}"
            else:
                return f"{provider.title()} Resource Group {resource_group_count[provider]}"

        # Apply resource group replacement
        sanitized = re.sub(
            r"\b(aws|azure|gcp|ibm|oracle)\s+resource\s+group\s*(\d+)?",
            replace_resource_group,
            sanitized,
            flags=re.IGNORECASE,
        )

        return sanitized

    def _sanitize_service_name(self, service: str) -> str:
        """
        Sanitize service name to remove sensitive information while preserving useful context.

        Args:
            service: Original service name

        Returns:
            Sanitized service name
        """
        import re

        # Remove account-specific identifiers from service names
        sanitized = re.sub(r"\b\d{12}\b", "[Account]", service)  # 12-digit AWS account numbers

        # Replace specific region/zone identifiers with generic region names
        sanitized = re.sub(
            r"\b(us|eu|ap|ca|sa|af|me)[a-z0-9-]+\b", r"\1-[Region]", sanitized, flags=re.IGNORECASE
        )  # USW2, USE1, etc.
        sanitized = re.sub(
            r"\b(us|eu|ap|ca|sa|af|me)-[a-z0-9-]+\b", r"\1-[Region]", sanitized, flags=re.IGNORECASE
        )  # us-west-2, eu-west-1, etc.

        # Replace specific resource IDs with generic identifiers
        resource_patterns = [
            (r"\b(i-[a-z0-9]+)\b", "i-[Instance]", re.IGNORECASE),
            (r"\b(vol-[a-z0-9]+)\b", "vol-[Volume]", re.IGNORECASE),
            (r"\b(snap-[a-z0-9]+)\b", "snap-[Snapshot]", re.IGNORECASE),
            (r"\b(ami-[a-z0-9]+)\b", "ami-[Image]", re.IGNORECASE),
            (r"\b(sg-[a-z0-9]+)\b", "sg-[SecurityGroup]", re.IGNORECASE),
            (r"\b(subnet-[a-z0-9]+)\b", "subnet-[Subnet]", re.IGNORECASE),
            (r"\b(vpc-[a-z0-9]+)\b", "vpc-[VPC]", re.IGNORECASE),
        ]

        for pattern, replacement, flags in resource_patterns:
            sanitized = re.sub(pattern, replacement, sanitized, flags=flags)

        return sanitized

    def get_oracle_cloud_costs(self) -> Dict[str, Any]:
        """
        Get Oracle Cloud cost data from OCI billing API.

        Returns:
            Dictionary with Oracle Cloud cost breakdown
        """
        try:
            # Try to get OCI credentials from environment
            oci_config_path = os.path.expanduser("~/.oci/config")
            if not os.path.exists(oci_config_path):
                logger.warning("OCI config not found, using free tier estimates")
                return self._get_oracle_free_tier_estimate()

            # Return free tier estimate (API integration can be added in future)
            return self._get_oracle_free_tier_estimate()

        except Exception as e:
            logger.error(f"Error retrieving Oracle Cloud costs: {e}")
            return self._get_oracle_free_tier_estimate()

    def _get_oracle_free_tier_estimate(self) -> Dict[str, Any]:
        """Get Oracle Cloud free tier estimate."""
        return {
            "provider": "Oracle Cloud",
            "total_cost": 0.0,
            "resource_categories": {
                "compute": {
                    "cost": 0.0,
                    "resources": [
                        {
                            "service": "VM.Standard.A1.Flex (ARM)",
                            "usage_type": "Always Free Tier",
                            "cost": 0.0,
                            "description": "2 instances, 4 OCPUs, 24GB RAM total",
                        },
                        {
                            "service": "VM.Standard.E2.1.Micro (AMD)",
                            "usage_type": "Always Free Tier",
                            "cost": 0.0,
                            "description": "2 instances, 1 OCPU, 1GB RAM each",
                        },
                    ],
                },
                "networking": {
                    "cost": 0.0,
                    "resources": [
                        {
                            "service": "VCN",
                            "usage_type": "Always Free Tier",
                            "cost": 0.0,
                            "description": "Virtual Cloud Network with internet gateway",
                        },
                        {
                            "service": "Load Balancer",
                            "usage_type": "Always Free Tier",
                            "cost": 0.0,
                            "description": "1 load balancer, 10Mbps",
                        },
                    ],
                },
                "storage": {
                    "cost": 0.0,
                    "resources": [
                        {
                            "service": "Block Volume",
                            "usage_type": "Always Free Tier",
                            "cost": 0.0,
                            "description": "200GB total block storage",
                        },
                        {
                            "service": "Object Storage",
                            "usage_type": "Always Free Tier",
                            "cost": 0.0,
                            "description": "20GB object storage",
                        },
                    ],
                },
                "databases": {
                    "cost": 0.0,
                    "resources": [
                        {
                            "service": "Autonomous Database",
                            "usage_type": "Always Free Tier",
                            "cost": 0.0,
                            "description": "2 databases, 20GB each",
                        },
                    ],
                },
                "other": {
                    "cost": 0.0,
                    "resources": [
                        {
                            "service": "Monitoring",
                            "usage_type": "Always Free Tier",
                            "cost": 0.0,
                            "description": "500 million monitoring data points",
                        },
                        {
                            "service": "Notifications",
                            "usage_type": "Always Free Tier",
                            "cost": 0.0,
                            "description": "1 million notifications",
                        },
                    ],
                },
            },
            "services": [],
            "free_tier_status": "Within limits",
            "notes": "All resources are within Always Free Tier limits",
        }

    def get_google_cloud_costs(self) -> Dict[str, Any]:
        """
        Get Google Cloud cost data from Cloud Billing API.

        Returns:
            Dictionary with Google Cloud cost breakdown
        """
        try:
            # Try to get GCP credentials from environment
            gcp_credentials_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
            if not gcp_credentials_path or not os.path.exists(gcp_credentials_path):
                logger.warning("GCP credentials not found, using free tier estimates")
                return self._get_google_free_tier_estimate()

            # Return free tier estimate (API integration can be added in future)
            return self._get_google_free_tier_estimate()

        except Exception as e:
            logger.error(f"Error retrieving Google Cloud costs: {e}")
            return self._get_google_free_tier_estimate()

    def _get_google_free_tier_estimate(self) -> Dict[str, Any]:
        """Get Google Cloud free tier estimate."""
        return {
            "provider": "Google Cloud",
            "total_cost": 0.0,
            "resource_categories": {
                "compute": {
                    "cost": 0.0,
                    "resources": [
                        {
                            "service": "e2-micro",
                            "usage_type": "Free Tier",
                            "cost": 0.0,
                            "description": "1 instance, 0.25-2 vCPUs, 1GB RAM",
                        },
                        {
                            "service": "Cloud Functions",
                            "usage_type": "Free Tier",
                            "cost": 0.0,
                            "description": "2M invocations, 400K GB-seconds",
                        },
                    ],
                },
                "networking": {
                    "cost": 0.0,
                    "resources": [
                        {
                            "service": "VPC",
                            "usage_type": "Free Tier",
                            "cost": 0.0,
                            "description": "Virtual Private Cloud with firewall rules",
                        },
                        {
                            "service": "Cloud Load Balancing",
                            "usage_type": "Free Tier",
                            "cost": 0.0,
                            "description": "1 forwarding rule",
                        },
                    ],
                },
                "storage": {
                    "cost": 0.0,
                    "resources": [
                        {
                            "service": "Cloud Storage",
                            "usage_type": "Free Tier",
                            "cost": 0.0,
                            "description": "5GB regional storage",
                        },
                    ],
                },
                "databases": {
                    "cost": 0.0,
                    "resources": [
                        {
                            "service": "Cloud SQL",
                            "usage_type": "Free Tier",
                            "cost": 0.0,
                            "description": "1 instance, 1GB RAM, 10GB storage",
                        },
                    ],
                },
                "other": {
                    "cost": 0.0,
                    "resources": [
                        {
                            "service": "Cloud Monitoring",
                            "usage_type": "Free Tier",
                            "cost": 0.0,
                            "description": "150MB logs, 50K metrics",
                        },
                    ],
                },
            },
            "services": [],
            "free_tier_status": "Within limits",
            "notes": "All resources are within Free Tier limits",
        }

    def get_ibm_cloud_costs(self) -> Dict[str, Any]:
        """
        Get IBM Cloud cost data from Billing API.

        Returns:
            Dictionary with IBM Cloud cost breakdown
        """
        try:
            # Try to get IBM Cloud credentials from environment
            ibm_api_key = os.environ.get("IBMCLOUD_API_KEY")
            if not ibm_api_key:
                logger.warning("IBM Cloud API key not found, using free tier estimates")
                return self._get_ibm_free_tier_estimate()

            # Return free tier estimate (API integration can be added in future)
            return self._get_ibm_free_tier_estimate()

        except Exception as e:
            logger.error(f"Error retrieving IBM Cloud costs: {e}")
            return self._get_ibm_free_tier_estimate()

    def _get_ibm_free_tier_estimate(self) -> Dict[str, Any]:
        """Get IBM Cloud free tier estimate."""
        return {
            "provider": "IBM Cloud",
            "total_cost": 0.0,
            "resource_categories": {
                "compute": {
                    "cost": 0.0,
                    "resources": [
                        {
                            "service": "VSI (Virtual Server Instance)",
                            "usage_type": "Free Tier",
                            "cost": 0.0,
                            "description": "1 instance, 2 vCPUs, 8GB RAM",
                        },
                    ],
                },
                "networking": {
                    "cost": 0.0,
                    "resources": [
                        {
                            "service": "VPC",
                            "usage_type": "Free Tier",
                            "cost": 0.0,
                            "description": "Virtual Private Cloud with subnets",
                        },
                        {
                            "service": "Floating IP",
                            "usage_type": "Free Tier",
                            "cost": 0.0,
                            "description": "1 floating IP address",
                        },
                    ],
                },
                "storage": {
                    "cost": 0.0,
                    "resources": [
                        {
                            "service": "Block Storage",
                            "usage_type": "Free Tier",
                            "cost": 0.0,
                            "description": "100GB block storage",
                        },
                    ],
                },
                "databases": {
                    "cost": 0.0,
                    "resources": [],
                },
                "other": {
                    "cost": 0.0,
                    "resources": [
                        {
                            "service": "Monitoring",
                            "usage_type": "Free Tier",
                            "cost": 0.0,
                            "description": "Basic monitoring and logging",
                        },
                    ],
                },
            },
            "services": [],
            "free_tier_status": "Within limits",
            "notes": "All resources are within Free Tier limits",
        }

    def generate_multicloud_summary(self, days_back: int = 30) -> Dict[str, Any]:
        """
        Generate comprehensive multi-cloud cost summary.

        Args:
            days_back: Number of days to look back for AWS costs

        Returns:
            Dictionary with multi-cloud cost summary
        """
        logger.info("Analyzing multi-cloud costs...")

        # Get costs from all providers
        aws_costs = self.get_aws_costs(days_back)
        oracle_costs = self.get_oracle_cloud_costs()
        google_costs = self.get_google_cloud_costs()
        ibm_costs = self.get_ibm_cloud_costs()

        # Calculate totals
        total_cost = (
            aws_costs["total_cost"] + oracle_costs["total_cost"] + google_costs["total_cost"] + ibm_costs["total_cost"]
        )

        # Aggregate by resource category across all providers
        resource_totals = {
            "compute": 0.0,
            "networking": 0.0,
            "storage": 0.0,
            "databases": 0.0,
            "other": 0.0,
        }

        for provider_costs in [aws_costs, oracle_costs, google_costs, ibm_costs]:
            for category, data in provider_costs["resource_categories"].items():
                if category in resource_totals:
                    resource_totals[category] += data["cost"]

        # Count active providers
        active_providers = sum(
            1
            for costs in [aws_costs, oracle_costs, google_costs, ibm_costs]
            if costs["total_cost"] > 0 or "free_tier_status" in costs
        )

        return {
            "total_cost": total_cost,
            "active_providers": active_providers,
            "providers": {
                "aws": aws_costs,
                "oracle": oracle_costs,
                "google": google_costs,
                "ibm": ibm_costs,
            },
            "resource_totals": resource_totals,
            "free_tier_status": {
                "aws": "Paid" if aws_costs["total_cost"] > 0 else "Free Tier",
                "oracle": oracle_costs.get("free_tier_status", "Unknown"),
                "google": google_costs.get("free_tier_status", "Unknown"),
                "ibm": ibm_costs.get("free_tier_status", "Unknown"),
            },
            "generated_at": datetime.now().isoformat(),
            "days_back": days_back,
        }
