"""Ansible Vault secrets management strategy."""
import os
import subprocess
import yaml
import hashlib
from typing import Dict, Optional

from clint.secrets.base import SecretsStrategy


class AnsibleVaultStrategy(SecretsStrategy):
    """Secrets management using Ansible Vault."""

    def __init__(
        self,
        vault_password_file: str = "/app/vault-password",
        secrets_file: str = "/app/secrets/all-secrets.env",
    ):
        """
        Initialize Ansible Vault strategy.

        Args:
            vault_password_file: Path to Ansible Vault password file
            secrets_file: Path to encrypted Ansible Vault secrets file
        """
        self.vault_password_file = vault_password_file
        self.secrets_file = secrets_file
        self.secrets_cache: Optional[Dict[str, str]] = None

    def load_secrets(self) -> Dict[str, str]:
        """
        Load and decrypt secrets from Ansible Vault.

        Returns:
            Dictionary of environment variables
        """
        if self.secrets_cache is not None:
            return self.secrets_cache

        try:
            # Check if vault password file exists
            if not os.path.exists(self.vault_password_file):
                raise FileNotFoundError(
                    f"Vault password file not found: {self.vault_password_file}"
                )

            # Check if secrets file exists
            if not os.path.exists(self.secrets_file):
                raise FileNotFoundError(f"Secrets file not found: {self.secrets_file}")

            # Decrypt secrets using ansible-vault
            result = subprocess.run(
                [
                    "ansible-vault",
                    "view",
                    self.secrets_file,
                    "--vault-password-file",
                    self.vault_password_file,
                ],
                capture_output=True,
                text=True,
                check=True,
            )

            # Parse the decrypted YAML
            secrets_data = yaml.safe_load(result.stdout)

            # Convert to environment variable format
            secrets = {}
            for key, value in secrets_data.items():
                if key.startswith("vault_"):
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
        Get a specific secret by key.

        Args:
            key: Secret key name
            default: Default value if key not found

        Returns:
            Secret value or default
        """
        secrets = self.load_secrets()
        return secrets.get(key, default)

    def get_vault_password_hash(self) -> str:
        """
        Get SHA256 hash of vault password file (first 16 chars).

        Returns:
            Hash string or "not_found"
        """
        if os.path.exists(self.vault_password_file):
            with open(self.vault_password_file, "rb") as f:
                return hashlib.sha256(f.read()).hexdigest()[:16]
        return "not_found"

    def get_secrets_file_hash(self) -> str:
        """
        Get SHA256 hash of secrets file (first 16 chars).

        Returns:
            Hash string or "not_found"
        """
        if os.path.exists(self.secrets_file):
            with open(self.secrets_file, "rb") as f:
                return hashlib.sha256(f.read()).hexdigest()[:16]
        return "not_found"

