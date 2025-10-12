"""Tests for the InternalReportGenerator module."""

import os
import sys
import tempfile
from unittest.mock import patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import pytest

from src.internal_report_generator import InternalReportGenerator


class TestInternalReportGenerator:
    """Test cases for InternalReportGenerator."""

    def test_init_default_output_dir(self):
        """Test InternalReportGenerator initialization with default output directory."""
        with patch("os.makedirs") as mock_makedirs:
            generator = InternalReportGenerator()

            assert generator.output_dir == "internal_reports"
            mock_makedirs.assert_called_once_with("internal_reports", exist_ok=True)

    def test_init_custom_output_dir(self):
        """Test InternalReportGenerator initialization with custom output directory."""
        with patch("os.makedirs") as mock_makedirs:
            generator = InternalReportGenerator("custom_internal_reports")

            assert generator.output_dir == "custom_internal_reports"
            mock_makedirs.assert_called_once_with(
                "custom_internal_reports", exist_ok=True
            )

    def test_generate_detailed_report_success(self):
        """Test successful detailed report generation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            generator = InternalReportGenerator(temp_dir)

            summary = {
                "total_cost": 200.0,
                "service_count": 2,
                "top_services": [
                    {"service": "Amazon EC2", "cost": 150.0, "percentage": 75.0},
                    {"service": "Amazon S3", "cost": 50.0, "percentage": 25.0},
                ],
            }

            detailed_costs = [
                {
                    "service": "Amazon EC2",
                    "resource_id": "i-123456",
                    "cost": 100.0,
                    "date": "2023-01-01",
                },
                {
                    "service": "Amazon EC2",
                    "resource_id": "i-789012",
                    "cost": 50.0,
                    "date": "2023-01-02",
                },
                {
                    "service": "Amazon S3",
                    "resource_id": "storage",
                    "cost": 50.0,
                    "date": "2023-01-01",
                },
            ]

            tag_costs = [
                {
                    "service": "Amazon EC2",
                    "tag_key": "Environment",
                    "tag_value": "production",
                    "cost": 120.0,
                },
                {
                    "service": "Amazon EC2",
                    "tag_key": "Environment",
                    "tag_value": "staging",
                    "cost": 30.0,
                },
            ]

            billing_info = {
                "current_cycle_start": "2023-01-01",
                "current_cycle_days": 15,
                "previous_cycle_start": "2022-12-01",
                "previous_cycle_end": "2022-12-31",
                "previous_cycle_days": 31,
            }

            current_cycle_costs = [
                {"service": "Amazon EC2", "cost": 150.0},
                {"service": "Amazon S3", "cost": 50.0},
            ]

            previous_cycle_costs = [
                {"service": "Amazon EC2", "cost": 100.0},
                {"service": "Amazon S3", "cost": 30.0},
            ]

            with patch("datetime.datetime") as mock_datetime:
                mock_datetime.now.return_value.strftime.return_value = (
                    "2023-01-01 12:00:00 UTC"
                )

                result = generator.generate_detailed_report(
                    title="Internal Test Report",
                    summary=summary,
                    detailed_costs=detailed_costs,
                    tag_costs=tag_costs,
                    days_back=30,
                    account_id="123456789012",
                    billing_info=billing_info,
                    current_cycle_costs=current_cycle_costs,
                    previous_cycle_costs=previous_cycle_costs,
                )

                # Check that file was created
                assert result == os.path.join(temp_dir, "index.html")
                assert os.path.exists(result)

                # Check file content
                with open(result, "r") as f:
                    content = f.read()
                    assert "Internal Test Report" in content
                    assert "$200.00" in content
                    assert "123456789012" in content
                    assert "INTERNAL REPORT" in content
                    assert "Amazon EC2" in content
                    assert "i-123456" in content
                    assert "production" in content

    def test_generate_detailed_report_minimal_data(self):
        """Test detailed report generation with minimal data."""
        with tempfile.TemporaryDirectory() as temp_dir:
            generator = InternalReportGenerator(temp_dir)

            summary = {"total_cost": 0.0, "service_count": 0, "top_services": []}

            with patch("datetime.datetime") as mock_datetime:
                mock_datetime.now.return_value.strftime.return_value = (
                    "2023-01-01 12:00:00 UTC"
                )

                result = generator.generate_detailed_report(
                    title="Empty Report",
                    summary=summary,
                    detailed_costs=[],
                    tag_costs=[],
                    days_back=7,
                    account_id="123456789012",
                )

                # Check that file was created
                assert os.path.exists(result)

                # Check file content
                with open(result, "r") as f:
                    content = f.read()
                    assert "Empty Report" in content
                    assert "$0.00" in content
                    assert "No service data available" in content
                    assert "No detailed cost data available" in content

    def test_print_console_summary(self):
        """Test console summary printing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            generator = InternalReportGenerator(temp_dir)

            summary = {
                "total_cost": 150.0,
                "service_count": 2,
                "top_services": [
                    {"service": "Amazon EC2", "cost": 100.0, "percentage": 66.7},
                    {"service": "Amazon S3", "cost": 50.0, "percentage": 33.3},
                ],
            }

            detailed_costs = [
                {
                    "service": "Amazon EC2",
                    "resource_id": "i-123456",
                    "cost": 75.0,
                    "date": "2023-01-01",
                },
                {
                    "service": "Amazon EC2",
                    "resource_id": "i-789012",
                    "cost": 25.0,
                    "date": "2023-01-02",
                },
                {
                    "service": "Amazon S3",
                    "resource_id": "storage",
                    "cost": 50.0,
                    "date": "2023-01-01",
                },
            ]

            # Test that the method runs without error
            generator.print_console_summary(
                summary=summary,
                detailed_costs=detailed_costs,
                days_back=30,
                account_id="123456789012",
            )

    def test_generate_html_report_billing_comparison(self):
        """Test HTML report generation with billing cycle comparison."""
        with tempfile.TemporaryDirectory() as temp_dir:
            generator = InternalReportGenerator(temp_dir)

            summary = {"total_cost": 100.0, "service_count": 1, "top_services": []}
            detailed_costs = []
            tag_costs = []

            billing_info = {
                "current_cycle_start": "2023-01-01",
                "current_cycle_days": 10,
                "previous_cycle_start": "2022-12-01",
                "previous_cycle_end": "2022-12-31",
                "previous_cycle_days": 31,
            }

            current_cycle_costs = [{"service": "Amazon EC2", "cost": 50.0}]
            previous_cycle_costs = [{"service": "Amazon EC2", "cost": 100.0}]

            with patch("datetime.datetime") as mock_datetime:
                mock_datetime.now.return_value.strftime.return_value = (
                    "2023-01-01 12:00:00 UTC"
                )

                result = generator.generate_detailed_report(
                    title="Billing Test Report",
                    summary=summary,
                    detailed_costs=detailed_costs,
                    tag_costs=tag_costs,
                    days_back=30,
                    account_id="123456789012",
                    billing_info=billing_info,
                    current_cycle_costs=current_cycle_costs,
                    previous_cycle_costs=previous_cycle_costs,
                )

                with open(result, "r") as f:
                    content = f.read()

                    # Check billing cycle information
                    assert "Current Billing Cycle" in content
                    assert "Previous Billing Cycle" in content
                    assert "$50.00" in content  # Current cycle
                    assert "$100.00" in content  # Previous cycle
                    assert "Change:" in content
                    assert "-50.00" in content  # Negative change

    def test_generate_html_report_no_billing_info(self):
        """Test HTML report generation without billing information."""
        with tempfile.TemporaryDirectory() as temp_dir:
            generator = InternalReportGenerator(temp_dir)

            summary = {"total_cost": 50.0, "service_count": 1, "top_services": []}
            detailed_costs = [
                {
                    "service": "Amazon EC2",
                    "resource_id": "i-123",
                    "cost": 50.0,
                    "date": "2023-01-01",
                }
            ]
            tag_costs = []

            with patch("datetime.datetime") as mock_datetime:
                mock_datetime.now.return_value.strftime.return_value = (
                    "2023-01-01 12:00:00 UTC"
                )

                result = generator.generate_detailed_report(
                    title="No Billing Report",
                    summary=summary,
                    detailed_costs=detailed_costs,
                    tag_costs=tag_costs,
                    days_back=30,
                    account_id="123456789012",
                )

                with open(result, "r") as f:
                    content = f.read()

                    # Should still contain the report content
                    assert "No Billing Report" in content
                    assert "$50.00" in content
                    assert "Amazon EC2" in content

    def test_generate_html_report_with_tags(self):
        """Test HTML report generation with tag costs."""
        with tempfile.TemporaryDirectory() as temp_dir:
            generator = InternalReportGenerator(temp_dir)

            summary = {"total_cost": 100.0, "service_count": 1, "top_services": []}
            detailed_costs = []
            tag_costs = [
                {
                    "service": "Amazon EC2",
                    "tag_key": "Environment",
                    "tag_value": "production",
                    "cost": 80.0,
                },
                {
                    "service": "Amazon EC2",
                    "tag_key": "Environment",
                    "tag_value": "staging",
                    "cost": 20.0,
                },
            ]

            with patch("datetime.datetime") as mock_datetime:
                mock_datetime.now.return_value.strftime.return_value = (
                    "2023-01-01 12:00:00 UTC"
                )

                result = generator.generate_detailed_report(
                    title="Tagged Report",
                    summary=summary,
                    detailed_costs=detailed_costs,
                    tag_costs=tag_costs,
                    days_back=30,
                    account_id="123456789012",
                )

                with open(result, "r") as f:
                    content = f.read()

                    # Check tag information
                    assert "Cost by Tags" in content
                    assert "production" in content
                    assert "staging" in content
                    assert "$80.00" in content
                    assert "$20.00" in content

    def test_generate_html_report_no_tags(self):
        """Test HTML report generation without tag costs."""
        with tempfile.TemporaryDirectory() as temp_dir:
            generator = InternalReportGenerator(temp_dir)

            summary = {"total_cost": 50.0, "service_count": 1, "top_services": []}
            detailed_costs = []
            tag_costs = []

            with patch("datetime.datetime") as mock_datetime:
                mock_datetime.now.return_value.strftime.return_value = (
                    "2023-01-01 12:00:00 UTC"
                )

                result = generator.generate_detailed_report(
                    title="No Tags Report",
                    summary=summary,
                    detailed_costs=detailed_costs,
                    tag_costs=tag_costs,
                    days_back=30,
                    account_id="123456789012",
                )

                with open(result, "r") as f:
                    content = f.read()

                    # Should not contain tag section
                    assert "Cost by Tags" not in content


if __name__ == "__main__":
    pytest.main([__file__])
