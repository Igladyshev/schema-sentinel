#!/usr/bin/env python
"""Complete example: Generate tables, DDL, and load to SQLite."""

from pathlib import Path

import pandas as pd

from yaml_shredder.data_loader import SQLiteLoader
from yaml_shredder.ddl_generator import DDLGenerator

# Example data representing MPM deployment structure
deployments_df = pd.DataFrame(
    {
        "id": [1, 2, 3],
        "deployment_code": ["AZ_001", "BS_005", "CO_010"],
        "name": ["Arizona Deployment 1", "Big Sky Deployment 5", "Colorado Deployment 10"],
        "region": ["Southwest", "Northwest", "Mountain"],
        "active": [True, True, False],
        "deployment_date": pd.to_datetime(["2024-01-15", "2024-03-20", "2023-11-10"]),
    }
)

communities_df = pd.DataFrame(
    {
        "id": [1, 2, 3, 4, 5],
        "parent_id": [1, 1, 2, 2, 3],
        "name": ["Phoenix North", "Phoenix South", "Bozeman", "Big Sky", "Denver Metro"],
        "population": [5000, 3500, 4200, 1800, 8500],
        "households": [1800, 1200, 1500, 650, 3200],
    }
)

sensor_actions_df = pd.DataFrame(
    {
        "id": [1, 2, 3, 4, 5, 6],
        "parent_id": [1, 1, 2, 2, 3, 3],
        "sensor_type": ["temperature", "humidity", "motion", "temperature", "pressure", "motion"],
        "threshold": [75.5, 60.0, None, 80.0, 1013.25, None],
        "alert_level": ["warning", "info", "critical", "warning", "info", "critical"],
        "enabled": [True, True, False, True, True, False],
    }
)

report_actions_df = pd.DataFrame(
    {
        "id": [1, 2, 3, 4],
        "parent_id": [1, 1, 2, 3],
        "report_type": ["daily", "weekly", "daily", "monthly"],
        "recipients": ["admin@example.com", "team@example.com", "ops@example.com", "exec@example.com"],
        "format": ["pdf", "html", "pdf", "excel"],
    }
)

# Collect all tables
tables = {
    "deployments": deployments_df,
    "communities": communities_df,
    "sensor_actions": sensor_actions_df,
    "report_actions": report_actions_df,
}

# Define relationships
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
    {
        "child_table": "report_actions",
        "parent_table": "deployments",
        "foreign_keys": ["id"],
    },
]

print("=" * 70)
print("COMPLETE WORKFLOW: TABLES → DDL → SQLite DATABASE")
print("=" * 70)
print(f"\nTables: {len(tables)}")
print(f"Total rows: {sum(len(df) for df in tables.values())}")

# Step 1: Generate DDL
print(f"\n{'=' * 70}")
print("STEP 1: GENERATE DDL")
print(f"{'=' * 70}\n")

ddl_gen = DDLGenerator(dialect="sqlite")
ddl_statements = ddl_gen.generate_ddl(tables, relationships)
ddl_gen.print_ddl()

# Save DDL
ddl_file = Path("resources/mpm-sqlite-ddl.sql")
ddl_gen.save_ddl(ddl_file)

# Step 2: Load to SQLite
print(f"\n{'=' * 70}")
print("STEP 2: LOAD TO SQLite")
print(f"{'=' * 70}\n")

db_path = Path("resources/meta-db/schema-sentinel.db")

print(f"\nUsing database: {db_path}")
with SQLiteLoader(db_path) as loader:
    loader.load_tables(tables, if_exists="replace", create_indexes=True)
    loader.print_summary()

    # Step 3: Query the database
    print(f"\n{'=' * 70}")
    print("STEP 3: QUERY EXAMPLES")
    print(f"{'=' * 70}\n")

    # Example 1: Get all deployments
    print("Query 1: All active deployments")
    result = loader.query("""
        SELECT deployment_code, name, region
        FROM deployments
        WHERE active = 1
        ORDER BY name
    """)
    print(result.to_string(index=False))

    # Example 2: Join deployments with communities
    print("\n\nQuery 2: Deployments with community counts")
    result = loader.query("""
        SELECT
            d.deployment_code,
            d.name AS deployment_name,
            COUNT(c.id) AS num_communities,
            SUM(c.population) AS total_population
        FROM deployments d
        LEFT JOIN communities c ON c.parent_id = d.id
        GROUP BY d.id, d.deployment_code, d.name
        ORDER BY d.deployment_code
    """)
    print(result.to_string(index=False))

    # Example 3: Sensor actions by deployment
    print("\n\nQuery 3: Enabled sensor actions by deployment")
    result = loader.query("""
        SELECT
            d.deployment_code,
            sa.sensor_type,
            sa.threshold,
            sa.alert_level
        FROM sensor_actions sa
        JOIN deployments d ON sa.parent_id = d.id
        WHERE sa.enabled = 1
        ORDER BY d.deployment_code, sa.sensor_type
    """)
    print(result.to_string(index=False))

    # Example 4: Full summary with all relationships
    print("\n\nQuery 4: Deployment summary with all child records")
    result = loader.query("""
        SELECT
            d.deployment_code,
            d.name,
            COUNT(DISTINCT c.id) AS communities,
            COUNT(DISTINCT sa.id) AS sensor_actions,
            COUNT(DISTINCT ra.id) AS report_actions
        FROM deployments d
        LEFT JOIN communities c ON c.parent_id = d.id
        LEFT JOIN sensor_actions sa ON sa.parent_id = d.id
        LEFT JOIN report_actions ra ON ra.parent_id = d.id
        GROUP BY d.id, d.deployment_code, d.name
        ORDER BY d.deployment_code
    """)
    print(result.to_string(index=False))

print(f"\n{'=' * 70}")
print("✓ COMPLETE WORKFLOW FINISHED!")
print(f"{'=' * 70}")
print("\nGenerated files:")
print(f"  - DDL: {ddl_file}")
print(f"  - Database: {db_path}")
print("\nTo explore database:")
print(f"  sqlite3 {db_path}")
