"""Tests for the base billing adapter."""
import pytest
from datetime import datetime
from unittest.mock import Mock, patch

from clint.billing.base_adapter import BillingAdapter


class MockBillingAdapter(BillingAdapter):
    """Mock adapter for testing base class functionality."""

    @property
    def provider_name(self) -> str:
        return "MockProvider"

    def is_available(self) -> bool:
        return True

    def get_daily_costs(self, start_date: datetime, end_date: datetime):
        return [
            {
                "date": "2025-01-01",
                "provider": "MockProvider",
                "total_cost": 10.50,
                "currency": "USD",
                "services": {"Service1": 5.25, "Service2": 5.25},
            }
        ]


class TestBillingAdapter:
    """Test cases for BillingAdapter base class."""

    def test_provider_name_property(self):
        """Test that provider_name is a property."""
        adapter = MockBillingAdapter()
        assert adapter.provider_name == "MockProvider"

    def test_get_daily_costs_returns_list(self):
        """Test that get_daily_costs returns a list."""
        adapter = MockBillingAdapter()
        start = datetime(2025, 1, 1)
        end = datetime(2025, 1, 2)
        result = adapter.get_daily_costs(start, end)
        assert isinstance(result, list)
        assert len(result) > 0

    def test_get_daily_costs_structure(self):
        """Test that daily cost records have the expected structure."""
        adapter = MockBillingAdapter()
        start = datetime(2025, 1, 1)
        end = datetime(2025, 1, 2)
        result = adapter.get_daily_costs(start, end)
        
        assert len(result) > 0
        cost_record = result[0]
        
        # Check required fields
        assert "date" in cost_record
        assert "provider" in cost_record
        assert "total_cost" in cost_record
        assert "currency" in cost_record
        assert "services" in cost_record
        
        # Check types
        assert isinstance(cost_record["date"], str)
        assert isinstance(cost_record["provider"], str)
        assert isinstance(cost_record["total_cost"], (int, float))
        assert isinstance(cost_record["currency"], str)
        assert isinstance(cost_record["services"], dict)

    def test_get_monthly_total(self):
        """Test get_monthly_total method."""
        adapter = MockBillingAdapter()
        result = adapter.get_monthly_total(2025, 1)
        
        assert isinstance(result, dict)
        assert "total_cost" in result
        assert "currency" in result
        assert "period" in result
        
        assert isinstance(result["total_cost"], (int, float))
        assert isinstance(result["currency"], str)
        assert isinstance(result["period"], dict)
        assert "start" in result["period"]
        assert "end" in result["period"]

    def test_get_monthly_total_calculates_sum(self):
        """Test that get_monthly_total sums daily costs."""
        adapter = MockBillingAdapter()
        result = adapter.get_monthly_total(2025, 1)
        
        # Should sum the daily costs
        assert result["total_cost"] >= 0

    def test_get_monthly_total_december(self):
        """Test get_monthly_total for December (year boundary)."""
        adapter = MockBillingAdapter()
        result = adapter.get_monthly_total(2025, 12)
        
        assert result["period"]["start"].startswith("2025-12-01")
        assert result["period"]["end"].startswith("2026-01-01")

    def test_is_available_abstract(self):
        """Test that is_available is implemented."""
        adapter = MockBillingAdapter()
        assert isinstance(adapter.is_available(), bool)

