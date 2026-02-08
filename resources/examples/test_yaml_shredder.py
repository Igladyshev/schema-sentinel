#!/usr/bin/env python
"""Comprehensive test of YAML shredder functionality."""

from pathlib import Path

import yaml

from yaml_shredder.ddl_generator import DDLGenerator
from yaml_shredder.schema_generator import SchemaGenerator
from yaml_shredder.structure_analyzer import StructureAnalyzer
from yaml_shredder.table_generator import TableGenerator


def main():
    """Test all YAML shredder components."""
    # Use one MPM file for testing
    yaml_file = Path("resources/master-mpm/XY/XY_123-mpm.yaml")

    print(f"\n{'=' * 60}")
    print("YAML SHREDDER - COMPREHENSIVE TEST")
    print(f"{'=' * 60}")
    print(f"\nInput file: {yaml_file}")

    # Load YAML
    with open(yaml_file) as f:
        data = yaml.safe_load(f)

    print(f"Loaded YAML with {len(data)} top-level keys: {list(data.keys())}")

    # 1. Generate Schema
    print(f"\n{'=' * 60}")
    print("STEP 1: SCHEMA GENERATION")
    print(f"{'=' * 60}")

    generator = SchemaGenerator()
    generator.add_yaml_file(yaml_file)
    generator.generate_schema()

    output_schema = Path("resources/bs-mpm-schema.json")
    generator.save_schema(output_schema)

    stats = generator.get_stats()
    print("\n✓ Schema generated:")
    print(f"  Properties: {stats['schema_properties']}")
    print(f"  Required fields: {stats['required_fields']}")
    print(f"  Saved to: {output_schema}")

    # 2. Analyze Structure
    print(f"\n{'=' * 60}")
    print("STEP 2: STRUCTURE ANALYSIS")
    print(f"{'=' * 60}")

    analyzer = StructureAnalyzer()
    analysis = analyzer.analyze(data)
    analyzer.print_summary(analysis)

    # 3. Generate Tables
    print(f"\n{'=' * 60}")
    print("STEP 3: TABLE GENERATION")
    print(f"{'=' * 60}\n")

    table_gen = TableGenerator()
    tables = table_gen.generate_tables(data, root_table_name="MPM_CONFIG")

    table_gen.print_summary()

    # Save tables
    output_dir = Path("resources/generated-tables")
    table_gen.save_tables(output_dir, format="csv")
    # 4. Generate DDL
    print(f"\n{'=' * 60}")
    print("STEP 4: DDL GENERATION")
    print(f"{'=' * 60}\n")

    ddl_gen = DDLGenerator(dialect="snowflake")
    ddl_gen.generate_ddl(tables, table_gen.relationships)

    ddl_gen.print_ddl()

    # Save DDL
    output_ddl = Path("resources/generated-ddl.sql")
    ddl_gen.save_ddl(output_ddl)

    print(f"\n{'=' * 60}")
    print("✓ YAML SHREDDER TEST COMPLETE!")
    print(f"{'=' * 60}\n")


if __name__ == "__main__":
    main()
