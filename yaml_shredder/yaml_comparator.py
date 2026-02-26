"""YAML Comparator for comparing YAML files.

Compares two YAML files by loading them into SQLite or DuckDB databases and comparing their structure and data.
"""

import json
import logging
import sqlite3
from copy import deepcopy
from pathlib import Path
from typing import Any

import pandas as pd
import yaml

from yaml_shredder.data_comparer import DataComparer
from yaml_shredder.data_loader import DuckDBLoader, SQLiteLoader
from yaml_shredder.table_generator import TableGenerator

log = logging.getLogger(__name__)


class YAMLComparator:
    """Compare two YAML files by converting them to SQLite or DuckDB databases and comparing schemas/data."""

    def __init__(self, output_dir: Path | None = None, use_duckdb: bool = False):
        """Initialize the YAML comparator.

        Args:
            output_dir: Directory to store temporary databases. Defaults to ./temp_dbs/
            use_duckdb: If True, use DuckDB instead of SQLite (faster for complex data)
        """
        self.output_dir = output_dir or Path("./temp_dbs")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.use_duckdb = use_duckdb

    def load_yaml_to_db(self, yaml_path: Path, root_table_name: str = "root", max_depth: int | None = None) -> Path:
        """Load a YAML file into a SQLite or DuckDB database.

        Args:
            yaml_path: Path to the YAML file
            root_table_name: Name for the root table
            max_depth: Maximum depth for flattening nested dictionaries

        Returns:
            Path to the created database
        """
        yaml_path = Path(yaml_path)
        if not yaml_path.exists():
            raise FileNotFoundError(f"YAML file not found: {yaml_path}")

        # Create database path based on YAML filename
        db_ext = ".duckdb" if self.use_duckdb else ".db"
        db_path = self.output_dir / f"{yaml_path.stem}{db_ext}"

        log.info(f"Loading {yaml_path} into {db_path} (using {'DuckDB' if self.use_duckdb else 'SQLite'})")

        # Load YAML data
        with open(yaml_path) as f:
            data = yaml.safe_load(f)

        # Generate tables from YAML structure
        table_gen = TableGenerator(max_depth=max_depth)
        tables = table_gen.generate_tables(data, root_table_name=root_table_name, source_file=yaml_path)

        log.info(f"Generated {len(tables)} tables from {yaml_path.name}")

        # Load tables into chosen database
        if self.use_duckdb:
            loader = DuckDBLoader(db_path)
        else:
            loader = SQLiteLoader(db_path)

        loader.connect()
        try:
            loader.load_tables(tables, if_exists="replace", create_indexes=True)
            log.info(f"Successfully loaded data into {db_path}")
        finally:
            loader.disconnect()

        return db_path

    def get_table_info(self, db_path: Path) -> dict[str, pd.DataFrame]:
        """Get schema information for all tables in SQLite or DuckDB database.

        Args:
            db_path: Path to the database

        Returns:
            Dictionary mapping table names to their schema DataFrames
        """
        if self.use_duckdb:
            # Use DuckDB
            loader = DuckDBLoader(db_path)
            loader.connect()
            try:
                table_names = loader.list_tables()
                table_schemas = {}
                for table_name in table_names:
                    schema_df = loader.get_table_info(table_name)
                    table_schemas[table_name] = schema_df
                return table_schemas
            finally:
                loader.disconnect()
        else:
            # Use SQLite
            conn = sqlite3.connect(db_path)
            try:
                # Get list of tables
                tables_query = "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
                tables_df = pd.read_sql_query(tables_query, conn)
                table_names = tables_df["name"].tolist()

                # Get schema for each table
                table_schemas = {}
                for table_name in table_names:
                    schema_query = f'PRAGMA table_info("{table_name}")'
                    schema_df = pd.read_sql_query(schema_query, conn)
                    table_schemas[table_name] = schema_df

                return table_schemas
            finally:
                conn.close()

    def get_row_counts(self, db_path: Path) -> dict[str, int]:
        """Get row counts for all tables in SQLite or DuckDB database.

        Args:
            db_path: Path to the database

        Returns:
            Dictionary mapping table names to their row counts
        """
        if self.use_duckdb:
            # Use DuckDB
            loader = DuckDBLoader(db_path)
            loader.connect()
            try:
                table_names = loader.list_tables()
                row_counts = {}
                for table_name in table_names:
                    count_result = loader.query(f'SELECT COUNT(*) as count FROM "{table_name}"')
                    row_counts[table_name] = int(count_result["count"].iloc[0])
                return row_counts
            finally:
                loader.disconnect()
        else:
            # Use SQLite
            conn = sqlite3.connect(db_path)
            try:
                # Get list of tables
                tables_query = "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
                tables_df = pd.read_sql_query(tables_query, conn)
                table_names = tables_df["name"].tolist()

                # Get row count for each table
                row_counts = {}
                for table_name in table_names:
                    count_query = f'SELECT COUNT(*) as count FROM "{table_name}"'
                    count_df = pd.read_sql_query(count_query, conn)
                    row_counts[table_name] = int(count_df["count"].iloc[0])

                return row_counts
            finally:
                conn.close()

    def compare_databases(self, db1_path: Path, db2_path: Path) -> dict:
        """Compare two databases (SQLite or DuckDB).

        Args:
            db1_path: Path to the first database
            db2_path: Path to the second database

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

    def _load_structured_file(self, file_path: Path) -> dict[str, Any]:
        """Load a YAML or JSON file and validate root type.

        Args:
            file_path: File path to load

        Returns:
            Parsed dictionary data

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file content is invalid for sync
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        if not file_path.is_file():
            raise ValueError(f"Path is not a file: {file_path}")
        if file_path.stat().st_size == 0:
            raise ValueError(f"File is empty: {file_path}")

        allowed_extensions = {".yaml", ".yml", ".json"}
        suffix = file_path.suffix.lower()
        if suffix and suffix not in allowed_extensions:
            raise ValueError(
                f"Unsupported file extension for sync: {file_path.suffix}. Supported extensions: .yaml, .yml, .json"
            )

        with open(file_path) as f:
            if suffix == ".json":
                try:
                    data = json.load(f)
                except json.JSONDecodeError as exc:
                    raise ValueError(f"Invalid JSON file: {file_path}") from exc
            else:
                try:
                    data = yaml.safe_load(f)
                except yaml.YAMLError as exc:
                    raise ValueError(f"Invalid YAML file: {file_path}") from exc

        if data is None:
            raise ValueError(f"File contains no data: {file_path}")
        if not isinstance(data, dict):
            raise ValueError(f"File {file_path} must contain a dictionary at root level, got {type(data).__name__}")

        return data

    def _schema_signature(self, node: Any) -> dict[str, Any]:
        """Build a deterministic schema signature for nested structures."""
        if isinstance(node, dict):
            return {
                "type": "dict",
                "keys": {key: self._schema_signature(value) for key, value in sorted(node.items())},
            }
        if isinstance(node, list):
            item_signatures = [self._schema_signature(item) for item in node]
            unique_signatures = sorted(
                {json.dumps(signature, sort_keys=True, separators=(",", ":")) for signature in item_signatures}
            )
            return {
                "type": "list",
                "items": [json.loads(signature) for signature in unique_signatures],
            }
        return {"type": type(node).__name__}

    def _validate_sync_inputs(self, left_file: Path, right_file: Path) -> tuple[dict[str, Any], dict[str, Any]]:
        """Validate sync inputs and ensure schema compatibility."""
        left_path = Path(left_file)
        right_path = Path(right_file)

        if left_path.resolve() == right_path.resolve():
            raise ValueError("left_file and right_file must be different files")

        left_data = self._load_structured_file(left_path)
        right_data = self._load_structured_file(right_path)

        left_schema = self._schema_signature(left_data)
        right_schema = self._schema_signature(right_data)

        if left_schema != right_schema:
            raise ValueError(
                "Input files do not share the same schema. "
                "Run comparison report to inspect structural differences before merge."
            )

        return left_data, right_data

    def _path_to_str(self, path: tuple[str, ...]) -> str:
        """Convert a path tuple to a display string."""
        if not path:
            return "$"
        return "$." + ".".join(path)

    def _collect_discrepancies(
        self,
        left_node: Any,
        right_node: Any,
        path: tuple[str, ...],
        discrepancies: dict[str, list[dict[str, Any]]],
    ) -> None:
        """Recursively collect node-level discrepancies between two structures."""
        if isinstance(left_node, dict) and isinstance(right_node, dict):
            left_keys = set(left_node)
            right_keys = set(right_node)

            for key in sorted(left_keys - right_keys):
                discrepancies["missing_in_right"].append(
                    {
                        "path": self._path_to_str(path + (str(key),)),
                        "node": left_node[key],
                    }
                )

            for key in sorted(right_keys - left_keys):
                discrepancies["missing_in_left"].append(
                    {
                        "path": self._path_to_str(path + (str(key),)),
                        "node": right_node[key],
                    }
                )

            for key in sorted(left_keys & right_keys):
                self._collect_discrepancies(
                    left_node[key],
                    right_node[key],
                    path + (str(key),),
                    discrepancies,
                )
            return

        if isinstance(left_node, list) and isinstance(right_node, list):
            max_len = max(len(left_node), len(right_node))
            for index in range(max_len):
                segment = f"[{index}]"
                if index >= len(right_node):
                    discrepancies["missing_in_right"].append(
                        {
                            "path": self._path_to_str(path + (segment,)),
                            "node": left_node[index],
                        }
                    )
                    continue
                if index >= len(left_node):
                    discrepancies["missing_in_left"].append(
                        {
                            "path": self._path_to_str(path + (segment,)),
                            "node": right_node[index],
                        }
                    )
                    continue
                self._collect_discrepancies(left_node[index], right_node[index], path + (segment,), discrepancies)
            return

        if left_node != right_node:
            discrepancies["different_values"].append(
                {
                    "path": self._path_to_str(path),
                    "left": left_node,
                    "right": right_node,
                    "left_type": type(left_node).__name__,
                    "right_type": type(right_node).__name__,
                }
            )

    def _format_value(self, value: Any) -> str:
        """Format Python value for markdown report blocks."""
        return yaml.safe_dump(value, sort_keys=True, allow_unicode=True, default_flow_style=False).rstrip()

    def _build_sync_markdown_report(
        self,
        left_file: Path,
        right_file: Path,
        base_report: str,
        discrepancies: dict[str, list[dict[str, Any]]],
        merge_direction: str,
        merged_outputs: dict[str, Path],
    ) -> str:
        """Build markdown report for sync discrepancies and merge summary."""
        lines = [base_report, "", "---", "", "# YAML Sync Discrepancy Details", ""]
        lines.append("## Inputs")
        lines.append("")
        lines.append(f"- **Left file:** `{left_file}`")
        lines.append(f"- **Right file:** `{right_file}`")
        lines.append("")
        lines.append("## Node Difference Summary")
        lines.append("")
        lines.append(f"- **Missing in right:** {len(discrepancies['missing_in_right'])}")
        lines.append(f"- **Missing in left:** {len(discrepancies['missing_in_left'])}")
        lines.append(f"- **Different values:** {len(discrepancies['different_values'])}")
        lines.append("")

        if discrepancies["missing_in_right"]:
            lines.append("## Nodes Missing in Right")
            lines.append("")
            for item in discrepancies["missing_in_right"]:
                lines.append(f"### `{item['path']}`")
                lines.append("")
                lines.append("```yaml")
                lines.append(self._format_value(item["node"]))
                lines.append("```")
                lines.append("")

        if discrepancies["missing_in_left"]:
            lines.append("## Nodes Missing in Left")
            lines.append("")
            for item in discrepancies["missing_in_left"]:
                lines.append(f"### `{item['path']}`")
                lines.append("")
                lines.append("```yaml")
                lines.append(self._format_value(item["node"]))
                lines.append("```")
                lines.append("")

        if discrepancies["different_values"]:
            lines.append("## Different Values")
            lines.append("")
            for item in discrepancies["different_values"]:
                lines.append(f"### `{item['path']}`")
                lines.append("")
                lines.append(f"- **Left type:** `{item['left_type']}`")
                lines.append(f"- **Right type:** `{item['right_type']}`")
                lines.append("")
                lines.append("**Left value:**")
                lines.append("```yaml")
                lines.append(self._format_value(item["left"]))
                lines.append("```")
                lines.append("")
                lines.append("**Right value:**")
                lines.append("```yaml")
                lines.append(self._format_value(item["right"]))
                lines.append("```")
                lines.append("")

        lines.append("## Merge")
        lines.append("")
        lines.append(f"- **Direction:** `{merge_direction}`")
        if merged_outputs:
            lines.append("- **Updated files:**")
            for side, path in merged_outputs.items():
                lines.append(f"  - `{side}`: `{path}`")
        else:
            lines.append("- **Updated files:** none (report-only mode)")
        lines.append("")

        return "\n".join(lines)

    def _merge_structures(self, source: Any, target: Any) -> Any:
        """Merge source into target recursively with source winning conflicts."""
        if isinstance(source, dict) and isinstance(target, dict):
            merged = deepcopy(target)
            for key, source_value in source.items():
                if key in merged:
                    merged[key] = self._merge_structures(source_value, merged[key])
                else:
                    merged[key] = deepcopy(source_value)
            return merged

        if isinstance(source, list):
            return deepcopy(source)

        return deepcopy(source)

    def _write_structured_file(self, path: Path, data: dict[str, Any]) -> None:
        """Write merged data preserving YAML/JSON based on file extension."""
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.suffix.lower() == ".json":
            with open(path, "w") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                f.write("\n")
            return

        with open(path, "w") as f:
            yaml.safe_dump(data, f, sort_keys=False, allow_unicode=True)

    def sync_yaml_files(
        self,
        left_file: Path,
        right_file: Path,
        output_report: Path | None = None,
        merge_direction: str = "none",
        keep_dbs: bool = False,
        root_table_name: str = "root",
        max_depth: int | None = None,
        left_output: Path | None = None,
        right_output: Path | None = None,
    ) -> dict[str, Any]:
        """Validate, compare, report differences, and optionally merge two YAML/JSON files.

        Args:
            left_file: Path to the left YAML/JSON file
            right_file: Path to the right YAML/JSON file
            output_report: Optional path for markdown report
            merge_direction: Merge direction: none, left-to-right, right-to-left, both
            keep_dbs: Whether to keep temporary comparison databases
            root_table_name: Root table name for database comparison workflow
            max_depth: Maximum flattening depth for DB comparison
            left_output: Optional output path for left result (for merges affecting left)
            right_output: Optional output path for right result (for merges affecting right)

        Returns:
            Dict with report content, report path, discrepancies, and merged output paths
        """
        allowed_directions = {"none", "left-to-right", "right-to-left", "both"}
        if merge_direction not in allowed_directions:
            raise ValueError(
                f"Invalid merge_direction: {merge_direction}. Expected one of: none, left-to-right, right-to-left, both"
            )

        left_path = Path(left_file)
        right_path = Path(right_file)
        left_data, right_data = self._validate_sync_inputs(left_path, right_path)

        schema_report = self.compare_yaml_files(
            yaml1_path=left_path,
            yaml2_path=right_path,
            output_report=None,
            keep_dbs=keep_dbs,
            root_table_name=root_table_name,
            max_depth=max_depth,
        )

        discrepancies: dict[str, list[dict[str, Any]]] = {
            "missing_in_right": [],
            "missing_in_left": [],
            "different_values": [],
        }
        self._collect_discrepancies(left_data, right_data, (), discrepancies)

        merged_outputs: dict[str, Path] = {}
        if merge_direction in {"left-to-right", "both"}:
            merged_right = self._merge_structures(left_data, right_data)
            right_target = Path(right_output) if right_output else right_path
            self._write_structured_file(right_target, merged_right)
            merged_outputs["right"] = right_target

        if merge_direction in {"right-to-left", "both"}:
            merged_left = self._merge_structures(right_data, left_data)
            left_target = Path(left_output) if left_output else left_path
            self._write_structured_file(left_target, merged_left)
            merged_outputs["left"] = left_target

        report_path = (
            Path(output_report) if output_report else Path(f"{left_path.stem}_vs_{right_path.stem}_sync_report.md")
        )
        report = self._build_sync_markdown_report(
            left_file=left_path,
            right_file=right_path,
            base_report=schema_report,
            discrepancies=discrepancies,
            merge_direction=merge_direction,
            merged_outputs=merged_outputs,
        )

        report_path.parent.mkdir(parents=True, exist_ok=True)
        with open(report_path, "w") as f:
            f.write(report)

        return {
            "report": report,
            "report_path": report_path,
            "discrepancies": discrepancies,
            "merge_direction": merge_direction,
            "merged_outputs": merged_outputs,
        }

    def compare_yaml_files(
        self,
        yaml1_path: Path,
        yaml2_path: Path,
        output_report: Path | None = None,
        keep_dbs: bool = False,
        root_table_name: str = "root",
        max_depth: int | None = None,
    ) -> str:
        """Complete workflow: load two YAML files, compare, and generate report.

        Args:
            yaml1_path: Path to the first YAML file
            yaml2_path: Path to the second YAML file
            output_report: Optional path to save the comparison report
            keep_dbs: Whether to keep the temporary SQLite databases
            root_table_name: Name for the root table in both databases
            max_depth: Maximum depth for flattening nested dictionaries

        Returns:
            Markdown formatted comparison report
        """
        log.info(f"Comparing {yaml1_path.name} with {yaml2_path.name}")

        # Load YAML files into databases
        db1_path = self.load_yaml_to_db(yaml1_path, root_table_name=root_table_name, max_depth=max_depth)
        db2_path = self.load_yaml_to_db(yaml2_path, root_table_name=root_table_name, max_depth=max_depth)

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

    def compare_data(
        self,
        yaml1_path: Path,
        yaml2_path: Path,
        output_report: Path | None = None,
        root_table_name: str = "root",
        max_depth: int | None = None,
        primary_keys: dict[str, list[str]] | None = None,
    ) -> dict:
        """Full data comparison workflow: analyze, match tables, and compare data.

        This performs deep data comparison using primary key detection to identify
        added, removed, and modified records across matched tables.

        Args:
            yaml1_path: Path to the first YAML file
            yaml2_path: Path to the second YAML file
            output_report: Optional path to save the comparison report
            root_table_name: Name for the root table in both datasets
            max_depth: Maximum depth for flattening nested dictionaries
            primary_keys: Optional dict of table_name -> primary_key columns for explicit PK specification

        Returns:
            Dictionary containing full data comparison results
        """
        yaml1_path = Path(yaml1_path)
        yaml2_path = Path(yaml2_path)

        log.info(f"Performing full data comparison: {yaml1_path.name} vs {yaml2_path.name}")

        # Load YAML data
        with open(yaml1_path) as f:
            data1 = yaml.safe_load(f)
        with open(yaml2_path) as f:
            data2 = yaml.safe_load(f)

        # Generate tables from both YAML files
        table_gen1 = TableGenerator(max_depth=max_depth)
        tables1 = table_gen1.generate_tables(data1, root_table_name=root_table_name, source_file=yaml1_path)

        table_gen2 = TableGenerator(max_depth=max_depth)
        tables2 = table_gen2.generate_tables(data2, root_table_name=root_table_name, source_file=yaml2_path)

        log.info(f"Generated {len(tables1)} tables from {yaml1_path.name}")
        log.info(f"Generated {len(tables2)} tables from {yaml2_path.name}")

        # Compare datasets using DataComparer
        comparer = DataComparer()
        comparison = comparer.compare_datasets(tables1, tables2, primary_keys=primary_keys)

        # Add file metadata
        comparison["metadata"] = {
            "file1": str(yaml1_path),
            "file2": str(yaml2_path),
            "file1_name": yaml1_path.name,
            "file2_name": yaml2_path.name,
        }

        # Generate and save report if requested
        if output_report:
            report = comparer.generate_comparison_report(comparison)
            output_path = Path(output_report)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "w") as f:
                f.write(report)
            log.info(f"Data comparison report saved to {output_path}")

        return comparison

    def compare_yaml_files_full(
        self,
        yaml1_path: Path,
        yaml2_path: Path,
        output_report: Path | None = None,
        keep_dbs: bool = False,
        root_table_name: str = "root",
        max_depth: int | None = None,
        primary_keys: dict[str, list[str]] | None = None,
    ) -> tuple[str, dict]:
        """Complete workflow combining schema comparison and data comparison.

        This provides both structure comparison (existing behavior) and
        full data comparison with primary key detection.

        Args:
            yaml1_path: Path to the first YAML file
            yaml2_path: Path to the second YAML file
            output_report: Optional path to save the comparison report
            keep_dbs: Whether to keep the temporary SQLite databases
            root_table_name: Name for the root table in both databases
            max_depth: Maximum depth for flattening nested dictionaries
            primary_keys: Optional dict of table_name -> primary_key columns

        Returns:
            Tuple of (schema_report_markdown, data_comparison_dict)
        """
        # Run schema comparison (existing)
        schema_report = self.compare_yaml_files(
            yaml1_path=yaml1_path,
            yaml2_path=yaml2_path,
            output_report=None,
            keep_dbs=keep_dbs,
            root_table_name=root_table_name,
            max_depth=max_depth,
        )

        # Run data comparison (new)
        output_path = Path(output_report) if output_report else None
        data_output = output_path.with_suffix(".data.md") if output_path else None
        data_comparison = self.compare_data(
            yaml1_path=yaml1_path,
            yaml2_path=yaml2_path,
            output_report=data_output,
            root_table_name=root_table_name,
            max_depth=max_depth,
            primary_keys=primary_keys,
        )

        # Save combined report if requested
        if output_path:
            comparer = DataComparer()
            data_report = comparer.generate_comparison_report(data_comparison)

            combined_report = schema_report + "\n\n---\n\n" + data_report
            with open(output_path, "w") as f:
                f.write(combined_report)
            log.info(f"Combined comparison report saved to {output_path}")

        return schema_report, data_comparison
