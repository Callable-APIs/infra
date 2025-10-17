#!/usr/bin/env python3
"""
HashiCorp Vault Secrets Manager
Fetches secrets directly from Vault server
"""

import os
import hvac
from typing import Dict, Optional

class VaultSecretsManager:
    def __init__(self, vault_url: str = None, vault_token: str = None):
        self.vault_url = vault_url or os.getenv('VAULT_ADDR', 'https://vault.callableapis.com')
        self.vault_token = vault_token or os.getenv('VAULT_TOKEN')
        self.client = None
        self.secrets_cache: Optional[Dict] = None
        
        if not self.vault_token:
            raise ValueError("VAULT_TOKEN environment variable is required")
    
    def connect(self):
        """Connect to Vault server"""
        if self.client:
            return self.client
        
        self.client = hvac.Client(url=self.vault_url, token=self.vault_token)
        
        # Verify connection
        if not self.client.is_authenticated():
            raise RuntimeError("Failed to authenticate with Vault")
        
        return self.client
    
    def load_secrets(self) -> Dict[str, str]:
        """Load secrets directly from Vault"""
        if self.secrets_cache is not None:
            return self.secrets_cache
        
        try:
            client = self.connect()
            
            # Read secrets from Vault
            # Assuming secrets are stored at 'callableapis/secrets'
            response = client.secrets.kv.v2.read_secret_version(
                path='callableapis/secrets'
            )
            
            secrets_data = response['data']['data']
            
            # Convert to environment variable format
            secrets = {}
            for key, value in secrets_data.items():
                if key.startswith('vault_'):
                    # Remove 'vault_' prefix and convert to uppercase
                    env_key = key[6:].upper()
                    secrets[env_key] = value
                else:
                    secrets[key.upper()] = value
            
            self.secrets_cache = secrets
            return secrets
            
        except Exception as e:
            raise RuntimeError(f"Error loading secrets from Vault: {e}")
    
    def get_secret(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """Get a specific secret by key"""
        secrets = self.load_secrets()
        return secrets.get(key, default)
    
    def setup_environment(self) -> None:
        """Set up environment variables from secrets"""
        secrets = self.load_secrets()
        for key, value in secrets.items():
            os.environ[key] = value
        
        print(f"Loaded {len(secrets)} secrets into environment from Vault")

def main():
    """Standalone script to test Vault secrets loading"""
    try:
        manager = VaultSecretsManager()
        secrets = manager.load_secrets()
        
        print("Vault Secrets Manager")
        print("=" * 25)
        print(f"Loaded {len(secrets)} secrets from Vault:")
        
        for key, value in secrets.items():
            # Mask sensitive values
            if 'password' in key.lower() or 'secret' in key.lower() or 'key' in key.lower():
                masked_value = '*' * len(value) if value else 'None'
                print(f"  {key}: {masked_value}")
            else:
                print(f"  {key}: {value}")
                
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
