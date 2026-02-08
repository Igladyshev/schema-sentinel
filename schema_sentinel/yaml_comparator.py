"""YAML Comparator for Schema Sentinel.

Compares two YAML files by loading them into SQLite databases and comparing their structure and data.
"""

import logging
import sqlite3
from pathlib import Path

import pandas as pd
import yaml

from yaml_shredder import SQLiteLoader, TableGenerator

log = logging.getLogger(__name__)


class YAMLComparator:
    """Compare two YAML files by converting them to SQLite databases and comparing schemas/data."""

    def __init__(self, output_dir: Path | None = None):
        """Initialize the YAML comparator.

        Args:
            output_dir: Directory to store temporary SQLite databases. Defaults to ./temp_dbs/
        """
        self.output_dir = output_dir or Path("./temp_dbs")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def load_yaml_to_db(self, yaml_path: Path, root_table_name: str = "root") -> Path:
        """Load a YAML file into a SQLite database.

        Args:
            yaml_path: Path to the YAML file
            root_table_name: Name for the root table

        Returns:
            Path to the created SQLite database
        """
        yaml_path = Path(yaml_path)
        if not yaml_path.exists():
            raise FileNotFoundError(f"YAML file not found: {yaml_path}")

        # Create database path based on YAML filename
        db_path = self.output_dir / f"{yaml_path.stem}.db"

        log.info(f"Loading {yaml_path} into {db_path}")

        # Load YAML data
        with open(yaml_path) as f:
            data = yaml.safe_load(f)

        # Generate tables from YAML structure
        table_gen = TableGenerator()
        tables = table_gen.generate_tables(data, root_table_name=root_table_name, source_file=yaml_path)

        log.info(f"Generated {len(tables)} tables from {yaml_path.name}")

        # Load tables into SQLite
        loader = SQLiteLoader(db_path)
        loader.connect()
        try:
            loader.load_tables(tables, if_exists="replace", create_indexes=True)
            log.info(f"Successfully loaded data into {db_path}")
        finally:
            loader.disconnect()

        return db_path

    def get_table_info(self, db_path: Path) -> dict[str, pd.DataFrame]:
        """Get schema information for all tables in a SQLite database.

        Args:
            db_path: Path to the SQLite database

        Returns:
            Dictionary mapping table names to their schema DataFrames
        """
        conn = sqlite3.connect(db_path)
        try:
            # Get list of tables
            tables_query = "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
            tables_df = pd.read_sql_query(tables_query, conn)
            table_names = tables_df["name"].tolist()

            # Get schema for each table
            table_schemas = {}
            for table_name in table_names:
                schema_query = f"PRAGMA table_info({table_name})"
                schema_df = pd.read_sql_query(schema_query, conn)
                table_schemas[table_name] = schema_df

            return table_schemas
        finally:
            conn.close()

    def get_row_counts(self, db_path: Path) -> dict[str, int]:
        """Get row counts for all tables in a SQLite database.

        Args:
            db_path: Path to the SQLite database

        Returns:
            Dictionary mapping table names to their row counts
        """
        conn = sqlite3.connect(db_path)
        try:
            # Get list of tables
            tables_query = "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
            tables_df = pd.read_sql_query(tables_query, conn)
            table_names = tables_df["name"].tolist()

            # Get row count for each table
            row_counts = {}
            for table_name in table_names:
                count_query = f"SELECT COUNT(*) as count FROM {table_name}"
                count_df = pd.read_sql_query(count_query, conn)
                row_counts[table_name] = int(count_df["count"].iloc[0])

            return row_counts
        finally:
            conn.close()

    def compare_databases(self, db1_path: Path, db2_path: Path) -> dict:
        """Compare two SQLite databases.

        Args:
            db1_path: Path to the first SQLite database
            db2_path: Path to the second SQLite database

        Returns:
            Dictionary containing comparison results
        """
        log.info(f"Comparing {db1_path.name} with {db2_path.name}")

        # Get table information
        db1_schemas = self.get_table_info(db1_path)
        db2_schemas = self.get_table_info(db2_path)

        db1_tables = set(db1_schemas.keys())
        db2_tables = set(db2_schemas.keys())

        # Get row counts
        db1_counts = self.get_row_counts(db1_path)
        db2_counts = self.get_row_counts(db2_path)

        comparison = {
            "db1_name": db1_path.stem,
            "db2_name": db2_path.stem,
            "tables_only_in_db1": sorted(db1_tables - db2_tables),
            "tables_only_in_db2": sorted(db2_tables - db1_tables),
            "common_tables": sorted(db1_tables & db2_tables),
            "schema_differences": {},
            "row_count_differences": {},
        }

        # Compare schemas for common tables
        for table_name in comparison["common_tables"]:
            schema1 = db1_schemas[table_name]
            schema2 = db2_schemas[table_name]

            # Compare column names and types
            schema1_cols = set(zip(schema1["name"].tolist(), schema1["type"].tolist(), strict=True))
            schema2_cols = set(zip(schema2["name"].tolist(), schema2["type"].tolist(), strict=True))

            cols_only_in_1 = schema1_cols - schema2_cols
            cols_only_in_2 = schema2_cols - schema1_cols

            if cols_only_in_1 or cols_only_in_2:
                comparison["schema_differences"][table_name] = {
                    "columns_only_in_db1": sorted(cols_only_in_1),
                    "columns_only_in_db2": sorted(cols_only_in_2),
                }

            # Compare row counts
            count1 = db1_counts[table_name]
            count2 = db2_counts[table_name]
            if count1 != count2:
                comparison["row_count_differences"][table_name] = {
                    "db1_count": count1,
                    "db2_count": count2,
                    "difference": count2 - count1,
                }

        return comparison

    def generate_report(self, comparison: dict, output_path: Path | None = None) -> str:
        """Generate a markdown report from comparison results.

        Args:
            comparison: Comparison results from compare_databases
            output_path: Optional path to save the report. If provided, writes to file.

        Returns:
            Markdown formatted report as a string
        """
        lines = []
        lines.append("# YAML Comparison Report")
        lines.append("")
        lines.append("## Summary")
        lines.append("")
        lines.append(f"- **File 1:** {comparison['db1_name']}")
        lines.append(f"- **File 2:** {comparison['db2_name']}")
        lines.append(f"- **Tables in common:** {len(comparison['common_tables'])}")
        lines.append(f"- **Tables only in File 1:** {len(comparison['tables_only_in_db1'])}")
        lines.append(f"- **Tables only in File 2:** {len(comparison['tables_only_in_db2'])}")
        lines.append(f"- **Schema differences:** {len(comparison['schema_differences'])}")
        lines.append(f"- **Row count differences:** {len(comparison['row_count_differences'])}")
        lines.append("")

        # Tables only in DB1
        if comparison["tables_only_in_db1"]:
            lines.append("## Tables Only in File 1")
            lines.append("")
            for table in comparison["tables_only_in_db1"]:
                lines.append(f"- `{table}`")
            lines.append("")

        # Tables only in DB2
        if comparison["tables_only_in_db2"]:
            lines.append("## Tables Only in File 2")
            lines.append("")
            for table in comparison["tables_only_in_db2"]:
                lines.append(f"- `{table}`")
            lines.append("")

        # Schema differences
        if comparison["schema_differences"]:
            lines.append("## Schema Differences")
            lines.append("")
            for table, diffs in comparison["schema_differences"].items():
                lines.append(f"### Table: `{table}`")
                lines.append("")
                if diffs["columns_only_in_db1"]:
                    lines.append("**Columns only in File 1:**")
                    for col_name, col_type in diffs["columns_only_in_db1"]:
                        lines.append(f"- `{col_name}` ({col_type})")
                    lines.append("")
                if diffs["columns_only_in_db2"]:
                    lines.append("**Columns only in File 2:**")
                    for col_name, col_type in diffs["columns_only_in_db2"]:
                        lines.append(f"- `{col_name}` ({col_type})")
                    lines.append("")

        # Row count differences
        if comparison["row_count_differences"]:
            lines.append("## Row Count Differences")
            lines.append("")
            lines.append("| Table | File 1 Count | File 2 Count | Difference |")
            lines.append("|-------|--------------|--------------|------------|")
            for table, counts in comparison["row_count_differences"].items():
                diff_str = f"+{counts['difference']}" if counts["difference"] > 0 else str(counts["difference"])
                lines.append(f"| `{table}` | {counts['db1_count']} | {counts['db2_count']} | {diff_str} |")
            lines.append("")

        # Common tables with no differences
        tables_with_no_diffs = [
            t
            for t in comparison["common_tables"]
            if t not in comparison["schema_differences"] and t not in comparison["row_count_differences"]
        ]
        if tables_with_no_diffs:
            lines.append("## Tables with No Differences")
            lines.append("")
            for table in tables_with_no_diffs:
                lines.append(f"- `{table}`")
            lines.append("")

        report = "\n".join(lines)

        # Save to file if output path provided
        if output_path:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "w") as f:
                f.write(report)
            log.info(f"Report saved to {output_path}")

        return report

    def compare_yaml_files(
        self,
        yaml1_path: Path,
        yaml2_path: Path,
        output_report: Path | None = None,
        keep_dbs: bool = False,
        root_table_name: str = "root",
    ) -> str:
        """Complete workflow: load two YAML files, compare, and generate report.

        Args:
            yaml1_path: Path to the first YAML file
            yaml2_path: Path to the second YAML file
            output_report: Optional path to save the comparison report
            keep_dbs: Whether to keep the temporary SQLite databases
            root_table_name: Name for the root table in both databases

        Returns:
            Markdown formatted comparison report
        """
        log.info(f"Comparing {yaml1_path.name} with {yaml2_path.name}")

        # Load YAML files into databases
        db1_path = self.load_yaml_to_db(yaml1_path, root_table_name=root_table_name)
        db2_path = self.load_yaml_to_db(yaml2_path, root_table_name=root_table_name)

        # Compare databases
        comparison = self.compare_databases(db1_path, db2_path)

        # Generate report
        report = self.generate_report(comparison, output_path=output_report)

        # Clean up databases if requested
        if not keep_dbs:
            db1_path.unlink(missing_ok=True)
            db2_path.unlink(missing_ok=True)
            log.info("Temporary databases cleaned up")

        return report
