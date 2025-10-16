#!/usr/bin/env python3
"""
Cursor Agent for Multi-Cloud Infrastructure Management
Runs on cron to manage and monitor multi-cloud resources
"""

import os
import sys
import json
import logging
import subprocess
import yaml
from datetime import datetime
from pathlib import Path

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent / "src"))

from multicloud_cost_explorer import MultiCloudCostExplorer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/cursor-agent.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class CursorAgent:
    """Cursor agent for multi-cloud management"""
    
    def __init__(self, config_path: str = "/home/cursor-agent/.cursor/config.yaml"):
        self.config_path = config_path
        self.config = self.load_config()
        self.cost_explorer = MultiCloudCostExplorer()
        
    def load_config(self) -> dict:
        """Load configuration from YAML file"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    return yaml.safe_load(f)
            else:
                # Create default config
                default_config = {
                    'providers': {
                        'aws': {'enabled': True, 'region': 'us-west-2'},
                        'google': {'enabled': True, 'region': 'us-central1'},
                        'oracle': {'enabled': True, 'region': 'us-ashburn-1'},
                        'ibm': {'enabled': True, 'region': 'us-south'}
                    },
                    'monitoring': {
                        'cost_check_interval': 24,  # hours
                        'health_check_interval': 1,  # hours
                        'log_retention_days': 30
                    },
                    'notifications': {
                        'enabled': False,
                        'webhook_url': None
                    }
                }
                self.save_config(default_config)
                return default_config
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            return {}
    
    def save_config(self, config: dict):
        """Save configuration to YAML file"""
        try:
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            with open(self.config_path, 'w') as f:
                yaml.dump(config, f, default_flow_style=False)
        except Exception as e:
            logger.error(f"Error saving config: {e}")
    
    def check_instance_health(self, hostname: str, provider: str) -> dict:
        """Check health of a specific instance"""
        try:
            # SSH to instance and check basic health
            cmd = [
                'ssh', '-o', 'ConnectTimeout=10', '-o', 'StrictHostKeyChecking=no',
                hostname, 'uptime'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                return {
                    'hostname': hostname,
                    'provider': provider,
                    'status': 'healthy',
                    'uptime': result.stdout.strip(),
                    'checked_at': datetime.now().isoformat()
                }
            else:
                return {
                    'hostname': hostname,
                    'provider': provider,
                    'status': 'unhealthy',
                    'error': result.stderr.strip(),
                    'checked_at': datetime.now().isoformat()
                }
        except subprocess.TimeoutExpired:
            return {
                'hostname': hostname,
                'provider': provider,
                'status': 'timeout',
                'error': 'SSH connection timeout',
                'checked_at': datetime.now().isoformat()
            }
        except Exception as e:
            return {
                'hostname': hostname,
                'provider': provider,
                'status': 'error',
                'error': str(e),
                'checked_at': datetime.now().isoformat()
            }
    
    def check_all_instances(self) -> list:
        """Check health of all instances"""
        instances = [
            {'hostname': 'oracle-arm-1', 'provider': 'Oracle Cloud'},
            {'hostname': 'oracle-arm-2', 'provider': 'Oracle Cloud'},
            {'hostname': 'google-e2-micro', 'provider': 'Google Cloud'},
            {'hostname': 'ibm-vsi', 'provider': 'IBM Cloud'},
            {'hostname': 'aws-eb', 'provider': 'AWS'}
        ]
        
        health_checks = []
        for instance in instances:
            if self.config.get('providers', {}).get(instance['provider'].lower().replace(' ', '_'), {}).get('enabled', True):
                health = self.check_instance_health(instance['hostname'], instance['provider'])
                health_checks.append(health)
                logger.info(f"Health check for {instance['hostname']}: {health['status']}")
        
        return health_checks
    
    def generate_cost_report(self) -> str:
        """Generate multi-cloud cost report"""
        try:
            summary = self.cost_explorer.generate_multicloud_summary(30)
            logger.info("Generated multi-cloud cost report")
            return summary
        except Exception as e:
            logger.error(f"Error generating cost report: {e}")
            return f"Error generating cost report: {e}"
    
    def update_dns_records(self):
        """Update Cloudflare DNS records with current instance IPs"""
        try:
            # This would integrate with Cloudflare API to update DNS records
            # For now, just log the action
            logger.info("DNS update check - would update Cloudflare records here")
        except Exception as e:
            logger.error(f"Error updating DNS records: {e}")
    
    def cleanup_logs(self):
        """Clean up old log files"""
        try:
            log_dir = Path('/var/log/cursor-agent')
            if log_dir.exists():
                cutoff_date = datetime.now().timestamp() - (self.config.get('monitoring', {}).get('log_retention_days', 30) * 24 * 3600)
                
                for log_file in log_dir.glob('*.log*'):
                    if log_file.stat().st_mtime < cutoff_date:
                        log_file.unlink()
                        logger.info(f"Cleaned up old log file: {log_file}")
        except Exception as e:
            logger.error(f"Error cleaning up logs: {e}")
    
    def run_health_checks(self):
        """Run health checks on all instances"""
        logger.info("Starting health checks...")
        health_checks = self.check_all_instances()
        
        # Save health check results
        health_file = Path('/var/log/cursor-agent/health_checks.json')
        health_file.parent.mkdir(exist_ok=True)
        
        with open(health_file, 'w') as f:
            json.dump(health_checks, f, indent=2)
        
        # Check for unhealthy instances
        unhealthy = [h for h in health_checks if h['status'] != 'healthy']
        if unhealthy:
            logger.warning(f"Found {len(unhealthy)} unhealthy instances")
            for instance in unhealthy:
                logger.warning(f"Unhealthy: {instance['hostname']} ({instance['provider']}) - {instance.get('error', 'Unknown error')}")
        
        logger.info(f"Health checks completed. {len(health_checks)} instances checked.")
    
    def run_cost_analysis(self):
        """Run cost analysis across all providers"""
        logger.info("Starting cost analysis...")
        try:
            cost_report = self.generate_cost_report()
            
            # Save cost report
            cost_file = Path('/var/log/cursor-agent/cost_report.txt')
            cost_file.parent.mkdir(exist_ok=True)
            
            with open(cost_file, 'w') as f:
                f.write(cost_report)
            
            logger.info("Cost analysis completed")
        except Exception as e:
            logger.error(f"Error in cost analysis: {e}")
    
    def run_maintenance(self):
        """Run maintenance tasks"""
        logger.info("Starting maintenance tasks...")
        
        # Clean up old logs
        self.cleanup_logs()
        
        # Update DNS records
        self.update_dns_records()
        
        logger.info("Maintenance tasks completed")
    
    def run(self, task: str = 'all'):
        """Run the cursor agent with specified task"""
        logger.info(f"Cursor Agent starting - Task: {task}")
        
        try:
            if task in ['all', 'health']:
                self.run_health_checks()
            
            if task in ['all', 'cost']:
                self.run_cost_analysis()
            
            if task in ['all', 'maintenance']:
                self.run_maintenance()
            
            logger.info("Cursor Agent completed successfully")
        except Exception as e:
            logger.error(f"Cursor Agent error: {e}")
            sys.exit(1)

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Cursor Agent for Multi-Cloud Management')
    parser.add_argument('--task', choices=['all', 'health', 'cost', 'maintenance'], 
                       default='all', help='Task to run')
    parser.add_argument('--config', default='/home/cursor-agent/.cursor/config.yaml',
                       help='Configuration file path')
    
    args = parser.parse_args()
    
    agent = CursorAgent(args.config)
    agent.run(args.task)

if __name__ == '__main__':
    main()

