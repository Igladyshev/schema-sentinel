"""Generate tabular structures from nested YAML/JSON data."""

from pathlib import Path
from typing import Any

import pandas as pd


class TableGenerator:
    """Generate relational tables from nested data structures."""

    def __init__(self):
        """Initialize the table generator."""
        self.tables = {}
        self.relationships = []

    def generate_tables(self, data: dict[str, Any], root_table_name: str = "ROOT") -> dict[str, pd.DataFrame]:
        """
        Generate tables from nested data.

        Args:
            data: Source data dictionary
            root_table_name: Name for the root table

        Returns:
            Dictionary of table_name -> DataFrame

        Raises:
            TypeError: If data is not a dictionary
        """
        # Validate input type
        if not isinstance(data, dict):
            raise TypeError(
                f"generate_tables expects a dictionary at the root level, "
                f"but got {type(data).__name__}. Lists and scalars are not supported."
            )

        # Extract root-level scalar fields into root table
        root_data = {k: v for k, v in data.items() if not isinstance(v, (list, dict))}
        if root_data:
            self.tables[root_table_name] = pd.DataFrame([root_data])

        # Process nested structures
        self._process_structure(data, root_table_name, {})

        return self.tables

    def _process_structure(self, obj: Any, parent_table: str, parent_keys: dict[str, Any], path: str = "") -> None:
        """
        Recursively process structure to extract tables.

        Args:
            obj: Object to process
            parent_table: Name of parent table
            parent_keys: Keys from parent for foreign key relationships
            path: Current path in structure
        """
        if isinstance(obj, dict):
            for key, value in obj.items():
                current_path = f"{path}.{key}" if path else key

                if isinstance(value, list) and value and isinstance(value[0], dict):
                    # Array of objects -> create table
                    table_name = self._path_to_table_name(current_path)
                    self._create_table_from_array(value, table_name, parent_table, parent_keys)
                elif isinstance(value, dict):
                    # Nested object -> continue traversal
                    self._process_structure(value, parent_table, parent_keys, current_path)

    def _create_table_from_array(
        self, array: list[dict[str, Any]], table_name: str, parent_table: str, parent_keys: dict[str, Any]
    ) -> None:
        """
        Create a table from an array of objects.

        Args:
            array: Array of objects
            table_name: Name for the table
            parent_table: Parent table name
            parent_keys: Parent keys for relationships
        """
        # Flatten objects and add parent foreign keys
        rows = []
        for i, item in enumerate(array):
            row = self._flatten_dict(item)

            # Add parent foreign keys
            for parent_key, parent_value in parent_keys.items():
                row[f"parent_{parent_key}"] = parent_value

            # Add row index for ordering
            row["_row_index"] = i

            rows.append(row)

        # Create DataFrame
        df = pd.DataFrame(rows)

        # Store table
        self.tables[table_name] = df

        # Record relationship
        if parent_keys:
            self.relationships.append(
                {"parent_table": parent_table, "child_table": table_name, "foreign_keys": list(parent_keys.keys())}
            )

        # Process nested arrays within this array
        for i, item in enumerate(array):  # noqa: B007
            item_keys = {**parent_keys}
            # Add identifying keys from this level
            for key in ["id", "name", "code"]:
                if key in item:
                    item_keys[key] = item[key]
                    break

            for key, value in item.items():
                if isinstance(value, list) and value and isinstance(value[0], dict):
                    nested_table_name = f"{table_name}_{key}"
                    self._create_table_from_array(value, nested_table_name, table_name, item_keys)

    def _flatten_dict(self, d: dict[str, Any], parent_key: str = "", sep: str = "_") -> dict[str, Any]:
        """
        Flatten nested dictionary, keeping only scalar values.

        Args:
            d: Dictionary to flatten
            parent_key: Parent key for nested items
            sep: Separator for nested keys

        Returns:
            Flattened dictionary
        """
        items = []

        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k

            if isinstance(v, dict):
                # Recursively flatten nested dict
                items.extend(self._flatten_dict(v, new_key, sep=sep).items())
            elif isinstance(v, list):
                # For lists, convert to JSON string or skip
                if v and not isinstance(v[0], dict):
                    # Simple list - join as string
                    items.append((new_key, ", ".join(map(str, v))))
                # Skip lists of objects (they become separate tables)
            else:
                # Scalar value
                items.append((new_key, v))

        return dict(items)

    def _path_to_table_name(self, path: str) -> str:
        """
        Convert path to table name.

        Args:
            path: Path like "actions" or "warehouse.settings"

        Returns:
            Table name
        """
        parts = path.replace(".", "_").split("_")
        return "_".join(parts).upper()

    def save_tables(self, output_dir: str | Path, format: str = "csv") -> None:
        """
        Save all tables to files.

        Args:
            output_dir: Directory to save tables
            format: Output format ('csv', 'parquet', 'excel')
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        for table_name, df in self.tables.items():
            if format == "csv":
                filepath = output_dir / f"{table_name}.csv"
                df.to_csv(filepath, index=False)
            elif format == "parquet":
                filepath = output_dir / f"{table_name}.parquet"
                df.to_parquet(filepath, index=False)
            elif format == "excel":
                filepath = output_dir / f"{table_name}.xlsx"
                df.to_excel(filepath, index=False)

            print(f"Saved {table_name}: {len(df)} rows, {len(df.columns)} columns -> {filepath}")

    def print_summary(self) -> None:
        """Print summary of generated tables."""
        print(f"\n{'=' * 60}")
        print("GENERATED TABLES SUMMARY")
        print(f"{'=' * 60}\n")

        print(f"Total tables: {len(self.tables)}\n")

        for table_name, df in self.tables.items():
            print(f"Table: {table_name}")
            print(f"  Rows: {len(df)}")
            print(f"  Columns: {len(df.columns)}")
            print(f"  Column names: {', '.join(df.columns[:5])}")
            if len(df.columns) > 5:
                print(f"    ... and {len(df.columns) - 5} more")
            print()

        if self.relationships:
            print(f"{'-' * 60}")
            print("RELATIONSHIPS:")
            print(f"{'-' * 60}\n")
            for rel in self.relationships:
                print(f"{rel['parent_table']} -> {rel['child_table']}")
                print(f"  Foreign keys: {', '.join(rel['foreign_keys'])}\n")
