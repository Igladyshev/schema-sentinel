"""Example: Compare two YAML files using YAMLComparator.

This example demonstrates how to compare two YAML configuration files
by loading them into SQLite databases and comparing their structure and data.

Note: This example uses master-mpm YAML files which are excluded from version control.
"""

from pathlib import Path

from schema_sentinel.yaml_comparator import YAMLComparator


def main():
    """Compare two YAML files from the master-mpm directory."""
    # Setup paths
    resources_dir = Path(__file__).parent.parent
    master_mpm_dir = resources_dir / "master-mpm"

    # Check if master-mpm directory exists
    if not master_mpm_dir.exists():
        print(f"Error: {master_mpm_dir} directory not found")
        print("This example requires YAML files in resources/master-mpm/")
        return

    # Select two YAML files to compare
    yaml1 = master_mpm_dir / "XY_123-mpm.yaml"
    yaml2 = master_mpm_dir / "CD_789-mpm.yaml"

    if not yaml1.exists() or not yaml2.exists():
        print("Error: Required YAML files not found")
        print(f"  Expected: {yaml1}")
        print(f"  Expected: {yaml2}")
        return

    print("=" * 70)
    print("YAML File Comparison Example")
    print("=" * 70)
    print()
    print("Comparing:")
    print(f"  File 1: {yaml1.name}")
    print(f"  File 2: {yaml2.name}")
    print()

    # Create comparator
    comparator = YAMLComparator(output_dir=Path("./temp_dbs"))

    # Compare YAML files
    report = comparator.compare_yaml_files(
        yaml1_path=yaml1,
        yaml2_path=yaml2,
        output_report=Path("./yaml_comparison_report.md"),
        keep_dbs=True,  # Keep databases for inspection
        root_table_name="deployment",
    )

    print("=" * 70)
    print("Comparison Report")
    print("=" * 70)
    print()
    print(report)
    print()
    print("=" * 70)
    print("✓ Complete!")
    print("=" * 70)
    print()
    print("Generated files:")
    print("  - yaml_comparison_report.md (Comparison report)")
    print("  - temp_dbs/XY_123-mpm.db (Database from File 1)")
    print("  - temp_dbs/CD_789-mpm.db (Database from File 2)")
    print()
    print("You can inspect the databases using:")
    print("  sqlite3 temp_dbs/XY_123-mpm.db")
    print("  .tables")
    print("  SELECT * FROM deployment;")


if __name__ == "__main__":
    main()
