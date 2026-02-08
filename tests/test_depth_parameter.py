"""Tests for depth parameter functionality in TableGenerator - controls dictionary flattening."""

import json
from pathlib import Path

import pytest

from yaml_shredder.table_generator import TableGenerator


@pytest.fixture
def nested_dict_data():
    """Sample nested dictionary structure for testing depth control."""
    return {
        "name": "MyApp",
        "version": "1.0",
        "deployment": {"env": "prod", "region": "us-east-1", "config": {"timeout": 30, "retries": 3}},
        "query_reference": {"sql": "SELECT * FROM table", "params": {"limit": 100}},
    }


def test_depth_none_flattens_all_dicts(nested_dict_data):
    """Test that max_depth=None (default) flattens all nested dictionaries."""
    gen = TableGenerator(max_depth=None)
    tables = gen.generate_tables(nested_dict_data, root_table_name="ROOT")

    # Root scalars go to descriptor table
    assert "ROOT" in tables
    root_table = tables["ROOT"]
    assert "name" in root_table.columns
    assert "version" in root_table.columns

    # Root-level dicts become separate tables, fully flattened
    assert "DEPLOYMENT" in tables
    deployment_table = tables["DEPLOYMENT"]
    assert "env" in deployment_table.columns
    assert "region" in deployment_table.columns
    assert "config_timeout" in deployment_table.columns
    assert "config_retries" in deployment_table.columns

    assert "QUERY_REFERENCE" in tables
    query_table = tables["QUERY_REFERENCE"]
    assert "sql" in query_table.columns
    assert "params_limit" in query_table.columns


def test_depth_0_no_dict_flattening(nested_dict_data):
    """Test that max_depth=0 keeps all nested dictionaries as JSON."""
    gen = TableGenerator(max_depth=0)
    tables = gen.generate_tables(nested_dict_data, root_table_name="ROOT")

    # Root scalars go to descriptor table
    assert "ROOT" in tables
    root_table = tables["ROOT"]
    assert "name" in root_table.columns
    assert "version" in root_table.columns

    # Root-level dicts become separate tables with nested dicts as JSON
    assert "DEPLOYMENT" in tables
    deployment_table = tables["DEPLOYMENT"]
    assert "env" in deployment_table.columns
    assert "region" in deployment_table.columns
    assert "config" in deployment_table.columns  # Kept as JSON

    # Nested config should be JSON string
    config_value = deployment_table["config"].values[0]
    assert isinstance(config_value, str)
    config_parsed = json.loads(config_value)
    assert config_parsed["timeout"] == 30

    assert "QUERY_REFERENCE" in tables
    query_table = tables["QUERY_REFERENCE"]
    assert "sql" in query_table.columns
    assert "params" in query_table.columns  # Kept as JSON


def test_depth_1_first_level_flattening(nested_dict_data):
    """Test that max_depth=1 keeps nested dictionaries as JSON (no flattening)."""
    gen = TableGenerator(max_depth=1)
    tables = gen.generate_tables(nested_dict_data, root_table_name="ROOT")

    # Root scalars go to descriptor table
    assert "ROOT" in tables
    root_table = tables["ROOT"]
    assert "name" in root_table.columns
    assert "version" in root_table.columns

    # Root-level dicts become separate tables with nested dicts as JSON
    assert "DEPLOYMENT" in tables
    deployment_table = tables["DEPLOYMENT"]
    assert "env" in deployment_table.columns
    assert "region" in deployment_table.columns
    assert "config" in deployment_table.columns  # Kept as JSON

    # Should NOT be flattened further
    assert "config_timeout" not in deployment_table.columns

    # Verify it's JSON
    config_value = deployment_table["config"].values[0]
    assert isinstance(config_value, str)
    config_parsed = json.loads(config_value)
    assert config_parsed["timeout"] == 30

    assert "QUERY_REFERENCE" in tables
    query_table = tables["QUERY_REFERENCE"]
    assert "sql" in query_table.columns
    assert "params" in query_table.columns  # Kept as JSON
    assert "params_limit" not in query_table.columns


def test_depth_2_two_level_flattening(nested_dict_data):
    """Test that max_depth=2 flattens first level, keeps second level as JSON."""
    gen = TableGenerator(max_depth=2)
    tables = gen.generate_tables(nested_dict_data, root_table_name="ROOT")

    # Root scalars go to descriptor table
    assert "ROOT" in tables
    root_table = tables["ROOT"]

    # Root-level dicts become separate tables, flattened one level
    assert "DEPLOYMENT" in tables
    deployment_table = tables["DEPLOYMENT"]
    assert "env" in deployment_table.columns
    assert "region" in deployment_table.columns
    assert "config_timeout" in deployment_table.columns
    assert "config_retries" in deployment_table.columns

    assert "QUERY_REFERENCE" in tables
    query_table = tables["QUERY_REFERENCE"]
    assert "sql" in query_table.columns
    assert "params_limit" in query_table.columns


def test_array_processing_independent_of_depth():
    """Test that arrays are always processed into tables regardless of dict depth."""
    data = {
        "items": [
            {"id": 1, "metadata": {"color": "red", "size": "large"}, "tags": [{"tag_id": 1, "tag_name": "urgent"}]}
        ]
    }

    # Even with depth=0, arrays should still create tables
    gen = TableGenerator(max_depth=0)
    tables = gen.generate_tables(data, root_table_name="ROOT")

    assert "ITEMS" in tables
    assert "ITEMS_tags" in tables

    # But dicts within arrays respect depth
    items_table = tables["ITEMS"]
    assert "metadata" in items_table.columns  # Kept as JSON at depth=0
    metadata_value = items_table["metadata"].values[0]
    assert isinstance(metadata_value, str)


def test_source_file_naming():
    """Test that source_file parameter affects root table naming."""
    data = {"field1": "value1", "field2": "value2"}

    # Without source_file
    gen1 = TableGenerator()
    tables1 = gen1.generate_tables(data, root_table_name="CUSTOM")
    assert "CUSTOM" in tables1

    # With source_file
    gen2 = TableGenerator()
    tables2 = gen2.generate_tables(data, source_file=Path("myfile.yaml"))
    assert "MYFILE" in tables2
    assert "CUSTOM" not in tables2


def test_backward_compatibility():
    """Test that default behavior (None depth) maintains full flattening."""
    data = {"scalar": "value", "level1": {"level2": {"level3": "value"}}}

    gen = TableGenerator()  # No max_depth specified
    tables = gen.generate_tables(data, root_table_name="ROOT")

    # Root scalar goes to descriptor table
    root_table = tables["ROOT"]
    assert "scalar" in root_table.columns

    # Root-level dict becomes separate table, fully flattened
    assert "LEVEL1" in tables
    level1_table = tables["LEVEL1"]
    assert "level2_level3" in level1_table.columns
