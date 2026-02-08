"""Generate markdown documentation from SQLite database tables."""

import sqlite3
from pathlib import Path

import pandas as pd


class MarkdownDocGenerator:
    """Generate markdown documentation from SQLite database tables."""

    def __init__(self, db_path: str | Path):
        """Initialize document generator.

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = Path(db_path)
        if not self.db_path.exists():
            raise FileNotFoundError(f"Database file not found: {db_path}")

        self.connection = None
        self.tables_info = {}

    def connect(self) -> None:
        """Establish connection to SQLite database."""
        self.connection = sqlite3.connect(str(self.db_path))

    def disconnect(self) -> None:
        """Close database connection."""
        if self.connection:
            self.connection.close()
            self.connection = None

    def get_tables(self) -> list[str]:
        """Get list of all tables in the database.

        Returns:
            List of table names
        """
        query = "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        cursor = self.connection.cursor()
        cursor.execute(query)
        return [row[0] for row in cursor.fetchall()]

    def get_table_data(self, table_name: str) -> pd.DataFrame:
        """Get data from a table.

        Args:
            table_name: Name of the table

        Returns:
            DataFrame with table data
        """
        return pd.read_sql_query(f'SELECT * FROM "{table_name}"', self.connection)

    def get_table_schema(self, table_name: str) -> list[tuple[str, str]]:
        """Get schema information for a table.

        Args:
            table_name: Name of the table

        Returns:
            List of tuples (column_name, column_type)
        """
        cursor = self.connection.cursor()
        cursor.execute(f'PRAGMA table_info("{table_name}")')
        return [(row[1], row[2]) for row in cursor.fetchall()]

    def generate_markdown(self, output_path: Path | None = None, doc_name: str | None = None) -> str:
        """Generate markdown documentation for all tables in the database.

        Args:
            output_path: Optional path to save markdown file
            doc_name: Optional custom name for the document

        Returns:
            Generated markdown content
        """
        if not self.connection:
            self.connect()

        tables = self.get_tables()

        # Build markdown content
        lines = []

        # Title
        if doc_name:
            lines.append(f"# {doc_name}")
        else:
            lines.append(f"# Database Documentation: {self.db_path.stem}")

        lines.append("")
        lines.append(f"**Generated from:** `{self.db_path.name}`")
        lines.append("")
        lines.append(f"**Total tables:** {len(tables)}")
        lines.append("")

        # Table of contents
        lines.append("## Table of Contents")
        lines.append("")
        for table in tables:
            lines.append(f"- [{table}](#{table.lower()})")
        lines.append("")

        # Generate documentation for each table
        for table in tables:
            lines.append("---")
            lines.append("")
            lines.append(f"## {table}")
            lines.append("")

            # Get schema
            schema = self.get_table_schema(table)
            lines.append("### Schema")
            lines.append("")
            lines.append("| Column | Type |")
            lines.append("|--------|------|")
            for col_name, col_type in schema:
                lines.append(f"| `{col_name}` | {col_type} |")
            lines.append("")

            # Get data
            df = self.get_table_data(table)
            row_count = len(df)

            lines.append(f"### Data ({row_count} rows)")
            lines.append("")

            if row_count == 0:
                lines.append("*No data in this table.*")
                lines.append("")
            else:
                # Convert DataFrame to markdown table
                markdown_table = self._dataframe_to_markdown(df)
                lines.append(markdown_table)
                lines.append("")

        markdown_content = "\n".join(lines)

        # Save to file if output path provided
        if output_path:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "w") as f:
                f.write(markdown_content)
            print(f"✓ Markdown documentation saved to: {output_path}")

        return markdown_content

    def _dataframe_to_markdown(self, df: pd.DataFrame, max_col_width: int = 50) -> str:
        """Convert DataFrame to markdown table.

        Args:
            df: DataFrame to convert
            max_col_width: Maximum width for column content (truncate longer values, except JSON)

        Returns:
            Markdown table string
        """

        # Check if value looks like JSON/array and should not be truncated
        def is_json_like(val_str):
            stripped = val_str.strip()
            # JSON objects or arrays
            if stripped.startswith(("{", "[")):
                return True
            # Comma-separated lists (likely arrays)
            if "," in val_str and len(val_str) > max_col_width:
                return True
            return False

        # Truncate long values (but not JSON objects/arrays)
        def truncate_value(val):
            val_str = str(val)
            # Don't truncate JSON objects, arrays, or comma-separated lists
            if is_json_like(val_str):
                return val_str
            # Truncate other long values
            if len(val_str) > max_col_width:
                return val_str[: max_col_width - 3] + "..."
            return val_str

        lines = []

        # Header
        header = "| " + " | ".join(df.columns) + " |"
        lines.append(header)

        # Separator
        separator = "| " + " | ".join(["---"] * len(df.columns)) + " |"
        lines.append(separator)

        # Rows
        for _, row in df.iterrows():
            row_values = [truncate_value(val) for val in row]
            row_str = "| " + " | ".join(row_values) + " |"
            lines.append(row_str)

        return "\n".join(lines)


def generate_doc_from_yaml(
    yaml_path: Path,
    output_dir: Path,
    root_name: str = "ROOT",
    max_depth: int | None = None,
    keep_db: bool = False,
) -> Path:
    """Generate markdown documentation from YAML file.

    This is a convenience function that:
    1. Loads YAML into a temporary SQLite database
    2. Generates markdown documentation
    3. Optionally cleans up the database

    Args:
        yaml_path: Path to YAML file
        output_dir: Directory to save markdown documentation
        root_name: Name for the root table
        max_depth: Maximum depth for flattening nested dictionaries
        keep_db: Whether to keep the temporary database file

    Returns:
        Path to generated markdown file
    """
    import yaml

    from yaml_shredder.data_loader import SQLiteLoader
    from yaml_shredder.table_generator import TableGenerator

    # Load YAML data
    with open(yaml_path) as f:
        data = yaml.safe_load(f)

    # Create temporary database
    temp_db = output_dir / f"{yaml_path.stem}.db"

    # Generate tables
    table_gen = TableGenerator(max_depth=max_depth)
    tables = table_gen.generate_tables(data, root_table_name=root_name, source_file=yaml_path)

    # Load into SQLite
    loader = SQLiteLoader(temp_db)
    loader.connect()
    loader.load_tables(tables, if_exists="replace", create_indexes=True)
    loader.disconnect()

    # Generate markdown documentation
    doc_gen = MarkdownDocGenerator(temp_db)
    doc_gen.connect()

    output_path = output_dir / f"{yaml_path.stem}.md"
    doc_gen.generate_markdown(output_path=output_path, doc_name=yaml_path.stem.replace("-", " ").title())

    doc_gen.disconnect()

    # Clean up database if requested
    if not keep_db and temp_db.exists():
        temp_db.unlink()
        print(f"✓ Temporary database removed: {temp_db}")

    return output_path
