"""
Basic tests for the AWS infrastructure reporting tool.

These tests verify the sanitization and report generation functionality
without requiring AWS credentials.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import shutil
import tempfile

from report_generator import ReportGenerator
from sanitizer import (
    generate_summary_stats,
    mask_account_id,
    sanitize_arn,
    sanitize_dict,
    sanitize_service_name,
)


def test_mask_account_id():
    """Test account ID masking."""
    assert mask_account_id("123456789012") == "****-****-9012"
    assert mask_account_id("999888777666") == "****-****-7666"
    assert mask_account_id("UNKNOWN") == "UNKNOWN"
    assert mask_account_id("") == "UNKNOWN"
    print("✅ test_mask_account_id passed")


def test_sanitize_arn():
    """Test ARN sanitization."""
    arn = "arn:aws:s3:us-east-1:123456789012:bucket/my-bucket"
    sanitized = sanitize_arn(arn)

    # Should mask account ID
    assert "123456789012" not in sanitized
    assert "****-****-9012" in sanitized

    arn2 = "arn:aws:iam::999888777666:role/MyRole"
    sanitized2 = sanitize_arn(arn2)
    assert "999888777666" not in sanitized2
    assert "****-****-7666" in sanitized2

    print("✅ test_sanitize_arn passed")


def test_sanitize_service_name():
    """Test service name sanitization."""
    # Service names are public, should not be changed
    assert sanitize_service_name("Amazon EC2") == "Amazon EC2"
    assert sanitize_service_name("Amazon S3") == "Amazon S3"
    print("✅ test_sanitize_service_name passed")


def test_generate_summary_stats():
    """Test summary statistics generation."""
    cost_data = [
        {"service": "Amazon EC2", "cost": 100.00},
        {"service": "Amazon S3", "cost": 50.00},
        {"service": "Amazon RDS", "cost": 30.00},
    ]

    summary = generate_summary_stats(cost_data)

    assert summary["total_cost"] == 180.0
    assert summary["service_count"] == 3
    assert len(summary["top_services"]) == 3

    # Check top service
    assert summary["top_services"][0]["service"] == "Amazon EC2"
    assert summary["top_services"][0]["cost"] == 100.0

    # Check percentages
    assert summary["top_services"][0]["percentage"] == 55.6  # 100/180 * 100

    print("✅ test_generate_summary_stats passed")


def test_generate_summary_stats_empty():
    """Test summary statistics with empty data."""
    summary = generate_summary_stats([])

    assert summary["total_cost"] == 0.0
    assert summary["service_count"] == 0
    assert len(summary["top_services"]) == 0

    print("✅ test_generate_summary_stats_empty passed")


def test_sanitize_dict():
    """Test dictionary sanitization."""
    data = {
        "Account": "123456789012",
        "ARN": "arn:aws:s3:us-east-1:123456789012:bucket/test",
        "Service": "Amazon EC2",
        "Cost": 100.50,
        "RequestId": "should-be-removed",
    }

    sanitized = sanitize_dict(data, mask_accounts=True)

    # Account ID should be masked
    assert sanitized["Account"] == "****-****-9012"

    # ARN should be sanitized
    assert "123456789012" not in sanitized["ARN"]

    # Service and cost should be unchanged
    assert sanitized["Service"] == "Amazon EC2"
    assert sanitized["Cost"] == 100.50

    # RequestId should be removed
    assert "RequestId" not in sanitized

    print("✅ test_sanitize_dict passed")


def test_report_generation():
    """Test HTML report generation."""
    # Create temporary directory
    temp_dir = tempfile.mkdtemp()

    try:
        generator = ReportGenerator(output_dir=temp_dir)

        summary = {
            "total_cost": 150.00,
            "service_count": 3,
            "top_services": [
                {"service": "Amazon EC2", "cost": 100.00, "percentage": 66.7},
                {"service": "Amazon S3", "cost": 30.00, "percentage": 20.0},
                {"service": "Amazon RDS", "cost": 20.00, "percentage": 13.3},
            ],
        }

        services = [
            {"service": "Amazon EC2", "cost": 100.00},
            {"service": "Amazon S3", "cost": 30.00},
            {"service": "Amazon RDS", "cost": 20.00},
        ]

        report_path = generator.generate_html_report(
            title="Test Report",
            summary=summary,
            services=services,
            days_back=30,
            account_id="****-****-1234",
        )

        # Check files were created
        assert os.path.exists(report_path)
        assert os.path.exists(os.path.join(temp_dir, "index.html"))

        # Read and verify content
        with open(report_path, "r") as f:
            content = f.read()
            assert "Test Report" in content
            assert "$150.00" in content
            assert "Amazon EC2" in content
            assert "****-****-1234" in content
            assert "Privacy Notice" in content

        print("✅ test_report_generation passed")

    finally:
        # Cleanup
        shutil.rmtree(temp_dir)


def run_all_tests():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("Running AWS Infrastructure Reporting Tool Tests")
    print("=" * 60 + "\n")

    test_mask_account_id()
    test_sanitize_arn()
    test_sanitize_service_name()
    test_generate_summary_stats()
    test_generate_summary_stats_empty()
    test_sanitize_dict()
    test_report_generation()

    print("\n" + "=" * 60)
    print("✅ All tests passed!")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    run_all_tests()
