"""Tests for billing manager."""
import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock

from clint.billing.manager import BillingManager


class TestBillingManager:
    """Test cases for BillingManager."""

    def test_init_all_providers(self):
        """Test initialization with all providers."""
        with patch("clint.billing.manager.AWSBillingAdapter") as mock_aws, \
             patch("clint.billing.manager.OCIBillingAdapter") as mock_oci, \
             patch("clint.billing.manager.IBMBillingAdapter") as mock_ibm:
            
            mock_aws_adapter = Mock()
            type(mock_aws_adapter).provider_name = property(lambda self: "AWS")
            mock_aws_adapter.is_available.return_value = True
            mock_aws.return_value = mock_aws_adapter
            
            mock_oci_adapter = Mock()
            mock_oci_adapter.provider_name = "Oracle Cloud"
            mock_oci_adapter.is_available.return_value = False  # No credentials
            mock_oci.return_value = mock_oci_adapter
            
            mock_ibm_adapter = Mock()
            mock_ibm_adapter.provider_name = "IBM Cloud"
            mock_ibm_adapter.is_available.return_value = False  # No credentials
            mock_ibm.return_value = mock_ibm_adapter
            
            manager = BillingManager()
            
            assert "AWS" in manager.get_available_providers()

    def test_init_specific_providers(self):
        """Test initialization with specific providers."""
        with patch("clint.billing.manager.AWSBillingAdapter") as mock_aws:
            mock_aws_adapter = Mock()
            type(mock_aws_adapter).provider_name = property(lambda self: "AWS")
            mock_aws_adapter.is_available.return_value = True
            mock_aws.return_value = mock_aws_adapter
            
            manager = BillingManager(providers=["aws"])
            
            assert "AWS" in manager.get_available_providers()
            assert len(manager.get_available_providers()) == 1

    def test_provider_aliases(self):
        """Test that provider aliases work correctly."""
        with patch("clint.billing.manager.OCIBillingAdapter") as mock_oci:
            mock_oci_adapter = Mock()
            type(mock_oci_adapter).provider_name = property(lambda self: "Oracle Cloud")
            mock_oci_adapter.is_available.return_value = True
            mock_oci.return_value = mock_oci_adapter
            
            # Test "oracle" alias
            manager1 = BillingManager(providers=["oracle"])
            assert "Oracle Cloud" in manager1.get_available_providers()
            
            # Test "oci" alias
            manager2 = BillingManager(providers=["oci"])
            assert "Oracle Cloud" in manager2.get_available_providers()

    def test_get_daily_costs_structure(self):
        """Test get_daily_costs returns correct structure."""
        with patch("clint.billing.manager.AWSBillingAdapter") as mock_aws_class:
            mock_aws_adapter = Mock()
            # provider_name is a property, not an attribute
            type(mock_aws_adapter).provider_name = property(lambda self: "AWS")
            mock_aws_adapter.is_available.return_value = True
            mock_aws_adapter.get_daily_costs.return_value = [
                {
                    "date": "2025-01-01",
                    "provider": "AWS",
                    "total_cost": 10.50,
                    "currency": "USD",
                    "services": {"EC2": 10.50},
                },
                {
                    "date": "2025-01-02",
                    "provider": "AWS",
                    "total_cost": 5.25,
                    "currency": "USD",
                    "services": {"S3": 5.25},
                },
            ]
            mock_aws_class.return_value = mock_aws_adapter
            
            manager = BillingManager(providers=["aws"])
            # Manually set the adapter since initialization might not work with mocks
            manager.adapters["AWS"] = mock_aws_adapter
            
            start = datetime(2025, 1, 1)
            end = datetime(2025, 1, 3)
            result = manager.get_daily_costs(start, end)
            
            assert "period" in result
            assert "providers" in result
            assert "daily_totals" in result
            assert "errors" in result
            
            assert "AWS" in result["providers"]
            assert len(result["providers"]["AWS"]) == 2
            
            # Check daily totals aggregation
            assert "2025-01-01" in result["daily_totals"]
            assert "2025-01-02" in result["daily_totals"]
            assert result["daily_totals"]["2025-01-01"]["total"] == 10.50
            assert result["daily_totals"]["2025-01-02"]["total"] == 5.25

    def test_get_daily_costs_multiple_providers(self):
        """Test get_daily_costs aggregates costs from multiple providers."""
        with patch("clint.billing.manager.AWSBillingAdapter") as mock_aws_class, \
             patch("clint.billing.manager.OCIBillingAdapter") as mock_oci_class:
            
            mock_aws_adapter = Mock()
            type(mock_aws_adapter).provider_name = property(lambda self: "AWS")
            mock_aws_adapter.is_available.return_value = True
            mock_aws_adapter.get_daily_costs.return_value = [
                {
                    "date": "2025-01-01",
                    "provider": "AWS",
                    "total_cost": 10.0,
                    "currency": "USD",
                    "services": {},
                }
            ]
            mock_aws_class.return_value = mock_aws_adapter
            
            mock_oci_adapter = Mock()
            type(mock_oci_adapter).provider_name = property(lambda self: "Oracle Cloud")
            mock_oci_adapter.is_available.return_value = True
            mock_oci_adapter.get_daily_costs.return_value = [
                {
                    "date": "2025-01-01",
                    "provider": "Oracle Cloud",
                    "total_cost": 5.0,
                    "currency": "USD",
                    "services": {},
                }
            ]
            mock_oci_class.return_value = mock_oci_adapter
            
            manager = BillingManager(providers=["aws", "oracle"])
            # Manually set the adapters since initialization might not work with mocks
            manager.adapters["AWS"] = mock_aws_adapter
            manager.adapters["Oracle Cloud"] = mock_oci_adapter
            
            start = datetime(2025, 1, 1)
            end = datetime(2025, 1, 2)
            result = manager.get_daily_costs(start, end)
            
            # Check that both providers are included
            assert "AWS" in result["providers"]
            assert "Oracle Cloud" in result["providers"]
            
            # Check that daily totals aggregate across providers
            assert result["daily_totals"]["2025-01-01"]["total"] == 15.0
            assert "AWS" in result["daily_totals"]["2025-01-01"]["by_provider"]
            assert "Oracle Cloud" in result["daily_totals"]["2025-01-01"]["by_provider"]

    def test_get_daily_costs_with_days_parameter(self):
        """Test get_daily_costs convenience parameter."""
        with patch("clint.billing.manager.AWSBillingAdapter") as mock_aws_class:
            mock_aws_adapter = Mock()
            type(mock_aws_adapter).provider_name = property(lambda self: "AWS")
            mock_aws_adapter.is_available.return_value = True
            mock_aws_adapter.get_daily_costs.return_value = []
            mock_aws_class.return_value = mock_aws_adapter
            
            manager = BillingManager(providers=["aws"])
            # Manually set the adapter since initialization might not work with mocks
            manager.adapters["AWS"] = mock_aws_adapter
            
            result = manager.get_daily_costs(days=7)
            
            # Should calculate dates from days parameter
            assert "period" in result
            # Verify adapter was called with calculated dates
            mock_aws_adapter.get_daily_costs.assert_called_once()
            call_args = mock_aws_adapter.get_daily_costs.call_args[0]
            assert isinstance(call_args[0], datetime)
            assert isinstance(call_args[1], datetime)

    def test_get_daily_costs_handles_errors(self):
        """Test get_daily_costs handles adapter errors gracefully."""
        with patch("clint.billing.manager.AWSBillingAdapter") as mock_aws_class:
            mock_aws_adapter = Mock()
            type(mock_aws_adapter).provider_name = property(lambda self: "AWS")
            mock_aws_adapter.is_available.return_value = True
            mock_aws_adapter.get_daily_costs.side_effect = Exception("API Error")
            mock_aws_class.return_value = mock_aws_adapter
            
            manager = BillingManager(providers=["aws"])
            # Manually set the adapter since initialization might not work with mocks
            manager.adapters["AWS"] = mock_aws_adapter
            
            start = datetime(2025, 1, 1)
            end = datetime(2025, 1, 2)
            result = manager.get_daily_costs(start, end)
            
            assert len(result["errors"]) > 0
            assert "AWS" in result["providers"]
            assert result["providers"]["AWS"] == []

    def test_get_monthly_comparison_structure(self):
        """Test get_monthly_comparison returns correct structure."""
        with patch("clint.billing.manager.AWSBillingAdapter") as mock_aws_class:
            mock_aws_adapter = Mock()
            type(mock_aws_adapter).provider_name = property(lambda self: "AWS")
            mock_aws_adapter.is_available.return_value = True
            
            # Mock current month costs
            def mock_get_daily_costs(start, end):
                if start.month == 11:  # Current month
                    return [
                        {
                            "date": "2025-11-01",
                            "provider": "AWS",
                            "total_cost": 10.0,
                            "currency": "USD",
                            "services": {},
                        }
                    ]
                else:  # Previous month
                    return [
                        {
                            "date": "2025-10-01",
                            "provider": "AWS",
                            "total_cost": 5.0,
                            "currency": "USD",
                            "services": {},
                        }
                    ]
            
            mock_aws_adapter.get_daily_costs = Mock(side_effect=mock_get_daily_costs)
            mock_aws_class.return_value = mock_aws_adapter
            
            manager = BillingManager(providers=["aws"])
            result = manager.get_monthly_comparison(2025, 11)
            
            assert "current_month" in result
            assert "previous_month" in result
            assert "comparison" in result
            
            assert result["current_month"]["year"] == 2025
            assert result["current_month"]["month"] == 11
            assert "total_cost" in result["current_month"]
            assert "by_provider" in result["current_month"]
            
            assert result["previous_month"]["year"] == 2025
            assert result["previous_month"]["month"] == 10
            
            assert "total_change" in result["comparison"]
            assert "total_change_percent" in result["comparison"]
            assert "by_provider" in result["comparison"]

    def test_get_monthly_comparison_calculates_changes(self):
        """Test get_monthly_comparison calculates changes correctly."""
        with patch("clint.billing.manager.AWSBillingAdapter") as mock_aws_class:
            mock_aws_adapter = Mock()
            type(mock_aws_adapter).provider_name = property(lambda self: "AWS")
            mock_aws_adapter.is_available.return_value = True
            
            # Mock costs: current month = 100, previous month = 50
            def mock_get_daily_costs(start, end):
                if start.month == 11:  # Current month
                    return [
                        {
                            "date": "2025-11-01",
                            "provider": "AWS",
                            "total_cost": 100.0,
                            "currency": "USD",
                            "services": {},
                        }
                    ]
                else:  # Previous month
                    return [
                        {
                            "date": "2025-10-01",
                            "provider": "AWS",
                            "total_cost": 50.0,
                            "currency": "USD",
                            "services": {},
                        }
                    ]
            
            mock_aws_adapter.get_daily_costs = Mock(side_effect=mock_get_daily_costs)
            mock_aws_class.return_value = mock_aws_adapter
            
            manager = BillingManager(providers=["aws"])
            # Manually set the adapter since initialization might not work with mocks
            manager.adapters["AWS"] = mock_aws_adapter
            
            result = manager.get_monthly_comparison(2025, 11)
            
            assert result["comparison"]["total_change"] == 50.0
            assert result["comparison"]["total_change_percent"] == 100.0  # 50/50 * 100
            
            assert "AWS" in result["comparison"]["by_provider"]
            provider_comp = result["comparison"]["by_provider"]["AWS"]
            assert provider_comp["current"] == 100.0
            assert provider_comp["previous"] == 50.0
            assert provider_comp["change"] == 50.0
            assert provider_comp["change_percent"] == 100.0

    def test_get_monthly_comparison_december(self):
        """Test get_monthly_comparison handles December (year boundary)."""
        with patch("clint.billing.manager.AWSBillingAdapter") as mock_aws_class:
            mock_aws_adapter = Mock()
            type(mock_aws_adapter).provider_name = property(lambda self: "AWS")
            mock_aws_adapter.is_available.return_value = True
            mock_aws_adapter.get_daily_costs.return_value = []
            mock_aws_class.return_value = mock_aws_adapter
            
            manager = BillingManager(providers=["aws"])
            # Manually set the adapter since initialization might not work with mocks
            manager.adapters["AWS"] = mock_aws_adapter
            
            result = manager.get_monthly_comparison(2025, 12)
            
            # December should compare with November
            assert result["current_month"]["month"] == 12
            assert result["previous_month"]["month"] == 11
            assert result["previous_month"]["year"] == 2025

