#!/usr/bin/env python
"""Quick test with just one YAML file."""

import json
from pathlib import Path

import yaml
from genson import SchemaBuilder

# Use just one file for quick test
yaml_file = Path("resources/master-mpm/BS/BS_005-mpm.yaml")

print(f"Processing: {yaml_file}")

with open(yaml_file) as f:
    data = yaml.safe_load(f)

print(f"Loaded YAML with {len(data)} top-level keys")
print(f"Keys: {list(data.keys())}")

# Build schema
builder = SchemaBuilder()
builder.add_object(data)
schema = builder.to_schema()

# Save
output = Path("resources/bs-mpm-schema.json")
with open(output, "w") as f:
    json.dump(schema, f, indent=2)

print("\n✓ Schema generated!")
print(f"  Properties: {len(schema.get('properties', {}))}")
print(f"  Output: {output}")
