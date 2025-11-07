"""Oracle Cloud Infrastructure billing adapter."""
import logging
import os
from collections import defaultdict
from datetime import datetime
from typing import Any, Dict, List, Optional

from src.billing.base_adapter import BillingAdapter
from src.oci_billing_client import OCIBillingClient

logger = logging.getLogger(__name__)


class OCIBillingAdapter(BillingAdapter):
    """Oracle Cloud Infrastructure billing adapter."""

    def __init__(self, compartment_id: Optional[str] = None):
        """
        Initialize OCI billing adapter.

        Args:
            compartment_id: OCI compartment OCID (optional, from env if not provided)
        """
        self.compartment_id = compartment_id or os.environ.get("OCI_COMPARTMENT_ID")
        self.client = None
        self._initialized = False

    @property
    def provider_name(self) -> str:
        """Return Oracle Cloud provider name."""
        return "Oracle Cloud"

    def _init_client(self):
        """Initialize OCI billing client."""
        if self._initialized:
            return

        try:
            self.client = OCIBillingClient()
            logger.info("Oracle Cloud billing client initialized")
        except Exception as e:
            logger.warning(f"Could not initialize OCI client: {e}")
            self.client = None

        self._initialized = True

    def is_available(self) -> bool:
        """Check if OCI adapter is available."""
        if not self.compartment_id:
            return False

        self._init_client()
        return self.client is not None

    def get_daily_costs(
        self, start_date: datetime, end_date: datetime
    ) -> List[Dict[str, Any]]:
        """
        Get Oracle Cloud costs broken down by day.

        Args:
            start_date: Start date
            end_date: End date

        Returns:
            List of daily cost records
        """
        if not self.is_available():
            return []

        try:
            # Get daily costs
            costs = self.client.get_usage_costs(
                self.compartment_id, start_date, end_date, granularity="DAILY"
            )

            # Group by date
            daily_costs_dict = defaultdict(lambda: {"services": {}, "total_cost": 0.0})

            for cost in costs:
                date_str = cost.get("time_usage_started")
                if not date_str:
                    continue

                # Parse date (ISO format)
                try:
                    if isinstance(date_str, str):
                        date_obj = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
                    else:
                        date_obj = date_str
                    date = date_obj.strftime("%Y-%m-%d")
                except Exception:
                    logger.warning(f"Could not parse date: {date_str}")
                    continue

                service = cost.get("service", "Unknown")
                amount = cost.get("computed_amount", 0.0)
                currency = cost.get("currency", "USD")

                if date not in daily_costs_dict:
                    daily_costs_dict[date] = {
                        "services": {},
                        "total_cost": 0.0,
                        "currency": currency,
                    }

                daily_costs_dict[date]["services"][service] = (
                    daily_costs_dict[date]["services"].get(service, 0.0) + amount
                )
                daily_costs_dict[date]["total_cost"] += amount

            # Convert to list format
            daily_costs = []
            for date, data in sorted(daily_costs_dict.items()):
                daily_costs.append(
                    {
                        "date": date,
                        "provider": self.provider_name,
                        "total_cost": data["total_cost"],
                        "currency": data.get("currency", "USD"),
                        "services": data["services"],
                    }
                )

            logger.info(f"Retrieved {len(daily_costs)} days of Oracle Cloud cost data")
            return daily_costs

        except Exception as e:
            logger.error(f"Error retrieving OCI costs: {e}", exc_info=True)
            return []

