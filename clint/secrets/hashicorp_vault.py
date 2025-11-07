"""HashiCorp Vault secrets management strategy."""
import os
from typing import Dict, Optional

try:
    import hvac
    HVAC_AVAILABLE = True
except ImportError:
    HVAC_AVAILABLE = False

from clint.secrets.base import SecretsStrategy


class HashiCorpVaultStrategy(SecretsStrategy):
    """Secrets management using HashiCorp Vault."""

    def __init__(
        self,
        vault_url: Optional[str] = None,
        vault_token: Optional[str] = None,
        secrets_path: str = "callableapis/secrets",
    ):
        """
        Initialize HashiCorp Vault strategy.

        Args:
            vault_url: Vault server URL (defaults to VAULT_ADDR env var)
            vault_token: Vault authentication token (defaults to VAULT_TOKEN env var)
            secrets_path: Path to secrets in Vault KV store
        """
        if not HVAC_AVAILABLE:
            raise ImportError(
                "hvac package is required for HashiCorp Vault strategy. Install with: pip install hvac"
            )

        self.vault_url = vault_url or os.getenv("VAULT_ADDR", "https://vault.callableapis.com")
        self.vault_token = vault_token or os.getenv("VAULT_TOKEN")
        self.secrets_path = secrets_path
        self.client = None
        self.secrets_cache: Optional[Dict[str, str]] = None

        if not self.vault_token:
            raise ValueError("VAULT_TOKEN environment variable is required")

    def connect(self):
        """Connect to Vault server."""
        if self.client:
            return self.client

        self.client = hvac.Client(url=self.vault_url, token=self.vault_token)

        # Verify connection
        if not self.client.is_authenticated():
            raise RuntimeError("Failed to authenticate with Vault")

        return self.client

    def load_secrets(self) -> Dict[str, str]:
        """
        Load secrets directly from HashiCorp Vault.

        Returns:
            Dictionary of environment variables
        """
        if self.secrets_cache is not None:
            return self.secrets_cache

        try:
            client = self.connect()

            # Read secrets from Vault KV v2
            response = client.secrets.kv.v2.read_secret_version(path=self.secrets_path)

            secrets_data = response["data"]["data"]

            # Convert to environment variable format
            secrets = {}
            for key, value in secrets_data.items():
                if key.startswith("vault_"):
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

