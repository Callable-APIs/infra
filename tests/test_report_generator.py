"""Tests for the ReportGenerator module."""

import os
import shutil
import sys
import tempfile
from unittest.mock import patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import pytest

from src.report_generator import ReportGenerator


class TestReportGenerator:
    """Test cases for ReportGenerator."""

    def test_init_default_output_dir(self):
        """Test ReportGenerator initialization with default output directory."""
        with patch("os.makedirs") as mock_makedirs:
            generator = ReportGenerator()

            assert generator.output_dir == "reports"
            mock_makedirs.assert_called_once_with("reports", exist_ok=True)

    def test_init_custom_output_dir(self):
        """Test ReportGenerator initialization with custom output directory."""
        with patch("os.makedirs") as mock_makedirs:
            generator = ReportGenerator("custom_reports")

            assert generator.output_dir == "custom_reports"
            mock_makedirs.assert_called_once_with("custom_reports", exist_ok=True)

    def test_generate_html_report_success(self):
        """Test successful HTML report generation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            generator = ReportGenerator(temp_dir)

            summary = {
                "total_cost": 150.0,
                "service_count": 3,
                "top_services": [
                    {"service": "Amazon EC2", "cost": 100.0, "percentage": 66.7},
                    {"service": "Amazon S3", "cost": 30.0, "percentage": 20.0},
                    {"service": "Amazon RDS", "cost": 20.0, "percentage": 13.3},
                ],
            }

            services = [
                {"service": "Amazon EC2", "cost": 100.0},
                {"service": "Amazon S3", "cost": 30.0},
                {"service": "Amazon RDS", "cost": 20.0},
            ]

            with patch("src.report_generator.datetime") as mock_datetime:
                mock_datetime.now.return_value.strftime.side_effect = [
                    "2023-01-01 12:00:00 UTC",  # For generated_at
                    "20230101_120000",  # For filename timestamp
                ]

                result = generator.generate_html_report(
                    title="Test Report",
                    summary=summary,
                    services=services,
                    days_back=30,
                    account_id="****-****-1234",
                )

                # Check that files were created
                assert os.path.exists(result)

                # Check file content
                with open(result, "r") as f:
                    content = f.read()
                    assert "Test Report" in content
                    assert "$150.00" in content
                    assert "Amazon EC2" in content
                    assert "****-****-1234" in content
                    assert "Privacy Notice" in content

    def test_generate_html_report_no_services(self):
        """Test HTML report generation with no services."""
        with tempfile.TemporaryDirectory() as temp_dir:
            generator = ReportGenerator(temp_dir)

            summary = {"total_cost": 0.0, "service_count": 0, "top_services": []}

            with patch("src.report_generator.datetime") as mock_datetime:
                mock_datetime.now.return_value.strftime.side_effect = [
                    "2023-01-01 12:00:00 UTC",
                    "20230101_120000",
                ]

                result = generator.generate_html_report(
                    title="Empty Report",
                    summary=summary,
                    services=[],
                    days_back=7,
                    account_id=None,
                )

                # Check that files were created
                assert os.path.exists(result)

                # Check file content
                with open(result, "r") as f:
                    content = f.read()
                    assert "Empty Report" in content
                    assert "$0.00" in content
                    # Template doesn't show "No service data available" when services list is empty
                    # It just omits the services section entirely

    def test_generate_html_report_without_account_id(self):
        """Test HTML report generation without account ID."""
        with tempfile.TemporaryDirectory() as temp_dir:
            generator = ReportGenerator(temp_dir)

            summary = {
                "total_cost": 50.0,
                "service_count": 1,
                "top_services": [{"service": "Amazon EC2", "cost": 50.0, "percentage": 100.0}],
            }

            with patch("src.report_generator.datetime") as mock_datetime:
                mock_datetime.now.return_value.strftime.side_effect = [
                    "2023-01-01 12:00:00 UTC",
                    "20230101_120000",
                ]

                result = generator.generate_html_report(
                    title="Test Report",
                    summary=summary,
                    services=[{"service": "Amazon EC2", "cost": 50.0}],
                    days_back=14,
                    account_id=None,
                )

                # Check file content doesn't include account ID
                with open(result, "r") as f:
                    content = f.read()
                    assert "Account:" not in content

    def test_generate_html_report_creates_timestamped_file(self):
        """Test that generate_html_report creates timestamped file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            generator = ReportGenerator(temp_dir)

            summary = {
                "total_cost": 100.0,
                "service_count": 1,
                "top_services": [{"service": "Amazon EC2", "cost": 100.0, "percentage": 100.0}],
            }

            with patch("src.report_generator.datetime") as mock_datetime:
                mock_datetime.now.return_value.strftime.side_effect = [
                    "2023-01-01 12:00:00 UTC",
                    "20230101_120000",
                ]

                result = generator.generate_html_report(
                    title="Test Report",
                    summary=summary,
                    services=[{"service": "Amazon EC2", "cost": 100.0}],
                    days_back=30,
                    account_id="****-****-1234",
                )

                # Check that timestamped file exists
                timestamped_file = os.path.join(temp_dir, "aws_cost_report_20230101_120000.html")
                assert os.path.exists(timestamped_file)
                assert result == timestamped_file

                # Check file content
                with open(timestamped_file, "r") as f:
                    content = f.read()
                    assert "Test Report" in content
                    assert "Amazon EC2" in content

    def test_generate_html_report_template_rendering(self):
        """Test that Jinja2 template is properly rendered."""
        with tempfile.TemporaryDirectory() as temp_dir:
            generator = ReportGenerator(temp_dir)

            summary = {
                "total_cost": 75.5,
                "service_count": 2,
                "top_services": [
                    {"service": "Amazon EC2", "cost": 50.0, "percentage": 66.2},
                    {"service": "Amazon S3", "cost": 25.5, "percentage": 33.8},
                ],
            }

            services = [
                {"service": "Amazon EC2", "cost": 50.0},
                {"service": "Amazon S3", "cost": 25.5},
            ]

            with patch("src.report_generator.datetime") as mock_datetime:
                mock_datetime.now.return_value.strftime.side_effect = [
                    "2023-01-01 12:00:00 UTC",
                    "20230101_120000",
                ]

                result = generator.generate_html_report(
                    title="Template Test Report",
                    summary=summary,
                    services=services,
                    days_back=30,
                    account_id="****-****-5678",
                )

                with open(result, "r") as f:
                    content = f.read()

                    # Check template variables are rendered
                    assert "Template Test Report" in content
                    assert "2023-01-01 12:00:00 UTC" in content
                    assert "Last 30 days" in content
                    assert "****-****-5678" in content

                    # Check summary data
                    assert "$75.50" in content
                    assert "2" in content  # service_count

                    # Check service data
                    assert "Amazon EC2" in content
                    assert "Amazon S3" in content
                    assert "$50.00" in content
                    assert "$25.50" in content

                    # Check percentages
                    assert "66.2%" in content
                    assert "33.8%" in content

    def test_generate_html_report_file_naming(self):
        """Test that generated files have correct naming pattern."""
        with tempfile.TemporaryDirectory() as temp_dir:
            generator = ReportGenerator(temp_dir)

            summary = {"total_cost": 0.0, "service_count": 0, "top_services": []}

            with patch("src.report_generator.datetime") as mock_datetime:
                mock_datetime.now.return_value.strftime.side_effect = [
                    "2023-01-01 12:00:00 UTC",
                    "20230101_120000",
                ]

                result = generator.generate_html_report(
                    title="Test Report",
                    summary=summary,
                    services=[],
                    days_back=30,
                    account_id=None,
                )

                # Check filename pattern
                expected_filename = "aws_cost_report_20230101_120000.html"
                assert result.endswith(expected_filename)

                # Check that file exists
                assert os.path.exists(result)


if __name__ == "__main__":
    pytest.main([__file__])
