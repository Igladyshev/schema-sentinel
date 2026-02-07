#!/usr/bin/env python
"""Simple SQLite loader test."""

from pathlib import Path

import pandas as pd

from yaml_shredder.data_loader import SQLiteLoader
from yaml_shredder.ddl_generator import DDLGenerator

print("Creating test data...")
df = pd.DataFrame(
    {
        "id": [1, 2, 3],
        "name": ["Alice", "Bob", "Charlie"],
        "age": [25, 30, 35],
    }
)

print("Generating SQLite DDL...")
ddl_gen = DDLGenerator(dialect="sqlite")
ddl = ddl_gen.generate_ddl({"users": df})
print(ddl["users"])

db_file = Path("resources/meta-db/schema-sentinel.db")

print(f"\nUsing database: {db_file}")
loader = SQLiteLoader(db_file)
loader.connect()
loader.load_tables({"users": df})

print("\nQuerying database...")
result = loader.query("SELECT * FROM users ORDER BY age")
print(result)

loader.print_summary()
loader.disconnect()

print(f"\n✓ Test complete! Database: {db_file}")
