"""Configuration manager for Schema Sentinel."""

import os
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Any, Optional


@dataclass
class PathConfig:
    """Path-related configuration."""

    project_name: str = "schema-sentinel"
    project_home: Path | None = None
    temp_dir: Path | None = None
    resources_dir: Path | None = None
    meta_db_dir: Path | None = None

    def __post_init__(self):
        """Auto-calculate paths if not provided."""
        if self.project_home is None:
            self.project_home = Path(os.path.dirname(os.path.join(os.path.abspath("./"), self.project_name)))

        if self.temp_dir is None:
            temp = os.getenv("TEMP") if os.name == "nt" else "/tmp"
            self.temp_dir = Path(temp)

        if self.resources_dir is None:
            self.resources_dir = self.project_home / "resources"

        if self.meta_db_dir is None:
            self.meta_db_dir = self.resources_dir / "meta-db"

        # Ensure the meta-db directory exists (best effort)
        try:
            self.meta_db_dir.mkdir(parents=True, exist_ok=True)
        except (OSError, PermissionError):
            # Directory creation failed (e.g., read-only filesystem, insufficient permissions)
            # This is okay - the directory will be created when needed by SQLite operations
            pass


@dataclass
class LogConfig:
    """Logging configuration."""

    level: str = "INFO"
    file: Path | None = None
    format: str = "%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s"

    def __post_init__(self):
        """Set log level from environment and calculate log file path."""
        self.level = os.getenv("LOG_LEVEL", self.level)
        if self.file is None:
            temp = os.getenv("TEMP") if os.name == "nt" else "/tmp"
            self.file = Path(temp) / "schema-sentinel.log"


@dataclass
class DatabaseConfig:
    """Database-related configuration."""

    data_retention_days: int = 7
    account_map: dict[str, str] = field(
        default_factory=lambda: {
            "dev": os.getenv("SNOWFLAKE_DEV_ACCOUNT", "YOUR_DEV_ACCOUNT"),
            "staging": os.getenv("SNOWFLAKE_STAGING_ACCOUNT", "YOUR_STAGING_ACCOUNT"),
            "prod": os.getenv("SNOWFLAKE_PROD_ACCOUNT", "YOUR_PROD_ACCOUNT"),
        }
    )
    env_map: dict[str, str] = field(
        default_factory=lambda: {
            "dev": "DEV",
            "staging": "STAGING",
            "prod": "PROD",
        }
    )


@dataclass
class MetadataConfig:
    """Metadata extraction configuration."""

    attributes_to_exclude: list = field(
        default_factory=lambda: [
            "database_id",
            "table_id",
            "environment",
            "version",
            "created",
            "last_altered",
            "schema_id",
            "id",
            "column_id",
            "last_suspended",
            "table_constraint_id",
            "column_constraint_id",
            "referential_constraint_id",
            "view_id",
            "pipe_id",
            "task_id",
            "stream_id",
            "function_id",
            "procedure_id",
            "last_ddl",
            "stale_after",
            "bytes",
            "row_count",
        ]
    )
    custom_view_filters: dict[str, Any] = field(default_factory=dict)


class ConfigManager:
    """Centralized configuration manager for Schema Sentinel.

    Manages all configuration settings including paths, logging,
    database connections, and metadata extraction options.

    Examples:
        >>> config = ConfigManager.get_instance()
        >>> print(config.paths.project_home)
        >>> print(config.logging.level)
        >>> print(config.database.account_map)
    """

    _instance: Optional["ConfigManager"] = None

    def __init__(self, config_file: Path | None = None):
        """Initialize configuration manager.

        Args:
            config_file: Optional path to YAML config file
        """
        self.paths = PathConfig()
        self.logging = LogConfig()
        self.database = DatabaseConfig()
        self.metadata = MetadataConfig()

        # Load from file if provided
        if config_file and config_file.exists():
            self._load_from_file(config_file)

    @classmethod
    def get_instance(cls, config_file: Path | None = None) -> "ConfigManager":
        """Get singleton instance of ConfigManager.

        Args:
            config_file: Optional path to YAML config file

        Returns:
            ConfigManager singleton instance
        """
        if cls._instance is None:
            cls._instance = cls(config_file)
        return cls._instance

    @classmethod
    def reset(cls):
        """Reset singleton instance (useful for testing)."""
        cls._instance = None

    def _load_from_file(self, config_file: Path):
        """Load configuration from YAML file.

        Args:
            config_file: Path to YAML configuration file
        """
        try:
            import yaml

            with open(config_file) as f:
                config_data = yaml.safe_load(f)

            # Handle empty config file (safe_load returns None)
            if config_data is None:
                config_data = {}

            # Update configurations from file
            if "paths" in config_data:
                for key, value in config_data["paths"].items():
                    if hasattr(self.paths, key):
                        # Don't convert project_name to Path
                        if key == "project_name":
                            setattr(self.paths, key, value)
                        else:
                            setattr(self.paths, key, Path(value) if value else None)

            if "logging" in config_data:
                for key, value in config_data["logging"].items():
                    if hasattr(self.logging, key):
                        setattr(self.logging, key, value)

            if "database" in config_data:
                for key, value in config_data["database"].items():
                    if hasattr(self.database, key):
                        setattr(self.database, key, value)

            if "metadata" in config_data:
                for key, value in config_data["metadata"].items():
                    if hasattr(self.metadata, key):
                        setattr(self.metadata, key, value)
        except ImportError:
            # YAML not available, skip file loading
            pass

    def to_dict(self) -> dict[str, Any]:
        """Export configuration as dictionary.

        Returns:
            Dictionary representation of all configuration
        """
        return {
            "paths": {
                "project_name": self.paths.project_name,
                "project_home": str(self.paths.project_home),
                "temp_dir": str(self.paths.temp_dir),
                "resources_dir": str(self.paths.resources_dir),
                "meta_db_dir": str(self.paths.meta_db_dir),
            },
            "logging": {
                "level": self.logging.level,
                "file": str(self.logging.file),
                "format": self.logging.format,
            },
            "database": {
                "data_retention_days": self.database.data_retention_days,
                "account_map": self.database.account_map,
                "env_map": self.database.env_map,
            },
            "metadata": {
                "attributes_to_exclude": self.metadata.attributes_to_exclude,
                "custom_view_filters": self.metadata.custom_view_filters,
            },
        }


@lru_cache(maxsize=1)
def get_config() -> ConfigManager:
    """Get the global configuration manager instance.

    Looks for configuration files in common locations:
    - ./schema_sentinel_config.yaml
    - ~/.schema-sentinel/config.yaml
    - /etc/schema-sentinel/config.yaml

    Returns:
        ConfigManager singleton instance
    """
    config_locations = [
        Path("schema_sentinel_config.yaml"),
        Path.home() / ".schema-sentinel" / "config.yaml",
        Path("/etc/schema-sentinel/config.yaml"),
    ]

    for config_file in config_locations:
        if config_file.exists():
            return ConfigManager.get_instance(config_file)

    return ConfigManager.get_instance()
