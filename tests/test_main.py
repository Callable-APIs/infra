"""Tests for the main module."""

import os
import sys
from unittest.mock import Mock, mock_open, patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import pytest

from src.main import load_config, main


class TestMainModule:
    """Test cases for the main module."""

    def test_load_config_file_exists(self):
        """Test loading configuration from existing file."""
        mock_config = {
            "aws": {"region": "us-west-2"},
            "cost_explorer": {"days_back": 7},
            "report": {"title": "Test Report"},
        }

        with patch("os.path.exists", return_value=True):
            with patch(
                "builtins.open",
                mock_open(
                    read_data="aws:\n  region: us-west-2\ncost_explorer:\n  days_back: 7\nreport:\n  title: Test Report"
                ),
            ):
                with patch("yaml.safe_load", return_value=mock_config):
                    config = load_config("test_config.yaml")

                    assert config["aws"]["region"] == "us-west-2"
                assert config["cost_explorer"]["days_back"] == 7
                assert config["report"]["title"] == "Test Report"

    def test_load_config_file_not_exists(self):
        """Test loading configuration when file doesn't exist."""
        with patch("os.path.exists", return_value=False):
            config = load_config("nonexistent.yaml")

            assert config["aws"]["region"] == "us-east-1"
            assert config["cost_explorer"]["days_back"] == 30
            assert config["report"]["title"] == "AWS Cost and Usage Report"

    def test_load_config_empty_file(self):
        """Test loading configuration from empty file."""
        with patch("os.path.exists", return_value=True):
            with patch("builtins.open", mock_open(read_data="")):
                with patch("yaml.safe_load", return_value=None):
                    config = load_config("empty.yaml")

                    assert config == {}

    @patch("src.main.CostExplorerClient")
    @patch("src.main.ReportGenerator")
    @patch("src.main.load_config")
    def test_main_public_report_success(self, mock_load_config, mock_report_generator, mock_cost_explorer):
        """Test successful public report generation."""
        # Setup mocks
        mock_config = {
            "aws": {"region": "us-east-1"},
            "cost_explorer": {"days_back": 30},
            "report": {
                "title": "Test Report",
                "output_dir": "reports",
                "mask_account_ids": True,
            },
        }
        mock_load_config.return_value = mock_config

        mock_ce_client = Mock()
        mock_ce_client.get_account_id.return_value = "123456789012"
        mock_ce_client.get_services_cost_summary.return_value = [{"service": "Amazon EC2", "cost": 100.0}]
        mock_cost_explorer.return_value = mock_ce_client

        mock_generator = Mock()
        mock_generator.generate_html_report.return_value = "reports/test_report.html"
        mock_report_generator.return_value = mock_generator

        # Mock generate_summary_stats
        with patch("src.main.generate_summary_stats") as mock_generate_summary:
            mock_generate_summary.return_value = {
                "total_cost": 100.0,
                "service_count": 1,
                "top_services": [{"service": "Amazon EC2", "cost": 100.0, "percentage": 100.0}],
            }

            # Mock mask_account_id
            with patch("src.main.mask_account_id", return_value="****-****-9012"):
                # Test with --no-internal flag (default behavior)
                with patch("sys.argv", ["main.py"]):
                    result = main()

                    assert result == 0
                    mock_ce_client.get_services_cost_summary.assert_called_once_with(days_back=30)
                    mock_generator.generate_html_report.assert_called_once()

    @patch("src.main.CostExplorerClient")
    @patch("src.main.InternalReportGenerator")
    @patch("src.main.load_config")
    def test_main_internal_report_success(self, mock_load_config, mock_internal_generator, mock_cost_explorer):
        """Test successful internal report generation."""
        # Setup mocks
        mock_config = {
            "aws": {"region": "us-east-1"},
            "cost_explorer": {"days_back": 30},
            "report": {
                "title": "Test Report",
                "output_dir": "reports",
                "mask_account_ids": True,
            },
        }
        mock_load_config.return_value = mock_config

        mock_ce_client = Mock()
        mock_ce_client.get_account_id.return_value = "123456789012"
        mock_ce_client.get_services_cost_summary.return_value = [{"service": "Amazon EC2", "cost": 100.0}]
        mock_ce_client.get_detailed_cost_breakdown.return_value = [
            {
                "service": "Amazon EC2",
                "resource_id": "i-123456",
                "cost": 50.0,
                "date": "2023-01-01",
            }
        ]
        mock_ce_client.get_cost_by_tag.return_value = [
            {
                "service": "Amazon EC2",
                "tag_key": "Environment",
                "tag_value": "production",
                "cost": 25.0,
            }
        ]
        mock_ce_client.get_billing_cycle_info.return_value = {
            "current_cycle_start": "2023-01-01",
            "current_cycle_days": 15,
            "previous_cycle_start": "2022-12-01",
            "previous_cycle_end": "2022-12-31",
            "previous_cycle_days": 31,
        }
        mock_ce_client.get_billing_cycle_costs.return_value = [{"service": "Amazon EC2", "cost": 200.0}]
        mock_cost_explorer.return_value = mock_ce_client

        mock_generator = Mock()
        mock_generator.generate_detailed_report.return_value = "internal_reports/index.html"
        mock_internal_generator.return_value = mock_generator

        # Mock generate_summary_stats
        with patch("src.main.generate_summary_stats") as mock_generate_summary:
            mock_generate_summary.return_value = {
                "total_cost": 100.0,
                "service_count": 1,
                "top_services": [{"service": "Amazon EC2", "cost": 100.0, "percentage": 100.0}],
            }

            # Test with --internal flag
            with patch("sys.argv", ["main.py", "--internal"]):
                result = main()

                assert result == 0
                mock_ce_client.get_detailed_cost_breakdown.assert_called_once_with(days_back=30)
                mock_ce_client.get_cost_by_tag.assert_called_once_with(days_back=30)
                mock_ce_client.get_billing_cycle_info.assert_called_once()
                mock_generator.generate_detailed_report.assert_called_once()

    @patch("src.main.CostExplorerClient")
    @patch("src.main.InternalReportGenerator")
    @patch("src.main.load_config")
    def test_main_internal_console_only(self, mock_load_config, mock_internal_generator, mock_cost_explorer):
        """Test internal report with console-only output."""
        # Setup mocks
        mock_config = {
            "aws": {"region": "us-east-1"},
            "cost_explorer": {"days_back": 30},
            "report": {
                "title": "Test Report",
                "output_dir": "reports",
                "mask_account_ids": True,
            },
        }
        mock_load_config.return_value = mock_config

        mock_ce_client = Mock()
        mock_ce_client.get_account_id.return_value = "123456789012"
        mock_ce_client.get_services_cost_summary.return_value = []
        mock_ce_client.get_detailed_cost_breakdown.return_value = []
        mock_ce_client.get_cost_by_tag.return_value = []
        mock_ce_client.get_billing_cycle_info.return_value = {
            "current_cycle_start": "2023-01-01",
            "current_cycle_days": 15,
            "previous_cycle_start": "2022-12-01",
            "previous_cycle_end": "2022-12-31",
            "previous_cycle_days": 31,
        }
        mock_ce_client.get_billing_cycle_costs.return_value = []
        mock_cost_explorer.return_value = mock_ce_client

        mock_generator = Mock()
        mock_internal_generator.return_value = mock_generator

        # Mock generate_summary_stats
        with patch("src.main.generate_summary_stats") as mock_generate_summary:
            mock_generate_summary.return_value = {
                "total_cost": 0.0,
                "service_count": 0,
                "top_services": [],
            }

            # Test with --internal --console-only flags
            with patch("sys.argv", ["main.py", "--internal", "--console-only"]):
                result = main()

                assert result == 0
                mock_generator.print_console_summary.assert_called_once()

    @patch("src.main.load_config")
    def test_main_exception_handling(self, mock_load_config):
        """Test exception handling in main function."""
        mock_load_config.side_effect = Exception("Config error")

        with patch("sys.argv", ["main.py"]):
            result = main()

            assert result == 1

    def test_main_with_command_line_args(self):
        """Test main function with command line arguments."""
        with patch("src.main.load_config") as mock_load_config:
            mock_config = {
                "aws": {"region": "us-east-1"},
                "cost_explorer": {"days_back": 30},
                "report": {
                    "title": "Test Report",
                    "output_dir": "reports",
                    "mask_account_ids": True,
                },
            }
            mock_load_config.return_value = mock_config

            with patch("src.main.CostExplorerClient") as mock_ce_class:
                mock_ce_client = Mock()
                mock_ce_client.get_account_id.return_value = "123456789012"
                mock_ce_client.get_services_cost_summary.return_value = []
                mock_ce_class.return_value = mock_ce_client

                with patch("src.main.ReportGenerator") as mock_report_class:
                    mock_generator = Mock()
                    mock_generator.generate_html_report.return_value = "reports/test.html"
                    mock_report_class.return_value = mock_generator

                    with patch("src.main.generate_summary_stats") as mock_generate_summary:
                        mock_generate_summary.return_value = {
                            "total_cost": 0.0,
                            "service_count": 0,
                            "top_services": [],
                        }

                        with patch("main.mask_account_id", return_value="****-****-9012"):
                            # Test with custom arguments
                            with patch(
                                "sys.argv",
                                [
                                    "main.py",
                                    "--days",
                                    "7",
                                    "--output",
                                    "custom_reports",
                                    "--no-mask",
                                ],
                            ):
                                result = main()

                                assert result == 0
                                # Verify config was overridden
                                mock_ce_client.get_services_cost_summary.assert_called_once_with(days_back=7)


if __name__ == "__main__":
    pytest.main([__file__])
