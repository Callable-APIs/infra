"""
Domain management utilities for CallableAPIs infrastructure.

This module provides access to domain information used across the infrastructure,
including GoDaddy domains migrated to Cloudflare and their associated nameservers.
"""

from typing import Dict, List


class DomainManager:
    """
    Manages domain information for CallableAPIs infrastructure.
    
    Provides access to domain lists, nameservers, and domain mappings
    used across Terraform configurations and infrastructure management.
    """
    
    # GoDaddy domains migrated to Cloudflare
    # This list matches the domains defined in terraform/cloudflare-godaddy-domains.tf
    GODADDY_DOMAINS = [
        "cocoonspamini.com",
        "glassbubble.net",
        "iheartdinos.com",
        "jughunt.com",
        "lipbalmjunkie.com",
        "ohsorad.com",
        "rosamimosa.com",
        "taicho.com",
        "tokyo3.com",
    ]
    
    # Domain key mapping (used in Terraform for_each loops)
    # Maps short keys to full domain names
    DOMAIN_MAPPING = {
        "cocoonspamini": "cocoonspamini.com",
        "glassbubble": "glassbubble.net",
        "iheartdinos": "iheartdinos.com",
        "jughunt": "jughunt.com",
        "lipbalmjunkie": "lipbalmjunkie.com",
        "ohsorad": "ohsorad.com",
        "rosamimosa": "rosamimosa.com",
        "taicho": "taicho.com",
        "tokyo3": "tokyo3.com",
    }
    
    # Cloudflare nameservers for all domains
    # All domains use the same nameservers
    CLOUDFLARE_NAMESERVERS = [
        "nora.ns.cloudflare.com",
        "wells.ns.cloudflare.com",
    ]
    
    @classmethod
    def get_domains(cls) -> List[str]:
        """
        Get list of all GoDaddy domains migrated to Cloudflare.
        
        Returns:
            List[str]: List of domain names (e.g., ["cocoonspamini.com", ...])
        
        Example:
            >>> domains = DomainManager.get_domains()
            >>> print(f"Managing {len(domains)} domains")
            Managing 9 domains
        """
        return cls.GODADDY_DOMAINS.copy()
    
    @classmethod
    def get_domain_mapping(cls) -> Dict[str, str]:
        """
        Get domain key-to-domain mapping used in Terraform configurations.
        
        Returns:
            Dict[str, str]: Mapping of short keys to full domain names
                (e.g., {"tokyo3": "tokyo3.com", ...})
        
        Example:
            >>> mapping = DomainManager.get_domain_mapping()
            >>> print(mapping["tokyo3"])
            tokyo3.com
        """
        return cls.DOMAIN_MAPPING.copy()
    
    @classmethod
    def get_nameservers(cls) -> List[str]:
        """
        Get Cloudflare nameservers for all domains.
        
        All domains use the same nameservers. These need to be configured
        in GoDaddy for DNS to be fully managed by Cloudflare.
        
        Returns:
            List[str]: List of nameserver hostnames
        
        Example:
            >>> nameservers = DomainManager.get_nameservers()
            >>> print(f"Nameservers: {', '.join(nameservers)}")
            Nameservers: nora.ns.cloudflare.com, wells.ns.cloudflare.com
        """
        return cls.CLOUDFLARE_NAMESERVERS.copy()
    
    @classmethod
    def get_domain_by_key(cls, key: str) -> str:
        """
        Get full domain name by short key.
        
        Args:
            key: Short domain key (e.g., "tokyo3")
        
        Returns:
            str: Full domain name (e.g., "tokyo3.com")
        
        Raises:
            KeyError: If key is not found in domain mapping
        
        Example:
            >>> domain = DomainManager.get_domain_by_key("tokyo3")
            >>> print(domain)
            tokyo3.com
        """
        if key not in cls.DOMAIN_MAPPING:
            raise KeyError(f"Domain key '{key}' not found. Available keys: {list(cls.DOMAIN_MAPPING.keys())}")
        return cls.DOMAIN_MAPPING[key]
    
    @classmethod
    def get_key_by_domain(cls, domain: str) -> str:
        """
        Get short key for a full domain name.
        
        Args:
            domain: Full domain name (e.g., "tokyo3.com")
        
        Returns:
            str: Short domain key (e.g., "tokyo3")
        
        Raises:
            KeyError: If domain is not found in domain mapping
        
        Example:
            >>> key = DomainManager.get_key_by_domain("tokyo3.com")
            >>> print(key)
            tokyo3
        """
        for key, value in cls.DOMAIN_MAPPING.items():
            if value == domain:
                return key
        raise KeyError(f"Domain '{domain}' not found. Available domains: {cls.GODADDY_DOMAINS}")


# Convenience functions for easy access
def get_domains() -> List[str]:
    """
    Convenience function to get list of all domains.
    
    Returns:
        List[str]: List of domain names
    
    Example:
        >>> from clint.domains import get_domains
        >>> domains = get_domains()
    """
    return DomainManager.get_domains()


def get_nameservers() -> List[str]:
    """
    Convenience function to get Cloudflare nameservers.
    
    Returns:
        List[str]: List of nameserver hostnames
    
    Example:
        >>> from clint.domains import get_nameservers
        >>> nameservers = get_nameservers()
    """
    return DomainManager.get_nameservers()

