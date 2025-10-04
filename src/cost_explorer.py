"""AWS Cost Explorer client wrapper."""
import boto3
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class CostExplorerClient:
    """Client for interacting with AWS Cost Explorer API."""
    
    def __init__(self, region: str = 'us-east-1', profile: Optional[str] = None):
        """
        Initialize Cost Explorer client.
        
        Args:
            region: AWS region (Cost Explorer data is in us-east-1)
            profile: AWS profile name (optional)
        """
        session_kwargs = {'region_name': region}
        if profile:
            session_kwargs['profile_name'] = profile
            
        session = boto3.Session(**session_kwargs)
        self.client = session.client('ce')
        self.sts_client = session.client('sts')
        
    def get_account_id(self) -> str:
        """Get the AWS account ID."""
        try:
            identity = self.sts_client.get_caller_identity()
            return identity['Account']
        except Exception as e:
            logger.warning(f"Could not retrieve account ID: {e}")
            return "UNKNOWN"
    
    def get_cost_and_usage(
        self,
        days_back: int = 30,
        granularity: str = 'DAILY',
        metrics: List[str] = None
    ) -> Dict:
        """
        Retrieve cost and usage data from AWS Cost Explorer.
        
        Args:
            days_back: Number of days to look back
            granularity: DAILY, MONTHLY, or HOURLY
            metrics: List of metrics to retrieve (default: UnblendedCost, UsageQuantity)
            
        Returns:
            Dictionary containing cost and usage data
        """
        if metrics is None:
            metrics = ['UnblendedCost', 'UsageQuantity']
            
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days_back)
        
        try:
            response = self.client.get_cost_and_usage(
                TimePeriod={
                    'Start': start_date.strftime('%Y-%m-%d'),
                    'End': end_date.strftime('%Y-%m-%d')
                },
                Granularity=granularity,
                Metrics=metrics,
                GroupBy=[
                    {
                        'Type': 'DIMENSION',
                        'Key': 'SERVICE'
                    }
                ]
            )
            return response
        except Exception as e:
            logger.error(f"Error retrieving cost data: {e}")
            raise
    
    def get_cost_forecast(self, days_forward: int = 30) -> Dict:
        """
        Get cost forecast for the specified number of days.
        
        Args:
            days_forward: Number of days to forecast
            
        Returns:
            Dictionary containing forecast data
        """
        start_date = datetime.now().date()
        end_date = start_date + timedelta(days=days_forward)
        
        try:
            response = self.client.get_cost_forecast(
                TimePeriod={
                    'Start': start_date.strftime('%Y-%m-%d'),
                    'End': end_date.strftime('%Y-%m-%d')
                },
                Metric='UNBLENDED_COST',
                Granularity='MONTHLY'
            )
            return response
        except Exception as e:
            logger.error(f"Error retrieving cost forecast: {e}")
            return {}
    
    def get_services_cost_summary(self, days_back: int = 30) -> List[Dict]:
        """
        Get cost summary grouped by service.
        
        Args:
            days_back: Number of days to look back
            
        Returns:
            List of dictionaries with service name and cost
        """
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days_back)
        
        try:
            response = self.client.get_cost_and_usage(
                TimePeriod={
                    'Start': start_date.strftime('%Y-%m-%d'),
                    'End': end_date.strftime('%Y-%m-%d')
                },
                Granularity='MONTHLY',
                Metrics=['UnblendedCost'],
                GroupBy=[
                    {
                        'Type': 'DIMENSION',
                        'Key': 'SERVICE'
                    }
                ]
            )
            
            services = []
            for result in response.get('ResultsByTime', []):
                for group in result.get('Groups', []):
                    service_name = group['Keys'][0]
                    cost = float(group['Metrics']['UnblendedCost']['Amount'])
                    services.append({
                        'service': service_name,
                        'cost': cost
                    })
            
            # Aggregate costs by service
            service_totals = {}
            for item in services:
                service = item['service']
                cost = item['cost']
                if service in service_totals:
                    service_totals[service] += cost
                else:
                    service_totals[service] = cost
            
            # Convert to list and sort by cost
            result = [
                {'service': service, 'cost': cost}
                for service, cost in service_totals.items()
            ]
            result.sort(key=lambda x: x['cost'], reverse=True)
            
            return result
        except Exception as e:
            logger.error(f"Error retrieving services cost summary: {e}")
            return []
