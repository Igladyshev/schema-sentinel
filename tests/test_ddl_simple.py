#!/usr/bin/env python
"""Simple DDL generator test."""

import pandas as pd

from yaml_shredder.ddl_generator import DDLGenerator

# Create sample DataFrame
df = pd.DataFrame(
    {
        "id": [1, 2, 3],
        "name": ["Alice", "Bob", "Charlie"],
        "age": [25, 30, 35],
        "active": [True, False, True],
    }
)

# Generate DDL
ddl_gen = DDLGenerator(dialect="snowflake")
ddl = ddl_gen.generate_ddl({"users": df})

# Print DDL
ddl_gen.print_ddl()

# Save to file
ddl_gen.save_ddl("resources/test-ddl.sql")

print("\nTest completed successfully!")
