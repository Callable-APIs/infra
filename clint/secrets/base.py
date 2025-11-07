"""Base strategy interface for secrets management."""
from abc import ABC, abstractmethod
from typing import Dict, Optional


class SecretsStrategy(ABC):
    """Base interface for secrets management strategies."""

    @abstractmethod
    def load_secrets(self) -> Dict[str, str]:
        """
        Load secrets from the configured source.
        
        Returns:
            Dictionary of environment variable key-value pairs
        """
        pass

    @abstractmethod
    def get_secret(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """
        Get a specific secret by key.
        
        Args:
            key: Secret key name
            default: Default value if key not found
            
        Returns:
            Secret value or default
        """
        pass

    def get_secret_keys(self) -> list:
        """
        Get list of available secret keys (without values).
        
        Returns:
            List of secret key names
        """
        secrets = self.load_secrets()
        return list(secrets.keys())

    def setup_environment(self) -> None:
        """
        Set up environment variables from secrets.
        """
        import os
        secrets = self.load_secrets()
        for key, value in secrets.items():
            os.environ[key] = value

