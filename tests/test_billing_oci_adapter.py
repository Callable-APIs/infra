"""Tests for Oracle Cloud Infrastructure billing adapter."""
import pytest
from datetime import datetime
from unittest.mock import Mock, patch

from clint.billing.oci_adapter import OCIBillingAdapter


class TestOCIBillingAdapter:
    """Test cases for OCIBillingAdapter."""

    def test_provider_name(self):
        """Test provider name."""
        adapter = OCIBillingAdapter()
        assert adapter.provider_name == "Oracle Cloud"

    def test_is_available_without_compartment_id(self):
        """Test is_available returns False when compartment_id is missing."""
        adapter = OCIBillingAdapter()
        adapter._initialized = True
        assert adapter.is_available() is False

    def test_is_available_with_compartment_id(self):
        """Test is_available when compartment_id is provided."""
        adapter = OCIBillingAdapter(compartment_id="ocid1.compartment.oc1..test")
        adapter._initialized = True
        adapter.client = Mock()
        assert adapter.is_available() is True

    @patch("clint.billing.oci_adapter.OCIBillingClient")
    def test_init_client_success(self, mock_client_class):
        """Test successful client initialization."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        adapter = OCIBillingAdapter(compartment_id="ocid1.compartment.oc1..test")
        adapter._init_client()
        
        assert adapter.client == mock_client
        assert adapter._initialized is True

    def test_get_daily_costs_structure(self):
        """Test get_daily_costs returns correct structure."""
        adapter = OCIBillingAdapter(compartment_id="ocid1.compartment.oc1..test")
        adapter.client = Mock()
        adapter._initialized = True
        
        # Mock OCI client response structure
        mock_costs = [
            {
                "time_usage_started": "2025-01-01T00:00:00Z",
                "service": "Compute",
                "computed_amount": 10.50,
                "currency": "USD",
            },
            {
                "time_usage_started": "2025-01-01T00:00:00Z",
                "service": "Storage",
                "computed_amount": 5.25,
                "currency": "USD",
            },
            {
                "time_usage_started": "2025-01-02T00:00:00Z",
                "service": "Compute",
                "computed_amount": 8.00,
                "currency": "USD",
            },
        ]
        
        adapter.client.get_usage_costs = Mock(return_value=mock_costs)
        
        start = datetime(2025, 1, 1)
        end = datetime(2025, 1, 3)
        result = adapter.get_daily_costs(start, end)
        
        assert isinstance(result, list)
        assert len(result) == 2  # Two days
        
        # Check first day
        day1 = result[0]
        assert day1["date"] == "2025-01-01"
        assert day1["provider"] == "Oracle Cloud"
        assert day1["total_cost"] == 15.75  # 10.50 + 5.25
        assert day1["currency"] == "USD"
        assert "Compute" in day1["services"]
        assert "Storage" in day1["services"]
        assert day1["services"]["Compute"] == 10.50
        assert day1["services"]["Storage"] == 5.25
        
        # Check second day
        day2 = result[1]
        assert day2["date"] == "2025-01-02"
        assert day2["total_cost"] == 8.00
        assert day2["services"]["Compute"] == 8.00

    def test_get_daily_costs_groups_by_date(self):
        """Test that costs are properly grouped by date."""
        adapter = OCIBillingAdapter(compartment_id="ocid1.compartment.oc1..test")
        adapter.client = Mock()
        adapter._initialized = True
        
        # Multiple costs on same day
        mock_costs = [
            {
                "time_usage_started": "2025-01-01T00:00:00Z",
                "service": "Service1",
                "computed_amount": 5.0,
                "currency": "USD",
            },
            {
                "time_usage_started": "2025-01-01T12:00:00Z",
                "service": "Service2",
                "computed_amount": 3.0,
                "currency": "USD",
            },
        ]
        
        adapter.client.get_usage_costs = Mock(return_value=mock_costs)
        
        start = datetime(2025, 1, 1)
        end = datetime(2025, 1, 2)
        result = adapter.get_daily_costs(start, end)
        
        assert len(result) == 1
        assert result[0]["total_cost"] == 8.0
        assert len(result[0]["services"]) == 2

    def test_get_daily_costs_handles_missing_date(self):
        """Test get_daily_costs handles missing date gracefully."""
        adapter = OCIBillingAdapter(compartment_id="ocid1.compartment.oc1..test")
        adapter.client = Mock()
        adapter._initialized = True
        
        mock_costs = [
            {
                "service": "Compute",
                "computed_amount": 10.50,
                "currency": "USD",
                # Missing time_usage_started
            }
        ]
        
        adapter.client.get_usage_costs = Mock(return_value=mock_costs)
        
        start = datetime(2025, 1, 1)
        end = datetime(2025, 1, 2)
        result = adapter.get_daily_costs(start, end)
        
        # Should skip records without dates
        assert len(result) == 0

    def test_get_daily_costs_handles_errors(self):
        """Test get_daily_costs handles errors gracefully."""
        adapter = OCIBillingAdapter(compartment_id="ocid1.compartment.oc1..test")
        adapter.client = Mock()
        adapter._initialized = True
        
        adapter.client.get_usage_costs.side_effect = Exception("API Error")
        
        start = datetime(2025, 1, 1)
        end = datetime(2025, 1, 2)
        result = adapter.get_daily_costs(start, end)
        
        assert result == []

    def test_get_daily_costs_not_available(self):
        """Test get_daily_costs returns empty list when adapter not available."""
        adapter = OCIBillingAdapter()  # No compartment_id
        adapter._initialized = True
        
        start = datetime(2025, 1, 1)
        end = datetime(2025, 1, 2)
        result = adapter.get_daily_costs(start, end)
        
        assert result == []

