"""Tests for Data Comparer functionality in YAML Shredder."""

import pandas as pd
import pytest

from yaml_shredder.data_comparer import DataComparer, PrimaryKeyDetector, TableMatcher


class TestPrimaryKeyDetector:
    """Tests for PrimaryKeyDetector class."""

    def test_detect_id_column(self):
        """Test detection of 'id' column as primary key."""
        detector = PrimaryKeyDetector()
        df = pd.DataFrame({"id": [1, 2, 3], "name": ["a", "b", "c"], "value": [10, 20, 30]})
        pk = detector.detect_primary_key(df, "test_table")
        assert pk == ["id"]

    def test_detect_code_column(self):
        """Test detection of 'code' column as primary key."""
        detector = PrimaryKeyDetector()
        df = pd.DataFrame(
            {"code": ["A001", "A002", "A003"], "description": ["First", "Second", "Third"], "value": [10, 20, 30]}
        )
        pk = detector.detect_primary_key(df, "test_table")
        assert pk == ["code"]

    def test_detect_action_code_column(self):
        """Test detection of column ending with _code as primary key."""
        detector = PrimaryKeyDetector()
        df = pd.DataFrame(
            {
                "action_code": ["ACT001", "ACT002", "ACT003"],
                "action_type": ["sensor", "report", "alert"],
                "value": [10, 20, 30],
            }
        )
        pk = detector.detect_primary_key(df, "test_table")
        assert pk == ["action_code"]

    def test_detect_name_when_unique(self):
        """Test detection of 'name' column when it's unique."""
        detector = PrimaryKeyDetector()
        df = pd.DataFrame(
            {"name": ["server1", "server2", "server3"], "ip": ["1.1.1.1", "2.2.2.2", "3.3.3.3"], "port": [80, 80, 80]}
        )
        pk = detector.detect_primary_key(df, "test_table")
        assert pk == ["name"]

    def test_no_pk_for_non_unique_columns(self):
        """Test that non-unique columns are not selected as pk."""
        detector = PrimaryKeyDetector()
        df = pd.DataFrame(
            {
                "name": ["a", "a", "b"],  # Not unique
                "type": ["x", "y", "x"],  # Not unique
                "value": [1, 2, 3],
            }
        )
        pk = detector.detect_primary_key(df, "test_table")
        # Should return empty or composite key
        assert pk == [] or len(pk) > 1

    def test_empty_dataframe(self):
        """Test handling of empty DataFrame."""
        detector = PrimaryKeyDetector()
        df = pd.DataFrame()
        pk = detector.detect_primary_key(df, "test_table")
        assert pk == []

    def test_priority_id_over_name(self):
        """Test that 'id' is preferred over 'name' when both are unique."""
        detector = PrimaryKeyDetector()
        df = pd.DataFrame({"id": [1, 2, 3], "name": ["a", "b", "c"], "value": [10, 20, 30]})
        pk = detector.detect_primary_key(df, "test_table")
        assert pk == ["id"]


class TestTableMatcher:
    """Tests for TableMatcher class."""

    def test_exact_match(self):
        """Test exact name matching."""
        matcher = TableMatcher()
        tables1 = {"USERS": pd.DataFrame(), "ORDERS": pd.DataFrame()}
        tables2 = {"USERS": pd.DataFrame(), "PRODUCTS": pd.DataFrame()}

        result = matcher.match_tables(tables1, tables2)

        assert len(result["matches"]) == 1
        assert result["matches"][0]["table1_name"] == "USERS"
        assert result["matches"][0]["table2_name"] == "USERS"
        assert result["matches"][0]["match_type"] == "exact"
        assert "ORDERS" in result["only_in_first"]
        assert "PRODUCTS" in result["only_in_second"]

    def test_plural_singular_match(self):
        """Test matching singular and plural table names."""
        matcher = TableMatcher()
        tables1 = {"REPORT": pd.DataFrame(), "ACTION": pd.DataFrame()}
        tables2 = {"REPORTS": pd.DataFrame(), "ACTIONS": pd.DataFrame()}

        result = matcher.match_tables(tables1, tables2)

        assert len(result["matches"]) == 2
        table1_names = {m["table1_name"] for m in result["matches"]}
        assert "REPORT" in table1_names
        assert "ACTION" in table1_names

    def test_ies_plural_match(self):
        """Test matching -y/-ies plural forms."""
        matcher = TableMatcher()
        tables1 = {"COMMUNITY": pd.DataFrame()}
        tables2 = {"COMMUNITIES": pd.DataFrame()}

        result = matcher.match_tables(tables1, tables2)

        assert len(result["matches"]) == 1
        assert result["matches"][0]["table1_name"] == "COMMUNITY"
        assert result["matches"][0]["table2_name"] == "COMMUNITIES"

    def test_no_match_for_dissimilar_names(self):
        """Test that dissimilar names don't match."""
        matcher = TableMatcher(similarity_threshold=0.8)
        tables1 = {"USERS": pd.DataFrame()}
        tables2 = {"PRODUCTS": pd.DataFrame()}

        result = matcher.match_tables(tables1, tables2)

        assert len(result["matches"]) == 0
        assert "USERS" in result["only_in_first"]
        assert "PRODUCTS" in result["only_in_second"]


class TestDataComparer:
    """Tests for DataComparer class."""

    def test_compare_identical_tables(self):
        """Test comparison of identical tables."""
        comparer = DataComparer()
        df1 = pd.DataFrame({"id": [1, 2, 3], "name": ["a", "b", "c"], "value": [10, 20, 30]})
        df2 = df1.copy()

        result = comparer.compare_tables(df1, df2, table_name="test")

        assert result["rows_only_in_first"] == 0
        assert result["rows_only_in_second"] == 0
        assert result["rows_modified"] == 0
        assert result["rows_unchanged"] == 3

    def test_compare_with_added_rows(self):
        """Test comparison when second table has additional rows."""
        comparer = DataComparer()
        df1 = pd.DataFrame({"id": [1, 2], "name": ["a", "b"]})
        df2 = pd.DataFrame({"id": [1, 2, 3], "name": ["a", "b", "c"]})

        result = comparer.compare_tables(df1, df2, table_name="test")

        assert result["rows_only_in_first"] == 0
        assert result["rows_only_in_second"] == 1
        assert result["rows_modified"] == 0
        assert result["rows_unchanged"] == 2

    def test_compare_with_removed_rows(self):
        """Test comparison when second table has fewer rows."""
        comparer = DataComparer()
        df1 = pd.DataFrame({"id": [1, 2, 3], "name": ["a", "b", "c"]})
        df2 = pd.DataFrame({"id": [1, 2], "name": ["a", "b"]})

        result = comparer.compare_tables(df1, df2, table_name="test")

        assert result["rows_only_in_first"] == 1
        assert result["rows_only_in_second"] == 0
        assert result["rows_modified"] == 0
        assert result["rows_unchanged"] == 2

    def test_compare_with_modified_rows(self):
        """Test comparison when rows have been modified."""
        comparer = DataComparer()
        df1 = pd.DataFrame({"id": [1, 2, 3], "name": ["a", "b", "c"], "value": [10, 20, 30]})
        df2 = pd.DataFrame(
            {
                "id": [1, 2, 3],
                "name": ["a", "b", "c"],
                "value": [10, 25, 35],  # Modified values for id=2 and id=3
            }
        )

        result = comparer.compare_tables(df1, df2, table_name="test")

        assert result["rows_only_in_first"] == 0
        assert result["rows_only_in_second"] == 0
        assert result["rows_modified"] == 2
        assert result["rows_unchanged"] == 1

        # Check field differences
        assert len(result["field_differences"]) == 2
        for diff in result["field_differences"]:
            assert diff["field"] == "value"

    def test_compare_with_explicit_primary_key(self):
        """Test comparison with explicitly specified primary key."""
        comparer = DataComparer()
        df1 = pd.DataFrame({"code": ["A", "B", "C"], "value": [1, 2, 3]})
        df2 = pd.DataFrame(
            {
                "code": ["A", "B", "C"],
                "value": [1, 5, 3],  # Changed value for code=B
            }
        )

        result = comparer.compare_tables(df1, df2, primary_key=["code"], table_name="test")

        assert result["rows_modified"] == 1
        assert result["rows_unchanged"] == 2
        assert result["primary_key"] == ["code"]

    def test_compare_with_different_columns(self):
        """Test comparison when tables have different column sets."""
        comparer = DataComparer()
        df1 = pd.DataFrame({"id": [1, 2], "name": ["a", "b"], "old_col": ["x", "y"]})
        df2 = pd.DataFrame({"id": [1, 2], "name": ["a", "b"], "new_col": ["p", "q"]})

        result = comparer.compare_tables(df1, df2, table_name="test")

        assert "old_col" in result["columns_only_in_first"]
        assert "new_col" in result["columns_only_in_second"]

    def test_compare_datasets(self):
        """Test comparing complete datasets with multiple tables."""
        comparer = DataComparer()

        tables1 = {
            "USERS": pd.DataFrame({"id": [1, 2], "name": ["alice", "bob"]}),
            "ORDERS": pd.DataFrame({"id": [1, 2], "user_id": [1, 2], "total": [100, 200]}),
        }

        tables2 = {
            "USERS": pd.DataFrame({"id": [1, 2, 3], "name": ["alice", "bob", "charlie"]}),
            "ORDERS": pd.DataFrame({"id": [1, 2], "user_id": [1, 2], "total": [100, 250]}),
        }

        result = comparer.compare_datasets(tables1, tables2)

        assert result["summary"]["tables_matched"] == 2
        assert result["summary"]["tables_with_differences"] == 2

        # Check USERS table comparison
        users_comp = next(c for c in result["table_comparisons"] if c["table_name"] == "USERS")
        assert users_comp["rows_only_in_second"] == 1

        # Check ORDERS table comparison
        orders_comp = next(c for c in result["table_comparisons"] if c["table_name"] == "ORDERS")
        assert orders_comp["rows_modified"] == 1

    def test_compare_without_primary_key(self):
        """Test comparison when no primary key can be detected."""
        comparer = DataComparer()
        df1 = pd.DataFrame(
            {
                "type": ["a", "a", "b"],  # Non-unique
                "status": ["active", "inactive", "active"],  # Non-unique
            }
        )
        df2 = pd.DataFrame({"type": ["a", "b", "b"], "status": ["active", "active", "inactive"]})

        result = comparer.compare_tables(df1, df2, table_name="test")

        assert result["primary_key_detected"] is False
        # Should still provide comparison using row-based matching
        assert "rows_only_in_first" in result
        assert "rows_only_in_second" in result

    def test_generate_comparison_report(self):
        """Test report generation."""
        comparer = DataComparer()

        tables1 = {
            "USERS": pd.DataFrame({"id": [1, 2], "name": ["alice", "bob"]}),
        }
        tables2 = {
            "USERS": pd.DataFrame({"id": [1, 2], "name": ["alice", "robert"]}),
        }

        comparison = comparer.compare_datasets(tables1, tables2)
        report = comparer.generate_comparison_report(comparison)

        assert "# Data Comparison Report" in report
        assert "USERS" in report
        assert "Primary Key" in report
        assert "Row Statistics" in report


@pytest.fixture
def sample_yaml_files_for_data_comparison(tmp_path):
    """Create sample YAML files for data comparison testing."""
    yaml1 = tmp_path / "data1.yaml"
    yaml2 = tmp_path / "data2.yaml"

    yaml1.write_text("""
version: "1.0"
users:
  - id: 1
    name: alice
    email: alice@example.com
  - id: 2
    name: bob
    email: bob@example.com
products:
  - code: P001
    name: Widget
    price: 9.99
  - code: P002
    name: Gadget
    price: 19.99
""")

    yaml2.write_text("""
version: "1.1"
users:
  - id: 1
    name: alice
    email: alice@newdomain.com
  - id: 2
    name: bob
    email: bob@example.com
  - id: 3
    name: charlie
    email: charlie@example.com
products:
  - code: P001
    name: Widget Pro
    price: 12.99
  - code: P003
    name: Doohickey
    price: 29.99
""")

    return yaml1, yaml2


class TestYAMLComparatorDataIntegration:
    """Integration tests for YAML Comparator with data comparison."""

    def test_compare_data_method(self, sample_yaml_files_for_data_comparison, tmp_path):
        """Test the compare_data method on the YAMLComparator."""
        from schema_sentinel.yaml_comparator import YAMLComparator

        yaml1, yaml2 = sample_yaml_files_for_data_comparison
        comparator = YAMLComparator(output_dir=tmp_path / "dbs")

        result = comparator.compare_data(yaml1, yaml2)

        assert "summary" in result
        assert "table_comparisons" in result
        assert result["metadata"]["file1_name"] == "data1.yaml"
        assert result["metadata"]["file2_name"] == "data2.yaml"

    def test_compare_data_with_report(self, sample_yaml_files_for_data_comparison, tmp_path):
        """Test compare_data with report generation."""
        from schema_sentinel.yaml_comparator import YAMLComparator

        yaml1, yaml2 = sample_yaml_files_for_data_comparison
        comparator = YAMLComparator(output_dir=tmp_path / "dbs")
        report_path = tmp_path / "comparison_report.md"

        comparator.compare_data(yaml1, yaml2, output_report=report_path)

        assert report_path.exists()
        content = report_path.read_text()
        assert "# Data Comparison Report" in content

    def test_compare_yaml_files_full(self, sample_yaml_files_for_data_comparison, tmp_path):
        """Test the combined schema and data comparison."""
        from schema_sentinel.yaml_comparator import YAMLComparator

        yaml1, yaml2 = sample_yaml_files_for_data_comparison
        comparator = YAMLComparator(output_dir=tmp_path / "dbs")
        report_path = tmp_path / "full_report.md"

        schema_report, data_comparison = comparator.compare_yaml_files_full(yaml1, yaml2, output_report=report_path)

        assert "# YAML Comparison Report" in schema_report
        assert "summary" in data_comparison
        assert report_path.exists()
