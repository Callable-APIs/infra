#!/usr/bin/env python3
"""
CallableAPIs Vault Secrets Manager
Handles loading and decrypting secrets from Ansible Vault
"""

import os
import subprocess
import tempfile
import yaml
import hashlib
from pathlib import Path
from typing import Dict, Optional

class VaultSecretsManager:
    def __init__(self, vault_password_file: str = "/app/vault-password"):
        self.vault_password_file = vault_password_file
        self.secrets_cache: Optional[Dict] = None
    
    def load_secrets(self) -> Dict[str, str]:
        """
        Load and decrypt secrets from Ansible Vault
        Returns a dictionary of environment variables
        """
        if self.secrets_cache is not None:
            return self.secrets_cache
        
        try:
            # Check if vault password file exists
            if not os.path.exists(self.vault_password_file):
                raise FileNotFoundError(f"Vault password file not found: {self.vault_password_file}")
            
            # Check if secrets file exists
            secrets_file = "/app/secrets/all-secrets.env"
            if not os.path.exists(secrets_file):
                raise FileNotFoundError(f"Secrets file not found: {secrets_file}")
            
            # Read vault password
            with open(self.vault_password_file, 'r') as f:
                vault_password = f.read().strip()
            
            # Decrypt secrets using ansible-vault
            result = subprocess.run([
                'ansible-vault', 'view', secrets_file,
                '--vault-password-file', self.vault_password_file
            ], capture_output=True, text=True, check=True)
            
            # Parse the decrypted YAML
            secrets_data = yaml.safe_load(result.stdout)
            
            # Convert to environment variable format
            secrets = {}
            for key, value in secrets_data.items():
                if key.startswith('vault_'):
                    # Remove 'vault_' prefix and convert to uppercase
                    env_key = key[6:].upper()
                    secrets[env_key] = value
            
            self.secrets_cache = secrets
            return secrets
            
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to decrypt secrets: {e.stderr}")
        except Exception as e:
            raise RuntimeError(f"Error loading secrets: {e}")
    
    def get_secret(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """
        Get a specific secret by key
        """
        secrets = self.load_secrets()
        return secrets.get(key, default)
    
    def get_secret_keys(self) -> list:
        """
        Get list of secret keys (without values)
        """
        secrets = self.load_secrets()
        return list(secrets.keys())
    
    def get_vault_password_hash(self) -> str:
        """
        Get SHA256 hash of vault password file
        """
        if os.path.exists(self.vault_password_file):
            with open(self.vault_password_file, 'rb') as f:
                return hashlib.sha256(f.read()).hexdigest()[:16]
        return "not_found"
    
    def get_secrets_file_hash(self) -> str:
        """
        Get SHA256 hash of secrets file
        """
        secrets_file = "/app/secrets/all-secrets.env"
        if os.path.exists(secrets_file):
            with open(secrets_file, 'rb') as f:
                return hashlib.sha256(f.read()).hexdigest()[:16]
        return "not_found"
    
    def setup_environment(self) -> None:
        """
        Set up environment variables from secrets
        """
        secrets = self.load_secrets()
        for key, value in secrets.items():
            os.environ[key] = value

def main():
    """
    Standalone script to load and display secrets
    """
    try:
        manager = VaultSecretsManager()
        secrets = manager.load_secrets()
        
        print("CallableAPIs Vault Secrets Manager")
        print("=" * 40)
        print(f"Loaded {len(secrets)} secrets:")
        
        for key in secrets.keys():
            print(f"  {key}")
                
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
