#!/usr/bin/env python
"""Test script to generate JSON schema from MPM YAML files."""

from pathlib import Path

from yaml_shredder.schema_generator import generate_schema_from_directory


def main():
    """Generate schema from MPM YAML files."""
    # Set paths
    project_root = Path(__file__).parent
    mpm_directory = project_root / "resources" / "master-mpm"
    output_file = project_root / "resources" / "generated-mpm-schema.json"

    print(f"Scanning directory: {mpm_directory}")
    print(f"Output file: {output_file}")
    print()

    # Generate schema
    schema = generate_schema_from_directory(directory=mpm_directory, pattern="*.yaml", output_file=output_file)

    print()
    print("Schema preview (top-level properties):")
    for prop in schema.get("properties", {}).keys():
        print(f"  - {prop}")

    print()
    print(f"Full schema saved to: {output_file}")


if __name__ == "__main__":
    main()
