"""AWS billing adapter."""
import logging
import os
from datetime import datetime
from typing import Any, Dict, List

try:
    import boto3
    from botocore.exceptions import ClientError, NoCredentialsError
    AWS_AVAILABLE = True
except ImportError:
    AWS_AVAILABLE = False

from src.billing.base_adapter import BillingAdapter

logger = logging.getLogger(__name__)


class AWSBillingAdapter(BillingAdapter):
    """AWS Cost Explorer billing adapter."""

    def __init__(self):
        """Initialize AWS billing adapter."""
        self.client = None
        self._initialized = False

    @property
    def provider_name(self) -> str:
        """Return AWS provider name."""
        return "AWS"

    def _init_client(self):
        """Initialize AWS Cost Explorer client."""
        if self._initialized:
            return

        if not AWS_AVAILABLE:
            logger.warning("boto3 not available, AWS costs will be skipped")
            self._initialized = True
            return

        try:
            self.client = boto3.client("ce", region_name="us-east-1")
            logger.info("AWS Cost Explorer client initialized")
        except NoCredentialsError:
            logger.warning("AWS credentials not found, AWS costs will be skipped")
        except Exception as e:
            logger.warning(f"Could not initialize AWS client: {e}")

        self._initialized = True

    def is_available(self) -> bool:
        """Check if AWS adapter is available."""
        self._init_client()
        return self.client is not None

    def get_daily_costs(
        self, start_date: datetime, end_date: datetime
    ) -> List[Dict[str, Any]]:
        """
        Get AWS costs broken down by day.

        Args:
            start_date: Start date
            end_date: End date

        Returns:
            List of daily cost records
        """
        if not self.is_available():
            return []

        try:
            response = self.client.get_cost_and_usage(
                TimePeriod={
                    "Start": start_date.strftime("%Y-%m-%d"),
                    "End": end_date.strftime("%Y-%m-%d"),
                },
                Granularity="DAILY",
                Metrics=["UnblendedCost", "BlendedCost"],
                GroupBy=[{"Type": "DIMENSION", "Key": "SERVICE"}],
            )

            daily_costs = []
            for result in response.get("ResultsByTime", []):
                date = result["TimePeriod"]["Start"]
                
                # Get total cost - try UnblendedCost first, fall back to BlendedCost
                total_metrics = result.get("Total", {})
                if "UnblendedCost" in total_metrics:
                    total_cost = float(total_metrics["UnblendedCost"]["Amount"])
                    currency = total_metrics["UnblendedCost"].get("Unit", "USD")
                elif "BlendedCost" in total_metrics:
                    total_cost = float(total_metrics["BlendedCost"]["Amount"])
                    currency = total_metrics["BlendedCost"].get("Unit", "USD")
                else:
                    logger.warning(f"No cost metrics found for {date}, skipping")
                    continue

                # Service breakdown
                services = {}
                for group in result.get("Groups", []):
                    service_name = group["Keys"][0]
                    group_metrics = group.get("Metrics", {})
                    if "UnblendedCost" in group_metrics:
                        service_cost = float(group_metrics["UnblendedCost"]["Amount"])
                    elif "BlendedCost" in group_metrics:
                        service_cost = float(group_metrics["BlendedCost"]["Amount"])
                    else:
                        service_cost = 0.0
                    services[service_name] = service_cost

                daily_costs.append(
                    {
                        "date": date,
                        "provider": self.provider_name,
                        "total_cost": total_cost,
                        "currency": currency,
                        "services": services,
                    }
                )

            logger.info(f"Retrieved {len(daily_costs)} days of AWS cost data")
            return daily_costs

        except ClientError as e:
            logger.error(f"AWS API error: {e}")
            return []
        except Exception as e:
            logger.error(f"Error retrieving AWS costs: {e}", exc_info=True)
            return []

