"""IBM Cloud billing adapter."""
import logging
import os
from collections import defaultdict
from datetime import datetime
from typing import Any, Dict, List

from clint.billing.base_adapter import BillingAdapter
from clint.billing.ibm_client import IBMBillingClient

logger = logging.getLogger(__name__)


class IBMBillingAdapter(BillingAdapter):
    """IBM Cloud billing adapter."""

    def __init__(self):
        """Initialize IBM Cloud billing adapter."""
        self.client = None
        self._initialized = False

    @property
    def provider_name(self) -> str:
        """Return IBM Cloud provider name."""
        return "IBM Cloud"

    def _init_client(self):
        """Initialize IBM Cloud billing client."""
        if self._initialized:
            return

        try:
            self.client = IBMBillingClient()
            logger.info("IBM Cloud billing client initialized")
        except Exception as e:
            logger.warning(f"Could not initialize IBM Cloud client: {e}")
            self.client = None

        self._initialized = True

    def is_available(self) -> bool:
        """Check if IBM Cloud adapter is available."""
        self._init_client()
        return self.client is not None

    def get_daily_costs(
        self, start_date: datetime, end_date: datetime
    ) -> List[Dict[str, Any]]:
        """
        Get IBM Cloud costs broken down by day.

        Args:
            start_date: Start date
            end_date: End date

        Returns:
            List of daily cost records
        """
        if not self.is_available():
            return []

        try:
            # Get usage costs (IBM Cloud API may not support daily granularity)
            costs = self.client.get_usage_costs(start_date=start_date, end_date=end_date)

            # Group by date if available, otherwise aggregate by month
            daily_costs_dict = defaultdict(lambda: {"services": {}, "total_cost": 0.0})

            for cost in costs:
                # Try to extract date from cost record
                date_str = cost.get("start_time") or cost.get("start_date")
                if not date_str:
                    # If no date, use start_date
                    date = start_date.strftime("%Y-%m-%d")
                else:
                    try:
                        if isinstance(date_str, str):
                            # Try parsing different date formats
                            if "T" in date_str:
                                date_obj = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
                            else:
                                date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                        else:
                            date_obj = date_str
                        date = date_obj.strftime("%Y-%m-%d")
                    except Exception:
                        date = start_date.strftime("%Y-%m-%d")

                category = cost.get("category") or cost.get("resource_name", "Unknown")
                amount = cost.get("cost", 0.0)
                currency = cost.get("currency", "USD")

                if date not in daily_costs_dict:
                    daily_costs_dict[date] = {
                        "services": {},
                        "total_cost": 0.0,
                        "currency": currency,
                    }

                daily_costs_dict[date]["services"][category] = (
                    daily_costs_dict[date]["services"].get(category, 0.0) + amount
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

            logger.info(f"Retrieved {len(daily_costs)} days of IBM Cloud cost data")
            return daily_costs

        except Exception as e:
            logger.error(f"Error retrieving IBM Cloud costs: {e}", exc_info=True)
            return []

