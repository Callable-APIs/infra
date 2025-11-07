"""Billing adapter manager for coordinating multiple providers."""
import logging
from collections import defaultdict
from datetime import datetime
from typing import Any, Dict, List, Optional, Set

from src.billing.aws_adapter import AWSBillingAdapter
from src.billing.base_adapter import BillingAdapter
from src.billing.ibm_adapter import IBMBillingAdapter
from src.billing.oci_adapter import OCIBillingAdapter

logger = logging.getLogger(__name__)


class BillingManager:
    """Manager for coordinating billing adapters across multiple cloud providers."""

    # Map of provider names to adapter classes
    ADAPTERS = {
        "aws": AWSBillingAdapter,
        "oracle": OCIBillingAdapter,
        "oci": OCIBillingAdapter,  # Alias
        "ibm": IBMBillingAdapter,
        "ibmcloud": IBMBillingAdapter,  # Alias
    }

    def __init__(self, providers: Optional[List[str]] = None, oci_compartment_id: Optional[str] = None):
        """
        Initialize billing manager.

        Args:
            providers: List of provider names to include (None = all available)
            oci_compartment_id: OCI compartment OCID (optional, from env if not provided)
        """
        self.providers = providers
        self.oci_compartment_id = oci_compartment_id
        self.adapters: Dict[str, BillingAdapter] = {}
        self._initialize_adapters()

    def _initialize_adapters(self):
        """Initialize adapters for requested providers."""
        # Normalize provider names
        requested_providers = set()
        if self.providers:
            for provider in self.providers:
                provider_lower = provider.lower()
                # Map aliases
                if provider_lower in ["oracle", "oci"]:
                    requested_providers.add("oracle")
                elif provider_lower in ["ibm", "ibmcloud"]:
                    requested_providers.add("ibm")
                elif provider_lower == "aws":
                    requested_providers.add("aws")
                else:
                    logger.warning(f"Unknown provider: {provider}, skipping")

        # Initialize adapters
        for provider_key, adapter_class in self.ADAPTERS.items():
            # Skip if specific providers requested and this one isn't
            if requested_providers and provider_key not in requested_providers:
                continue

            # Skip duplicates (aliases)
            if provider_key in ["oci", "ibmcloud"]:
                continue

            try:
                if provider_key == "oracle":
                    adapter = adapter_class(compartment_id=self.oci_compartment_id)
                else:
                    adapter = adapter_class()

                if adapter.is_available():
                    self.adapters[adapter.provider_name] = adapter
                    logger.info(f"Initialized {adapter.provider_name} billing adapter")
                else:
                    logger.info(f"{adapter.provider_name} adapter not available (missing credentials)")
            except Exception as e:
                logger.warning(f"Could not initialize {provider_key} adapter: {e}")

    def get_available_providers(self) -> List[str]:
        """Get list of available provider names."""
        return list(self.adapters.keys())

    def get_daily_costs(
        self, start_date: datetime, end_date: datetime
    ) -> Dict[str, Any]:
        """
        Get daily costs from all configured adapters.

        Args:
            start_date: Start date
            end_date: End date

        Returns:
            Dictionary with:
            - period: Start and end dates
            - providers: Dict mapping provider names to daily cost lists
            - daily_totals: Dict mapping dates to total costs across all providers
            - errors: List of error messages
        """
        result = {
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat(),
            },
            "providers": {},
            "daily_totals": {},
            "errors": [],
        }

        # Get costs from each adapter
        for provider_name, adapter in self.adapters.items():
            try:
                logger.info(f"Retrieving costs from {provider_name}...")
                costs = adapter.get_daily_costs(start_date, end_date)
                result["providers"][provider_name] = costs
            except Exception as e:
                error_msg = f"Error retrieving {provider_name} costs: {e}"
                logger.error(error_msg, exc_info=True)
                result["errors"].append(error_msg)
                result["providers"][provider_name] = []

        # Calculate daily totals across all providers
        daily_totals = defaultdict(lambda: {"total": 0.0, "by_provider": {}})
        for provider_name, costs in result["providers"].items():
            for cost_record in costs:
                date = cost_record["date"]
                amount = cost_record["total_cost"]
                daily_totals[date]["total"] += amount
                daily_totals[date]["by_provider"][provider_name] = amount

        result["daily_totals"] = dict(sorted(daily_totals.items()))

        return result

    def get_monthly_comparison(
        self, current_year: int, current_month: int
    ) -> Dict[str, Any]:
        """
        Get month-over-month comparison.

        Args:
            current_year: Current year
            current_month: Current month (1-12)

        Returns:
            Dictionary with month-over-month comparison data
        """
        # Calculate date ranges
        current_start = datetime(current_year, current_month, 1)
        if current_month == 12:
            current_end = datetime(current_year + 1, 1, 1)
            previous_start = datetime(current_year, 11, 1)
            previous_end = datetime(current_year, 12, 1)
        else:
            current_end = datetime(current_year, current_month + 1, 1)
            previous_start = datetime(current_year, current_month - 1, 1)
            previous_end = current_start

        # Get current month costs
        logger.info(f"Retrieving costs for {current_start.strftime('%B %Y')}...")
        current_costs = self.get_daily_costs(current_start, current_end)

        # Get previous month costs
        logger.info(f"Retrieving costs for {previous_start.strftime('%B %Y')}...")
        previous_costs = self.get_daily_costs(previous_start, previous_end)

        # Calculate totals
        current_total = sum(
            daily["total"] for daily in current_costs["daily_totals"].values()
        )
        previous_total = sum(
            daily["total"] for daily in previous_costs["daily_totals"].values()
        )

        # Calculate by provider
        current_by_provider = {}
        previous_by_provider = {}

        for provider_name in self.get_available_providers():
            current_by_provider[provider_name] = sum(
                cost["total_cost"]
                for cost in current_costs["providers"].get(provider_name, [])
            )
            previous_by_provider[provider_name] = sum(
                cost["total_cost"]
                for cost in previous_costs["providers"].get(provider_name, [])
            )

        comparison = {
            "current_month": {
                "year": current_year,
                "month": current_month,
                "period": {
                    "start": current_start.isoformat(),
                    "end": current_end.isoformat(),
                },
                "total_cost": current_total,
                "by_provider": current_by_provider,
                "daily_costs": current_costs,
            },
            "previous_month": {
                "year": previous_start.year,
                "month": previous_start.month,
                "period": {
                    "start": previous_start.isoformat(),
                    "end": previous_end.isoformat(),
                },
                "total_cost": previous_total,
                "by_provider": previous_by_provider,
                "daily_costs": previous_costs,
            },
            "comparison": {
                "total_change": current_total - previous_total,
                "total_change_percent": (
                    ((current_total - previous_total) / previous_total * 100)
                    if previous_total > 0
                    else 0.0
                ),
                "by_provider": {},
            },
        }

        # Calculate provider-level changes
        for provider_name in self.get_available_providers():
            current = current_by_provider.get(provider_name, 0.0)
            previous = previous_by_provider.get(provider_name, 0.0)
            change = current - previous
            change_percent = (change / previous * 100) if previous > 0 else 0.0

            comparison["comparison"]["by_provider"][provider_name] = {
                "current": current,
                "previous": previous,
                "change": change,
                "change_percent": change_percent,
            }

        return comparison

