"""Base adapter class for cloud provider billing."""
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, List, Optional


class BillingAdapter(ABC):
    """Base class for cloud provider billing adapters."""

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Return the name of the cloud provider."""
        pass

    @abstractmethod
    def get_daily_costs(
        self, start_date: datetime, end_date: datetime
    ) -> List[Dict[str, Any]]:
        """
        Get daily costs for the specified date range.

        Args:
            start_date: Start date (inclusive)
            end_date: End date (exclusive)

        Returns:
            List of daily cost records, each with:
            - date: YYYY-MM-DD format
            - provider: Provider name
            - total_cost: Total cost for the day
            - currency: Currency code (e.g., "USD")
            - services: Dict of service/resource costs
        """
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """
        Check if the adapter is available (credentials configured).

        Returns:
            True if adapter can be used, False otherwise
        """
        pass

    def get_monthly_total(
        self, year: int, month: int
    ) -> Dict[str, Any]:
        """
        Get total cost for a specific month.

        Args:
            year: Year
            month: Month (1-12)

        Returns:
            Dictionary with:
            - total_cost: Total cost for the month
            - currency: Currency code
            - period: Start and end dates
        """
        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1)
        else:
            end_date = datetime(year, month + 1, 1)

        daily_costs = self.get_daily_costs(start_date, end_date)
        total = sum(cost["total_cost"] for cost in daily_costs)

        return {
            "total_cost": total,
            "currency": daily_costs[0]["currency"] if daily_costs else "USD",
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat(),
            },
        }

