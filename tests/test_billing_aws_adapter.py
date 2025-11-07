"""Tests for AWS billing adapter."""
import pytest
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock

from clint.billing.aws_adapter import AWSBillingAdapter


class TestAWSBillingAdapter:
    """Test cases for AWSBillingAdapter."""

    def test_provider_name(self):
        """Test provider name."""
        adapter = AWSBillingAdapter()
        assert adapter.provider_name == "AWS"

    def test_is_available_without_credentials(self):
        """Test is_available when credentials are missing."""
        adapter = AWSBillingAdapter()
        # Without mocking, should return False if no credentials
        # We'll test with mocked credentials separately
        adapter._initialized = True
        adapter.client = None
        assert adapter.is_available() is False

    def test_is_available_with_credentials(self):
        """Test is_available when credentials are present."""
        adapter = AWSBillingAdapter()
        adapter._initialized = True
        adapter.client = Mock()
        assert adapter.is_available() is True

    @patch("clint.billing.aws_adapter.boto3")
    def test_init_client_success(self, mock_boto3):
        """Test successful client initialization."""
        mock_client = Mock()
        mock_boto3.client.return_value = mock_client
        
        adapter = AWSBillingAdapter()
        adapter._init_client()
        
        assert adapter.client == mock_client
        assert adapter._initialized is True
        mock_boto3.client.assert_called_once_with("ce", region_name="us-east-1")

    @patch("clint.billing.aws_adapter.boto3")
    def test_init_client_no_credentials(self, mock_boto3):
        """Test client initialization without credentials."""
        from botocore.exceptions import NoCredentialsError
        
        mock_boto3.client.side_effect = NoCredentialsError()
        
        adapter = AWSBillingAdapter()
        adapter._init_client()
        
        assert adapter.client is None
        assert adapter._initialized is True

    def test_get_daily_costs_structure(self):
        """Test get_daily_costs returns correct structure."""
        adapter = AWSBillingAdapter()
        adapter.client = Mock()
        adapter._initialized = True
        
        # Mock AWS Cost Explorer API response
        mock_response = {
            "ResultsByTime": [
                {
                    "TimePeriod": {"Start": "2025-01-01", "End": "2025-01-02"},
                    "Total": {
                        "UnblendedCost": {"Amount": "10.50", "Unit": "USD"}
                    },
                    "Groups": [
                        {
                            "Keys": ["Amazon EC2"],
                            "Metrics": {
                                "UnblendedCost": {"Amount": "5.25", "Unit": "USD"}
                            }
                        },
                        {
                            "Keys": ["Amazon S3"],
                            "Metrics": {
                                "UnblendedCost": {"Amount": "5.25", "Unit": "USD"}
                            }
                        }
                    ]
                }
            ]
        }
        
        adapter.client.get_cost_and_usage = Mock(return_value=mock_response)
        
        start = datetime(2025, 1, 1)
        end = datetime(2025, 1, 2)
        result = adapter.get_daily_costs(start, end)
        
        assert isinstance(result, list)
        assert len(result) == 1
        
        cost_record = result[0]
        assert cost_record["date"] == "2025-01-01"
        assert cost_record["provider"] == "AWS"
        assert cost_record["total_cost"] == 10.50
        assert cost_record["currency"] == "USD"
        assert isinstance(cost_record["services"], dict)
        assert "Amazon EC2" in cost_record["services"]
        assert "Amazon S3" in cost_record["services"]
        assert cost_record["services"]["Amazon EC2"] == 5.25
        assert cost_record["services"]["Amazon S3"] == 5.25

    def test_get_daily_costs_blended_cost_fallback(self):
        """Test get_daily_costs falls back to BlendedCost when UnblendedCost not available."""
        adapter = AWSBillingAdapter()
        adapter.client = Mock()
        adapter._initialized = True
        
        # Mock response with only BlendedCost
        mock_response = {
            "ResultsByTime": [
                {
                    "TimePeriod": {"Start": "2025-01-01", "End": "2025-01-02"},
                    "Total": {
                        "BlendedCost": {"Amount": "10.50", "Unit": "USD"}
                    },
                    "Groups": [
                        {
                            "Keys": ["Amazon EC2"],
                            "Metrics": {
                                "BlendedCost": {"Amount": "5.25", "Unit": "USD"}
                            }
                        }
                    ]
                }
            ]
        }
        
        adapter.client.get_cost_and_usage = Mock(return_value=mock_response)
        
        start = datetime(2025, 1, 1)
        end = datetime(2025, 1, 2)
        result = adapter.get_daily_costs(start, end)
        
        assert len(result) == 1
        assert result[0]["total_cost"] == 10.50

    def test_get_daily_costs_no_metrics(self):
        """Test get_daily_costs handles missing metrics gracefully."""
        adapter = AWSBillingAdapter()
        adapter.client = Mock()
        adapter._initialized = True
        
        # Mock response with no cost metrics
        mock_response = {
            "ResultsByTime": [
                {
                    "TimePeriod": {"Start": "2025-01-01", "End": "2025-01-02"},
                    "Total": {},
                    "Groups": []
                }
            ]
        }
        
        adapter.client.get_cost_and_usage = Mock(return_value=mock_response)
        
        start = datetime(2025, 1, 1)
        end = datetime(2025, 1, 2)
        result = adapter.get_daily_costs(start, end)
        
        # Should skip days with no metrics
        assert len(result) == 0

    def test_get_daily_costs_api_error(self):
        """Test get_daily_costs handles API errors gracefully."""
        adapter = AWSBillingAdapter()
        adapter.client = Mock()
        adapter._initialized = True
        
        from botocore.exceptions import ClientError
        
        error_response = {"Error": {"Code": "AccessDenied", "Message": "Access denied"}}
        adapter.client.get_cost_and_usage.side_effect = ClientError(error_response, "GetCostAndUsage")
        
        start = datetime(2025, 1, 1)
        end = datetime(2025, 1, 2)
        result = adapter.get_daily_costs(start, end)
        
        assert result == []

    def test_get_daily_costs_not_available(self):
        """Test get_daily_costs returns empty list when adapter not available."""
        adapter = AWSBillingAdapter()
        adapter.client = None
        adapter._initialized = True
        
        start = datetime(2025, 1, 1)
        end = datetime(2025, 1, 2)
        result = adapter.get_daily_costs(start, end)
        
        assert result == []

