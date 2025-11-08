"""IBM Cloud billing API client."""
import logging
import os
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import requests
from ibm_cloud_sdk_core import IAMTokenManager
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator

# Initialize logger first
logger = logging.getLogger(__name__)

# Try to import IBM Platform Services SDK
try:
    from ibm_platform_services.usage_reports_v4 import UsageReportsV4
    IBM_SDK_AVAILABLE = True
    logger.info("IBM Platform Services SDK imported successfully")
except ImportError as e:
    IBM_SDK_AVAILABLE = False
    logger.warning(f"ibm-platform-services SDK not available: {e}. Falling back to REST API.")


class IBMBillingClient:
    """Client for retrieving IBM Cloud billing data."""

    def __init__(self, api_key: Optional[str] = None, region: Optional[str] = None):
        """
        Initialize IBM Cloud billing client.

        Args:
            api_key: IBM Cloud API key
            region: IBM Cloud region
        """
        self.api_key = api_key or os.environ.get("IBMCLOUD_API_KEY")
        self.region = region or os.environ.get("IBMCLOUD_REGION", "us-south")

        if not self.api_key:
            raise ValueError("IBM Cloud API key is required")

        # Initialize IAM token manager
        self.token_manager = IAMTokenManager(apikey=self.api_key)
        
        # Initialize IBM Platform Services SDK if available
        self.usage_reports_service = None
        if IBM_SDK_AVAILABLE:
            try:
                authenticator = IAMAuthenticator(apikey=self.api_key)
                self.usage_reports_service = UsageReportsV4(authenticator=authenticator)
                logger.info("Initialized IBM Platform Services UsageReportsV4 SDK")
            except Exception as e:
                logger.warning(f"Failed to initialize IBM Platform Services SDK: {e}")
                self.usage_reports_service = None

    def _get_iam_token(self) -> str:
        """Get IAM access token."""
        try:
            token_response = self.token_manager.get_token()
            return token_response
        except Exception as e:
            logger.error(f"Error getting IAM token: {e}")
            raise

    def get_usage_costs(
        self,
        account_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> List[Dict[str, Any]]:
        """
        Get usage costs from IBM Cloud Usage Metering API.

        Args:
            account_id: IBM Cloud account ID (optional, will try to get from API)
            start_date: Start date for cost query
            end_date: End date for cost query

        Returns:
            List of cost records
        """
        # Try IBM Platform Services SDK first
        if self.usage_reports_service and IBM_SDK_AVAILABLE:
            try:
                logger.info("Attempting to retrieve usage costs using IBM Platform Services SDK")
                return self._get_usage_costs_via_sdk(account_id, start_date, end_date)
            except Exception as e:
                logger.warning(f"IBM Platform Services SDK failed: {e}. Falling back to REST API.")
        
        # Fall back to REST API
        token = self._get_iam_token()

        # Get account ID if not provided
        if not account_id:
            account_id = self._get_account_id(token)

        # Try multiple API endpoints
        endpoints_to_try = []
        
        # Method 1: Try billing units first (most reliable)
        billing_unit_id = self._get_billing_unit_id(token)
        if billing_unit_id:
            endpoints_to_try.append({
                "url": f"https://billing.cloud.ibm.com/v4/billing-units/{billing_unit_id}/usage",
                "method": "billing_unit",
            })
            endpoints_to_try.append({
                "url": f"https://billing.cloud.ibm.com/v4/billing-units/{billing_unit_id}/costs",
                "method": "billing_unit_costs",
            })

        # Method 2: Try with account ID (GUID format)
        if account_id:
            endpoints_to_try.append({
                "url": f"https://billing.cloud.ibm.com/v4/accounts/{account_id}/usage",
                "method": "account_usage",
            })
            endpoints_to_try.append({
                "url": f"https://billing.cloud.ibm.com/v4/accounts/{account_id}/costs",
                "method": "account_costs",
            })

        # Method 3: Try usage metering API without account ID
        endpoints_to_try.append({
            "url": "https://billing.cloud.ibm.com/v4/usage",
            "method": "usage_metering",
        })
        
        # Method 4: Try Enterprise Billing API (if enterprise account)
        if account_id:
            endpoints_to_try.append({
                "url": f"https://enterprise.cloud.ibm.com/v1/accounts/{account_id}/usage",
                "method": "enterprise_usage",
            })
        
        # Method 5: Try Cost Management API
        endpoints_to_try.append({
            "url": "https://cost-management.cloud.ibm.com/v1/cost-reports",
            "method": "cost_reports",
        })
        
        # Method 6: Try Usage Reports API
        if account_id:
            endpoints_to_try.append({
                "url": f"https://billing.cloud.ibm.com/v1/accounts/{account_id}/usage-reports",
                "method": "usage_reports",
            })

        # Try each endpoint
        for endpoint in endpoints_to_try:
            try:
                logger.info(f"Trying endpoint: {endpoint['url']} (method: {endpoint['method']})")
                costs = self._try_get_costs_from_endpoint(
                    endpoint["url"], token, start_date, end_date, endpoint["method"]
                )
                if costs:
                    logger.info(f"Successfully retrieved {len(costs)} cost records using {endpoint['method']}")
                    return costs
            except Exception as e:
                logger.warning(f"Endpoint {endpoint['url']} failed: {e}")
                continue

        logger.warning("All IBM Cloud billing API endpoints failed. Returning empty list.")
        return []

    def _get_billing_unit_id(self, token: str) -> Optional[str]:
        """Get billing unit ID from API."""
        try:
            # Try with account ID parameter
            account_id = self._get_account_id(token)
            
            url = "https://billing.cloud.ibm.com/v1/billing-units"
            headers = {
                "Authorization": f"Bearer {token}",
                "Accept": "application/json",
            }
            
            params = {}
            if account_id:
                params["account_id"] = account_id

            response = requests.get(url, headers=headers, params=params, timeout=30)
            if response.status_code == 200:
                data = response.json()
                if "resources" in data and len(data["resources"]) > 0:
                    billing_unit_id = data["resources"][0].get("id")
                    if billing_unit_id:
                        logger.info(f"Retrieved billing unit ID: {billing_unit_id}")
                        return billing_unit_id
            else:
                logger.debug(f"Billing units API returned {response.status_code}: {response.text[:200]}")

        except Exception as e:
            logger.debug(f"Could not get billing unit ID: {e}")

        return None

    def _try_get_costs_from_endpoint(
        self,
        url: str,
        token: str,
        start_date: Optional[datetime],
        end_date: Optional[datetime],
        method: str,
    ) -> List[Dict[str, Any]]:
        """Try to get costs from a specific endpoint."""
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
        }

        params = {}
        if start_date:
            params["start_time"] = start_date.strftime("%Y-%m-%d")
        if end_date:
            params["end_time"] = end_date.strftime("%Y-%m-%d")

        response = requests.get(url, headers=headers, params=params, timeout=30)
        
        if response.status_code == 404:
            logger.warning(f"Endpoint not found (404): {url}")
            logger.debug(f"Response: {response.text[:500]}")
            return []
        
        if response.status_code != 200:
            logger.warning(f"Endpoint returned {response.status_code}: {url}")
            logger.debug(f"Response: {response.text[:500]}")
            return []
        
        response.raise_for_status()
        data = response.json()
        costs = []

        # Parse different response formats
        if "resources" in data:
            for resource in data["resources"]:
                cost_value = 0.0
                # Try different cost field names
                if "cost" in resource:
                    cost_value = float(resource.get("cost", 0))
                elif "computed_amount" in resource:
                    cost_value = float(resource.get("computed_amount", 0))
                elif "amount" in resource:
                    cost_value = float(resource.get("amount", 0))
                elif "billing_cost" in resource:
                    cost_value = float(resource.get("billing_cost", 0))

                costs.append(
                    {
                        "resource_id": resource.get("resource_id") or resource.get("id"),
                        "resource_name": resource.get("resource_name") or resource.get("name"),
                        "category": resource.get("category") or resource.get("service_name"),
                        "cost": cost_value,
                        "currency": resource.get("currency", "USD"),
                        "usage": resource.get("usage", {}),
                        "start_time": resource.get("start_time") or resource.get("start_date"),
                        "end_time": resource.get("end_time") or resource.get("end_date"),
                        "method": method,
                    }
                )
        elif "costs" in data:
            # Alternative response format
            for cost in data["costs"]:
                costs.append(
                    {
                        "resource_id": cost.get("resource_id"),
                        "resource_name": cost.get("resource_name"),
                        "category": cost.get("category"),
                        "cost": float(cost.get("cost", 0)),
                        "currency": cost.get("currency", "USD"),
                        "usage": cost.get("usage", {}),
                        "start_time": cost.get("start_time"),
                        "end_time": cost.get("end_time"),
                        "method": method,
                    }
                )

        return costs

    def _get_account_id(self, token: str) -> Optional[str]:
        """Get IBM Cloud account ID from API."""
        # Try environment variable first
        account_id = os.environ.get("IBMCLOUD_ACCOUNT_ID")
        if account_id:
            logger.info(f"Using account ID from environment: {account_id}")
            return account_id
        
        # Try Account Management API (most reliable)
        try:
            url = "https://accounts.cloud.ibm.com/v1/accounts"
            headers = {
                "Authorization": f"Bearer {token}",
                "Accept": "application/json",
            }

            response = requests.get(url, headers=headers, timeout=30)
            if response.status_code == 200:
                data = response.json()
                if "resources" in data and len(data["resources"]) > 0:
                    # Get account GUID from metadata
                    account = data["resources"][0]
                    account_guid = account.get("metadata", {}).get("guid")
                    if account_guid:
                        logger.info(f"Retrieved account ID (GUID) from Account Management API: {account_guid}")
                        return account_guid
                    
                    # Also check for linked IMS account ID
                    linked_accounts = account.get("metadata", {}).get("linked_accounts", [])
                    if linked_accounts and len(linked_accounts) > 0:
                        ims_id = linked_accounts[0].get("id")
                        if ims_id:
                            logger.info(f"Retrieved IMS account ID from Account Management API: {ims_id}")
                            return ims_id

        except Exception as e:
            logger.warning(f"Could not get account ID from Account Management API: {e}")
        
        # Try alternative method - get from billing units
        try:
            url = "https://billing.cloud.ibm.com/v1/billing-units"
            headers = {
                "Authorization": f"Bearer {token}",
                "Accept": "application/json",
            }

            response = requests.get(url, headers=headers, timeout=30)
            if response.status_code == 200:
                data = response.json()
                if "resources" in data and len(data["resources"]) > 0:
                    account_id = data["resources"][0].get("account_id")
                    if account_id:
                        logger.info(f"Retrieved account ID from billing units API: {account_id}")
                        return account_id
            else:
                logger.warning(f"Billing units API returned {response.status_code}: {response.text[:200]}")

        except Exception as e2:
            logger.warning(f"Alternative method to get account ID also failed: {e2}")

        logger.warning("Could not determine account ID. Some billing APIs may not work without it.")
        return None

    def _get_usage_costs_via_sdk(
        self,
        account_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> List[Dict[str, Any]]:
        """
        Get usage costs using IBM Platform Services SDK.
        
        Args:
            account_id: IBM Cloud account ID
            start_date: Start date for cost query
            end_date: End date for cost query
            
        Returns:
            List of cost records
        """
        if not self.usage_reports_service:
            raise ValueError("Usage Reports service not initialized")
        
        # Get account ID if not provided
        if not account_id:
            token = self._get_iam_token()
            account_id = self._get_account_id(token)
        
        if not account_id:
            raise ValueError("Account ID is required for SDK usage")
        
        costs = []
        
        try:
            # Prepare date parameters - SDK expects YYYY-MM format
            start_time = start_date.strftime("%Y-%m") if start_date else None
            end_time = end_date.strftime("%Y-%m") if end_date else None
            
            # Get account usage - pass parameters directly
            response = self.usage_reports_service.get_account_usage(
                account_id=account_id,
                billingmonth=start_time if start_time else None,
            )
            
            if response.get_status_code() == 200:
                result = response.get_result()
                
                # Parse response - result is a dictionary
                if isinstance(result, dict) and 'resources' in result:
                    resources = result.get('resources', [])
                    currency = result.get('currency_code', 'USD')
                    
                    for resource in resources:
                        resource_id = resource.get('resource_id', 'Unknown')
                        billable_cost = float(resource.get('billable_cost', 0) or 0)
                        
                        # Extract resource name from resource_id (e.g., 'is.instance' -> 'IBM Cloud Instance')
                        resource_name = resource_id.replace('is.', 'IBM Cloud ').replace('.', ' ').title()
                        
                        costs.append({
                            "resource_id": resource_id,
                            "resource_name": resource_name,
                            "category": resource_id.split('.')[0] if '.' in resource_id else resource_id,
                            "cost": billable_cost,
                            "currency": currency,
                            "usage": resource.get('usage', []),
                            "start_time": result.get('month', start_time),
                            "end_time": result.get('month', end_time),
                            "method": "ibm_sdk",
                        })
                
                logger.info(f"Retrieved {len(costs)} cost records using IBM Platform Services SDK")
                return costs
            else:
                logger.warning(f"IBM Platform Services SDK returned status {response.get_status_code()}")
                return []
                
        except Exception as e:
            logger.error(f"Error using IBM Platform Services SDK: {e}", exc_info=True)
            raise

    def get_instance_costs(
        self,
        start_date: datetime,
        end_date: datetime,
        instance_names: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Get costs for specific compute instances.

        Args:
            start_date: Start date
            end_date: End date
            instance_names: Optional list of instance names to filter

        Returns:
            Dictionary with instance costs
        """
        costs = self.get_usage_costs(start_date=start_date, end_date=end_date)

        # Filter for compute instances
        instance_costs = {}
        total_cost = 0.0

        for cost in costs:
            # Include all costs (not just compute/VSI) since IBM Cloud uses different resource IDs
            # Filter by instance_names if provided, otherwise include all
            instance_name = cost.get("resource_name", "Unknown")
            if instance_names and instance_name not in instance_names:
                continue

            if instance_name not in instance_costs:
                instance_costs[instance_name] = {
                    "total_cost": 0.0,
                    "currency": cost.get("currency", "USD"),
                    "details": [],
                }

            instance_costs[instance_name]["total_cost"] += cost["cost"]
            instance_costs[instance_name]["details"].append(cost)
            total_cost += cost["cost"]

        return {
            "instances": instance_costs,
            "total_cost": total_cost,
            "currency": "USD",
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat(),
            },
        }

    def get_monthly_costs(self, year: int, month: int) -> Dict[str, Any]:
        """
        Get costs for a specific month.

        Args:
            year: Year
            month: Month (1-12)

        Returns:
            Dictionary with monthly costs
        """
        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1)
        else:
            end_date = datetime(year, month + 1, 1)

        return self.get_instance_costs(start_date, end_date)

