"""Configuration management for Schema Sentinel.

This module provides centralized configuration management through the
ConfigManager class and its sub-configurations:

- PathConfig: Project paths and directories
- LogConfig: Logging configuration
- DatabaseConfig: Database connection settings
- MetadataConfig: Metadata extraction settings

Example:
    >>> from schema_sentinel.config import get_config
    >>> config = get_config()
    >>> print(config.paths.project_home)
    >>> print(config.logging.level)
"""

from schema_sentinel.config.manager import (
    ConfigManager,
    DatabaseConfig,
    LogConfig,
    MetadataConfig,
    PathConfig,
    get_config,
)

__all__ = [
    "ConfigManager",
    "PathConfig",
    "LogConfig",
    "DatabaseConfig",
    "MetadataConfig",
    "get_config",
]
