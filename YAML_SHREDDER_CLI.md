# YAML Shredder CLI

A command-line tool to analyze YAML/JSON files and convert them to relational tables.

## Quick Start

```bash
# Analyze structure
uv run python yaml_shredder_cli.py analyze input.yaml

# Generate JSON schema
uv run python yaml_shredder_cli.py schema input.yaml -o schema.json

# Generate tables (CSV)
uv run python yaml_shredder_cli.py tables input.yaml -o output_dir/

# Generate SQL DDL
uv run python yaml_shredder_cli.py ddl input.yaml -d sqlite -o output.sql

# Load into SQLite
uv run python yaml_shredder_cli.py load input.yaml -db database.db

# Complete workflow
uv run python yaml_shredder_cli.py all input.yaml \
  -db database.db \
  -s schema.json \
  -t tables/ \
  -ddl schema.sql
```

## Commands

### `analyze`
Analyze the structure of YAML/JSON file to identify nested arrays and patterns.

```bash
uv run python yaml_shredder_cli.py analyze input.yaml [-o analysis.json]
```

### `schema`
Generate JSON Schema from YAML/JSON examples.

```bash
uv run python yaml_shredder_cli.py schema input.yaml -o schema.json
# Or from directory
uv run python yaml_shredder_cli.py schema input_dir/ -o schema.json
```

### `tables`
Generate relational tables from nested YAML/JSON.

```bash
uv run python yaml_shredder_cli.py tables input.yaml \
  -o output_dir/ \
  -f csv \
  -r ROOT_TABLE_NAME
```

Formats: `csv`, `parquet`, `excel`

### `ddl`
Generate SQL DDL (CREATE TABLE) statements.

```bash
uv run python yaml_shredder_cli.py ddl input.yaml \
  -o schema.sql \
  -d snowflake \
  -r ROOT_TABLE_NAME
```

Dialects: `snowflake`, `postgres`, `mysql`, `sqlite`

### `load`
Load tables directly into SQLite database.

```bash
uv run python yaml_shredder_cli.py load input.yaml \
  -db database.db \
  -r ROOT_TABLE_NAME \
  --if-exists replace
```

Options:
- `--if-exists`: `fail`, `replace`, `append`
- `--no-indexes`: Don't create indexes
- `--create-ddl`: Execute DDL before loading

### `all`
Run complete workflow: analyze → schema → tables → DDL → load.

```bash
uv run python yaml_shredder_cli.py all input.yaml \
  -db database.db \
  -r ROOT_TABLE_NAME \
  -s schema.json \
  -t tables/ \
  -ddl schema.sql \
  -f csv \
  -d sqlite
```

## Examples

### Example 1: Complete Workflow - YAML to Database
```bash
# Load YAML configuration into database
uv run python yaml_shredder_cli.py all \
  data/config.yaml \
  -db resources/meta-db/schema-sentinel.db \
  -r APP_CONFIG \
  -ddl resources/meta-db/schema.sql
```

### Example 2: Generate Tables Only
```bash
# Convert YAML/JSON to CSV tables
uv run python yaml_shredder_cli.py tables \
  data/config.yaml \
  -o output/tables/ \
  -f csv \
  -r CONFIG_DATA
```

### Example 3: Generate Snowflake DDL
```bash
# Create DDL for Snowflake from YAML
uv run python yaml_shredder_cli.py ddl \
  data/config.yaml \
  -o output/snowflake-schema.sql \
  -d snowflake \
  -r CONFIG_DATA
```

### Example 4: Analyze Before Processing
```bash
# First analyze to see structure
uv run python yaml_shredder_cli.py analyze input.yaml

# Then generate tables based on analysis
uv run python yaml_shredder_cli.py tables input.yaml -o output/
```

## Python API

You can also use the modules directly in Python:

```python
from yaml_shredder.structure_analyzer import StructureAnalyzer
from yaml_shredder.table_generator import TableGenerator
from yaml_shredder.ddl_generator import DDLGenerator
from yaml_shredder.data_loader import SQLiteLoader

# Analyze
analyzer = StructureAnalyzer()
analysis = analyzer.analyze(data)

# Generate tables
table_gen = TableGenerator()
tables = table_gen.generate_tables(data, root_table_name="ROOT")

# Generate DDL
ddl_gen = DDLGenerator(dialect="sqlite")
ddl = ddl_gen.generate_ddl(tables, table_gen.relationships)

# Load to SQLite
loader = SQLiteLoader("database.db")
loader.connect()
loader.load_tables(tables)
loader.disconnect()
```
