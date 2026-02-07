#!/usr/bin/env python
"""Test schema generation from YAML file."""

import json
from pathlib import Path

import yaml
from genson import SchemaBuilder


def test_schema_generation():
    """Test that schema can be generated from example YAML data."""
    # Use example data file for schema generation test
    yaml_file = Path(__file__).parent.parent / "resources/examples/example-data.yaml"

    assert yaml_file.exists(), f"Example data file not found: {yaml_file}"

    # Load YAML
    with open(yaml_file) as f:
        data = yaml.safe_load(f)

    assert isinstance(data, dict), "YAML data should be a dictionary"
    assert len(data) > 0, "YAML data should not be empty"

    # Build schema
    builder = SchemaBuilder()
    builder.add_object(data)
    schema = builder.to_schema()

    # Verify schema structure
    assert "type" in schema, "Schema should have a 'type' field"
    assert schema["type"] == "object", "Schema type should be 'object'"
    assert "properties" in schema, "Schema should have 'properties'"
    assert len(schema["properties"]) > 0, "Schema should have at least one property"

    # Save to resources directory
    output = Path(__file__).parent.parent / "resources/example-schema-generated.json"
    with open(output, "w") as f:
        json.dump(schema, f, indent=2)

    assert output.exists(), f"Output file should be created: {output}"

    print("\n✓ Schema generated successfully!")
    print(f"  Input: {yaml_file}")
    print(f"  Properties: {len(schema.get('properties', {}))}")
    print(f"  Output: {output}")
