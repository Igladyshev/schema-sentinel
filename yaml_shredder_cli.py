#!/usr/bin/env python
"""CLI for YAML Shredder - analyze YAML/JSON and convert to relational tables."""

import argparse
import sys
from pathlib import Path

import yaml

from yaml_shredder.data_loader import SQLiteLoader
from yaml_shredder.ddl_generator import DDLGenerator
from yaml_shredder.schema_generator import SchemaGenerator
from yaml_shredder.structure_analyzer import StructureAnalyzer
from yaml_shredder.table_generator import TableGenerator


def load_yaml_or_json(file_path: Path) -> dict:
    """Load YAML or JSON file and validate it's a dictionary.
    
    Args:
        file_path: Path to YAML or JSON file
        
    Returns:
        Dictionary loaded from file
        
    Raises:
        ValueError: If the file is empty or root element is not a dictionary
    """
    import json

    with open(file_path) as f:
        if file_path.suffix.lower() in [".yaml", ".yml"]:
            data = yaml.safe_load(f)
        elif file_path.suffix.lower() == ".json":
            data = json.load(f)
        else:
            # Try YAML first, then JSON
            try:
                f.seek(0)
                data = yaml.safe_load(f)
            except yaml.YAMLError:
                f.seek(0)
                data = json.load(f)
    
    # Validate that we have a dictionary
    if data is None:
        raise ValueError(f"File {file_path} contains no data or only contains comments/whitespace")
    if not isinstance(data, dict):
        raise ValueError(
            f"File {file_path} must contain a dictionary at the root level, "
            f"but got {type(data).__name__}. Lists and scalars are not supported."
        )
    
    return data


def cmd_analyze(args):
    """Analyze YAML/JSON structure."""
    print(f"Analyzing: {args.input}")
    data = load_yaml_or_json(args.input)

    analyzer = StructureAnalyzer()
    analysis = analyzer.analyze(data)
    analyzer.print_summary(analysis)

    if args.output:
        import json

        with open(args.output, "w") as f:
            json.dump(analysis, f, indent=2)
        print(f"\n✓ Analysis saved to: {args.output}")


def cmd_schema(args):
    """Generate JSON schema."""
    print(f"Generating schema from: {args.input}")

    generator = SchemaGenerator()

    if args.input.is_dir():
        # Process directory
        for file in args.input.glob("**/*.yaml"):
            print(f"  Adding: {file}")
            generator.add_yaml_file(file)
        for file in args.input.glob("**/*.yml"):
            print(f"  Adding: {file}")
            generator.add_yaml_file(file)
        for file in args.input.glob("**/*.json"):
            print(f"  Adding: {file}")
            generator.add_json_file(file)
    else:
        # Single file
        if args.input.suffix.lower() == ".json":
            generator.add_json_file(args.input)
        else:
            generator.add_yaml_file(args.input)

    schema = generator.generate_schema()
    stats = generator.get_stats()

    print("\n✓ Schema generated:")
    print(f"  Properties: {stats['schema_properties']}")
    print(f"  Required fields: {stats['required_fields']}")

    if args.output:
        generator.save_schema(args.output)
    else:
        import json

        print(f"\n{json.dumps(schema, indent=2)}")


def cmd_tables(args):
    """Generate relational tables."""
    print(f"Generating tables from: {args.input}")
    data = load_yaml_or_json(args.input)

    table_gen = TableGenerator()
    tables = table_gen.generate_tables(data, root_table_name=args.root_name)

    table_gen.print_summary()

    if args.output:
        output_dir = Path(args.output)
        table_gen.save_tables(output_dir, format=args.format)
    else:
        # Just show first few rows of each table
        for table_name, df in tables.items():
            print(f"\n{table_name}:")
            print(df.head(3).to_string(index=False))


def cmd_ddl(args):
    """Generate SQL DDL."""
    print(f"Generating DDL from: {args.input}")
    data = load_yaml_or_json(args.input)

    # Generate tables
    table_gen = TableGenerator()
    tables = table_gen.generate_tables(data, root_table_name=args.root_name)

    # Generate DDL
    ddl_gen = DDLGenerator(dialect=args.dialect)
    ddl_gen.generate_ddl(tables, table_gen.relationships)

    if args.output:
        ddl_gen.save_ddl(args.output)
    else:
        ddl_gen.print_ddl()


def cmd_load(args):
    """Load tables into SQLite database."""
    print(f"Loading data from: {args.input}")
    data = load_yaml_or_json(args.input)

    # Generate tables
    print("\nGenerating tables...")
    table_gen = TableGenerator()
    tables = table_gen.generate_tables(data, root_table_name=args.root_name)
    table_gen.print_summary()

    # Load to SQLite
    print(f"\nLoading to database: {args.database}")
    loader = SQLiteLoader(args.database)
    loader.connect()

    if args.create_ddl:
        # Generate and execute DDL first
        print("Creating tables...")
        ddl_gen = DDLGenerator(dialect="sqlite")
        ddl_statements = ddl_gen.generate_ddl(tables, table_gen.relationships)
        loader.execute_ddl(ddl_statements)

    # Load data
    loader.load_tables(tables, if_exists=args.if_exists, create_indexes=not args.no_indexes)
    loader.print_summary()
    loader.disconnect()


def cmd_all(args):
    """Run complete workflow: analyze, schema, tables, DDL, and load."""
    print("=" * 70)
    print("YAML SHREDDER - COMPLETE WORKFLOW")
    print("=" * 70)
    print(f"\nInput: {args.input}")

    data = load_yaml_or_json(args.input)

    # Step 1: Analyze
    print(f"\n{'=' * 70}")
    print("STEP 1: STRUCTURE ANALYSIS")
    print(f"{'=' * 70}")
    analyzer = StructureAnalyzer()
    analysis = analyzer.analyze(data)
    analyzer.print_summary(analysis)

    # Step 2: Schema
    print(f"\n{'=' * 70}")
    print("STEP 2: SCHEMA GENERATION")
    print(f"{'=' * 70}")
    generator = SchemaGenerator()
    if args.input.suffix.lower() == ".json":
        generator.add_json_file(args.input)
    else:
        generator.add_yaml_file(args.input)
    generator.generate_schema()
    stats = generator.get_stats()
    print(f"\n✓ Schema: {stats['schema_properties']} properties, {stats['required_fields']} required")

    if args.schema_output:
        generator.save_schema(args.schema_output)

    # Step 3: Tables
    print(f"\n{'=' * 70}")
    print("STEP 3: TABLE GENERATION")
    print(f"{'=' * 70}")
    table_gen = TableGenerator()
    tables = table_gen.generate_tables(data, root_table_name=args.root_name)
    table_gen.print_summary()

    if args.tables_output:
        table_gen.save_tables(args.tables_output, format=args.format)

    # Step 4: DDL
    print(f"\n{'=' * 70}")
    print("STEP 4: DDL GENERATION")
    print(f"{'=' * 70}")
    ddl_gen = DDLGenerator(dialect=args.dialect)
    ddl_statements = ddl_gen.generate_ddl(tables, table_gen.relationships)

    if args.ddl_output:
        ddl_gen.save_ddl(args.ddl_output)
    else:
        print(f"\n✓ Generated DDL for {len(ddl_statements)} tables")

    # Step 5: Load
    if args.database:
        print(f"\n{'=' * 70}")
        print("STEP 5: DATABASE LOAD")
        print(f"{'=' * 70}")
        loader = SQLiteLoader(args.database)
        loader.connect()
        loader.load_tables(tables, if_exists=args.if_exists, create_indexes=True)
        loader.print_summary()
        loader.disconnect()

    print(f"\n{'=' * 70}")
    print("✓ WORKFLOW COMPLETE")
    print(f"{'=' * 70}")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="YAML Shredder - Analyze YAML/JSON and convert to relational tables",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Analyze command
    parser_analyze = subparsers.add_parser("analyze", help="Analyze structure of YAML/JSON file")
    parser_analyze.add_argument("input", type=Path, help="Input YAML/JSON file")
    parser_analyze.add_argument("-o", "--output", type=Path, help="Output JSON file for analysis")
    parser_analyze.set_defaults(func=cmd_analyze)

    # Schema command
    parser_schema = subparsers.add_parser("schema", help="Generate JSON schema")
    parser_schema.add_argument("input", type=Path, help="Input YAML/JSON file or directory")
    parser_schema.add_argument("-o", "--output", type=Path, help="Output JSON schema file")
    parser_schema.set_defaults(func=cmd_schema)

    # Tables command
    parser_tables = subparsers.add_parser("tables", help="Generate relational tables")
    parser_tables.add_argument("input", type=Path, help="Input YAML/JSON file")
    parser_tables.add_argument("-o", "--output", type=Path, help="Output directory for tables")
    parser_tables.add_argument(
        "-f", "--format", choices=["csv", "parquet", "excel"], default="csv", help="Output format"
    )
    parser_tables.add_argument("-r", "--root-name", default="ROOT", help="Root table name")
    parser_tables.set_defaults(func=cmd_tables)

    # DDL command
    parser_ddl = subparsers.add_parser("ddl", help="Generate SQL DDL statements")
    parser_ddl.add_argument("input", type=Path, help="Input YAML/JSON file")
    parser_ddl.add_argument("-o", "--output", type=Path, help="Output SQL file")
    parser_ddl.add_argument(
        "-d", "--dialect", choices=["snowflake", "postgres", "mysql", "sqlite"], default="snowflake", help="SQL dialect"
    )
    parser_ddl.add_argument("-r", "--root-name", default="ROOT", help="Root table name")
    parser_ddl.set_defaults(func=cmd_ddl)

    # Load command
    parser_load = subparsers.add_parser("load", help="Load tables into SQLite database")
    parser_load.add_argument("input", type=Path, help="Input YAML/JSON file")
    parser_load.add_argument("-db", "--database", type=Path, required=True, help="SQLite database file")
    parser_load.add_argument("-r", "--root-name", default="ROOT", help="Root table name")
    parser_load.add_argument(
        "--if-exists", choices=["fail", "replace", "append"], default="replace", help="What to do if table exists"
    )
    parser_load.add_argument("--no-indexes", action="store_true", help="Don't create indexes")
    parser_load.add_argument("--create-ddl", action="store_true", help="Create tables with DDL first")
    parser_load.set_defaults(func=cmd_load)

    # All command
    parser_all = subparsers.add_parser("all", help="Run complete workflow")
    parser_all.add_argument("input", type=Path, help="Input YAML/JSON file")
    parser_all.add_argument("-db", "--database", type=Path, help="SQLite database file")
    parser_all.add_argument("-r", "--root-name", default="ROOT", help="Root table name")
    parser_all.add_argument("-s", "--schema-output", type=Path, help="Output JSON schema file")
    parser_all.add_argument("-t", "--tables-output", type=Path, help="Output directory for tables")
    parser_all.add_argument("-ddl", "--ddl-output", type=Path, help="Output SQL DDL file")
    parser_all.add_argument(
        "-f", "--format", choices=["csv", "parquet", "excel"], default="csv", help="Table output format"
    )
    parser_all.add_argument(
        "-d", "--dialect", choices=["snowflake", "postgres", "mysql", "sqlite"], default="sqlite", help="SQL dialect"
    )
    parser_all.add_argument(
        "--if-exists", choices=["fail", "replace", "append"], default="replace", help="What to do if table exists"
    )
    parser_all.set_defaults(func=cmd_all)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    try:
        args.func(args)
    except Exception as e:
        print(f"\n❌ Error: {e}", file=sys.stderr)
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
