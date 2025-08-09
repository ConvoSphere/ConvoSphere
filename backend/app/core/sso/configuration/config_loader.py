"""
SSO Configuration Loader.

This module provides configuration loading functionality for SSO providers.
"""

import logging
import os
from typing import Any, Dict

logger = logging.getLogger(__name__)


def load_sso_config_from_env() -> Dict[str, Any]:
    """
    Load SSO configuration from environment variables.
    
    Returns:
        SSO configuration dictionary
    """
    config = {
        "providers": {},
        "default_provider": os.getenv("SSO_DEFAULT_PROVIDER", "ldap"),
        "session_timeout": int(os.getenv("SSO_SESSION_TIMEOUT", "3600")),
        "auto_sync_groups": os.getenv("SSO_AUTO_SYNC_GROUPS", "true").lower() == "true",
    }

    # LDAP Configuration
    if os.getenv("LDAP_ENABLED", "false").lower() == "true":
        config["providers"]["ldap"] = {
            "enabled": True,
            "name": "LDAP",
            "priority": int(os.getenv("LDAP_PRIORITY", "1")),
            "server_url": os.getenv("LDAP_SERVER_URL"),
            "base_dn": os.getenv("LDAP_BASE_DN"),
            "bind_dn": os.getenv("LDAP_BIND_DN"),
            "bind_password": os.getenv("LDAP_BIND_PASSWORD"),
            "user_search_base": os.getenv("LDAP_USER_SEARCH_BASE"),
            "group_search_base": os.getenv("LDAP_GROUP_SEARCH_BASE"),
            "user_search_filter": os.getenv("LDAP_USER_SEARCH_FILTER", "(sAMAccountName={username})"),
            "group_search_filter": os.getenv("LDAP_GROUP_SEARCH_FILTER", "(member={user_dn})"),
            "attributes": os.getenv("LDAP_ATTRIBUTES", "cn,mail,displayName,memberOf").split(","),
            "use_ssl": os.getenv("LDAP_USE_SSL", "true").lower() == "true",
            "timeout": int(os.getenv("LDAP_TIMEOUT", "10")),
            "default_role": os.getenv("LDAP_DEFAULT_ROLE", "user"),
            "auto_create_groups": os.getenv("LDAP_AUTO_CREATE_GROUPS", "false").lower() == "true",
            "role_mapping": _parse_role_mapping(os.getenv("LDAP_ROLE_MAPPING", "")),
            "group_mapping": _parse_group_mapping(os.getenv("LDAP_GROUP_MAPPING", "")),
        }

    # SAML Configuration
    if os.getenv("SAML_ENABLED", "false").lower() == "true":
        config["providers"]["saml"] = {
            "enabled": True,
            "name": "SAML",
            "priority": int(os.getenv("SAML_PRIORITY", "2")),
            "idp_metadata_url": os.getenv("SAML_IDP_METADATA_URL"),
            "idp_entity_id": os.getenv("SAML_IDP_ENTITY_ID"),
            "sp_entity_id": os.getenv("SAML_SP_ENTITY_ID"),
            "acs_url": os.getenv("SAML_ACS_URL"),
            "slo_url": os.getenv("SAML_SLO_URL"),
            "cert_file": os.getenv("SAML_CERT_FILE"),
            "key_file": os.getenv("SAML_KEY_FILE"),
            "default_role": os.getenv("SAML_DEFAULT_ROLE", "user"),
            "role_mapping": _parse_role_mapping(os.getenv("SAML_ROLE_MAPPING", "")),
            "attribute_mapping": {
                "username": os.getenv("SAML_ATTR_USERNAME", "urn:oid:0.9.2342.19200300.100.1.1"),
                "email": os.getenv("SAML_ATTR_EMAIL", "urn:oid:0.9.2342.19200300.100.1.3"),
                "first_name": os.getenv("SAML_ATTR_FIRST_NAME", "urn:oid:2.5.4.42"),
                "last_name": os.getenv("SAML_ATTR_LAST_NAME", "urn:oid:2.5.4.4"),
                "groups": os.getenv("SAML_ATTR_GROUPS", "urn:oid:1.3.6.1.4.1.5923.1.5.1.1"),
            },
        }

    # OAuth Configuration
    if os.getenv("OAUTH_ENABLED", "false").lower() == "true":
        config["providers"]["oauth"] = {
            "enabled": True,
            "name": "OAuth",
            "priority": int(os.getenv("OAUTH_PRIORITY", "3")),
            "client_id": os.getenv("OAUTH_CLIENT_ID"),
            "client_secret": os.getenv("OAUTH_CLIENT_SECRET"),
            "authorization_url": os.getenv("OAUTH_AUTHORIZATION_URL"),
            "token_url": os.getenv("OAUTH_TOKEN_URL"),
            "userinfo_url": os.getenv("OAUTH_USERINFO_URL"),
            "scope": os.getenv("OAUTH_SCOPE", "openid email profile"),
            "jwks_url": os.getenv("OAUTH_JWKS_URL"),
            "issuer": os.getenv("OAUTH_ISSUER"),
            "default_role": os.getenv("OAUTH_DEFAULT_ROLE", "user"),
            "role_mapping": _parse_role_mapping(os.getenv("OAUTH_ROLE_MAPPING", "")),
            "attribute_mapping": {
                "username": os.getenv("OAUTH_ATTR_USERNAME", "sub"),
                "email": os.getenv("OAUTH_ATTR_EMAIL", "email"),
                "first_name": os.getenv("OAUTH_ATTR_FIRST_NAME", "given_name"),
                "last_name": os.getenv("OAUTH_ATTR_LAST_NAME", "family_name"),
                "groups": os.getenv("OAUTH_ATTR_GROUPS", "groups"),
            },
        }

    logger.info(f"Loaded SSO configuration with {len(config['providers'])} providers")
    return config


def _parse_role_mapping(mapping_str: str) -> Dict[str, str]:
    """
    Parse role mapping from string format.
    
    Args:
        mapping_str: Role mapping string in format "group1:role1,group2:role2"
        
    Returns:
        Role mapping dictionary
    """
    if not mapping_str:
        return {}
    
    mapping = {}
    for item in mapping_str.split(","):
        if ":" in item:
            group, role = item.strip().split(":", 1)
            mapping[group.strip()] = role.strip()
    
    return mapping


def _parse_group_mapping(mapping_str: str) -> Dict[str, str]:
    """
    Parse group mapping from string format.
    
    Args:
        mapping_str: Group mapping string in format "ldap_group1:app_group1,ldap_group2:app_group2"
        
    Returns:
        Group mapping dictionary
    """
    if not mapping_str:
        return {}
    
    mapping = {}
    for item in mapping_str.split(","):
        if ":" in item:
            ldap_group, app_group = item.strip().split(":", 1)
            mapping[ldap_group.strip()] = app_group.strip()
    
    return mapping


def validate_sso_config(config: Dict[str, Any]) -> bool:
    """
    Validate SSO configuration.
    
    Args:
        config: SSO configuration dictionary
        
    Returns:
        True if configuration is valid
        
    Raises:
        ValueError: If configuration is invalid
    """
    if not config.get("providers"):
        raise ValueError("No SSO providers configured")

    for provider_name, provider_config in config["providers"].items():
        if not provider_config.get("enabled", False):
            continue

        if provider_name == "ldap":
            required_fields = ["server_url", "base_dn", "bind_dn", "bind_password"]
        elif provider_name == "saml":
            required_fields = ["idp_metadata_url", "sp_entity_id", "acs_url"]
        elif provider_name == "oauth":
            required_fields = ["client_id", "client_secret", "authorization_url", "token_url"]
        else:
            raise ValueError(f"Unknown SSO provider: {provider_name}")

        missing_fields = [field for field in required_fields if not provider_config.get(field)]
        if missing_fields:
            raise ValueError(f"Missing required fields for {provider_name}: {missing_fields}")

    return True


def get_provider_config(config: Dict[str, Any], provider_name: str) -> Dict[str, Any]:
    """
    Get configuration for specific provider.
    
    Args:
        config: SSO configuration dictionary
        provider_name: Name of the provider
        
    Returns:
        Provider configuration dictionary
        
    Raises:
        ValueError: If provider is not configured
    """
    if provider_name not in config.get("providers", {}):
        raise ValueError(f"Provider '{provider_name}' not configured")
    
    return config["providers"][provider_name]