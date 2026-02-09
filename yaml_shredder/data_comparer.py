"""Data comparison module for YAML Shredder.

Compares data between two YAML files using primary key detection and table matching.
"""

import logging
import re
from difflib import SequenceMatcher
from typing import Any

import pandas as pd

log = logging.getLogger(__name__)


class PrimaryKeyDetector:
    """Detect primary keys in table data."""

    # Common primary key column name patterns
    PK_PATTERNS = [
        r"^id$",
        r"^_id$",
        r"^key$",
        r"_id$",
        r"^code$",
        r"_code$",
        r"^name$",
        r"^uuid$",
        r"^guid$",
    ]

    # Priority order for identifying columns (higher = more likely to be PK)
    PK_PRIORITY = {
        "id": 100,
        "_id": 95,
        "key": 90,
        "uuid": 85,
        "guid": 85,
        "code": 80,
        "name": 70,
    }

    def __init__(self):
        """Initialize the primary key detector."""
        self.compiled_patterns = [re.compile(p, re.IGNORECASE) for p in self.PK_PATTERNS]

    def detect_primary_key(self, df: pd.DataFrame, table_name: str = "") -> list[str]:
        """Detect the primary key column(s) for a DataFrame.

        Args:
            df: DataFrame to analyze
            table_name: Name of the table (for logging)

        Returns:
            List of column names that form the primary key (empty if none detected)
        """
        if df.empty:
            return []

        candidates = self._find_pk_candidates(df)

        if not candidates:
            # Try to find a composite key from common identifying columns
            return self._find_composite_key(df)

        # Sort by priority and uniqueness
        scored_candidates = []
        for col in candidates:
            score = self._score_pk_candidate(df, col)
            scored_candidates.append((col, score))

        scored_candidates.sort(key=lambda x: x[1], reverse=True)

        # Return the best candidate if it's unique
        best_col, best_score = scored_candidates[0]
        if best_score > 0:
            log.debug(f"Detected primary key for {table_name}: {best_col} (score: {best_score})")
            return [best_col]

        # If no unique column, try composite key
        return self._find_composite_key(df)

    def _find_pk_candidates(self, df: pd.DataFrame) -> list[str]:
        """Find columns that match primary key naming patterns.

        Args:
            df: DataFrame to analyze

        Returns:
            List of candidate column names
        """
        candidates = []
        for col in df.columns:
            for pattern in self.compiled_patterns:
                if pattern.search(col):
                    candidates.append(col)
                    break
        return candidates

    def _score_pk_candidate(self, df: pd.DataFrame, col: str) -> int:
        """Score a primary key candidate based on uniqueness and naming.

        Args:
            df: DataFrame containing the column
            col: Column name to score

        Returns:
            Score (higher is better, 0 or negative means not suitable)
        """
        if col not in df.columns:
            return -1

        # Check uniqueness
        non_null_values = df[col].dropna()
        if len(non_null_values) == 0:
            return -1

        unique_ratio = len(non_null_values.unique()) / len(non_null_values)

        # Must be unique (or nearly unique for large datasets)
        if unique_ratio < 0.99:
            return 0

        # Base score from naming convention
        col_lower = col.lower()
        base_score = self.PK_PRIORITY.get(col_lower, 50)

        # Bonus for ending with common patterns
        if col_lower.endswith("_id"):
            base_score += 20
        elif col_lower.endswith("_code"):
            base_score += 15

        return int(base_score * unique_ratio)

    def _find_composite_key(self, df: pd.DataFrame) -> list[str]:
        """Find a composite primary key from common identifying columns.

        Args:
            df: DataFrame to analyze

        Returns:
            List of columns forming composite key (empty if none found)
        """
        if df.empty or len(df) <= 1:
            return []

        # Common identifying column combinations
        id_cols = [c for c in df.columns if c.lower() in ("id", "code", "name", "type", "action_code", "action_type")]

        if not id_cols:
            return []

        # Try combinations starting with most promising
        for i in range(len(id_cols)):
            for j in range(i + 1, len(id_cols) + 1):
                combo = id_cols[i:j]
                if len(combo) > 0:
                    # Check if this combination is unique
                    try:
                        grouped = df.groupby(combo).size()
                        if len(grouped) == len(df):
                            log.debug(f"Detected composite primary key: {combo}")
                            return combo
                    except (KeyError, ValueError):
                        continue

        return []


class TableMatcher:
    """Match tables between two datasets based on name similarity."""

    def __init__(self, similarity_threshold: float = 0.8):
        """Initialize the table matcher.

        Args:
            similarity_threshold: Minimum similarity ratio for matching (0-1)
        """
        self.similarity_threshold = similarity_threshold

    def match_tables(self, tables1: dict[str, pd.DataFrame], tables2: dict[str, pd.DataFrame]) -> list[dict[str, Any]]:
        """Match tables between two datasets.

        Args:
            tables1: First set of tables (name -> DataFrame)
            tables2: Second set of tables (name -> DataFrame)

        Returns:
            List of match dictionaries with keys:
                - table1_name: Name in first dataset
                - table2_name: Name in second dataset
                - match_type: 'exact', 'normalized', or 'similar'
                - similarity: Similarity score (1.0 for exact)
        """
        matches = []
        matched_t2 = set()

        names1 = set(tables1.keys())
        names2 = set(tables2.keys())

        # First pass: exact matches
        exact_matches = names1 & names2
        for name in exact_matches:
            matches.append(
                {
                    "table1_name": name,
                    "table2_name": name,
                    "match_type": "exact",
                    "similarity": 1.0,
                }
            )
            matched_t2.add(name)

        # Second pass: normalized name matches (singular/plural)
        remaining1 = names1 - exact_matches
        remaining2 = names2 - matched_t2

        for name1 in remaining1:
            norm1 = self._normalize_name(name1)
            best_match = None
            best_similarity = 0

            for name2 in remaining2:
                if name2 in matched_t2:
                    continue

                norm2 = self._normalize_name(name2)

                if norm1 == norm2:
                    best_match = name2
                    best_similarity = 0.95
                    break

                # Calculate similarity
                similarity = self._calculate_similarity(norm1, norm2)
                if similarity > best_similarity and similarity >= self.similarity_threshold:
                    best_match = name2
                    best_similarity = similarity

            if best_match:
                match_type = "normalized" if best_similarity >= 0.95 else "similar"
                matches.append(
                    {
                        "table1_name": name1,
                        "table2_name": best_match,
                        "match_type": match_type,
                        "similarity": best_similarity,
                    }
                )
                matched_t2.add(best_match)

        # Identify unmatched tables
        unmatched1 = names1 - {m["table1_name"] for m in matches}
        unmatched2 = names2 - matched_t2

        return {
            "matches": matches,
            "only_in_first": sorted(unmatched1),
            "only_in_second": sorted(unmatched2),
        }

    def _normalize_name(self, name: str) -> str:
        """Normalize a table name for comparison.

        Args:
            name: Table name to normalize

        Returns:
            Normalized name (lowercase, singular form)
        """
        name = name.lower().strip()

        # Remove common suffixes for pluralization
        if name.endswith("ies"):
            name = name[:-3] + "y"
        elif name.endswith("es") and not name.endswith("sse"):
            name = name[:-2]
        elif name.endswith("s") and not name.endswith("ss"):
            name = name[:-1]

        return name

    def _calculate_similarity(self, name1: str, name2: str) -> float:
        """Calculate similarity between two normalized names.

        Args:
            name1: First name
            name2: Second name

        Returns:
            Similarity ratio (0-1)
        """
        return SequenceMatcher(None, name1, name2).ratio()


class DataComparer:
    """Compare data between matched tables using primary keys."""

    def __init__(self):
        """Initialize the data comparer."""
        self.pk_detector = PrimaryKeyDetector()
        self.table_matcher = TableMatcher()

    def compare_tables(
        self,
        df1: pd.DataFrame,
        df2: pd.DataFrame,
        primary_key: list[str] | None = None,
        table_name: str = "",
    ) -> dict[str, Any]:
        """Compare data between two tables.

        Args:
            df1: First DataFrame
            df2: Second DataFrame
            primary_key: Primary key columns (auto-detected if None)
            table_name: Name of the table (for reporting)

        Returns:
            Comparison results dictionary
        """
        # Detect primary key if not provided
        if primary_key is None:
            primary_key = self.pk_detector.detect_primary_key(df1, table_name)
            if not primary_key:
                primary_key = self.pk_detector.detect_primary_key(df2, table_name)

        if not primary_key:
            log.warning(f"No primary key detected for {table_name}, using row-based comparison")
            return self._compare_without_pk(df1, df2, table_name)

        return self._compare_with_pk(df1, df2, primary_key, table_name)

    def _compare_with_pk(
        self,
        df1: pd.DataFrame,
        df2: pd.DataFrame,
        primary_key: list[str],
        table_name: str,
    ) -> dict[str, Any]:
        """Compare tables using primary key.

        Args:
            df1: First DataFrame
            df2: Second DataFrame
            primary_key: Primary key columns
            table_name: Table name for reporting

        Returns:
            Comparison results
        """
        # Ensure primary key columns exist in both DataFrames
        for col in primary_key:
            if col not in df1.columns:
                log.warning(f"Primary key column '{col}' not found in first DataFrame")
                return self._compare_without_pk(df1, df2, table_name)
            if col not in df2.columns:
                log.warning(f"Primary key column '{col}' not found in second DataFrame")
                return self._compare_without_pk(df1, df2, table_name)

        # Find common columns for comparison
        common_columns = list(set(df1.columns) & set(df2.columns))

        # Get keys from both DataFrames
        df1_keys = set(df1[primary_key].apply(tuple, axis=1))
        df2_keys = set(df2[primary_key].apply(tuple, axis=1))

        # Identify added, removed, and common keys
        only_in_first = df1_keys - df2_keys
        only_in_second = df2_keys - df1_keys
        common_keys = df1_keys & df2_keys

        # Get rows only in first
        rows_only_in_first = df1[df1[primary_key].apply(tuple, axis=1).isin(only_in_first)]

        # Get rows only in second
        rows_only_in_second = df2[df2[primary_key].apply(tuple, axis=1).isin(only_in_second)]

        # Compare common rows
        modified_rows = []
        field_differences = []

        for key_tuple in common_keys:
            # Create filter condition
            filter1 = pd.Series([True] * len(df1))
            filter2 = pd.Series([True] * len(df2))

            for i, col in enumerate(primary_key):
                filter1 = filter1 & (df1[col] == key_tuple[i])
                filter2 = filter2 & (df2[col] == key_tuple[i])

            row1 = df1[filter1].iloc[0] if filter1.any() else None
            row2 = df2[filter2].iloc[0] if filter2.any() else None

            if row1 is not None and row2 is not None:
                # Compare values in common columns
                differences = {}
                for col in common_columns:
                    if col in primary_key:
                        continue
                    val1 = row1[col]
                    val2 = row2[col]

                    # Handle NaN comparison
                    if pd.isna(val1) and pd.isna(val2):
                        continue
                    if val1 != val2:
                        differences[col] = {"old": val1, "new": val2}

                if differences:
                    modified_rows.append(
                        {
                            "primary_key": dict(zip(primary_key, key_tuple, strict=True)),
                            "differences": differences,
                        }
                    )
                    for col, diff in differences.items():
                        field_differences.append(
                            {
                                "primary_key": dict(zip(primary_key, key_tuple, strict=True)),
                                "field": col,
                                "old_value": diff["old"],
                                "new_value": diff["new"],
                            }
                        )

        return {
            "table_name": table_name,
            "primary_key": primary_key,
            "primary_key_detected": True,
            "rows_in_first": len(df1),
            "rows_in_second": len(df2),
            "common_columns": common_columns,
            "columns_only_in_first": list(set(df1.columns) - set(df2.columns)),
            "columns_only_in_second": list(set(df2.columns) - set(df1.columns)),
            "rows_only_in_first": len(only_in_first),
            "rows_only_in_second": len(only_in_second),
            "rows_modified": len(modified_rows),
            "rows_unchanged": len(common_keys) - len(modified_rows),
            "rows_only_in_first_data": rows_only_in_first.to_dict("records"),
            "rows_only_in_second_data": rows_only_in_second.to_dict("records"),
            "modified_rows": modified_rows,
            "field_differences": field_differences,
        }

    def _compare_without_pk(
        self,
        df1: pd.DataFrame,
        df2: pd.DataFrame,
        table_name: str,
    ) -> dict[str, Any]:
        """Compare tables without a primary key (set-based comparison).

        Args:
            df1: First DataFrame
            df2: Second DataFrame
            table_name: Table name for reporting

        Returns:
            Comparison results
        """
        # Find common columns
        common_columns = list(set(df1.columns) & set(df2.columns))

        if not common_columns:
            return {
                "table_name": table_name,
                "primary_key": [],
                "primary_key_detected": False,
                "error": "No common columns between tables",
                "columns_only_in_first": list(df1.columns),
                "columns_only_in_second": list(df2.columns),
            }

        # Use only common columns for comparison
        df1_common = df1[common_columns].copy()
        df2_common = df2[common_columns].copy()

        # Convert to hashable tuples for set operations
        df1_common = df1_common.fillna("__NULL__")
        df2_common = df2_common.fillna("__NULL__")

        rows1 = set(df1_common.apply(tuple, axis=1))
        rows2 = set(df2_common.apply(tuple, axis=1))

        only_in_first = rows1 - rows2
        only_in_second = rows2 - rows1
        common_rows = rows1 & rows2

        return {
            "table_name": table_name,
            "primary_key": [],
            "primary_key_detected": False,
            "rows_in_first": len(df1),
            "rows_in_second": len(df2),
            "common_columns": common_columns,
            "columns_only_in_first": list(set(df1.columns) - set(df2.columns)),
            "columns_only_in_second": list(set(df2.columns) - set(df1.columns)),
            "rows_only_in_first": len(only_in_first),
            "rows_only_in_second": len(only_in_second),
            "rows_unchanged": len(common_rows),
            "rows_modified": 0,
            "note": "Comparison done without primary key - set-based matching used",
        }

    def compare_datasets(
        self,
        tables1: dict[str, pd.DataFrame],
        tables2: dict[str, pd.DataFrame],
        primary_keys: dict[str, list[str]] | None = None,
    ) -> dict[str, Any]:
        """Compare two complete datasets (multiple tables).

        Args:
            tables1: First dataset (table_name -> DataFrame)
            tables2: Second dataset (table_name -> DataFrame)
            primary_keys: Optional dict of table_name -> primary_key columns

        Returns:
            Complete comparison results
        """
        primary_keys = primary_keys or {}

        # Match tables between datasets
        match_result = self.table_matcher.match_tables(tables1, tables2)

        # Compare matched tables
        table_comparisons = []
        for match in match_result["matches"]:
            t1_name = match["table1_name"]
            t2_name = match["table2_name"]

            df1 = tables1[t1_name]
            df2 = tables2[t2_name]

            # Use provided primary key or auto-detect
            pk = primary_keys.get(t1_name) or primary_keys.get(t2_name)

            comparison = self.compare_tables(df1, df2, pk, t1_name)
            comparison["match_info"] = match

            table_comparisons.append(comparison)

        return {
            "summary": {
                "tables_matched": len(match_result["matches"]),
                "tables_only_in_first": len(match_result["only_in_first"]),
                "tables_only_in_second": len(match_result["only_in_second"]),
                "tables_with_differences": sum(
                    1
                    for c in table_comparisons
                    if c.get("rows_only_in_first", 0) > 0
                    or c.get("rows_only_in_second", 0) > 0
                    or c.get("rows_modified", 0) > 0
                ),
            },
            "table_matching": match_result,
            "table_comparisons": table_comparisons,
        }

    def generate_comparison_report(self, comparison: dict[str, Any]) -> str:
        """Generate a markdown report from comparison results.

        Args:
            comparison: Results from compare_datasets

        Returns:
            Markdown formatted report
        """
        lines = []
        lines.append("# Data Comparison Report")
        lines.append("")

        # Summary
        lines.append("## Summary")
        lines.append("")
        summary = comparison["summary"]
        lines.append(f"- **Tables matched:** {summary['tables_matched']}")
        lines.append(f"- **Tables only in first file:** {summary['tables_only_in_first']}")
        lines.append(f"- **Tables only in second file:** {summary['tables_only_in_second']}")
        lines.append(f"- **Tables with differences:** {summary['tables_with_differences']}")
        lines.append("")

        # Unmatched tables
        match_info = comparison["table_matching"]
        if match_info["only_in_first"]:
            lines.append("## Tables Only in First File")
            lines.append("")
            for table in match_info["only_in_first"]:
                lines.append(f"- `{table}`")
            lines.append("")

        if match_info["only_in_second"]:
            lines.append("## Tables Only in Second File")
            lines.append("")
            for table in match_info["only_in_second"]:
                lines.append(f"- `{table}`")
            lines.append("")

        # Table comparisons
        lines.append("## Table Comparisons")
        lines.append("")

        for comp in comparison["table_comparisons"]:
            table_name = comp["table_name"]
            match = comp.get("match_info", {})

            lines.append(f"### Table: `{table_name}`")
            lines.append("")

            if match.get("match_type") == "similar" or match.get("match_type") == "normalized":
                lines.append(
                    f"*Matched with: `{match.get('table2_name')}` (similarity: {match.get('similarity', 0):.2f})*"
                )
                lines.append("")

            # Primary key info
            if comp.get("primary_key"):
                lines.append(f"**Primary Key:** `{', '.join(comp['primary_key'])}`")
            elif not comp.get("primary_key_detected"):
                lines.append("**Primary Key:** *Not detected (using row-based comparison)*")
            lines.append("")

            # Row counts
            lines.append("**Row Statistics:**")
            lines.append("")
            lines.append("| Metric | Count |")
            lines.append("|--------|-------|")
            lines.append(f"| Rows in first file | {comp.get('rows_in_first', 0)} |")
            lines.append(f"| Rows in second file | {comp.get('rows_in_second', 0)} |")
            lines.append(f"| Rows only in first | {comp.get('rows_only_in_first', 0)} |")
            lines.append(f"| Rows only in second | {comp.get('rows_only_in_second', 0)} |")
            lines.append(f"| Rows modified | {comp.get('rows_modified', 0)} |")
            lines.append(f"| Rows unchanged | {comp.get('rows_unchanged', 0)} |")
            lines.append("")

            # Column differences
            if comp.get("columns_only_in_first"):
                lines.append("**Columns only in first file:**")
                for col in comp["columns_only_in_first"]:
                    lines.append(f"- `{col}`")
                lines.append("")

            if comp.get("columns_only_in_second"):
                lines.append("**Columns only in second file:**")
                for col in comp["columns_only_in_second"]:
                    lines.append(f"- `{col}`")
                lines.append("")

            # Field differences (limit to first 10)
            if comp.get("field_differences"):
                lines.append("**Field-level differences:**")
                lines.append("")
                lines.append("| Primary Key | Field | Old Value | New Value |")
                lines.append("|-------------|-------|-----------|-----------|")

                for diff in comp["field_differences"][:20]:
                    pk_str = ", ".join(f"{k}={v}" for k, v in diff["primary_key"].items())
                    old_val = str(diff["old_value"])[:30]
                    new_val = str(diff["new_value"])[:30]
                    lines.append(f"| {pk_str} | `{diff['field']}` | {old_val} | {new_val} |")

                if len(comp["field_differences"]) > 20:
                    lines.append(f"| ... | ({len(comp['field_differences']) - 20} more differences) | ... | ... |")

                lines.append("")

            lines.append("---")
            lines.append("")

        return "\n".join(lines)
