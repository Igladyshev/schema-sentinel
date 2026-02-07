#!/usr/bin/env python
"""Simple test of schema generation."""

import json
from pathlib import Path

import yaml
from genson import SchemaBuilder

# Find YAML files
mpm_dir = Path(".")
yaml_files = sorted(mpm_dir.rglob("*.yaml"))

print(f"Found {len(yaml_files)} YAML files:")
for f in yaml_files:
    print(f"  - {f}")

# Build schema
builder = SchemaBuilder()

for yaml_file in yaml_files:
    print(f"\nProcessing: {yaml_file.name}")
    with open(yaml_file) as f:
        data = yaml.safe_load(f)
        builder.add_object(data)
        print(f"  Keys: {list(data.keys())[:5]}...")

# Generate schema
schema = builder.to_schema()

# Save
output = Path("./example-schema.json")
with open(output, "w") as f:
    json.dump(schema, f, indent=2)

print("\n✓ Schema generated successfully!")
print(f"  Properties: {len(schema.get('properties', {}))}")
print(f"  Output: {output}")
print("\nTop-level properties:")
for prop in list(schema.get("properties", {}).keys())[:10]:
    prop_type = schema["properties"][prop].get("type", "unknown")
    print(f"  - {prop}: {prop_type}")
