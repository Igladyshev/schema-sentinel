"""Unit tests for MPM parser functionality."""

from pathlib import Path

import pytest

from snowflake_local_testing.mpm_parser import MPMConfig

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


class TestMPMConfigProperties:
    """Test MPMConfig property accessors."""

    def test_deployment_version(self, mpm_config):
        """Test deployment_version property."""
        assert mpm_config.deployment_version == "0.0.5"

    def test_domain_code(self, mpm_config):
        """Test domain_code property."""
        assert mpm_config.domain_code == "BS"

    def test_warehouse_config(self, mpm_config):
        """Test warehouse_config property."""
        warehouse = mpm_config.warehouse_config
        assert warehouse["auto_suspend"] == 120
        assert warehouse["max_cluster_count"] == 4
        assert warehouse["scaling_policy"] == "STANDARD"
        assert warehouse["warehouse_size"] == "MEDIUM"

    def test_internal_stage(self, mpm_config):
        """Test internal_stage property."""
        assert mpm_config.internal_stage == "GENERIC_REPORTING.BS_005.REPORTING"

    def test_external_stage(self, mpm_config):
        """Test external_stage property."""
        assert mpm_config.external_stage == "GENERIC_REPORTING.REPORTING.PRODUCTION"

    def test_domain_timezone(self, mpm_config):
        """Test domain_timezone property."""
        assert mpm_config.domain_timezone == "US / Eastern"

    def test_communities_list(self, mpm_config):
        """Test communities property."""
        communities = mpm_config.communities
        assert len(communities) == 2
        assert communities[0]["id"] == 8571101
        assert communities[0]["name"] == "Baha_Mar_Casino"
        assert communities[1]["id"] == 8421102
        assert communities[1]["name"] == "Atlantis_Paradise_Island_Atlantis_Casino"

    def test_actions_list(self, mpm_config):
        """Test actions property."""
        actions = mpm_config.actions
        assert len(actions) > 0
        # Verify we have both SENSOR and REPORT types
        action_types = {action["action_type"] for action in actions}
        assert "SENSOR" in action_types
        assert "REPORT" in action_types


class TestDeploymentInfo:
    """Test deployment information extraction."""

    def test_get_deployment_info_structure(self, mpm_config):
        """Test deployment info has correct structure."""
        deployment = mpm_config.get_deployment_info()

        required_fields = [
            "deployment_version",
            "domain_code",
            "warehouse",  # Now a nested object
            "internal_stage",
            "external_stage",
            "domain_timezone",
        ]

        for field in required_fields:
            assert field in deployment, f"Missing field: {field}"

        # Verify warehouse is a nested object with correct structure
        assert isinstance(deployment["warehouse"], dict)
        assert "auto_suspend" in deployment["warehouse"]
        assert "max_cluster_count" in deployment["warehouse"]

    def test_get_deployment_info_values(self, mpm_config):
        """Test deployment info has correct values."""
        deployment = mpm_config.get_deployment_info()

        assert deployment["deployment_version"] == "0.0.5"
        assert deployment["domain_code"] == "BS"
        # Access warehouse fields from nested object
        assert deployment["warehouse"]["auto_suspend"] == 120
        assert deployment["warehouse"]["max_cluster_count"] == 4
        assert deployment["warehouse"]["scaling_policy"] == "STANDARD"
        assert deployment["warehouse"]["warehouse_size"] == "MEDIUM"
        assert deployment["internal_stage"] == "GENERIC_REPORTING.BS_005.REPORTING"
        assert deployment["external_stage"] == "GENERIC_REPORTING.REPORTING.PRODUCTION"


class TestCommunitiesList:
    """Test communities list extraction."""

    def test_get_communities_list_count(self, mpm_config):
        """Test correct number of communities returned."""
        communities = mpm_config.get_communities_list()
        assert len(communities) == 2

    def test_get_communities_list_structure(self, mpm_config):
        """Test communities have correct structure."""
        communities = mpm_config.get_communities_list()

        for community in communities:
            assert "deployment_version" in community
            assert "domain_code" in community
            assert "community_id" in community
            assert "community_name" in community

    def test_get_communities_list_values(self, mpm_config):
        """Test communities have correct values."""
        communities = mpm_config.get_communities_list()

        # First community
        assert communities[0]["deployment_version"] == "0.0.5"
        assert communities[0]["domain_code"] == "BS"
        assert communities[0]["community_id"] == 8571101
        assert communities[0]["community_name"] == "Baha_Mar_Casino"

        # Second community
        assert communities[1]["community_id"] == 8421102
        assert communities[1]["community_name"] == "Atlantis_Paradise_Island_Atlantis_Casino"


class TestSensorActions:
    """Test sensor actions extraction."""

    def test_get_sensor_actions_count(self, mpm_config):
        """Test that sensor actions are extracted."""
        sensors = mpm_config.get_sensor_actions()
        assert len(sensors) > 0

    def test_get_sensor_actions_structure(self, mpm_config):
        """Test sensor actions have correct structure."""
        sensors = mpm_config.get_sensor_actions()

        required_fields = [
            "deployment_version",
            "domain_code",
            "action_type",
            "action_code",
            "abbreviation",
            "dataset",
            "source_system",
            "schedule",  # Nested object
            "start_date",  # datetime object
            "parents",  # Nested list
            "query_reference",  # Nested object
        ]

        for sensor in sensors:
            for field in required_fields:
                assert field in sensor, f"Missing field: {field} in sensor {sensor.get('action_code')}"
            # Verify nested objects
            assert isinstance(sensor["schedule"], dict)
            assert isinstance(sensor["parents"], list)
            assert isinstance(sensor["query_reference"], dict)

    def test_get_sensor_actions_values(self, mpm_config):
        """Test specific sensor action values."""
        sensors = mpm_config.get_sensor_actions()

        # Find a specific sensor to test
        retail_liability_sensor = next((s for s in sensors if s["action_code"] == "retail_liability_bets"), None)

        assert retail_liability_sensor is not None
        assert retail_liability_sensor["action_type"] == "SENSOR"
        assert retail_liability_sensor["abbreviation"] == "RLBS"
        assert retail_liability_sensor["dataset"] == "retail_liability_bets"
        assert retail_liability_sensor["source_system"] == "BE"
        assert retail_liability_sensor["deployment_version"] == "0.0.5"
        assert retail_liability_sensor["domain_code"] == "BS"

    def test_sensor_actions_only_sensors(self, mpm_config):
        """Test that only SENSOR type actions are returned."""
        sensors = mpm_config.get_sensor_actions()

        for sensor in sensors:
            assert sensor["action_type"] == "SENSOR"


class TestReportActions:
    """Test report actions extraction."""

    def test_get_report_actions_count(self, mpm_config):
        """Test that report actions are extracted."""
        reports = mpm_config.get_report_actions()
        assert len(reports) > 0

    def test_get_report_actions_structure(self, mpm_config):
        """Test report actions have correct structure."""
        reports = mpm_config.get_report_actions()

        required_fields = [
            "deployment_version",
            "domain_code",
            "action_type",
            "action_code",
            "abbreviation",
            "report_name",
            "report_file_pattern",
            "communities",  # Nested list
            "consumer_tags",  # Nested object
            "schedule",  # Nested object
            "start_date",  # datetime object
            "parents",  # Nested list
            "query_reference",  # Nested object
            "header_information",  # Nested object
            "pii_information",  # Nested object
        ]

        for report in reports:
            for field in required_fields:
                assert field in report, f"Missing field: {field} in report {report.get('action_code')}"
            # Verify nested objects
            assert isinstance(report["consumer_tags"], dict)
            assert isinstance(report["schedule"], dict)

    def test_get_report_actions_values(self, mpm_config):
        """Test specific report action values."""
        reports = mpm_config.get_report_actions()

        # Find a specific report to test
        liability_report = next((r for r in reports if r["action_code"] == "retail_liability_ticket_report"), None)

        assert liability_report is not None
        assert liability_report["action_type"] == "REPORT"
        assert liability_report["abbreviation"] == "RSPLTR"
        assert liability_report["report_name"] == "Retail Sports Pool Liability Ticket Report"
        # Access consumer tags from nested object (keys are capitalized in YAML)
        assert liability_report["consumer_tags"]["Finance"] is True
        assert liability_report["consumer_tags"]["AML"] is False
        assert liability_report["consumer_tags"]["Regulatory"] is False
        assert liability_report["deployment_version"] == "0.0.5"
        assert liability_report["domain_code"] == "BS"

    def test_report_actions_only_reports(self, mpm_config):
        """Test that only REPORT type actions are returned."""
        reports = mpm_config.get_report_actions()

        for report in reports:
            assert report["action_type"] == "REPORT"

    def test_report_with_communities(self, mpm_config):
        """Test report action with communities list."""
        reports = mpm_config.get_report_actions()

        # Find a report with communities
        community_report = next(
            (r for r in reports if r["action_code"] == "retail_liability_ticket_report_per_community"), None
        )

        assert community_report is not None
        assert "Baha_Mar_Casino" in community_report["communities"]
        assert "Atlantis_Paradise_Island_Atlantis_Casino" in community_report["communities"]

    def test_report_with_parents(self, mpm_config):
        """Test report action with parent dependencies."""
        reports = mpm_config.get_report_actions()

        # Find a report with parents
        report_with_parents = next((r for r in reports if r["action_code"] == "retail_liability_ticket_report"), None)

        assert report_with_parents is not None
        assert "retail_liability_bets" in report_with_parents["parents"]


class TestActionCounts:
    """Test counts of different action types."""

    def test_total_actions_count(self, mpm_config):
        """Test total number of actions matches sensors + reports."""
        all_actions = mpm_config.actions
        sensors = mpm_config.get_sensor_actions()
        reports = mpm_config.get_report_actions()

        assert len(all_actions) == len(sensors) + len(reports)

    def test_sensors_vs_reports_count(self, mpm_config):
        """Test we have both sensors and reports."""
        sensors = mpm_config.get_sensor_actions()
        reports = mpm_config.get_report_actions()

        assert len(sensors) > 0, "Should have at least one sensor"
        assert len(reports) > 0, "Should have at least one report"
        assert len(reports) > len(sensors), "Typically more reports than sensors"
