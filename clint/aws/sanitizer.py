"""Data sanitization utilities to prevent leaking sensitive information."""
import hashlib
import re
from typing import Any, Dict, List


def mask_account_id(account_id: str) -> str:
    """
    Mask AWS account ID, showing only last 4 digits.

    Args:
        account_id: AWS account ID

    Returns:
        Masked account ID (e.g., "****-****-1234")
    """
    if not account_id or account_id == "UNKNOWN":
        return "UNKNOWN"

    # Keep last 4 digits, mask the rest
    if len(account_id) >= 4:
        return f"****-****-{account_id[-4:]}"
    return "****"


def sanitize_arn(arn: str) -> str:
    """
    Sanitize AWS ARN by masking account ID.

    Args:
        arn: AWS ARN string

    Returns:
        Sanitized ARN with masked account ID
    """
    # ARN format: arn:partition:service:region:account-id:resource
    pattern = r"arn:aws:[^:]+:[^:]*:(\d{12}):"
    return re.sub(pattern, lambda m: f"arn:aws:***:***:{mask_account_id(m.group(1))}:", arn)


def sanitize_service_name(service_name: str) -> str:
    """
    Sanitize service name - keep standard AWS service names as they are public.

    Args:
        service_name: AWS service name

    Returns:
        Sanitized service name
    """
    # AWS service names are not sensitive, return as-is
    return service_name


def sanitize_cost_data(data: Dict[str, Any], mask_accounts: bool = True) -> Dict[str, Any]:
    """
    Sanitize cost and usage data to prevent leaking sensitive information.

    Args:
        data: Cost and usage data from AWS Cost Explorer
        mask_accounts: Whether to mask account IDs

    Returns:
        Sanitized data dictionary
    """
    sanitized = data.copy()

    # Remove or mask potentially sensitive fields
    if "ResponseMetadata" in sanitized:
        # Keep only status code, remove request IDs and other metadata
        sanitized["ResponseMetadata"] = {"HTTPStatusCode": sanitized["ResponseMetadata"].get("HTTPStatusCode", 200)}

    # Process ResultsByTime
    if "ResultsByTime" in sanitized:
        for result in sanitized["ResultsByTime"]:
            # Service names are safe to display
            if "Groups" in result:
                for group in result["Groups"]:
                    # Keep service names as they are public information
                    pass

    return sanitized


def generate_summary_stats(cost_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Generate summary statistics from cost data without sensitive details.

    Args:
        cost_data: List of cost data entries

    Returns:
        Dictionary with summary statistics
    """
    if not cost_data:
        return {"total_cost": 0.0, "service_count": 0, "top_services": []}

    total_cost = sum(item.get("cost", 0) for item in cost_data)
    top_services = cost_data[:5]  # Top 5 services by cost

    return {
        "total_cost": round(total_cost, 2),
        "service_count": len(cost_data),
        "top_services": [
            {
                "service": item["service"],
                "cost": round(item["cost"], 2),
                "percentage": round((item["cost"] / total_cost * 100) if total_cost > 0 else 0, 1),
            }
            for item in top_services
        ],
    }


def sanitize_dict(data: Dict[str, Any], mask_accounts: bool = True) -> Dict[str, Any]:
    """
    Recursively sanitize a dictionary for safe public display.

    Args:
        data: Dictionary to sanitize
        mask_accounts: Whether to mask account IDs

    Returns:
        Sanitized dictionary
    """
    sanitized: Dict[str, Any] = {}

    for key, value in data.items():
        # Skip sensitive keys
        if key in ["RequestId", "HTTPHeaders", "RetryAttempts"]:
            continue

        if isinstance(value, dict):
            sanitized[key] = sanitize_dict(value, mask_accounts)
        elif isinstance(value, list):
            sanitized[key] = [sanitize_dict(item, mask_accounts) if isinstance(item, dict) else item for item in value]
        elif isinstance(value, str) and mask_accounts:
            # Check if value looks like an account ID
            if re.match(r"^\d{12}$", value):
                sanitized[key] = mask_account_id(value)
            # Check if value is an ARN
            elif value.startswith("arn:aws:"):
                sanitized[key] = sanitize_arn(value)
            else:
                sanitized[key] = value
        else:
            sanitized[key] = value

    return sanitized
