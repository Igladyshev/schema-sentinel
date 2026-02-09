"""Command-line interface for schema-sentinel."""

import json
from pathlib import Path

import click
import yaml as yaml_lib


def load_yaml_or_json(file_path: Path) -> dict:
    """Load YAML or JSON file and validate it's a dictionary."""
    with open(file_path) as f:
        if file_path.suffix.lower() in [".yaml", ".yml"]:
            data = yaml_lib.safe_load(f)
        elif file_path.suffix.lower() == ".json":
            data = json.load(f)
        else:
            try:
                f.seek(0)
                data = yaml_lib.safe_load(f)
            except yaml_lib.YAMLError:
                f.seek(0)
                data = json.load(f)

    if data is None:
        raise ValueError(f"File {file_path} contains no data")
    if not isinstance(data, dict):
        raise ValueError(f"File {file_path} must contain a dictionary at the root level")
    return data


@click.group()
@click.version_option()
def main():
    """Schema Sentinel - Data processing toolkit for schema comparison and metadata management."""
    pass


# =============================================================================
# YAML Command Group - YAML/JSON Processing
# =============================================================================


@main.group()
def yaml():
    """YAML/JSON processing commands - analyze, transform, load, and compare."""
    pass


@yaml.command()
@click.argument("input_file", type=click.Path(exists=True, path_type=Path))
@click.option("--output", "-o", type=click.Path(path_type=Path), help="Output file for analysis JSON")
@click.option(
    "--max-depth",
    type=int,
    default=None,
    help="Max depth for flattening (affects which structures become tables)",
)
def analyze(input_file: Path, output: Path | None, max_depth: int | None):
    """Analyze YAML/JSON structure and identify nested elements."""
    from yaml_shredder.structure_analyzer import StructureAnalyzer

    click.echo(f"Analyzing: {input_file}")
    data = load_yaml_or_json(input_file)

    analyzer = StructureAnalyzer(max_depth=max_depth)
    analysis = analyzer.analyze(data)
    analyzer.print_summary(analysis)

    if output:
        # Convert analysis dict to be JSON-serializable (handles tuple keys)
        def make_json_serializable(obj):
            if isinstance(obj, dict):
                return {str(k): make_json_serializable(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [make_json_serializable(item) for item in obj]
            return obj

        serializable_analysis = make_json_serializable(analysis)
        with open(output, "w") as f:
            json.dump(serializable_analysis, f, indent=2)
        click.echo(f"\n✓ Analysis saved to: {output}")


@yaml.command(name="schema")
@click.argument("input_file", type=click.Path(exists=True, path_type=Path))
@click.option("--output", "-o", type=click.Path(path_type=Path), help="Output file for schema JSON")
def generate_schema(input_file: Path, output: Path | None):
    """Generate JSON schema from YAML/JSON file."""
    from yaml_shredder.schema_generator import SchemaGenerator

    click.echo(f"Generating schema from: {input_file}")

    generator = SchemaGenerator()
    if input_file.suffix.lower() == ".json":
        generator.add_json_file(input_file)
    else:
        generator.add_yaml_file(input_file)

    schema_dict = generator.generate_schema()
    stats = generator.get_stats()

    click.echo("\n✓ Schema generated:")
    click.echo(f"  Properties: {stats['schema_properties']}")
    click.echo(f"  Required fields: {stats['required_fields']}")

    if output:
        generator.save_schema(output)
        click.echo(f"\n✓ Schema saved to: {output}")
    else:
        click.echo(f"\n{json.dumps(schema_dict, indent=2)}")


@yaml.command()
@click.argument("input_file", type=click.Path(exists=True, path_type=Path))
@click.option("--output", "-o", type=click.Path(path_type=Path), help="Output directory for tables")
@click.option(
    "--format", "-f", "fmt", default="csv", type=click.Choice(["csv", "json", "parquet"]), help="Output format"
)
@click.option("--root-name", "-r", default="ROOT", help="Name for the root table")
@click.option(
    "--depth",
    "-d",
    type=int,
    default=None,
    help="Max depth for flattening (0=none, 1=keep variants, 2+=flatten variants, None=flatten all)",
)
def tables(input_file: Path, output: Path | None, fmt: str, root_name: str, depth: int | None):
    """Generate relational tables from nested YAML/JSON."""
    from yaml_shredder.table_generator import TableGenerator

    click.echo(f"Generating tables from: {input_file}")
    data = load_yaml_or_json(input_file)

    table_gen = TableGenerator(max_depth=depth)
    tables_dict = table_gen.generate_tables(data, root_table_name=root_name, source_file=input_file)
    table_gen.print_summary()

    if output:
        output_dir = Path(output)
        try:
            table_gen.save_tables(output_dir, format=fmt)
            click.echo(f"\n✓ Tables saved to: {output_dir}")
        except Exception as e:
            click.echo(f"\n✗ Error saving tables: {e}", err=True)
            raise
    else:
        for table_name, df in tables_dict.items():
            click.echo(f"\n{table_name}:")
            click.echo(df.head(3).to_string(index=False))


@yaml.command()
@click.argument("input_file", type=click.Path(exists=True, path_type=Path))
@click.option("--output", "-o", type=click.Path(path_type=Path), help="Output file for DDL")
@click.option(
    "--dialect",
    "-d",
    default="snowflake",
    type=click.Choice(["snowflake", "postgresql", "mysql", "sqlite"]),
    help="SQL dialect",
)
@click.option("--root-name", "-r", default="ROOT", help="Name for the root table")
@click.option(
    "--max-depth",
    type=int,
    default=None,
    help="Max depth for flattening (0=none, 1=keep variants, 2+=flatten variants, None=flatten all)",
)
def ddl(input_file: Path, output: Path | None, dialect: str, root_name: str, max_depth: int | None):
    """Generate SQL DDL from YAML/JSON structure."""
    from yaml_shredder.ddl_generator import DDLGenerator
    from yaml_shredder.table_generator import TableGenerator

    click.echo(f"Generating {dialect} DDL from: {input_file}")
    data = load_yaml_or_json(input_file)

    table_gen = TableGenerator(max_depth=max_depth)
    tables_dict = table_gen.generate_tables(data, root_table_name=root_name, source_file=input_file)

    ddl_gen = DDLGenerator(dialect=dialect)
    ddl_gen.generate_ddl(tables_dict, table_gen.relationships)

    if output:
        ddl_gen.save_ddl(output)
        click.echo(f"\n✓ DDL saved to: {output}")
    else:
        ddl_gen.print_ddl()


@yaml.command()
@click.argument("input_file", type=click.Path(exists=True, path_type=Path))
@click.option("--database", "-db", required=True, type=click.Path(path_type=Path), help="SQLite database file")
@click.option("--root-name", "-r", default="ROOT", help="Name for the root table")
@click.option(
    "--if-exists", default="replace", type=click.Choice(["fail", "replace", "append"]), help="Action if table exists"
)
@click.option("--create-ddl", is_flag=True, help="Create tables before loading")
@click.option("--no-indexes", is_flag=True, help="Skip index creation")
@click.option(
    "--max-depth",
    type=int,
    default=None,
    help="Max depth for flattening (0=none, 1=keep variants, 2+=flatten variants, None=flatten all)",
)
def load(
    input_file: Path,
    database: Path,
    root_name: str,
    if_exists: str,
    create_ddl: bool,
    no_indexes: bool,
    max_depth: int | None,
):
    """Load YAML/JSON data into SQLite database."""
    from yaml_shredder.data_loader import SQLiteLoader
    from yaml_shredder.ddl_generator import DDLGenerator
    from yaml_shredder.table_generator import TableGenerator

    click.echo(f"Loading data from: {input_file}")
    data = load_yaml_or_json(input_file)

    table_gen = TableGenerator(max_depth=max_depth)
    tables_dict = table_gen.generate_tables(data, root_table_name=root_name, source_file=input_file)
    table_gen.print_summary()

    click.echo(f"\nLoading to database: {database}")
    loader = SQLiteLoader(str(database))
    loader.connect()

    if create_ddl:
        click.echo("Creating tables...")
        ddl_gen = DDLGenerator(dialect="sqlite")
        ddl_statements = ddl_gen.generate_ddl(tables_dict, table_gen.relationships)
        loader.execute_ddl(ddl_statements)

    loader.load_tables(tables_dict, if_exists=if_exists, create_indexes=not no_indexes)
    loader.print_summary()
    loader.disconnect()


@yaml.command(name="shred")
@click.argument("input_file", type=click.Path(exists=True, path_type=Path))
@click.option("--database", "-db", required=True, type=click.Path(path_type=Path), help="SQLite database file")
@click.option("--root-name", "-r", default="ROOT", help="Name for the root table")
@click.option("--ddl-output", "-ddl", type=click.Path(path_type=Path), help="Also save DDL to file")
@click.option(
    "--dialect",
    "-d",
    default="snowflake",
    type=click.Choice(["snowflake", "postgresql", "mysql", "sqlite"]),
    help="DDL dialect for --ddl-output",
)
@click.option(
    "--max-depth",
    type=int,
    default=None,
    help="Max depth for flattening (0=none, 1=keep variants, 2+=flatten variants, None=flatten all)",
)
def shred_all(
    input_file: Path, database: Path, root_name: str, ddl_output: Path | None, dialect: str, max_depth: int | None
):
    """Complete workflow: analyze → tables → DDL → load to SQLite."""
    from yaml_shredder.data_loader import SQLiteLoader
    from yaml_shredder.ddl_generator import DDLGenerator
    from yaml_shredder.structure_analyzer import StructureAnalyzer
    from yaml_shredder.table_generator import TableGenerator

    click.echo("=" * 70)
    click.echo("YAML SHREDDER - COMPLETE WORKFLOW")
    click.echo("=" * 70)
    click.echo(f"\nInput: {input_file}")

    data = load_yaml_or_json(input_file)

    # Step 1: Analyze
    click.echo(f"\n{'=' * 70}")
    click.echo("STEP 1: STRUCTURE ANALYSIS")
    click.echo(f"{'=' * 70}")
    analyzer = StructureAnalyzer(max_depth=max_depth)
    analysis = analyzer.analyze(data)
    analyzer.print_summary(analysis)

    # Step 2: Generate tables
    click.echo(f"\n{'=' * 70}")
    click.echo("STEP 2: TABLE GENERATION")
    click.echo(f"{'=' * 70}")
    table_gen = TableGenerator(max_depth=max_depth)
    tables_dict = table_gen.generate_tables(data, root_table_name=root_name, source_file=input_file)
    table_gen.print_summary()

    # Step 3: Generate DDL
    click.echo(f"\n{'=' * 70}")
    click.echo("STEP 3: DDL GENERATION")
    click.echo(f"{'=' * 70}")
    ddl_gen = DDLGenerator(dialect="sqlite")
    ddl_statements = ddl_gen.generate_ddl(tables_dict, table_gen.relationships)

    if ddl_output:
        output_ddl_gen = DDLGenerator(dialect=dialect)
        output_ddl_gen.generate_ddl(tables_dict, table_gen.relationships)
        output_ddl_gen.save_ddl(ddl_output)
        click.echo(f"✓ {dialect} DDL saved to: {ddl_output}")

    # Step 4: Load to SQLite
    click.echo(f"\n{'=' * 70}")
    click.echo("STEP 4: SQLITE LOADING")
    click.echo(f"{'=' * 70}")
    loader = SQLiteLoader(str(database))
    loader.connect()
    loader.execute_ddl(ddl_statements)
    loader.load_tables(tables_dict, if_exists="replace", create_indexes=True)
    loader.print_summary()
    loader.disconnect()

    click.echo(f"\n{'=' * 70}")
    click.echo("✓ COMPLETE!")
    click.echo(f"{'=' * 70}")
    click.echo(f"Database: {database}")


@yaml.command(name="doc")
@click.argument("input_file", type=click.Path(exists=True, path_type=Path))
@click.option(
    "--output-dir",
    "-o",
    type=click.Path(path_type=Path),
    default="resources/metadata-doc",
    help="Output directory for markdown documentation",
)
@click.option("--root-name", "-r", default="ROOT", help="Name for the root table")
@click.option(
    "--max-depth",
    type=int,
    default=None,
    help="Maximum depth for flattening (0=none, 1=first level, None=all levels)",
)
@click.option("--keep-db", is_flag=True, help="Keep the temporary SQLite database file")
def generate_doc(
    input_file: Path,
    output_dir: Path,
    root_name: str,
    max_depth: int | None,
    keep_db: bool,
):
    """Generate markdown documentation from YAML/JSON file.

    This command converts a YAML/JSON file into a SQLite database and generates
    comprehensive markdown documentation showing all tables with their schemas
    and data.

    Examples:

        # Generate documentation for a YAML file
        uv run schema-sentinel yaml doc config.yaml

        # Specify custom output directory
        uv run schema-sentinel yaml doc config.yaml -o docs/

        # Keep the temporary database file
        uv run schema-sentinel yaml doc config.yaml --keep-db

        # Control flattening depth
        uv run schema-sentinel yaml doc config.yaml --max-depth 1
    """
    from yaml_shredder.doc_generator import generate_doc_from_yaml

    click.echo(f"Generating documentation from: {input_file}")
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    try:
        output_path = generate_doc_from_yaml(
            yaml_path=input_file, output_dir=output_dir, root_name=root_name, max_depth=max_depth, keep_db=keep_db
        )

        click.echo(f"\n✓ Documentation generated: {output_path}")

        if keep_db:
            db_path = output_dir / f"{input_file.stem}.db"
            click.echo(f"✓ Database kept: {db_path}")

    except Exception as e:
        click.echo(f"✗ Error: {e}", err=True)
        raise click.Abort() from e


@yaml.command(name="compare")
@click.argument("yaml1", type=click.Path(exists=True, path_type=Path))
@click.argument("yaml2", type=click.Path(exists=True, path_type=Path))
@click.option("--output", "-o", type=click.Path(path_type=Path), help="Output path for comparison report (markdown)")
@click.option(
    "--db-dir", type=click.Path(path_type=Path), default="./temp_dbs", help="Directory for temporary databases"
)
@click.option("--keep-dbs", is_flag=True, help="Keep temporary SQLite databases after comparison")
@click.option("--root-name", default="root", help="Root table name for both YAML files")
@click.option(
    "--max-depth",
    type=int,
    default=None,
    help="Max depth for flattening (0=none, 1=keep variants, 2+=flatten variants, None=flatten all)",
)
def compare_yaml(
    yaml1: Path, yaml2: Path, output: Path | None, db_dir: Path, keep_dbs: bool, root_name: str, max_depth: int | None
):
    """Compare two YAML files by converting them to SQLite databases.

    This command loads two YAML files into separate SQLite databases,
    compares their table structures and data, and generates a detailed
    comparison report in markdown format.

    Examples:

        # Compare two YAML files and display report
        schema-sentinel compare-yaml file1.yaml file2.yaml

        # Save comparison report to file
        schema-sentinel compare-yaml file1.yaml file2.yaml -o comparison.md

        # Keep databases for inspection
        schema-sentinel compare-yaml file1.yaml file2.yaml --keep-dbs
    """
    from schema_sentinel.yaml_comparator import YAMLComparator

    click.echo("Comparing YAML files:")
    click.echo(f"  File 1: {yaml1}")
    click.echo(f"  File 2: {yaml2}")
    click.echo()

    comparator = YAMLComparator(output_dir=db_dir)

    try:
        report = comparator.compare_yaml_files(
            yaml1_path=yaml1,
            yaml2_path=yaml2,
            output_report=output,
            keep_dbs=keep_dbs,
            root_table_name=root_name,
            max_depth=max_depth,
        )

        if output:
            click.echo(f"✓ Comparison report saved to: {output}")
        else:
            click.echo(report)

        if keep_dbs:
            db1_name = yaml1.stem + ".db"
            db2_name = yaml2.stem + ".db"
            click.echo(f"\nDatabases kept in {db_dir}:")
            click.echo(f"  - {db1_name}")
            click.echo(f"  - {db2_name}")
    except Exception as e:
        click.echo(f"✗ Error: {e}", err=True)
        raise click.Abort() from e


# =============================================================================
# Schema Command Group - Snowflake Schema Management
# =============================================================================


@main.group()
def schema():
    """Snowflake schema extraction and comparison commands."""
    pass


@schema.command()
@click.argument("database")
@click.option("--env", "-e", default="dev", help="Environment (dev, staging, prod)")
def extract(database: str, env: str):
    """Extract metadata from a Snowflake database."""
    click.echo(f"Extracting metadata from {database} in {env} environment...")
    # Add implementation


@schema.command()
@click.argument("source")
@click.argument("target")
@click.option("--output", "-o", default="comparison_report", help="Output file name")
@click.option("--format", "-f", "fmt", default="md", type=click.Choice(["md", "html", "json"]), help="Output format")
def compare(source: str, target: str, output: str, fmt: str):
    """Compare two Snowflake schema snapshots."""
    click.echo(f"Comparing {source} with {target}...")
    # Add implementation


if __name__ == "__main__":
    main()
