#!/usr/bin/env python
"""Example showing DDL generation from YAML shredder tables."""

import pandas as pd

from yaml_shredder.ddl_generator import DDLGenerator

# Example: Simulate tables that would be generated from YAML shredder
# These represent a typical MPM configuration structure

# Parent table: deployments
deployments_df = pd.DataFrame(
    {
        "id": [1, 2],
        "deployment_code": ["XY_123", "AB_456"],
        "name": ["Region X Deployment", "Region Y Deployment"],
        "active": [True, True],
    }
)

# Child table: communities (related to deployments)
communities_df = pd.DataFrame(
    {
        "id": [1, 2, 3],
        "parent_id": [1, 1, 2],
        "name": ["Community A", "Community B", "Community C"],
        "population": [5000, 3500, 4200],
    }
)

# Child table: sensor_actions (related to deployments)
sensor_actions_df = pd.DataFrame(
    {
        "id": [1, 2, 3, 4],
        "parent_id": [1, 1, 2, 2],
        "sensor_type": ["temperature", "humidity", "motion", "temperature"],
        "threshold": [75.5, 60.0, None, 80.0],
        "enabled": [True, True, False, True],
    }
)

# Collect tables
tables = {
    "deployments": deployments_df,
    "communities": communities_df,
    "sensor_actions": sensor_actions_df,
}

# Define relationships (foreign keys)
relationships = [
    {
        "child_table": "communities",
        "parent_table": "deployments",
        "foreign_keys": ["id"],
    },
    {
        "child_table": "sensor_actions",
        "parent_table": "deployments",
        "foreign_keys": ["id"],
    },
]

print("=" * 70)
print("DDL GENERATION EXAMPLE")
print("=" * 70)
print(f"\nTables to generate: {list(tables.keys())}")
print(f"Relationships: {len(relationships)}")

# Generate DDL for Snowflake
print("\n" + "=" * 70)
print("SNOWFLAKE DDL")
print("=" * 70)

snowflake_gen = DDLGenerator(dialect="snowflake")
snowflake_ddl = snowflake_gen.generate_ddl(tables, relationships)
snowflake_gen.print_ddl()
snowflake_gen.save_ddl("resources/example-snowflake-ddl.sql")

# Generate DDL for PostgreSQL
print("\n" + "=" * 70)
print("POSTGRESQL DDL")
print("=" * 70)

postgres_gen = DDLGenerator(dialect="postgres")
postgres_ddl = postgres_gen.generate_ddl(tables, relationships)
postgres_gen.print_ddl()
postgres_gen.save_ddl("resources/example-postgres-ddl.sql")

print("\n" + "=" * 70)
print("✓ DDL GENERATION COMPLETE")
print("=" * 70)
print("\nGenerated files:")
print("  - resources/example-snowflake-ddl.sql")
print("  - resources/example-postgres-ddl.sql")
