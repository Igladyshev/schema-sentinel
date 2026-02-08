"""Generate tabular structures from nested YAML/JSON data."""

from pathlib import Path
from typing import Any

import pandas as pd


class TableGenerator:
    """Generate relational tables from nested data structures."""

    def __init__(self, max_depth: int | None = None):
        """Initialize the table generator.

        Args:
            max_depth: Maximum depth for flattening nested dictionaries.
                      0 = no flattening (keep nested dicts as JSON)
                      1 = flatten first level only (keep nested objects like 'deployment' as separate columns)
                      2+ = flatten deeper levels
                      None = flatten all levels (default behavior)
        """
        self.tables = {}
        self.relationships = []
        self.max_depth = max_depth

    def generate_tables(
        self, data: dict[str, Any], root_table_name: str = "ROOT", source_file: Path | None = None
    ) -> dict[str, pd.DataFrame]:
        """
        Generate tables from nested data.

        Strategy:
        - Root-level scalar attributes → descriptor table (named after file)
        - Root-level dictionaries → separate tables (one per dict key)
        - Root-level arrays → separate tables (existing behavior)

        Args:
            data: Source data dictionary
            root_table_name: Name for the root table (used if no source_file)
            source_file: Optional source file path to use for descriptor table naming

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

        # Determine descriptor table name from file
        descriptor_table_name = source_file.stem.upper() if source_file else root_table_name

        # Separate root-level data into scalars, dicts, and arrays
        root_scalars = {}
        root_dicts = {}
        root_arrays = {}

        for key, value in data.items():
            if isinstance(value, dict):
                root_dicts[key] = value
            elif isinstance(value, list):
                root_arrays[key] = value
            else:
                root_scalars[key] = value

        # Create descriptor table with scalar attributes only
        if root_scalars:
            df = pd.DataFrame([root_scalars])
            self.tables[descriptor_table_name] = df.drop_duplicates()

        # Process root-level dictionaries as separate tables
        for dict_key, dict_value in root_dicts.items():
            table_name = dict_key.upper()
            # Flatten the dict with depth control
            flattened = self._flatten_dict(dict_value, depth=0)
            if flattened:
                df = pd.DataFrame([flattened])
                self.tables[table_name] = df.drop_duplicates()

        # Process arrays at root level (arrays of objects become tables)
        self._process_structure(data, descriptor_table_name, {})

        return self.tables

    def _process_structure(self, obj: Any, parent_table: str, parent_keys: dict[str, Any], path: str = "") -> None:
        """
        Recursively process structure to extract tables from arrays.

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
                    # Nested object -> continue traversal for arrays
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
            row = self._flatten_dict(item, depth=0)

            # Add parent foreign keys
            for parent_key, parent_value in parent_keys.items():
                row[f"parent_{parent_key}"] = parent_value

            # Add row index for ordering
            row["_row_index"] = i

            rows.append(row)

        # Create DataFrame and remove duplicates
        df = pd.DataFrame(rows)

        # Drop duplicate rows (keep first occurrence)
        # Exclude _row_index from duplicate check if it exists
        subset_cols = [col for col in df.columns if col != "_row_index"]
        if subset_cols:
            df = df.drop_duplicates(subset=subset_cols, keep="first")

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

    def _flatten_dict(self, d: dict[str, Any], parent_key: str = "", sep: str = "_", depth: int = 0) -> dict[str, Any]:
        """
        Flatten nested dictionary with depth control.

        Args:
            d: Dictionary to flatten
            parent_key: Parent key for nested items
            sep: Separator for nested keys
            depth: Current depth in flattening (0 = root level)

        Returns:
            Flattened dictionary
        """
        import json

        items = []

        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k

            if isinstance(v, dict):
                # max_depth controls how many levels to flatten
                # depth=0 means we're at root level looking at first-level nested dicts
                # If max_depth=1, we stop flattening when we encounter nested dicts (depth >= 0)
                # If max_depth=2, we flatten first level but stop at second level (depth >= 1)
                if self.max_depth is not None and depth >= self.max_depth - 1:
                    # Keep nested dict as JSON string
                    items.append((new_key, json.dumps(v, default=str)))
                else:
                    # Continue flattening
                    items.extend(self._flatten_dict(v, new_key, sep=sep, depth=depth + 1).items())
            elif isinstance(v, list):
                # For lists of objects, skip (they become separate tables)
                # For simple lists, convert to string
                if v:
                    if isinstance(v[0], dict):
                        # Skip lists of objects (they become separate tables)
                        pass
                    else:
                        # Simple list - join as string
                        items.append((new_key, ", ".join(map(str, v))))
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
