"""Tests for configuration manager."""

import os
from pathlib import Path

from schema_sentinel.config import (
    ConfigManager,
    DatabaseConfig,
    LogConfig,
    MetadataConfig,
    PathConfig,
    get_config,
)


class TestPathConfig:
    """Test PathConfig dataclass."""

    def test_default_initialization(self):
        """Test default path configuration."""
        config = PathConfig()
        assert config.project_name == "schema-sentinel"
        assert config.project_home is not None
        assert config.temp_dir is not None
        assert config.resources_dir is not None
        assert config.meta_db_dir is not None

    def test_custom_paths(self):
        """Test custom path configuration."""
        config = PathConfig(
            project_home=Path("/custom/path"),
            resources_dir=Path("/custom/resources"),
        )
        assert config.project_home == Path("/custom/path")
        assert config.resources_dir == Path("/custom/resources")


class TestLogConfig:
    """Test LogConfig dataclass."""

    def test_default_initialization(self):
        """Test default logging configuration."""
        config = LogConfig()
        assert config.level in ["INFO", "DEBUG", "WARNING", "ERROR"]
        assert config.file is not None
        assert "schema-sentinel.log" in str(config.file)

    def test_environment_variable_override(self):
        """Test log level from environment variable."""
        os.environ["LOG_LEVEL"] = "DEBUG"
        config = LogConfig()
        assert config.level == "DEBUG"
        del os.environ["LOG_LEVEL"]

    def test_custom_log_file(self):
        """Test custom log file path."""
        config = LogConfig(file=Path("/var/log/custom.log"))
        assert config.file == Path("/var/log/custom.log")


class TestDatabaseConfig:
    """Test DatabaseConfig dataclass."""

    def test_default_initialization(self):
        """Test default database configuration."""
        config = DatabaseConfig()
        assert config.data_retention_days == 7
        assert "dev" in config.account_map
        assert "staging" in config.account_map
        assert "prod" in config.account_map
        assert config.env_map["dev"] == "DEV"

    def test_environment_variable_accounts(self):
        """Test account mapping from environment variables."""
        os.environ["SNOWFLAKE_DEV_ACCOUNT"] = "test_dev_account"
        config = DatabaseConfig()
        assert config.account_map["dev"] == "test_dev_account"
        del os.environ["SNOWFLAKE_DEV_ACCOUNT"]


class TestMetadataConfig:
    """Test MetadataConfig dataclass."""

    def test_default_initialization(self):
        """Test default metadata configuration."""
        config = MetadataConfig()
        assert isinstance(config.attributes_to_exclude, list)
        assert "database_id" in config.attributes_to_exclude
        assert "table_id" in config.attributes_to_exclude
        assert isinstance(config.custom_view_filters, dict)


class TestConfigManager:
    """Test ConfigManager class."""

    def teardown_method(self):
        """Reset config manager after each test."""
        ConfigManager.reset()

    def test_singleton_pattern(self):
        """Test that ConfigManager follows singleton pattern."""
        config1 = ConfigManager.get_instance()
        config2 = ConfigManager.get_instance()
        assert config1 is config2

    def test_reset_singleton(self):
        """Test resetting the singleton instance."""
        config1 = ConfigManager.get_instance()
        ConfigManager.reset()
        config2 = ConfigManager.get_instance()
        assert config1 is not config2

    def test_initialization(self):
        """Test ConfigManager initialization."""
        config = ConfigManager()
        assert isinstance(config.paths, PathConfig)
        assert isinstance(config.logging, LogConfig)
        assert isinstance(config.database, DatabaseConfig)
        assert isinstance(config.metadata, MetadataConfig)

    def test_to_dict(self):
        """Test exporting configuration as dictionary."""
        config = ConfigManager()
        config_dict = config.to_dict()
        assert "paths" in config_dict
        assert "logging" in config_dict
        assert "database" in config_dict
        assert "metadata" in config_dict
        assert "project_name" in config_dict["paths"]
        assert "level" in config_dict["logging"]

    def test_yaml_config_loading(self, tmp_path):
        """Test loading configuration from YAML file."""
        # Create a temporary config file
        config_file = tmp_path / "test_config.yaml"
        config_content = """
paths:
  project_name: "test-project"

logging:
  level: "DEBUG"

database:
  data_retention_days: 14

metadata:
  custom_view_filters:
    TEST_FILTER:
      TABLE_LIST: ["TABLE1", "TABLE2"]
"""
        config_file.write_text(config_content)

        # Load config from file
        config = ConfigManager(config_file=config_file)
        assert config.paths.project_name == "test-project"
        assert config.logging.level == "DEBUG"
        assert config.database.data_retention_days == 14
        assert "TEST_FILTER" in config.metadata.custom_view_filters

    def test_yaml_config_missing_file(self):
        """Test loading with non-existent config file."""
        config = ConfigManager(config_file=Path("/nonexistent/config.yaml"))
        # Should not raise an error, just use defaults
        assert config.paths.project_name == "schema-sentinel"


class TestGetConfig:
    """Test get_config helper function."""

    def teardown_method(self):
        """Reset config manager after each test."""
        ConfigManager.reset()
        # Clear the lru_cache
        get_config.cache_clear()

    def test_get_config_returns_manager(self):
        """Test that get_config returns a ConfigManager instance."""
        config = get_config()
        assert isinstance(config, ConfigManager)

    def test_get_config_cached(self):
        """Test that get_config uses caching."""
        config1 = get_config()
        config2 = get_config()
        assert config1 is config2
