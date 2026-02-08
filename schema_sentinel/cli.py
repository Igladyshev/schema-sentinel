"""Command-line interface for schema-sentinel."""

import click


@click.group()
@click.version_option()
def main():
    """Schema Sentinel - Data processing toolkit for schema comparison and metadata management."""
    pass


@main.command()
@click.argument("database")
@click.option("--env", "-e", default="dev", help="Environment (dev, staging, prod)")
def extract(database: str, env: str):
    """Extract metadata from a Snowflake database."""
    from schema_sentinel import get_snowflake_engine, extract_metadata

    click.echo(f"Extracting metadata from {database} in {env} environment...")
    # Add implementation


@main.command()
@click.argument("source")
@click.argument("target")
@click.option("--output", "-o", default="comparison_report", help="Output file name")
@click.option("--format", "-f", "fmt", default="md", type=click.Choice(["md", "html", "json"]), help="Output format")
def compare(source: str, target: str, output: str, fmt: str):
    """Compare two schema snapshots."""
    click.echo(f"Comparing {source} with {target}...")
    # Add implementation


if __name__ == "__main__":
    main()
