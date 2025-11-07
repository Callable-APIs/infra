"""Secrets manager factory using strategy pattern."""
import os
from typing import Optional

from clint.secrets.ansible_vault import AnsibleVaultStrategy
from clint.secrets.base import SecretsStrategy
from clint.secrets.hashicorp_vault import HashiCorpVaultStrategy


class SecretsManager:
    """
    Secrets manager that uses strategy pattern to support multiple backends.
    
    Default strategy is Ansible Vault, but can be configured via environment variables.
    """

    STRATEGIES = {
        "ansible_vault": AnsibleVaultStrategy,
        "hashicorp_vault": HashiCorpVaultStrategy,
    }

    def __init__(
        self,
        strategy: Optional[str] = None,
        **strategy_kwargs,
    ):
        """
        Initialize secrets manager with specified strategy.

        Args:
            strategy: Strategy name ('ansible_vault' or 'hashicorp_vault').
                     If None, uses SECRETS_STRATEGY env var or defaults to 'ansible_vault'
            **strategy_kwargs: Additional arguments to pass to strategy constructor
        """
        strategy_name = strategy or os.getenv("SECRETS_STRATEGY", "ansible_vault")

        if strategy_name not in self.STRATEGIES:
            raise ValueError(
                f"Unknown strategy: {strategy_name}. "
                f"Available strategies: {', '.join(self.STRATEGIES.keys())}"
            )

        strategy_class = self.STRATEGIES[strategy_name]
        self.strategy: SecretsStrategy = strategy_class(**strategy_kwargs)

    def load_secrets(self):
        """Load secrets using the configured strategy."""
        return self.strategy.load_secrets()

    def get_secret(self, key: str, default=None):
        """Get a specific secret by key."""
        return self.strategy.get_secret(key, default)

    def get_secret_keys(self) -> list:
        """Get list of available secret keys."""
        return self.strategy.get_secret_keys()

    def setup_environment(self) -> None:
        """Set up environment variables from secrets."""
        self.strategy.setup_environment()

    # Convenience methods for Ansible Vault specific features
    def get_vault_password_hash(self) -> str:
        """
        Get vault password hash (Ansible Vault only).

        Returns:
            Hash string or "unavailable" if not Ansible Vault strategy
        """
        if isinstance(self.strategy, AnsibleVaultStrategy):
            return self.strategy.get_vault_password_hash()
        return "unavailable"

    def get_secrets_file_hash(self) -> str:
        """
        Get secrets file hash (Ansible Vault only).

        Returns:
            Hash string or "unavailable" if not Ansible Vault strategy
        """
        if isinstance(self.strategy, AnsibleVaultStrategy):
            return self.strategy.get_secrets_file_hash()
        return "unavailable"


# Backward compatibility alias
VaultSecretsManager = SecretsManager

