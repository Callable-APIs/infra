"""
Multi-Cloud Cost Explorer
Supports AWS, Google Cloud, Oracle Cloud, and IBM Cloud cost analysis
"""

import boto3
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import os

logger = logging.getLogger(__name__)

class MultiCloudCostExplorer:
    """Cost explorer for multiple cloud providers"""
    
    def __init__(self):
        self.aws_client = None
        self.google_client = None
        self.oracle_client = None
        self.ibm_client = None
        
    def _get_aws_client(self):
        """Initialize AWS Cost Explorer client"""
        if not self.aws_client:
            self.aws_client = boto3.client('ce', region_name='us-east-1')
        return self.aws_client
    
    def get_aws_costs(self, start_date: str, end_date: str) -> Dict[str, Any]:
        """Get AWS costs for the specified period"""
        try:
            client = self._get_aws_client()
            
            response = client.get_cost_and_usage(
                TimePeriod={
                    'Start': start_date,
                    'End': end_date
                },
                Granularity='DAILY',
                Metrics=['BlendedCost'],
                GroupBy=[
                    {'Type': 'DIMENSION', 'Key': 'SERVICE'}
                ]
            )
            
            return {
                'provider': 'AWS',
                'costs': response['ResultsByTime'],
                'total_cost': sum(
                    float(day['Total']['BlendedCost']['Amount'])
                    for day in response['ResultsByTime']
                )
            }
        except Exception as e:
            logger.error(f"Error getting AWS costs: {e}")
            return {'provider': 'AWS', 'costs': [], 'total_cost': 0.0, 'error': str(e)}
    
    def get_google_costs(self, start_date: str, end_date: str) -> Dict[str, Any]:
        """Get Google Cloud costs for the specified period"""
        try:
            # Note: This would require Google Cloud Billing API setup
            # For now, return estimated costs based on free tier usage
            return {
                'provider': 'Google Cloud',
                'costs': [{
                    'TimePeriod': {'Start': start_date, 'End': end_date},
                    'Total': {'BlendedCost': {'Amount': '0.00', 'Unit': 'USD'}},
                    'Groups': [
                        {
                            'Keys': ['Compute Engine'],
                            'Metrics': {'BlendedCost': {'Amount': '0.00', 'Unit': 'USD'}}
                        }
                    ]
                }],
                'total_cost': 0.0,
                'note': 'Free tier - e2-micro instance'
            }
        except Exception as e:
            logger.error(f"Error getting Google Cloud costs: {e}")
            return {'provider': 'Google Cloud', 'costs': [], 'total_cost': 0.0, 'error': str(e)}
    
    def get_oracle_costs(self, start_date: str, end_date: str) -> Dict[str, Any]:
        """Get Oracle Cloud costs for the specified period"""
        try:
            # Note: This would require Oracle Cloud Billing API setup
            # For now, return estimated costs based on free tier usage
            return {
                'provider': 'Oracle Cloud',
                'costs': [{
                    'TimePeriod': {'Start': start_date, 'End': end_date},
                    'Total': {'BlendedCost': {'Amount': '0.00', 'Unit': 'USD'}},
                    'Groups': [
                        {
                            'Keys': ['Compute'],
                            'Metrics': {'BlendedCost': {'Amount': '0.00', 'Unit': 'USD'}}
                        }
                    ]
                }],
                'total_cost': 0.0,
                'note': 'Free tier - 1x VM.Standard.E5.Flex (1 OCPU, 12GB RAM) - node1 deployed'
            }
        except Exception as e:
            logger.error(f"Error getting Oracle Cloud costs: {e}")
            return {'provider': 'Oracle Cloud', 'costs': [], 'total_cost': 0.0, 'error': str(e)}
    
    def get_ibm_costs(self, start_date: str, end_date: str) -> Dict[str, Any]:
        """Get IBM Cloud costs for the specified period"""
        try:
            # Note: This would require IBM Cloud Billing API setup
            # For now, return estimated costs based on free tier usage
            return {
                'provider': 'IBM Cloud',
                'costs': [{
                    'TimePeriod': {'Start': start_date, 'End': end_date},
                    'Total': {'BlendedCost': {'Amount': '0.00', 'Unit': 'USD'}},
                    'Groups': [
                        {
                            'Keys': ['Virtual Servers'],
                            'Metrics': {'BlendedCost': {'Amount': '0.00', 'Unit': 'USD'}}
                        }
                    ]
                }],
                'total_cost': 0.0,
                'note': 'Free tier - VSI instance'
            }
        except Exception as e:
            logger.error(f"Error getting IBM Cloud costs: {e}")
            return {'provider': 'IBM Cloud', 'costs': [], 'total_cost': 0.0, 'error': str(e)}
    
    def get_all_costs(self, days_back: int = 30) -> Dict[str, Any]:
        """Get costs from all cloud providers"""
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
        
        logger.info(f"Getting multi-cloud costs from {start_date} to {end_date}")
        
        # Get costs from all providers
        aws_costs = self.get_aws_costs(start_date, end_date)
        google_costs = self.get_google_costs(start_date, end_date)
        oracle_costs = self.get_oracle_costs(start_date, end_date)
        ibm_costs = self.get_ibm_costs(start_date, end_date)
        
        # Calculate total costs
        total_cost = (
            aws_costs.get('total_cost', 0) +
            google_costs.get('total_cost', 0) +
            oracle_costs.get('total_cost', 0) +
            ibm_costs.get('total_cost', 0)
        )
        
        return {
            'period': {
                'start': start_date,
                'end': end_date,
                'days': days_back
            },
            'providers': {
                'aws': aws_costs,
                'google': google_costs,
                'oracle': oracle_costs,
                'ibm': ibm_costs
            },
            'total_cost': total_cost,
            'generated_at': datetime.now().isoformat()
        }
    
    def generate_multicloud_summary(self, days_back: int = 30) -> str:
        """Generate a summary of multi-cloud costs"""
        costs_data = self.get_all_costs(days_back)
        
        summary = f"""
MULTI-CLOUD COST ANALYSIS
========================
Period: {costs_data['period']['start']} to {costs_data['period']['end']} ({costs_data['period']['days']} days)
Total Cost: ${costs_data['total_cost']:.2f}

PROVIDER BREAKDOWN:
------------------
"""
        
        for provider, data in costs_data['providers'].items():
            provider_name = data['provider']
            cost = data.get('total_cost', 0)
            note = data.get('note', '')
            
            summary += f"{provider_name}: ${cost:.2f}"
            if note:
                summary += f" ({note})"
            summary += "\n"
            
            # Add error if present
            if 'error' in data:
                summary += f"  Error: {data['error']}\n"
        
        summary += f"""
FREE TIER RESOURCES:
-------------------
- Oracle Cloud: 1x VM.Standard.E5.Flex (1 OCPU, 12GB RAM) - node1.callableapis.com
- Google Cloud: 1x e2-micro (1 vCPU, 1GB RAM) - pending billing setup
- IBM Cloud: 1x VSI instance - pending deployment
- AWS: 1x t4g.micro (free tier eligible) - callableapis-java-env

Generated: {costs_data['generated_at']}
"""
        
        return summary

