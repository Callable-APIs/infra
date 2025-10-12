"""Tests for the CostExplorerClient module."""

import os
import sys
from unittest.mock import MagicMock, Mock, patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import pytest

from src.cost_explorer import CostExplorerClient


class TestCostExplorerClient:
    """Test cases for CostExplorerClient."""

    def test_init_default_region(self):
        """Test CostExplorerClient initialization with default region."""
        with patch("boto3.Session") as mock_session:
            mock_client = Mock()
            mock_sts_client = Mock()
            mock_session.return_value.client.side_effect = [
                mock_client,
                mock_sts_client,
            ]

            client = CostExplorerClient()

            assert client.client == mock_client
            assert client.sts_client == mock_sts_client
            mock_session.assert_called_once_with(region_name="us-east-1")

    def test_init_custom_region_and_profile(self):
        """Test CostExplorerClient initialization with custom region and profile."""
        with patch("boto3.Session") as mock_session:
            mock_client = Mock()
            mock_sts_client = Mock()
            mock_session.return_value.client.side_effect = [
                mock_client,
                mock_sts_client,
            ]

            client = CostExplorerClient(region="us-west-2", profile="test-profile")

            mock_session.assert_called_once_with(
                region_name="us-west-2", profile_name="test-profile"
            )

    def test_get_account_id_success(self):
        """Test successful account ID retrieval."""
        with patch("boto3.Session") as mock_session:
            mock_client = Mock()
            mock_sts_client = Mock()
            mock_session.return_value.client.side_effect = [
                mock_client,
                mock_sts_client,
            ]

            mock_sts_client.get_caller_identity.return_value = {
                "Account": "123456789012"
            }

            client = CostExplorerClient()
            account_id = client.get_account_id()

            assert account_id == "123456789012"
            mock_sts_client.get_caller_identity.assert_called_once()

    def test_get_account_id_failure(self):
        """Test account ID retrieval failure."""
        with patch("boto3.Session") as mock_session:
            mock_client = Mock()
            mock_sts_client = Mock()
            mock_session.return_value.client.side_effect = [
                mock_client,
                mock_sts_client,
            ]

            mock_sts_client.get_caller_identity.side_effect = Exception("STS error")

            client = CostExplorerClient()
            account_id = client.get_account_id()

            assert account_id == "UNKNOWN"

    def test_get_cost_and_usage_success(self):
        """Test successful cost and usage retrieval."""
        with patch("boto3.Session") as mock_session:
            mock_client = Mock()
            mock_sts_client = Mock()
            mock_session.return_value.client.side_effect = [
                mock_client,
                mock_sts_client,
            ]

            mock_response = {
                "ResultsByTime": [
                    {
                        "TimePeriod": {"Start": "2023-01-01", "End": "2023-01-02"},
                        "Groups": [
                            {
                                "Keys": ["Amazon EC2"],
                                "Metrics": {"UnblendedCost": {"Amount": "100.00"}},
                            }
                        ],
                    }
                ]
            }
            mock_client.get_cost_and_usage.return_value = mock_response

            client = CostExplorerClient()
            result = client.get_cost_and_usage(days_back=1)

            assert "ResultsByTime" in result
            mock_client.get_cost_and_usage.assert_called_once()

    def test_get_cost_and_usage_failure(self):
        """Test cost and usage retrieval failure."""
        with patch("boto3.Session") as mock_session:
            mock_client = Mock()
            mock_sts_client = Mock()
            mock_session.return_value.client.side_effect = [
                mock_client,
                mock_sts_client,
            ]

            mock_client.get_cost_and_usage.side_effect = Exception("API error")

            client = CostExplorerClient()

            with pytest.raises(Exception, match="API error"):
                client.get_cost_and_usage(days_back=1)

    def test_get_services_cost_summary_success(self):
        """Test successful services cost summary retrieval."""
        with patch("boto3.Session") as mock_session:
            mock_client = Mock()
            mock_sts_client = Mock()
            mock_session.return_value.client.side_effect = [
                mock_client,
                mock_sts_client,
            ]

            mock_response = {
                "ResultsByTime": [
                    {
                        "Groups": [
                            {
                                "Keys": ["Amazon EC2"],
                                "Metrics": {"UnblendedCost": {"Amount": "100.00"}},
                            },
                            {
                                "Keys": ["Amazon S3"],
                                "Metrics": {"UnblendedCost": {"Amount": "50.00"}},
                            },
                        ]
                    }
                ]
            }
            mock_client.get_cost_and_usage.return_value = mock_response

            client = CostExplorerClient()
            result = client.get_services_cost_summary(days_back=30)

            assert len(result) == 2
            assert result[0]["service"] == "Amazon EC2"
            assert result[0]["cost"] == 100.0
            assert result[1]["service"] == "Amazon S3"
            assert result[1]["cost"] == 50.0

    def test_get_services_cost_summary_failure(self):
        """Test services cost summary retrieval failure."""
        with patch("boto3.Session") as mock_session:
            mock_client = Mock()
            mock_sts_client = Mock()
            mock_session.return_value.client.side_effect = [
                mock_client,
                mock_sts_client,
            ]

            mock_client.get_cost_and_usage.side_effect = Exception("API error")

            client = CostExplorerClient()
            result = client.get_services_cost_summary(days_back=30)

            assert result == []

    def test_get_detailed_cost_breakdown_success(self):
        """Test successful detailed cost breakdown retrieval."""
        with patch("boto3.Session") as mock_session:
            mock_client = Mock()
            mock_sts_client = Mock()
            mock_session.return_value.client.side_effect = [
                mock_client,
                mock_sts_client,
            ]

            mock_response = {
                "ResultsByTime": [
                    {
                        "TimePeriod": {"Start": "2023-01-01"},
                        "Groups": [
                            {
                                "Keys": ["Amazon EC2", "t3.micro"],
                                "Metrics": {"UnblendedCost": {"Amount": "10.00"}},
                            }
                        ],
                    }
                ]
            }
            mock_client.get_cost_and_usage.return_value = mock_response

            client = CostExplorerClient()
            result = client.get_detailed_cost_breakdown(days_back=1)

            assert len(result) == 1
            assert result[0]["service"] == "Amazon EC2"
            assert result[0]["resource_id"] == "t3.micro"
            assert result[0]["cost"] == 10.0

    def test_get_cost_by_tag_success(self):
        """Test successful cost by tag retrieval."""
        with patch("boto3.Session") as mock_session:
            mock_client = Mock()
            mock_sts_client = Mock()
            mock_session.return_value.client.side_effect = [
                mock_client,
                mock_sts_client,
            ]

            mock_response = {
                "ResultsByTime": [
                    {
                        "Groups": [
                            {
                                "Keys": ["Amazon EC2", "production"],
                                "Metrics": {"UnblendedCost": {"Amount": "75.00"}},
                            }
                        ]
                    }
                ]
            }
            mock_client.get_cost_and_usage.return_value = mock_response

            client = CostExplorerClient()
            result = client.get_cost_by_tag(days_back=30, tag_key="Environment")

            assert len(result) == 1
            assert result[0]["service"] == "Amazon EC2"
            assert result[0]["tag_value"] == "production"
            assert result[0]["cost"] == 75.0

    def test_get_billing_cycle_info(self):
        """Test billing cycle info retrieval."""
        with patch("boto3.Session") as mock_session:
            mock_client = Mock()
            mock_sts_client = Mock()
            mock_session.return_value.client.side_effect = [
                mock_client,
                mock_sts_client,
            ]

            client = CostExplorerClient()
            result = client.get_billing_cycle_info()

            assert "current_cycle_start" in result
            assert "previous_cycle_start" in result
            assert "current_cycle_days" in result
            assert "previous_cycle_days" in result

    def test_get_billing_cycle_costs_success(self):
        """Test successful billing cycle costs retrieval."""
        with patch("boto3.Session") as mock_session:
            mock_client = Mock()
            mock_sts_client = Mock()
            mock_session.return_value.client.side_effect = [
                mock_client,
                mock_sts_client,
            ]

            mock_response = {
                "ResultsByTime": [
                    {
                        "Groups": [
                            {
                                "Keys": ["Amazon EC2"],
                                "Metrics": {"UnblendedCost": {"Amount": "200.00"}},
                            }
                        ]
                    }
                ]
            }
            mock_client.get_cost_and_usage.return_value = mock_response

            client = CostExplorerClient()
            result = client.get_billing_cycle_costs("2023-01-01", "2023-01-31")

            assert len(result) == 1
            assert result[0]["service"] == "Amazon EC2"
            assert result[0]["cost"] == 200.0

    def test_get_billing_cycle_costs_failure(self):
        """Test billing cycle costs retrieval failure."""
        with patch("boto3.Session") as mock_session:
            mock_client = Mock()
            mock_sts_client = Mock()
            mock_session.return_value.client.side_effect = [
                mock_client,
                mock_sts_client,
            ]

            mock_client.get_cost_and_usage.side_effect = Exception("API error")

            client = CostExplorerClient()
            result = client.get_billing_cycle_costs("2023-01-01", "2023-01-31")

            assert result == []

    def test_get_cost_forecast_success(self):
        """Test successful cost forecast retrieval."""
        with patch("boto3.Session") as mock_session:
            mock_client = Mock()
            mock_sts_client = Mock()
            mock_session.return_value.client.side_effect = [
                mock_client,
                mock_sts_client,
            ]

            mock_response = {
                "ForecastResultsByTime": [
                    {
                        "TimePeriod": {"Start": "2023-02-01", "End": "2023-02-28"},
                        "MeanValue": "150.00",
                    }
                ]
            }
            mock_client.get_cost_forecast.return_value = mock_response

            client = CostExplorerClient()
            result = client.get_cost_forecast(days_forward=30)

            assert "ForecastResultsByTime" in result

    def test_get_cost_forecast_failure(self):
        """Test cost forecast retrieval failure."""
        with patch("boto3.Session") as mock_session:
            mock_client = Mock()
            mock_sts_client = Mock()
            mock_session.return_value.client.side_effect = [
                mock_client,
                mock_sts_client,
            ]

            mock_client.get_cost_forecast.side_effect = Exception("API error")

            client = CostExplorerClient()
            result = client.get_cost_forecast(days_forward=30)

            assert result == {}


if __name__ == "__main__":
    pytest.main([__file__])
