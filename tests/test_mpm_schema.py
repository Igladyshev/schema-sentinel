"""Unit tests for MPM schema validation."""

from pathlib import Path

import pytest

from snowflake_local_testing.mpm_parser import MPMConfig


@pytest.fixture
def valid_yaml_path():
    """Path to valid YAML test file."""
    return Path(__file__).parent.parent / "resources" / "master-mpm" / "BS" / "BS_005-mpm.yaml"


@pytest.fixture
def temp_yaml_file(tmp_path):
    """Factory for creating temporary YAML files."""

    def _create_yaml(content: str) -> Path:
        yaml_file = tmp_path / "test_config.yaml"
        yaml_file.write_text(content)
        return yaml_file

    return _create_yaml


class TestMPMSchemaValidation:
    """Test cases for MPM schema validation."""

    def test_valid_yaml_file(self, valid_yaml_path):
        """Test that the actual BS_005-mpm.yaml file is valid."""
        is_valid, error = MPMConfig.validate_yaml_file(valid_yaml_path)
        assert is_valid is True, f"Valid YAML should pass validation. Error: {error}"
        assert error is None

    def test_load_valid_config(self, valid_yaml_path):
        """Test loading a valid configuration."""
        config = MPMConfig(valid_yaml_path)
        assert config.deployment_version == "BS_005"
        assert config.domain_code == "BS"
        assert len(config.communities) == 2
        assert len(config.actions) > 0

    def test_missing_required_field_deployment_version(self, temp_yaml_file):
        """Test validation fails when deployment_version is missing."""
        yaml_content = """
domain_code: BS
warehouse:
  auto_suspend: 120
  max_cluster_count: 4
  scaling_policy: STANDARD
  warehouse_size: MEDIUM
  warehouse_type: SNOWPARK-OPTIMIZED
internal_stage: GENERIC_REPORTING.BS_005.REPORTING
external_stage: GENERIC_REPORTING.REPORTING.PRODUCTION
domain_timezone: US / Eastern
communities:
  - id: 8571101
    name: Test_Community
actions:
  - action_type: SENSOR
    action_code: test_sensor
    abbreviation: TS
    dataset: test_dataset
    source_system: TEST
    parents: []
    schedule:
      crontab: "15 13 * * *"
      timezone: Etc/UTC
    query_reference:
      database_name: SDP
      query: SELECT 1
"""
        yaml_file = temp_yaml_file(yaml_content)
        is_valid, error = MPMConfig.validate_yaml_file(yaml_file)
        assert is_valid is False
        assert error is not None and ("deployment_version" in error.lower() or "required" in error.lower())

    def test_invalid_deployment_version_pattern(self, temp_yaml_file):
        """Test validation fails with invalid deployment_version pattern."""
        yaml_content = """
deployment_version: INVALID
domain_code: BS
warehouse:
  auto_suspend: 120
  max_cluster_count: 4
  scaling_policy: STANDARD
  warehouse_size: MEDIUM
  warehouse_type: SNOWPARK-OPTIMIZED
internal_stage: GENERIC_REPORTING.BS_005.REPORTING
external_stage: GENERIC_REPORTING.REPORTING.PRODUCTION
domain_timezone: US / Eastern
communities:
  - id: 8571101
    name: Test_Community
actions:
  - action_type: SENSOR
    action_code: test_sensor
    abbreviation: TS
    dataset: test_dataset
    source_system: TEST
    parents: []
    schedule:
      crontab: "15 13 * * *"
      timezone: Etc/UTC
    query_reference:
      database_name: SDP
      query: SELECT 1
"""
        yaml_file = temp_yaml_file(yaml_content)
        is_valid, error = MPMConfig.validate_yaml_file(yaml_file)
        assert is_valid is False
        assert error is not None and (
            isinstance(error, str) and ("pattern" in error.lower() or "does not match" in error.lower())
        )

    def test_invalid_action_type(self, temp_yaml_file):
        """Test validation fails with invalid action_type."""
        yaml_content = """
deployment_version: BS_005
domain_code: BS
warehouse:
  auto_suspend: 120
  max_cluster_count: 4
  scaling_policy: STANDARD
  warehouse_size: MEDIUM
  warehouse_type: SNOWPARK-OPTIMIZED
internal_stage: GENERIC_REPORTING.BS_005.REPORTING
external_stage: GENERIC_REPORTING.REPORTING.PRODUCTION
domain_timezone: US / Eastern
communities:
  - id: 8571101
    name: Test_Community
actions:
  - action_type: INVALID_TYPE
    action_code: test_action
    abbreviation: TA
    parents: []
    schedule:
      crontab: "15 13 * * *"
      timezone: Etc/UTC
    query_reference:
      database_name: SDP
      query: SELECT 1
"""
        yaml_file = temp_yaml_file(yaml_content)
        is_valid, error = MPMConfig.validate_yaml_file(yaml_file)
        assert is_valid is False
        # Schema validates action structure differently - checks required fields first
        assert error is not None and (
            "required" in error.lower() or "invalid_type" in error.lower() or "enum" in error.lower()
        )

    def test_missing_communities(self, temp_yaml_file):
        """Test validation fails when communities list is empty."""
        yaml_content = """
deployment_version: BS_005
domain_code: BS
warehouse:
  auto_suspend: 120
  max_cluster_count: 4
  scaling_policy: STANDARD
  warehouse_size: MEDIUM
  warehouse_type: SNOWPARK-OPTIMIZED
internal_stage: GENERIC_REPORTING.BS_005.REPORTING
external_stage: GENERIC_REPORTING.REPORTING.PRODUCTION
domain_timezone: US / Eastern
communities: []
actions:
  - action_type: SENSOR
    action_code: test_sensor
    abbreviation: TS
    dataset: test_dataset
    source_system: TEST
    parents: []
    schedule:
      crontab: "15 13 * * *"
      timezone: Etc/UTC
    query_reference:
      database_name: SDP
      query: SELECT 1
"""
        yaml_file = temp_yaml_file(yaml_content)
        is_valid, error = MPMConfig.validate_yaml_file(yaml_file)
        assert is_valid is False
        assert error is not None and (
            "non-empty" in error.lower() or "minitems" in error.lower() or "too short" in error.lower()
        )

    def test_invalid_crontab_pattern(self, temp_yaml_file):
        """Test validation fails with invalid crontab pattern."""
        yaml_content = """
deployment_version: BS_005
domain_code: BS
warehouse:
  auto_suspend: 120
  max_cluster_count: 4
  scaling_policy: STANDARD
  warehouse_size: MEDIUM
  warehouse_type: SNOWPARK-OPTIMIZED
internal_stage: GENERIC_REPORTING.BS_005.REPORTING
external_stage: GENERIC_REPORTING.REPORTING.PRODUCTION
domain_timezone: US / Eastern
communities:
  - id: 8571101
    name: Test_Community
actions:
  - action_type: SENSOR
    action_code: test_sensor
    abbreviation: TS
    dataset: test_dataset
    source_system: TEST
    parents: []
    schedule:
      crontab: "INVALID CRON"
      timezone: Etc/UTC
    query_reference:
      database_name: SDP
      query: SELECT 1
"""
        yaml_file = temp_yaml_file(yaml_content)
        is_valid, error = MPMConfig.validate_yaml_file(yaml_file)
        assert is_valid is False
        assert error is not None and ("pattern" in error.lower() or "does not match" in error.lower())

    def test_negative_warehouse_auto_suspend(self, temp_yaml_file):
        """Test validation fails with negative auto_suspend value."""
        yaml_content = """
deployment_version: BS_005
domain_code: BS
warehouse:
  auto_suspend: -1
  max_cluster_count: 4
  scaling_policy: STANDARD
  warehouse_size: MEDIUM
  warehouse_type: SNOWPARK-OPTIMIZED
internal_stage: GENERIC_REPORTING.BS_005.REPORTING
external_stage: GENERIC_REPORTING.REPORTING.PRODUCTION
domain_timezone: US / Eastern
communities:
  - id: 8571101
    name: Test_Community
actions:
  - action_type: SENSOR
    action_code: test_sensor
    abbreviation: TS
    dataset: test_dataset
    source_system: TEST
    parents: []
    schedule:
      crontab: "15 13 * * *"
      timezone: Etc/UTC
    query_reference:
      database_name: SDP
      query: SELECT 1
"""
        yaml_file = temp_yaml_file(yaml_content)
        is_valid, error = MPMConfig.validate_yaml_file(yaml_file)
        assert is_valid is False
        assert error is not None and ("minimum" in error.lower() or "less than" in error.lower())

    def test_invalid_warehouse_size(self, temp_yaml_file):
        """Test validation fails with invalid warehouse_size."""
        yaml_content = """
deployment_version: BS_005
domain_code: BS
warehouse:
  auto_suspend: 120
  max_cluster_count: 4
  scaling_policy: STANDARD
  warehouse_size: INVALID_SIZE
  warehouse_type: SNOWPARK-OPTIMIZED
internal_stage: GENERIC_REPORTING.BS_005.REPORTING
external_stage: GENERIC_REPORTING.REPORTING.PRODUCTION
domain_timezone: US / Eastern
communities:
  - id: 8571101
    name: Test_Community
actions:
  - action_type: SENSOR
    action_code: test_sensor
    abbreviation: TS
    dataset: test_dataset
    source_system: TEST
    parents: []
    schedule:
      crontab: "15 13 * * *"
      timezone: Etc/UTC
    query_reference:
      database_name: SDP
      query: SELECT 1
"""
        yaml_file = temp_yaml_file(yaml_content)
        is_valid, error = MPMConfig.validate_yaml_file(yaml_file)
        assert is_valid is False
        assert error is not None and ("enum" in error.lower() or "not one of" in error.lower())

    def test_file_not_found(self):
        """Test proper error handling for non-existent file."""
        is_valid, error = MPMConfig.validate_yaml_file("/nonexistent/path/file.yaml")
        assert is_valid is False
        assert error is not None and ("not found" in error.lower() or "file" in error.lower())
