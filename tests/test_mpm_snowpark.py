"""Unit tests for MPM Snowpark integration."""

from pathlib import Path
from unittest.mock import MagicMock

import pytest

from snowflake_local_testing.mpm_parser import MPMConfig
from snowflake_local_testing.mpm_snowpark import (
    COMMUNITY_STRUCT,
    DEPLOYMENT_STRUCT,
    REPORT_ACTION_STRUCT,
    SENSOR_ACTION_STRUCT,
    MPMSnowparkSaver,
)

# Check if MPM data is available (not in public repo)
MPM_DATA_DIR = Path(__file__).parent.parent / "resources" / "master-mpm"
MPM_DATA_AVAILABLE = MPM_DATA_DIR.exists()

pytestmark = pytest.mark.skipif(
    not MPM_DATA_AVAILABLE, reason="MPM data not available (proprietary files not in public repo)"
)


@pytest.fixture
def valid_yaml_path():
    """Path to valid YAML test file."""
    return Path(__file__).parent.parent / "resources" / "master-mpm" / "BS" / "BS_005-mpm.yaml"


@pytest.fixture
def mpm_config(valid_yaml_path):
    """Load MPM configuration from test file."""
    return MPMConfig(valid_yaml_path)


@pytest.fixture
def mock_session():
    """Create a mock Snowpark session."""
    session = MagicMock()

    # Mock SQL execution
    sql_result = MagicMock()
    sql_result.collect.return_value = []
    session.sql.return_value = sql_result

    # Mock dataframe creation
    mock_df = MagicMock()
    mock_write = MagicMock()
    mock_mode = MagicMock()
    mock_mode.save_as_table.return_value = None
    mock_write.mode.return_value = mock_mode
    mock_df.write = mock_write
    session.create_dataframe.return_value = mock_df

    # Mock table reads
    mock_table_df = MagicMock()
    mock_table_df.filter.return_value = mock_table_df
    mock_table_df.count.return_value = 1
    session.table.return_value = mock_table_df

    return session


@pytest.fixture
def saver(mock_session):
    """Create MPMSnowparkSaver with mock session."""
    return MPMSnowparkSaver(mock_session, database="TEST_DB", schema="TEST_SCHEMA")


class TestMPMSnowparkSaverInit:
    """Test MPMSnowparkSaver initialization."""

    def test_initialization(self, mock_session):
        """Test saver initializes correctly."""
        saver = MPMSnowparkSaver(mock_session, database="TEST_DB", schema="TEST_SCHEMA")

        assert saver.session == mock_session
        assert saver.database == "TEST_DB"
        assert saver.schema == "TEST_SCHEMA"

    def test_schema_creation_on_init(self, mock_session):
        """Test that database and schema are created on init."""
        _ = MPMSnowparkSaver(mock_session, database="TEST_DB", schema="TEST_SCHEMA")

        # Verify SQL was called to create database and schema
        calls = mock_session.sql.call_args_list
        assert len(calls) >= 2

        # Check database creation call (now with quoted identifiers)
        db_call = any('CREATE DATABASE IF NOT EXISTS "TEST_DB"' in str(c) for c in calls)
        assert db_call, "Database creation SQL not called"

        # Check schema creation call (now with quoted identifiers)
        schema_call = any('CREATE SCHEMA IF NOT EXISTS "TEST_DB"."TEST_SCHEMA"' in str(c) for c in calls)
        assert schema_call, "Schema creation SQL not called"


class TestSaveDeployment:
    """Test saving deployment configuration."""

    def test_save_deployment(self, saver, mpm_config, mock_session):
        """Test saving deployment data."""
        deployment = mpm_config.get_deployment_info()
        saver.save_deployment(deployment)

        # Verify create_dataframe was called with deployment data
        mock_session.create_dataframe.assert_called()
        call_args = mock_session.create_dataframe.call_args

        # Check data
        data_arg = call_args[0][0]
        assert len(data_arg) == 1
        assert data_arg[0]["deployment_version"] == "0.0.5"
        assert data_arg[0]["domain_code"] == "BS"

        # Check schema
        schema_arg = call_args[1]["schema"]
        assert schema_arg == DEPLOYMENT_STRUCT

    def test_save_deployment_with_mode(self, saver, mpm_config, mock_session):
        """Test saving deployment with different write modes."""
        deployment = mpm_config.get_deployment_info()

        # Test append mode
        saver.save_deployment(deployment, mode="append")
        mock_df = mock_session.create_dataframe.return_value
        mock_df.write.mode.assert_called_with("append")

        # Test overwrite mode
        saver.save_deployment(deployment, mode="overwrite")
        mock_df.write.mode.assert_called_with("overwrite")


class TestSaveCommunities:
    """Test saving communities list."""

    def test_save_communities(self, saver, mpm_config, mock_session):
        """Test saving communities data."""
        communities = mpm_config.get_communities_list()
        saver.save_communities(communities)

        # Verify create_dataframe was called
        mock_session.create_dataframe.assert_called()
        call_args = mock_session.create_dataframe.call_args

        # Check data
        data_arg = call_args[0][0]
        assert len(data_arg) == 2
        assert data_arg[0]["community_id"] == 8571101
        assert data_arg[0]["community_name"] == "Baha_Mar_Casino"

        # Check schema
        schema_arg = call_args[1]["schema"]
        assert schema_arg == COMMUNITY_STRUCT

    def test_save_empty_communities(self, saver, mock_session):
        """Test saving empty communities list does nothing."""
        saver.save_communities([])

        # Should not create dataframe for empty list
        mock_session.create_dataframe.assert_not_called()


class TestSaveSensorActions:
    """Test saving sensor actions."""

    def test_save_sensor_actions(self, saver, mpm_config, mock_session):
        """Test saving sensor actions data."""
        sensors = mpm_config.get_sensor_actions()
        saver.save_sensor_actions(sensors)

        # Verify create_dataframe was called
        mock_session.create_dataframe.assert_called()
        call_args = mock_session.create_dataframe.call_args

        # Check data
        data_arg = call_args[0][0]
        assert len(data_arg) > 0
        assert all(s["action_type"] == "SENSOR" for s in data_arg)

        # Check schema
        schema_arg = call_args[1]["schema"]
        assert schema_arg == SENSOR_ACTION_STRUCT

    def test_save_empty_sensors(self, saver, mock_session):
        """Test saving empty sensor actions list does nothing."""
        saver.save_sensor_actions([])

        # Should not create dataframe for empty list
        mock_session.create_dataframe.assert_not_called()


class TestSaveReportActions:
    """Test saving report actions."""

    def test_save_report_actions(self, saver, mpm_config, mock_session):
        """Test saving report actions data."""
        reports = mpm_config.get_report_actions()
        saver.save_report_actions(reports)

        # Verify create_dataframe was called
        mock_session.create_dataframe.assert_called()
        call_args = mock_session.create_dataframe.call_args

        # Check data
        data_arg = call_args[0][0]
        assert len(data_arg) > 0
        assert all(r["action_type"] == "REPORT" for r in data_arg)

        # Check schema
        schema_arg = call_args[1]["schema"]
        assert schema_arg == REPORT_ACTION_STRUCT

    def test_save_empty_reports(self, saver, mock_session):
        """Test saving empty report actions list does nothing."""
        saver.save_report_actions([])

        # Should not create dataframe for empty list
        mock_session.create_dataframe.assert_not_called()


class TestSaveAll:
    """Test saving all entities at once."""

    def test_save_all(self, saver, mpm_config, mock_session):
        """Test saving all MPM entities."""
        deployment = mpm_config.get_deployment_info()
        communities = mpm_config.get_communities_list()
        sensors = mpm_config.get_sensor_actions()
        reports = mpm_config.get_report_actions()

        result = saver.save_all(deployment, communities, sensors, reports)

        # Verify counts
        assert result["deployments"] == 1
        assert result["communities"] == len(communities)
        assert result["sensor_actions"] == len(sensors)
        assert result["report_actions"] == len(reports)

        # Verify create_dataframe was called 4 times (one for each entity type)
        assert mock_session.create_dataframe.call_count == 4

    def test_save_all_with_mode(self, saver, mpm_config, mock_session):
        """Test save_all respects write mode."""
        deployment = mpm_config.get_deployment_info()
        communities = mpm_config.get_communities_list()
        sensors = mpm_config.get_sensor_actions()
        reports = mpm_config.get_report_actions()

        saver.save_all(deployment, communities, sensors, reports, mode="overwrite")

        # Verify mode was set correctly for all saves
        mock_df = mock_session.create_dataframe.return_value
        calls = mock_df.write.mode.call_args_list
        assert all(call[0][0] == "overwrite" for call in calls)


class TestReadOperations:
    """Test read operations from Snowflake."""

    def test_read_deployment(self, saver, mock_session):
        """Test reading deployment configuration."""
        df = saver.read_deployment("BS_005")

        assert df is not None
        mock_session.table.assert_called_with('"TEST_DB"."TEST_SCHEMA"."DEPLOYMENTS"')

    def test_read_deployment_not_found(self, saver, mock_session):
        """Test reading non-existent deployment returns None."""
        mock_table_df = mock_session.table.return_value
        mock_table_df.count.return_value = 0

        df = saver.read_deployment("NONEXISTENT")
        assert df is None

    def test_read_communities(self, saver, mock_session):
        """Test reading communities."""
        df = saver.read_communities("BS_005")

        assert df is not None
        mock_session.table.assert_called_with('"TEST_DB"."TEST_SCHEMA"."COMMUNITIES"')

    def test_read_sensor_actions(self, saver, mock_session):
        """Test reading sensor actions."""
        df = saver.read_sensor_actions("BS_005")

        assert df is not None
        mock_session.table.assert_called_with('"TEST_DB"."TEST_SCHEMA"."SENSOR_ACTIONS"')

    def test_read_report_actions(self, saver, mock_session):
        """Test reading report actions."""
        df = saver.read_report_actions("BS_005")

        assert df is not None
        mock_session.table.assert_called_with('"TEST_DB"."TEST_SCHEMA"."REPORT_ACTIONS"')


class TestStructTypeDefinitions:
    """Test Snowpark struct type definitions."""

    def test_deployment_struct_fields(self):
        """Test DEPLOYMENT_STRUCT has correct fields."""
        field_names = [field.name for field in DEPLOYMENT_STRUCT.fields]

        expected_fields = [
            "DEPLOYMENT_VERSION",
            "DOMAIN_CODE",
            "WAREHOUSE",  # Now a single VARIANT field
            "INTERNAL_STAGE",
            "EXTERNAL_STAGE",
            "DOMAIN_TIMEZONE",
        ]

        assert field_names == expected_fields

    def test_community_struct_fields(self):
        """Test COMMUNITY_STRUCT has correct fields."""
        field_names = [field.name for field in COMMUNITY_STRUCT.fields]

        expected_fields = [
            "DEPLOYMENT_VERSION",
            "DOMAIN_CODE",
            "COMMUNITY_ID",
            "COMMUNITY_NAME",
        ]

        assert field_names == expected_fields

    def test_sensor_action_struct_fields(self):
        """Test SENSOR_ACTION_STRUCT has correct fields."""
        field_names = [field.name for field in SENSOR_ACTION_STRUCT.fields]

        assert "ACTION_TYPE" in field_names
        assert "ACTION_CODE" in field_names
        assert "DATASET" in field_names
        assert "SOURCE_SYSTEM" in field_names
        assert "SCHEDULE" in field_names  # VARIANT field
        assert "START_DATE" in field_names  # TimestampType field
        assert "PARENTS" in field_names  # VARIANT field
        assert "QUERY_REFERENCE" in field_names  # VARIANT field (combines query_database, query_schema, query_name)

    def test_report_action_struct_fields(self):
        """Test REPORT_ACTION_STRUCT has correct fields."""
        field_names = [field.name for field in REPORT_ACTION_STRUCT.fields]

        assert "ACTION_TYPE" in field_names
        assert "ACTION_CODE" in field_names
        assert "REPORT_NAME" in field_names
        assert "COMMUNITIES" in field_names  # VARIANT field
        assert (
            "CONSUMER_TAGS" in field_names
        )  # VARIANT field (replaces consumer_tag_aml, consumer_tag_finance, consumer_tag_regulatory)
        assert "SCHEDULE" in field_names  # VARIANT field
        assert "START_DATE" in field_names  # TimestampType field
        assert "PARENTS" in field_names  # VARIANT field
        assert "QUERY_REFERENCE" in field_names  # VARIANT field
        assert "HEADER_INFORMATION" in field_names  # VARIANT field
        assert "PII_INFORMATION" in field_names  # VARIANT field


class TestFullWorkflow:
    """Test complete workflow from YAML to Snowflake."""

    def test_complete_workflow(self, mock_session, valid_yaml_path):
        """Test loading YAML, extracting entities, and saving to Snowflake."""
        # Load configuration
        config = MPMConfig(valid_yaml_path)

        # Extract entities
        deployment = config.get_deployment_info()
        communities = config.get_communities_list()
        sensors = config.get_sensor_actions()
        reports = config.get_report_actions()

        # Verify extractions worked
        assert deployment["deployment_version"] == "0.0.5"
        assert len(communities) == 2
        assert len(sensors) > 0
        assert len(reports) > 0

        # Create saver and save all
        saver = MPMSnowparkSaver(mock_session)
        result = saver.save_all(deployment, communities, sensors, reports)

        # Verify save results
        assert result["deployments"] == 1
        assert result["communities"] == 2
        assert result["sensor_actions"] > 0
        assert result["report_actions"] > 0
