"""Tests for IBM Cloud billing adapter."""
import pytest
from datetime import datetime
from unittest.mock import Mock, patch

from clint.billing.ibm_adapter import IBMBillingAdapter


class TestIBMBillingAdapter:
    """Test cases for IBMBillingAdapter."""

    def test_provider_name(self):
        """Test provider name."""
        adapter = IBMBillingAdapter()
        assert adapter.provider_name == "IBM Cloud"

    def test_is_available_without_client(self):
        """Test is_available returns False when client is not initialized."""
        adapter = IBMBillingAdapter()
        adapter._initialized = True
        adapter.client = None
        assert adapter.is_available() is False

    def test_is_available_with_client(self):
        """Test is_available when client is initialized."""
        adapter = IBMBillingAdapter()
        adapter._initialized = True
        adapter.client = Mock()
        assert adapter.is_available() is True

    @patch("clint.billing.ibm_adapter.IBMBillingClient")
    def test_init_client_success(self, mock_client_class):
        """Test successful client initialization."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        adapter = IBMBillingAdapter()
        adapter._init_client()
        
        assert adapter.client == mock_client
        assert adapter._initialized is True

    def test_get_daily_costs_structure(self):
        """Test get_daily_costs returns correct structure."""
        adapter = IBMBillingAdapter()
        adapter.client = Mock()
        adapter._initialized = True
        
        # Mock IBM client response structure
        mock_costs = [
            {
                "start_time": "2025-01-01T00:00:00Z",
                "category": "compute",
                "cost": 10.50,
                "currency": "USD",
            },
            {
                "start_time": "2025-01-01T00:00:00Z",
                "category": "storage",
                "cost": 5.25,
                "currency": "USD",
            },
            {
                "start_time": "2025-01-02T00:00:00Z",
                "category": "compute",
                "cost": 8.00,
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
        assert day1["provider"] == "IBM Cloud"
        assert day1["total_cost"] == 15.75  # 10.50 + 5.25
        assert day1["currency"] == "USD"
        assert "compute" in day1["services"]
        assert "storage" in day1["services"]
        assert day1["services"]["compute"] == 10.50
        assert day1["services"]["storage"] == 5.25

    def test_get_daily_costs_handles_missing_date(self):
        """Test get_daily_costs handles missing date by using start_date."""
        adapter = IBMBillingAdapter()
        adapter.client = Mock()
        adapter._initialized = True
        
        mock_costs = [
            {
                "category": "compute",
                "cost": 10.50,
                "currency": "USD",
                # Missing start_time and start_date
            }
        ]
        
        adapter.client.get_usage_costs = Mock(return_value=mock_costs)
        
        start = datetime(2025, 1, 1)
        end = datetime(2025, 1, 2)
        result = adapter.get_daily_costs(start, end)
        
        # Should use start_date when date is missing
        assert len(result) == 1
        assert result[0]["date"] == "2025-01-01"

    def test_get_daily_costs_handles_errors(self):
        """Test get_daily_costs handles errors gracefully."""
        adapter = IBMBillingAdapter()
        adapter.client = Mock()
        adapter._initialized = True
        
        adapter.client.get_usage_costs.side_effect = Exception("API Error")
        
        start = datetime(2025, 1, 1)
        end = datetime(2025, 1, 2)
        result = adapter.get_daily_costs(start, end)
        
        assert result == []

    def test_get_daily_costs_not_available(self):
        """Test get_daily_costs returns empty list when adapter not available."""
        adapter = IBMBillingAdapter()
        adapter.client = None
        adapter._initialized = True
        
        start = datetime(2025, 1, 1)
        end = datetime(2025, 1, 2)
        result = adapter.get_daily_costs(start, end)
        
        assert result == []

