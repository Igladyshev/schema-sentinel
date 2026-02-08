"""Analyze and detect repeating structures in YAML/JSON data."""

from collections import defaultdict
from typing import Any


class StructureAnalyzer:
    """Analyze nested structures and detect repeating patterns."""

    def __init__(self, max_depth: int | None = None):
        """Initialize the structure analyzer.

        Args:
            max_depth: Maximum depth for flattening nested dictionaries.
                      This affects which arrays will become tables.
                      None = all arrays become tables (default)
        """
        self.arrays_found = []
        self.structure_patterns = defaultdict(list)
        self.max_depth = max_depth

    def analyze(self, data: dict[str, Any], path: str = "", depth: int = 0) -> dict[str, Any]:
        """
        Analyze data structure and detect repeating patterns.

        Args:
            data: Dictionary to analyze
            path: Current path in the structure (for nested objects)
            depth: Current dictionary nesting depth (for depth control)

        Returns:
            Analysis results including arrays and patterns
        """
        self._traverse(data, path, depth)

        return {
            "total_arrays": len(self.arrays_found),
            "arrays": self.arrays_found,
            "structure_patterns": dict(self.structure_patterns),
        }

    def _traverse(self, obj: Any, path: str = "", depth: int = 0) -> None:
        """
        Recursively traverse the object structure.

        Args:
            obj: Object to traverse
            path: Current path
            depth: Current dictionary nesting depth
        """
        if isinstance(obj, dict):
            for key, value in obj.items():
                current_path = f"{path}.{key}" if path else key
                # Increment depth when entering nested dict
                next_depth = depth + 1 if isinstance(value, dict) else depth
                self._traverse(value, current_path, next_depth)

        elif isinstance(obj, list) and obj:
            # Found an array - these always become tables regardless of depth
            array_info = self._analyze_array(obj, path, depth)
            self.arrays_found.append(array_info)

            # Continue traversing into array elements
            # Don't increment depth for arrays, only for nested dicts
            for i, item in enumerate(obj):
                item_path = f"{path}[{i}]"
                self._traverse(item, item_path, depth)

    def _analyze_array(self, array: list[Any], path: str, depth: int = 0) -> dict[str, Any]:
        """
        Analyze an array to detect its structure and patterns.

        Args:
            array: Array to analyze
            path: Path to this array
            depth: Current dictionary nesting depth

        Returns:
            Analysis of the array
        """
        if not array:
            return {"path": path, "length": 0, "type": "empty", "element_types": [], "depth": depth}

        # Determine element types
        element_types = [type(item).__name__ for item in array]
        unique_types = list(set(element_types))

        # For arrays of objects, detect common keys
        if all(isinstance(item, dict) for item in array):
            all_keys = [set(item.keys()) for item in array]
            common_keys = set.intersection(*all_keys) if all_keys else set()
            all_keys_union = set.union(*all_keys) if all_keys else set()
            optional_keys = all_keys_union - common_keys

            # Detect structure pattern
            structure_signature = tuple(sorted(common_keys))
            self.structure_patterns[structure_signature].append(path)

            return {
                "path": path,
                "length": len(array),
                "type": "object_array",
                "element_types": unique_types,
                "common_keys": sorted(common_keys),
                "optional_keys": sorted(optional_keys),
                "all_keys": sorted(all_keys_union),
                "structure_signature": structure_signature,
                "is_homogeneous": len(all_keys) == 1,
            }
        else:
            return {
                "path": path,
                "length": len(array),
                "type": "primitive_array" if len(unique_types) == 1 else "mixed_array",
                "element_types": unique_types,
            }

    def get_table_candidates(self) -> list[dict[str, Any]]:
        """
        Get arrays that are good candidates for conversion to tables.

        Returns:
            List of array information suitable for table generation
        """
        candidates = []

        for array_info in self.arrays_found:
            if array_info.get("type") == "object_array":
                # Object arrays are good table candidates
                candidates.append(
                    {
                        "path": array_info["path"],
                        "table_name": self._path_to_table_name(array_info["path"]),
                        "row_count": array_info["length"],
                        "columns": array_info["all_keys"],
                        "required_columns": array_info["common_keys"],
                        "optional_columns": array_info["optional_keys"],
                    }
                )

        return candidates

    def _path_to_table_name(self, path: str) -> str:
        """
        Convert a path to a suggested table name.

        Args:
            path: Path like "actions" or "communities"

        Returns:
            Suggested table name
        """
        # Remove array indices and clean up
        parts = path.replace("[", ".").replace("]", "").split(".")
        parts = [p for p in parts if p and not p.isdigit()]

        # Use the last meaningful part or join all
        if parts:
            return "_".join(parts).upper()
        return "UNKNOWN_TABLE"

    def print_summary(self, analysis: dict[str, Any]) -> None:
        """
        Print a human-readable summary of the analysis.

        Args:
            analysis: Analysis results from analyze()
        """
        print(f"\n{'=' * 60}")
        print("STRUCTURE ANALYSIS SUMMARY")
        print(f"{'=' * 60}")

        print(f"\nTotal arrays found: {analysis['total_arrays']}")

        print(f"\n{'-' * 60}")
        print("ARRAYS DETECTED:")
        print(f"{'-' * 60}")

        for i, array_info in enumerate(analysis["arrays"], 1):
            print(f"\n{i}. Path: {array_info['path']}")
            print(f"   Type: {array_info['type']}")
            print(f"   Length: {array_info['length']}")

            if array_info["type"] == "object_array":
                print(f"   Homogeneous: {array_info['is_homogeneous']}")
                print(f"   Common keys ({len(array_info['common_keys'])}): {', '.join(array_info['common_keys'][:5])}")
                if len(array_info["common_keys"]) > 5:
                    print(f"      ... and {len(array_info['common_keys']) - 5} more")
                if array_info["optional_keys"]:
                    print(
                        f"   Optional keys ({len(array_info['optional_keys'])}): {', '.join(list(array_info['optional_keys'])[:3])}"
                    )

        print(f"\n{'-' * 60}")
        print("TABLE CANDIDATES:")
        print(f"{'-' * 60}")

        candidates = self.get_table_candidates()
        for i, candidate in enumerate(candidates, 1):
            print(f"\n{i}. Table: {candidate['table_name']}")
            print(f"   Source: {candidate['path']}")
            print(f"   Rows: {candidate['row_count']}")
            print(f"   Columns: {len(candidate['columns'])}")
            print(f"   Required: {len(candidate['required_columns'])}")

        print(f"\n{'=' * 60}\n")
