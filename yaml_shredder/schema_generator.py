"""Automatic JSON Schema generation from YAML/JSON files."""

import json
from datetime import date, datetime
from pathlib import Path
from typing import Any

import yaml
from genson import SchemaBuilder


class SchemaGenerator:
    """Generate JSON Schema from multiple YAML/JSON examples."""

    def __init__(self):
        """Initialize the schema generator."""
        self.builder = SchemaBuilder()
        self.files_processed = []

    def _normalize_data(self, obj: Any) -> Any:
        """
        Normalize data by converting datetime objects to strings.

        Args:
            obj: Data to normalize

        Returns:
            Normalized data
        """
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        elif isinstance(obj, dict):
            return {k: self._normalize_data(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._normalize_data(item) for item in obj]
        else:
            return obj

    def add_yaml_file(self, file_path: str | Path) -> None:
        """
        Add a YAML file to the schema builder.

        Args:
            file_path: Path to YAML file
        """
        file_path = Path(file_path)
        with open(file_path) as f:
            data = yaml.safe_load(f)

        normalized_data = self._normalize_data(data)
        self.builder.add_object(normalized_data)
        self.files_processed.append(str(file_path))

    def add_json_file(self, file_path: str | Path) -> None:
        """
        Add a JSON file to the schema builder.

        Args:
            file_path: Path to JSON file
        """
        file_path = Path(file_path)
        with open(file_path) as f:
            data = json.load(f)

        normalized_data = self._normalize_data(data)
        self.builder.add_object(normalized_data)
        self.files_processed.append(str(file_path))

    def add_object(self, obj: dict[str, Any]) -> None:
        """
        Add a Python object to the schema builder.

        Args:
            obj: Dictionary object to add
        """
        normalized_data = self._normalize_data(obj)
        self.builder.add_object(normalized_data)

    def generate_schema(self) -> dict[str, Any]:
        """
        Generate the JSON schema from all added examples.

        Returns:
            JSON schema as dictionary
        """
        return self.builder.to_schema()

    def save_schema(self, output_path: str | Path) -> None:
        """
        Save the generated schema to a file.

        Args:
            output_path: Path where to save the schema
        """
        schema = self.generate_schema()
        output_path = Path(output_path)

        with open(output_path, "w") as f:
            json.dump(schema, f, indent=2)

    def get_stats(self) -> dict[str, Any]:
        """
        Get statistics about the schema generation process.

        Returns:
            Dictionary with statistics
        """
        schema = self.generate_schema()
        return {
            "files_processed": len(self.files_processed),
            "file_list": self.files_processed,
            "schema_properties": len(schema.get("properties", {})),
            "required_fields": len(schema.get("required", [])),
        }


def generate_schema_from_directory(
    directory: str | Path, pattern: str = "*.yaml", output_file: str | Path | None = None
) -> dict[str, Any]:
    """
    Generate schema from all matching files in a directory.

    Args:
        directory: Directory to scan
        pattern: File pattern to match (default: *.yaml)
        output_file: Optional path to save schema

    Returns:
        Generated JSON schema
    """
    directory = Path(directory)
    generator = SchemaGenerator()

    # Find all matching files
    files = sorted(directory.rglob(pattern))

    if not files:
        raise ValueError(f"No files matching '{pattern}' found in {directory}")

    # Process each file
    for file_path in files:
        if pattern.endswith(".yaml") or pattern.endswith(".yml"):
            generator.add_yaml_file(file_path)
        elif pattern.endswith(".json"):
            generator.add_json_file(file_path)

    # Generate and optionally save schema
    schema = generator.generate_schema()

    if output_file:
        generator.save_schema(output_file)

    # Print statistics
    stats = generator.get_stats()
    print("Schema generation complete:")
    print(f"  Files processed: {stats['files_processed']}")
    print(f"  Properties found: {stats['schema_properties']}")
    print(f"  Required fields: {stats['required_fields']}")

    return schema
