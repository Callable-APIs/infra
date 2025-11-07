"""
Infrastructure monitoring and management agent.

Provides automated health checks, cost analysis, and maintenance tasks
for multi-cloud infrastructure.
"""
import os
import json
import logging
import subprocess
import yaml
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class InfrastructureAgent:
    """
    Infrastructure monitoring and management agent.
    
    Provides automated health checks, cost analysis, and maintenance tasks
    for multi-cloud infrastructure.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the infrastructure agent.
        
        Args:
            config_path: Path to configuration YAML file. If None, uses default location.
        """
        if config_path is None:
            # Default to user's home directory or current directory
            home = Path.home()
            config_path = str(home / ".cursor" / "config.yaml")
            # Fallback to current directory if home config doesn't exist
            if not os.path.exists(config_path):
                config_path = str(Path.cwd() / ".cursor" / "config.yaml")
        
        self.config_path = config_path
        self.config = self.load_config()
        
    def load_config(self) -> dict:
        """
        Load configuration from YAML file.
        
        Returns:
            dict: Configuration dictionary with default values if file doesn't exist
        """
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    return yaml.safe_load(f) or {}
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
        """
        Save configuration to YAML file.
        
        Args:
            config: Configuration dictionary to save
        """
        try:
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            with open(self.config_path, 'w') as f:
                yaml.dump(config, f, default_flow_style=False)
        except Exception as e:
            logger.error(f"Error saving config: {e}")
    
    def check_instance_health(self, hostname: str, provider: str, user: str = "ansible") -> dict:
        """
        Check health of a specific instance via SSH.
        
        Args:
            hostname: Hostname or IP address of the instance
            provider: Cloud provider name
            user: SSH user (default: ansible)
        
        Returns:
            dict: Health check result with status, uptime, and timestamp
        """
        try:
            # SSH to instance and check basic health
            cmd = [
                'ssh', '-o', 'ConnectTimeout=10', '-o', 'StrictHostKeyChecking=no',
                f'{user}@{hostname}', 'uptime'
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
    
    def load_inventory_nodes(self, inventory_path: str = "ansible/inventory/production") -> List[Dict]:
        """
        Load node information from Ansible inventory.
        
        Args:
            inventory_path: Path to Ansible inventory file
        
        Returns:
            List[Dict]: List of node dictionaries with hostname, IP, provider, and role
        """
        nodes = []
        
        try:
            if os.path.exists(inventory_path):
                with open(inventory_path, 'r') as f:
                    current_group = None
                    for line in f:
                        line = line.strip()
                        if not line or line.startswith('#'):
                            continue
                        
                        # Check for group headers
                        if line.startswith('[') and line.endswith(']'):
                            current_group = line[1:-1]
                            continue
                        
                        # Parse host line (format: hostname ansible_host=IP ansible_user=user provider=provider role=role)
                        if 'ansible_host=' in line:
                            parts = line.split()
                            hostname = parts[0]
                            
                            # Extract variables
                            host_vars = {}
                            for part in parts[1:]:
                                if '=' in part:
                                    key, value = part.split('=', 1)
                                    host_vars[key] = value
                            
                            # Only include nodes from provider groups
                            if current_group in ['aws', 'google_cloud', 'oracle_cloud', 'ibm_cloud']:
                                provider_map = {
                                    'aws': 'AWS',
                                    'google_cloud': 'Google Cloud',
                                    'oracle_cloud': 'Oracle Cloud',
                                    'ibm_cloud': 'IBM Cloud'
                                }
                                
                                nodes.append({
                                    'hostname': hostname,
                                    'ip': host_vars.get('ansible_host', ''),
                                    'user': host_vars.get('ansible_user', 'ansible'),
                                    'provider': provider_map.get(current_group, current_group),
                                    'role': host_vars.get('role', 'general')
                                })
        except Exception as e:
            logger.error(f"Error loading inventory: {e}")
        
        return nodes
    
    def check_all_instances(self) -> List[dict]:
        """
        Check health of all instances from Ansible inventory.
        
        Returns:
            List[dict]: List of health check results for all instances
        """
        nodes = self.load_inventory_nodes()
        
        health_checks = []
        for node in nodes:
            provider_key = node['provider'].lower().replace(' ', '_')
            if self.config.get('providers', {}).get(provider_key, {}).get('enabled', True):
                health = self.check_instance_health(
                    node['hostname'],
                    node['provider'],
                    node['user']
                )
                health_checks.append(health)
                logger.info(f"Health check for {node['hostname']}: {health['status']}")
        
        return health_checks
    
    def generate_cost_report(self) -> str:
        """
        Generate multi-cloud cost report using clint billing module.
        
        Returns:
            str: Cost report summary
        """
        try:
            from clint.billing.manager import BillingManager
            
            manager = BillingManager()
            
            # Get daily costs for last 30 days
            daily_costs = manager.get_daily_costs(days=30)
            
            # Get month-over-month comparison
            now = datetime.now()
            comparison = manager.get_monthly_comparison(now.year, now.month)
            
            # Format report
            report_lines = [
                "=" * 80,
                "Multi-Cloud Cost Report",
                "=" * 80,
                f"Generated: {datetime.now().isoformat()}",
                "",
            ]
            
            if daily_costs:
                # Calculate total from daily costs
                total = 0.0
                for day_data in daily_costs.values():
                    if isinstance(day_data, dict):
                        total += day_data.get('total', 0.0)
                    elif isinstance(day_data, (int, float)):
                        total += day_data
                
                report_lines.extend([
                    "Daily Costs (Last 30 Days):",
                    "-" * 80,
                    f"Total: ${total:.2f}",
                    "",
                ])
            
            if comparison:
                current = comparison.get('current_month', {}).get('total_cost', 0.0)
                previous = comparison.get('previous_month', {}).get('total_cost', 0.0)
                change = current - previous
                change_pct = (change / previous * 100) if previous > 0 else 0.0
                
                report_lines.extend([
                    "Month-over-Month Comparison:",
                    "-" * 80,
                    f"Current Month: ${current:.2f}",
                    f"Previous Month: ${previous:.2f}",
                    f"Change: ${change:.2f} ({change_pct:+.1f}%)",
                ])
            
            report = "\n".join(report_lines)
            logger.info("Generated multi-cloud cost report")
            return report
        except Exception as e:
            logger.error(f"Error generating cost report: {e}")
            import traceback
            logger.debug(traceback.format_exc())
            return f"Error generating cost report: {e}"
    
    def update_dns_records(self):
        """
        Update Cloudflare DNS records with current instance IPs.
        
        This is a placeholder for future DNS management functionality.
        """
        try:
            logger.info("DNS update check - would update Cloudflare records here")
        except Exception as e:
            logger.error(f"Error updating DNS records: {e}")
    
    def cleanup_logs(self, log_dir: str = "/var/log/cursor-agent"):
        """
        Clean up old log files.
        
        Args:
            log_dir: Directory containing log files
        """
        try:
            log_path = Path(log_dir)
            if log_path.exists():
                retention_days = self.config.get('monitoring', {}).get('log_retention_days', 30)
                cutoff_date = datetime.now().timestamp() - (retention_days * 24 * 3600)
                
                for log_file in log_path.glob('*.log*'):
                    if log_file.stat().st_mtime < cutoff_date:
                        log_file.unlink()
                        logger.info(f"Cleaned up old log file: {log_file}")
        except Exception as e:
            logger.error(f"Error cleaning up logs: {e}")
    
    def run_health_checks(self, output_file: Optional[str] = None) -> List[dict]:
        """
        Run health checks on all instances.
        
        Args:
            output_file: Optional path to save health check results as JSON
        
        Returns:
            List[dict]: Health check results
        """
        logger.info("Starting health checks...")
        health_checks = self.check_all_instances()
        
        # Save health check results if output file specified
        if output_file:
            try:
                output_path = Path(output_file)
                output_path.parent.mkdir(parents=True, exist_ok=True)
                with open(output_path, 'w') as f:
                    json.dump(health_checks, f, indent=2)
                logger.info(f"Health check results saved to {output_file}")
            except Exception as e:
                logger.error(f"Error saving health checks: {e}")
        
        # Check for unhealthy instances
        unhealthy = [h for h in health_checks if h['status'] != 'healthy']
        if unhealthy:
            logger.warning(f"Found {len(unhealthy)} unhealthy instances")
            for instance in unhealthy:
                logger.warning(
                    f"Unhealthy: {instance['hostname']} ({instance['provider']}) - "
                    f"{instance.get('error', 'Unknown error')}"
                )
        
        logger.info(f"Health checks completed. {len(health_checks)} instances checked.")
        return health_checks
    
    def run_cost_analysis(self, output_file: Optional[str] = None) -> str:
        """
        Run cost analysis across all providers.
        
        Args:
            output_file: Optional path to save cost report
        
        Returns:
            str: Cost report text
        """
        logger.info("Starting cost analysis...")
        try:
            cost_report = self.generate_cost_report()
            
            # Save cost report if output file specified
            if output_file:
                try:
                    output_path = Path(output_file)
                    output_path.parent.mkdir(parents=True, exist_ok=True)
                    with open(output_path, 'w') as f:
                        f.write(cost_report)
                    logger.info(f"Cost report saved to {output_file}")
                except Exception as e:
                    logger.error(f"Error saving cost report: {e}")
            
            logger.info("Cost analysis completed")
            return cost_report
        except Exception as e:
            logger.error(f"Error in cost analysis: {e}")
            return f"Error in cost analysis: {e}"
    
    def run_maintenance(self):
        """Run maintenance tasks."""
        logger.info("Starting maintenance tasks...")
        
        # Clean up old logs
        self.cleanup_logs()
        
        # Update DNS records
        self.update_dns_records()
        
        logger.info("Maintenance tasks completed")
    
    def run(self, task: str = 'all', health_output: Optional[str] = None, 
            cost_output: Optional[str] = None):
        """
        Run the infrastructure agent with specified task.
        
        Args:
            task: Task to run ('all', 'health', 'cost', or 'maintenance')
            health_output: Optional path to save health check results
            cost_output: Optional path to save cost report
        """
        logger.info(f"Infrastructure Agent starting - Task: {task}")
        
        try:
            if task in ['all', 'health']:
                self.run_health_checks(health_output)
            
            if task in ['all', 'cost']:
                self.run_cost_analysis(cost_output)
            
            if task in ['all', 'maintenance']:
                self.run_maintenance()
            
            logger.info("Infrastructure Agent completed successfully")
        except Exception as e:
            logger.error(f"Infrastructure Agent error: {e}")
            raise

