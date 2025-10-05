"""AWS Cost Explorer client wrapper."""
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import boto3

logger = logging.getLogger(__name__)


class CostExplorerClient:
    """Client for interacting with AWS Cost Explorer API."""

    def __init__(self, region: str = "us-east-1", profile: Optional[str] = None):
        """
        Initialize Cost Explorer client.

        Args:
            region: AWS region (Cost Explorer data is in us-east-1)
            profile: AWS profile name (optional)
        """
        session_kwargs: Dict[str, Any] = {"region_name": region}
        if profile:
            session_kwargs["profile_name"] = profile

        session = boto3.Session(**session_kwargs)
        self.client = session.client("ce")
        self.sts_client = session.client("sts")

    def get_account_id(self) -> str:
        """Get the AWS account ID."""
        try:
            identity = self.sts_client.get_caller_identity()
            account_id = identity.get("Account", "UNKNOWN")
            return str(account_id)
        except Exception as e:
            logger.warning(f"Could not retrieve account ID: {e}")
            return "UNKNOWN"

    def get_cost_and_usage(
        self,
        days_back: int = 30,
        granularity: str = "DAILY",
        metrics: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Retrieve cost and usage data from AWS Cost Explorer.

        Args:
            days_back: Number of days to look back
            granularity: DAILY, MONTHLY, or HOURLY
            metrics: List of metrics to retrieve (default: UnblendedCost, UsageQuantity)

        Returns:
            Dictionary containing cost and usage data
        """
        if metrics is None:
            metrics = ["UnblendedCost", "UsageQuantity"]

        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days_back)

        try:
            response = self.client.get_cost_and_usage(
                TimePeriod={
                    "Start": start_date.strftime("%Y-%m-%d"),
                    "End": end_date.strftime("%Y-%m-%d"),
                },
                Granularity=granularity,
                Metrics=metrics,
                GroupBy=[{"Type": "DIMENSION", "Key": "SERVICE"}],
            )
            return dict(response)
        except Exception as e:
            logger.error(f"Error retrieving cost data: {e}")
            raise

    def get_cost_forecast(self, days_forward: int = 30) -> Dict[str, Any]:
        """
        Get cost forecast for the specified number of days.

        Args:
            days_forward: Number of days to forecast

        Returns:
            Dictionary containing forecast data
        """
        start_date = datetime.now().date()
        end_date = start_date + timedelta(days=days_forward)

        try:
            response = self.client.get_cost_forecast(
                TimePeriod={
                    "Start": start_date.strftime("%Y-%m-%d"),
                    "End": end_date.strftime("%Y-%m-%d"),
                },
                Metric="UNBLENDED_COST",
                Granularity="MONTHLY",
            )
            return dict(response)
        except Exception as e:
            logger.error(f"Error retrieving cost forecast: {e}")
            return {}

    def get_services_cost_summary(self, days_back: int = 30) -> List[Dict[str, Any]]:
        """
        Get cost summary grouped by service.

        Args:
            days_back: Number of days to look back

        Returns:
            List of dictionaries with service name and cost
        """
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days_back)

        try:
            response = self.client.get_cost_and_usage(
                TimePeriod={
                    "Start": start_date.strftime("%Y-%m-%d"),
                    "End": end_date.strftime("%Y-%m-%d"),
                },
                Granularity="MONTHLY",
                Metrics=["UnblendedCost"],
                GroupBy=[{"Type": "DIMENSION", "Key": "SERVICE"}],
            )

            services = []
            for result in response.get("ResultsByTime", []):
                for group in result.get("Groups", []):
                    service_name = group["Keys"][0]
                    cost = float(group["Metrics"]["UnblendedCost"]["Amount"])
                    services.append({"service": service_name, "cost": cost})

            # Aggregate costs by service
            service_totals: Dict[str, float] = {}
            for item in services:
                service = item["service"]
                cost = item["cost"]
                if service in service_totals:
                    service_totals[service] += cost
                else:
                    service_totals[service] = cost

            # Convert to list and sort by cost
            result = [
                {"service": service, "cost": cost}
                for service, cost in service_totals.items()
            ]
            result.sort(key=lambda x: x["cost"], reverse=True)

            return result
        except Exception as e:
            logger.error(f"Error retrieving services cost summary: {e}")
            return []

    def get_detailed_cost_breakdown(
        self, days_back: int = 30
    ) -> List[Dict[str, Any]]:
        """
        Get detailed cost breakdown by service and usage type.
        
        Args:
            days_back: Number of days to look back
            
        Returns:
            List of dictionaries with detailed cost information
        """
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days_back)
        
        try:
            # Get cost breakdown by service and usage type for more granular data
            response = self.client.get_cost_and_usage(
                TimePeriod={
                    "Start": start_date.strftime("%Y-%m-%d"),
                    "End": end_date.strftime("%Y-%m-%d"),
                },
                Granularity="DAILY",
                Metrics=["UnblendedCost"],
                GroupBy=[
                    {"Type": "DIMENSION", "Key": "SERVICE"},
                    {"Type": "DIMENSION", "Key": "USAGE_TYPE"},
                ],
            )
            
            detailed_costs = []
            for result in response.get("ResultsByTime", []):
                for group in result.get("Groups", []):
                    service = group["Keys"][0]
                    usage_type = group["Keys"][1] if len(group["Keys"]) > 1 else "General"
                    cost = float(group["Metrics"]["UnblendedCost"]["Amount"])
                    
                    if cost > 0:  # Only include resources with costs
                        detailed_costs.append({
                            "service": service,
                            "resource_id": usage_type,  # Using usage type as resource identifier
                            "cost": cost,
                            "date": result["TimePeriod"]["Start"],
                        })
            
            # Sort by cost descending
            detailed_costs.sort(key=lambda x: x["cost"], reverse=True)
            return detailed_costs
            
        except Exception as e:
            logger.error(f"Error retrieving detailed cost breakdown: {e}")
            return []

    def get_cost_by_tag(
        self, days_back: int = 30, tag_key: str = "Name"
    ) -> List[Dict[str, Any]]:
        """
        Get cost breakdown by tag.
        
        Args:
            days_back: Number of days to look back
            tag_key: Tag key to group by (e.g., 'Name', 'Environment')
            
        Returns:
            List of dictionaries with cost by tag
        """
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days_back)
        
        try:
            response = self.client.get_cost_and_usage(
                TimePeriod={
                    "Start": start_date.strftime("%Y-%m-%d"),
                    "End": end_date.strftime("%Y-%m-%d"),
                },
                Granularity="MONTHLY",
                Metrics=["UnblendedCost"],
                GroupBy=[
                    {"Type": "DIMENSION", "Key": "SERVICE"},
                    {"Type": "TAG", "Key": tag_key},
                ],
            )
            
            tag_costs = []
            for result in response.get("ResultsByTime", []):
                for group in result.get("Groups", []):
                    service = group["Keys"][0]
                    tag_value = group["Keys"][1] if len(group["Keys"]) > 1 else "Untagged"
                    cost = float(group["Metrics"]["UnblendedCost"]["Amount"])
                    
                    if cost > 0:
                        tag_costs.append({
                            "service": service,
                            "tag_key": tag_key,
                            "tag_value": tag_value,
                            "cost": cost,
                        })
            
            # Sort by cost descending
            tag_costs.sort(key=lambda x: x["cost"], reverse=True)
            return tag_costs
            
        except Exception as e:
            logger.error(f"Error retrieving cost by tag: {e}")
            return []

    def get_billing_cycle_info(self) -> Dict[str, Any]:
        """
        Get information about the AWS billing cycle.
        Uses a simplified approach based on calendar months.
        
        Returns:
            Dictionary with billing cycle information
        """
        try:
            current_date = datetime.now().date()
            
            # Use calendar month as billing cycle (simplified approach)
            # Current billing cycle starts on the 1st of current month
            current_cycle_start = current_date.replace(day=1)
            
            # Previous billing cycle
            if current_cycle_start.month == 1:
                # If current month is January, previous cycle was December of last year
                prev_cycle_start = current_cycle_start.replace(year=current_cycle_start.year - 1, month=12)
            else:
                # Previous cycle was last month
                prev_cycle_start = current_cycle_start.replace(month=current_cycle_start.month - 1)
            
            # Calculate end dates
            prev_cycle_end = current_cycle_start - timedelta(days=1)
            
            # Calculate days in each cycle
            current_cycle_days = (current_date - current_cycle_start).days + 1
            previous_cycle_days = (prev_cycle_end - prev_cycle_start).days + 1
            
            return {
                "billing_start_day": 1,  # Calendar month approach
                "current_cycle_start": current_cycle_start.strftime("%Y-%m-%d"),
                "current_cycle_days": current_cycle_days,
                "previous_cycle_start": prev_cycle_start.strftime("%Y-%m-%d"),
                "previous_cycle_end": prev_cycle_end.strftime("%Y-%m-%d"),
                "previous_cycle_days": previous_cycle_days,
            }
                
        except Exception as e:
            logger.error(f"Error retrieving billing cycle info: {e}")
            # Fallback to month-based billing
            current_date = datetime.now().date()
            cycle_start = current_date.replace(day=1)
            prev_cycle_start = (cycle_start - timedelta(days=1)).replace(day=1)
            prev_cycle_end = cycle_start - timedelta(days=1)
            
            return {
                "billing_start_day": 1,
                "current_cycle_start": cycle_start.strftime("%Y-%m-%d"),
                "current_cycle_days": (current_date - cycle_start).days + 1,
                "previous_cycle_start": prev_cycle_start.strftime("%Y-%m-%d"),
                "previous_cycle_end": prev_cycle_end.strftime("%Y-%m-%d"),
                "previous_cycle_days": (prev_cycle_end - prev_cycle_start).days + 1,
            }

    def get_billing_cycle_costs(
        self, cycle_start: str, cycle_end: str
    ) -> List[Dict[str, Any]]:
        """
        Get cost data for a specific billing cycle period.
        
        Args:
            cycle_start: Start date of billing cycle (YYYY-MM-DD)
            cycle_end: End date of billing cycle (YYYY-MM-DD)
            
        Returns:
            List of dictionaries with cost data for the period
        """
        try:
            response = self.client.get_cost_and_usage(
                TimePeriod={
                    "Start": cycle_start,
                    "End": cycle_end,
                },
                Granularity="MONTHLY",
                Metrics=["UnblendedCost"],
                GroupBy=[
                    {"Type": "DIMENSION", "Key": "SERVICE"},
                ],
            )
            
            services = []
            for result in response.get("ResultsByTime", []):
                for group in result.get("Groups", []):
                    service_name = group["Keys"][0]
                    cost = float(group["Metrics"]["UnblendedCost"]["Amount"])
                    services.append({
                        "service": service_name,
                        "cost": cost
                    })
            
            # Sort by cost descending
            services.sort(key=lambda x: x["cost"], reverse=True)
            return services
            
        except Exception as e:
            logger.error(f"Error retrieving billing cycle costs: {e}")
            return []
