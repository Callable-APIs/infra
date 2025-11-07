"""Oracle Cloud Infrastructure billing API client."""
import logging
import os
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import oci
from oci.config import from_file
from oci.exceptions import ServiceError

logger = logging.getLogger(__name__)


class OCIBillingClient:
    """Client for retrieving Oracle Cloud Infrastructure billing data."""

    def __init__(
        self,
        tenancy_ocid: Optional[str] = None,
        user_ocid: Optional[str] = None,
        fingerprint: Optional[str] = None,
        private_key_path: Optional[str] = None,
        region: Optional[str] = None,
    ):
        """
        Initialize OCI billing client.

        Args:
            tenancy_ocid: OCI tenancy OCID
            user_ocid: OCI user OCID
            fingerprint: OCI API key fingerprint
            private_key_path: Path to OCI private key file
            region: OCI region
        """
        # Try to get from environment if not provided
        self.tenancy_ocid = tenancy_ocid or os.environ.get("OCI_TENANCY_OCID")
        self.user_ocid = user_ocid or os.environ.get("OCI_USER_OCID")
        self.fingerprint = fingerprint or os.environ.get("OCI_FINGERPRINT")
        self.private_key_path = private_key_path or os.environ.get("OCI_PRIVATE_KEY_PATH")
        self.region = region or os.environ.get("OCI_REGION", "us-sanjose-1")

        if not all([self.tenancy_ocid, self.user_ocid, self.fingerprint, self.private_key_path]):
            raise ValueError("Missing required OCI credentials")

        # Load private key
        with open(self.private_key_path, "r") as f:
            self.private_key = f.read()

        # Create signer
        self.signer = oci.signer.Signer(
            tenancy=self.tenancy_ocid,
            user=self.user_ocid,
            fingerprint=self.fingerprint,
            private_key_file_location=self.private_key_path,
        )

        # Initialize clients
        self.config = {
            "tenancy": self.tenancy_ocid,
            "user": self.user_ocid,
            "fingerprint": self.fingerprint,
            "key_file": self.private_key_path,
            "region": self.region,
        }

        # Initialize Usage API client (for cost data)
        try:
            self.usage_client = oci.usage_api.UsageapiClient(self.config, signer=self.signer)
        except Exception as e:
            logger.warning(f"Could not initialize Usage API client: {e}")
            self.usage_client = None

        # Initialize Budget API client (for budget/cost tracking)
        try:
            self.budget_client = oci.budget.BudgetClient(self.config, signer=self.signer)
        except Exception as e:
            logger.warning(f"Could not initialize Budget API client: {e}")
            self.budget_client = None

        # Initialize Compute client to get instance details
        try:
            self.compute_client = oci.core.ComputeClient(self.config, signer=self.signer)
        except Exception as e:
            logger.warning(f"Could not initialize Compute API client: {e}")
            self.compute_client = None

    def get_usage_costs(
        self,
        compartment_id: str,
        start_date: datetime,
        end_date: datetime,
        granularity: str = "DAILY",
    ) -> List[Dict[str, Any]]:
        """
        Get usage costs for a time period.

        Args:
            compartment_id: OCI compartment OCID
            start_date: Start date for cost query
            end_date: End date for cost query
            granularity: Granularity (DAILY, MONTHLY)

        Returns:
            List of cost records
        """
        if not self.usage_client:
            logger.error("Usage API client not available")
            return []

        try:
            # Query usage costs
            request = oci.usage_api.models.RequestSummarizedUsagesDetails(
                tenant_id=self.tenancy_ocid,
                time_usage_started=start_date,
                time_usage_ended=end_date,
                granularity=granularity,
                group_by=["service", "skuName"],
                query_type="COST",
                compartment_depth=1,
            )

            response = self.usage_client.request_summarized_usages(request)

            logger.info(f"OCI Usage API response: {len(response.data.items) if response.data.items else 0} items found")
            
            costs = []
            total_amount = 0.0
            for item in response.data.items:
                amount = float(item.computed_amount) if item.computed_amount else 0.0
                total_amount += amount
                logger.info(f"OCI cost item: service={item.service}, sku={item.sku_name}, amount=${amount:.2f}")
                costs.append(
                    {
                        "time_usage_started": item.time_usage_started.isoformat() if item.time_usage_started else None,
                        "time_usage_ended": item.time_usage_ended.isoformat() if item.time_usage_ended else None,
                        "service": item.service,
                        "sku_name": item.sku_name,
                        "computed_amount": amount,
                        "computed_quantity": float(item.computed_quantity) if item.computed_quantity else 0.0,
                        "currency": item.currency,
                    }
                )
            
            logger.info(f"OCI total cost from API: ${total_amount:.2f}")

            if not costs:
                logger.warning(f"No cost data found for period {start_date} to {end_date}. This may be normal if instances were destroyed.")
            
            return costs

        except ServiceError as e:
            logger.error(f"OCI Service Error retrieving usage costs: {e}")
            logger.error(f"Error code: {e.code}, Message: {e.message}")
            return []
        except Exception as e:
            logger.error(f"Error retrieving OCI usage costs: {e}", exc_info=True)
            return []

    def get_instance_costs(
        self,
        compartment_id: str,
        start_date: datetime,
        end_date: datetime,
        instance_display_names: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Get costs for specific compute instances.

        Args:
            compartment_id: OCI compartment OCID
            start_date: Start date
            end_date: End date
            instance_display_names: Optional list of instance display names to filter

        Returns:
            Dictionary with instance costs
        """
        costs = self.get_usage_costs(compartment_id, start_date, end_date, granularity="DAILY")

        # Filter for compute instances (or all costs if no filter)
        instance_costs = {}
        total_cost = 0.0

        for cost in costs:
            # Include all costs, not just COMPUTE
            # If filtering by instance names, only include COMPUTE service
            if instance_display_names and cost["service"] != "COMPUTE":
                continue
            
            # For compute instances, try to match by display name
            if cost["service"] == "COMPUTE" and instance_display_names:
                instance_name = cost.get("sku_name", "Unknown")
                # Check if this matches any of our instance display names
                # OCI SKU names might not match display names exactly
                if not any(name.lower() in instance_name.lower() or instance_name.lower() in name.lower() 
                          for name in instance_display_names):
                    continue
            else:
                # Use service name for non-compute or when not filtering
                instance_name = f"{cost['service']} - {cost.get('sku_name', 'General')}"

            if instance_name not in instance_costs:
                instance_costs[instance_name] = {
                    "total_cost": 0.0,
                    "currency": cost.get("currency", "USD"),
                    "details": [],
                }

            instance_costs[instance_name]["total_cost"] += cost["computed_amount"]
            instance_costs[instance_name]["details"].append(cost)
            total_cost += cost["computed_amount"]

        return {
            "instances": instance_costs,
            "total_cost": total_cost,
            "currency": "USD",
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat(),
            },
        }

    def get_monthly_costs(self, compartment_id: str, year: int, month: int) -> Dict[str, Any]:
        """
        Get costs for a specific month.

        Args:
            compartment_id: OCI compartment OCID
            year: Year
            month: Month (1-12)

        Returns:
            Dictionary with monthly costs
        """
        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1)
        else:
            end_date = datetime(year, month + 1, 1)

        return self.get_instance_costs(compartment_id, start_date, end_date)

