"""Tests for YAML Comparator functionality."""

import sqlite3
from pathlib import Path

import pytest
import yaml

from schema_sentinel.yaml_comparator import YAMLComparator


@pytest.fixture
def temp_dir(tmp_path):
    """Create a temporary directory for test databases."""
    return tmp_path / "test_dbs"


@pytest.fixture
def sample_yaml_files(tmp_path):
    """Create sample YAML files for testing."""
    yaml1 = tmp_path / "config1.yaml"
    yaml2 = tmp_path / "config2.yaml"

    # YAML 1: Basic deployment config
    yaml1.write_text("""
deployment:
  version: 1.0
  environment: production
  servers:
    - name: server1
      ip: 192.168.1.1
      port: 8080
    - name: server2
      ip: 192.168.1.2
      port: 8080
  databases:
    - name: main_db
      type: postgresql
      replicas: 3
""")

    # YAML 2: Modified deployment config
    yaml2.write_text("""
deployment:
  version: 1.1
  environment: production
  servers:
    - name: server1
      ip: 192.168.1.1
      port: 8080
    - name: server3
      ip: 192.168.1.3
      port: 9090
  databases:
    - name: main_db
      type: postgresql
      replicas: 5
    - name: cache_db
      type: redis
      replicas: 2
""")

    return yaml1, yaml2


def test_yaml_comparator_initialization(temp_dir):
    """Test YAMLComparator initialization."""
    comparator = YAMLComparator(output_dir=temp_dir)
    assert comparator.output_dir == temp_dir
    assert temp_dir.exists()


def test_load_yaml_to_db(sample_yaml_files, temp_dir):
    """Test loading YAML file into SQLite database."""
    yaml1, _ = sample_yaml_files
    comparator = YAMLComparator(output_dir=temp_dir)

    db_path = comparator.load_yaml_to_db(yaml1, root_table_name="deployment")

    assert db_path.exists()
    assert db_path.suffix == ".db"

    # Verify database has tables
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]
    conn.close()

    assert len(tables) > 0
    # TableGenerator creates separate tables for nested arrays
    assert "DEPLOYMENT_SERVERS" in tables
    assert "DEPLOYMENT_DATABASES" in tables


def test_get_table_info(sample_yaml_files, temp_dir):
    """Test retrieving table schema information."""
    yaml1, _ = sample_yaml_files
    comparator = YAMLComparator(output_dir=temp_dir)

    db_path = comparator.load_yaml_to_db(yaml1, root_table_name="deployment")
    table_info = comparator.get_table_info(db_path)

    assert isinstance(table_info, dict)
    assert len(table_info) > 0
    # TableGenerator creates separate tables for nested arrays
    assert "DEPLOYMENT_SERVERS" in table_info
    assert "DEPLOYMENT_DATABASES" in table_info

    # Check schema DataFrame structure for one of the tables
    servers_schema = table_info["DEPLOYMENT_SERVERS"]
    assert "name" in servers_schema.columns
    assert "type" in servers_schema.columns


def test_get_row_counts(sample_yaml_files, temp_dir):
    """Test retrieving row counts for tables."""
    yaml1, _ = sample_yaml_files
    comparator = YAMLComparator(output_dir=temp_dir)

    db_path = comparator.load_yaml_to_db(yaml1, root_table_name="deployment")
    row_counts = comparator.get_row_counts(db_path)

    assert isinstance(row_counts, dict)
    assert len(row_counts) > 0
    assert all(isinstance(count, int) for count in row_counts.values())


def test_compare_databases(sample_yaml_files, temp_dir):
    """Test comparing two SQLite databases."""
    yaml1, yaml2 = sample_yaml_files
    comparator = YAMLComparator(output_dir=temp_dir)

    db1_path = comparator.load_yaml_to_db(yaml1, root_table_name="deployment")
    db2_path = comparator.load_yaml_to_db(yaml2, root_table_name="deployment")

    comparison = comparator.compare_databases(db1_path, db2_path)

    assert "db1_name" in comparison
    assert "db2_name" in comparison
    assert "common_tables" in comparison
    assert "tables_only_in_db1" in comparison
    assert "tables_only_in_db2" in comparison
    assert "schema_differences" in comparison
    assert "row_count_differences" in comparison

    # Verify comparison detected differences
    assert len(comparison["common_tables"]) > 0


def test_generate_report(sample_yaml_files, temp_dir, tmp_path):
    """Test generating markdown report from comparison."""
    yaml1, yaml2 = sample_yaml_files
    comparator = YAMLComparator(output_dir=temp_dir)

    db1_path = comparator.load_yaml_to_db(yaml1, root_table_name="deployment")
    db2_path = comparator.load_yaml_to_db(yaml2, root_table_name="deployment")

    comparison = comparator.compare_databases(db1_path, db2_path)
    report_path = tmp_path / "test_report.md"

    report = comparator.generate_report(comparison, output_path=report_path)

    assert isinstance(report, str)
    assert len(report) > 0
    assert "# YAML Comparison Report" in report
    assert report_path.exists()

    # Verify report contents
    with open(report_path) as f:
        saved_report = f.read()
    assert saved_report == report


def test_compare_yaml_files_complete_workflow(sample_yaml_files, temp_dir, tmp_path):
    """Test complete YAML comparison workflow."""
    yaml1, yaml2 = sample_yaml_files
    comparator = YAMLComparator(output_dir=temp_dir)

    report_path = tmp_path / "comparison.md"

    report = comparator.compare_yaml_files(
        yaml1_path=yaml1,
        yaml2_path=yaml2,
        output_report=report_path,
        keep_dbs=False,
        root_table_name="deployment",
    )

    assert isinstance(report, str)
    assert len(report) > 0
    assert report_path.exists()

    # Verify databases were cleaned up
    db1_path = temp_dir / f"{yaml1.stem}.db"
    db2_path = temp_dir / f"{yaml2.stem}.db"
    assert not db1_path.exists()
    assert not db2_path.exists()


def test_compare_yaml_files_keep_dbs(sample_yaml_files, temp_dir, tmp_path):
    """Test YAML comparison with database preservation."""
    yaml1, yaml2 = sample_yaml_files
    comparator = YAMLComparator(output_dir=temp_dir)

    report_path = tmp_path / "comparison.md"

    report = comparator.compare_yaml_files(
        yaml1_path=yaml1,
        yaml2_path=yaml2,
        output_report=report_path,
        keep_dbs=True,
        root_table_name="deployment",
    )

    assert isinstance(report, str)
    assert report_path.exists()

    # Verify databases were kept
    db1_path = temp_dir / f"{yaml1.stem}.db"
    db2_path = temp_dir / f"{yaml2.stem}.db"
    assert db1_path.exists()
    assert db2_path.exists()


def test_missing_yaml_file(temp_dir):
    """Test error handling for missing YAML file."""
    comparator = YAMLComparator(output_dir=temp_dir)

    with pytest.raises(FileNotFoundError):
        comparator.load_yaml_to_db(Path("nonexistent.yaml"))


def test_table_names_with_special_characters(temp_dir, tmp_path):
    """Test that table names with hyphens and other special characters are handled correctly."""
    # Create YAML files with structures that will generate table names with hyphens
    yaml1 = tmp_path / "DC_005-mpm.yaml"
    yaml1.write_text("""
DC_005-MPM:
  version: 1.0
  deployment:
    environment: production
  communities:
    - name: community1
      id: 1
    - name: community2
      id: 2
  actions:
    - action_id: A1
      description: First action
    - action_id: A2
      description: Second action
""")

    yaml2 = tmp_path / "CO_005-mpm.yaml"
    yaml2.write_text("""
CO_005-MPM:
  version: 1.1
  deployment:
    environment: staging
  actions:
    - action_id: A1
      description: Modified action
    - action_id: A3
      description: New action
""")

    comparator = YAMLComparator(output_dir=temp_dir)

    # This should not raise any SQL syntax errors
    db1_path = comparator.load_yaml_to_db(yaml1)
    db2_path = comparator.load_yaml_to_db(yaml2)

    # Verify databases exist
    assert db1_path.exists()
    assert db2_path.exists()

    # Get table info - this will test the PRAGMA table_info query with special chars
    table_info1 = comparator.get_table_info(db1_path)
    table_info2 = comparator.get_table_info(db2_path)

    # Verify we can get table info
    assert isinstance(table_info1, dict)
    assert isinstance(table_info2, dict)
    assert len(table_info1) > 0
    assert len(table_info2) > 0

    # Get row counts - this will test the SELECT COUNT query with special chars
    row_counts1 = comparator.get_row_counts(db1_path)
    row_counts2 = comparator.get_row_counts(db2_path)

    # Verify we can get row counts
    assert isinstance(row_counts1, dict)
    assert isinstance(row_counts2, dict)
    assert len(row_counts1) > 0
    assert len(row_counts2) > 0

    # Test full comparison workflow
    comparison = comparator.compare_databases(db1_path, db2_path)

    # Verify comparison completed successfully
    assert "db1_name" in comparison
    assert "db2_name" in comparison
    assert "common_tables" in comparison


def test_sync_yaml_files_report_only(temp_dir, tmp_path):
    """Test sync workflow creates detailed markdown report in report-only mode."""
    left_file = tmp_path / "left.yaml"
    right_file = tmp_path / "right.yaml"
    report_file = tmp_path / "sync_report.md"

    left_file.write_text(
        """
root:
  app:
    name: app-a
    replicas: 2
  feature:
    enabled: true
"""
    )
    right_file.write_text(
        """
root:
  app:
    name: app-b
    replicas: 1
  feature:
    enabled: false
"""
    )

    comparator = YAMLComparator(output_dir=temp_dir)
    result = comparator.sync_yaml_files(
        left_file=left_file,
        right_file=right_file,
        output_report=report_file,
        merge_direction="none",
        root_table_name="root",
    )

    assert report_file.exists()
    assert result["report_path"] == report_file
    assert "YAML Sync Discrepancy Details" in result["report"]
    assert "Different Values" in result["report"]
    assert result["merged_outputs"] == {}


def test_sync_yaml_files_schema_validation(temp_dir, tmp_path):
    """Test sync workflow fails when schemas are different."""
    left_file = tmp_path / "left.yaml"
    right_file = tmp_path / "right.yaml"

    left_file.write_text(
        """
root:
  app:
    name: app-a
    replicas: 2
"""
    )
    right_file.write_text(
        """
root:
  app:
    name: app-b
    ports:
      - 8080
"""
    )

    comparator = YAMLComparator(output_dir=temp_dir)

    with pytest.raises(ValueError, match="same schema"):
        comparator.sync_yaml_files(left_file=left_file, right_file=right_file)


def test_sync_yaml_files_left_to_right_merge(temp_dir, tmp_path):
    """Test left-to-right sync merge updates right content from left source."""
    left_file = tmp_path / "left.yaml"
    right_file = tmp_path / "right.yaml"
    report_file = tmp_path / "sync_report.md"

    left_file.write_text(
        """
root:
  app:
    name: canonical
    replicas: 3
"""
    )
    right_file.write_text(
        """
root:
  app:
    name: drifted
    replicas: 1
"""
    )

    comparator = YAMLComparator(output_dir=temp_dir)
    result = comparator.sync_yaml_files(
        left_file=left_file,
        right_file=right_file,
        output_report=report_file,
        merge_direction="left-to-right",
        root_table_name="root",
    )

    with open(right_file) as f:
        merged_right = yaml.safe_load(f)

    assert merged_right["root"]["app"]["name"] == "canonical"
    assert merged_right["root"]["app"]["replicas"] == 3
    assert "right" in result["merged_outputs"]


def test_sync_discrepancy_paths_use_identifier_key(temp_dir, tmp_path):
    """Test sync discrepancy paths use a dynamic identifier key instead of list index."""
    left_file = tmp_path / "left.yaml"
    right_file = tmp_path / "right.yaml"
    report_file = tmp_path / "sync_report.md"

    left_file.write_text(
        """
root:
  actions:
    - action_code: ACT_100
      parents:
        - etl.ROSI.player
        - etl.ROSI.businessactivity
  servers:
    - name: web01
      ip: 10.0.0.1
    - name: web02
      ip: 10.0.0.2
"""
    )
    right_file.write_text(
        """
root:
  actions:
    - action_code: ACT_100
      parents:
        - player
        - etl.ROSI.businessactivity
  servers:
    - name: web01
      ip: 10.0.0.99
    - name: web02
      ip: 10.0.0.2
"""
    )

    comparator = YAMLComparator(output_dir=temp_dir)
    result = comparator.sync_yaml_files(
        left_file=left_file,
        right_file=right_file,
        output_report=report_file,
        merge_direction="none",
        root_table_name="root",
    )

    diff_paths = [item["path"] for item in result["discrepancies"]["different_values"]]
    # actions list uses action_code as identifier
    assert "$.root.actions[ACT_100].parents[0]" in diff_paths
    # servers list uses name as identifier
    assert "$.root.servers[web01].ip" in diff_paths
