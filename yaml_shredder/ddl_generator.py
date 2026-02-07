"""Generate SQL DDL statements from table structures."""

from pathlib import Path
from typing import Any

import pandas as pd


class DDLGenerator:
    """Generate SQL DDL (CREATE TABLE) statements from DataFrames."""

    # Type mapping from pandas to SQL
    TYPE_MAPPING = {
        "int64": "INTEGER",
        "int32": "INTEGER",
        "float64": "FLOAT",
        "float32": "FLOAT",
        "bool": "BOOLEAN",
        "datetime64[ns]": "TIMESTAMP",
        "object": "VARCHAR(1000)",  # Default for strings
        "string": "VARCHAR(1000)",
    }

    SNOWFLAKE_TYPE_MAPPING = {
        "int64": "NUMBER",
        "int32": "NUMBER",
        "float64": "FLOAT",
        "float32": "FLOAT",
        "bool": "BOOLEAN",
        "datetime64[ns]": "TIMESTAMP_NTZ",
        "object": "VARCHAR(16777216)",  # Snowflake max VARCHAR
        "string": "VARCHAR(16777216)",
    }

    SQLITE_TYPE_MAPPING = {
        "int64": "INTEGER",
        "int32": "INTEGER",
        "float64": "REAL",
        "float32": "REAL",
        "bool": "INTEGER",  # SQLite uses 0/1 for boolean
        "datetime64[ns]": "TEXT",  # SQLite stores dates as TEXT or INTEGER
        "object": "TEXT",
        "string": "TEXT",
    }

    def __init__(self, dialect: str = "snowflake"):
        """
        Initialize DDL generator.

        Args:
            dialect: SQL dialect ('snowflake', 'postgres', 'mysql', 'sqlite', 'standard')
        """
        self.dialect = dialect.lower()
        self.ddl_statements = {}

        # Select type mapping based on dialect
        if self.dialect == "snowflake":
            self.type_map = self.SNOWFLAKE_TYPE_MAPPING
        elif self.dialect == "sqlite":
            self.type_map = self.SQLITE_TYPE_MAPPING
        else:
            self.type_map = self.TYPE_MAPPING

    def generate_ddl(
        self, tables: dict[str, pd.DataFrame], relationships: list[dict[str, Any]] | None = None
    ) -> dict[str, str]:
        """
        Generate DDL statements for all tables.

        Args:
            tables: Dictionary of table_name -> DataFrame
            relationships: Optional list of relationships for foreign keys

        Returns:
            Dictionary of table_name -> DDL statement
        """
        self.ddl_statements = {}

        for table_name, df in tables.items():
            ddl = self._generate_table_ddl(table_name, df)
            self.ddl_statements[table_name] = ddl

        # Add foreign key constraints if relationships provided
        if relationships:
            self._add_foreign_keys(relationships)

        return self.ddl_statements

    def _generate_table_ddl(self, table_name: str, df: pd.DataFrame) -> str:
        """
        Generate CREATE TABLE statement for a single table.

        Args:
            table_name: Name of the table
            df: DataFrame with the data

        Returns:
            CREATE TABLE DDL statement
        """
        # Start DDL
        ddl_lines = [f"CREATE TABLE {self._quote_identifier(table_name)} ("]

        # Add columns
        column_defs = []
        for col_name in df.columns:
            col_type = self._infer_column_type(df[col_name])
            nullable = "NULL" if df[col_name].isna().any() else "NOT NULL"

            # Special handling for certain columns
            if col_name.lower() in ["id", "_row_index"]:
                nullable = "NOT NULL"

            column_def = f"    {self._quote_identifier(col_name)} {col_type} {nullable}"
            column_defs.append(column_def)

        ddl_lines.append(",\n".join(column_defs))

        # Add primary key if obvious
        if "id" in [c.lower() for c in df.columns]:
            id_col = next(c for c in df.columns if c.lower() == "id")
            ddl_lines.append(f",\n    PRIMARY KEY ({self._quote_identifier(id_col)})")

        # Close statement
        ddl_lines.append(");")

        return "\n".join(ddl_lines)

    def _infer_column_type(self, series: pd.Series) -> str:
        """
        Infer SQL type from pandas Series.

        Args:
            series: Pandas Series to analyze

        Returns:
            SQL type string
        """
        dtype_str = str(series.dtype)

        # Check for string length if object type
        if dtype_str == "object":
            # Skip expensive calculation for large series
            if len(series) > 1000:
                sample_series = series.dropna().head(100)
            else:
                sample_series = series.dropna()

            if len(sample_series) == 0:
                return self.type_map.get("object", "VARCHAR(1000)")

            max_length = sample_series.astype(str).str.len().max()
            if pd.isna(max_length):
                return self.type_map.get("object", "VARCHAR(1000)")

            if self.dialect == "sqlite":
                # SQLite TEXT has no length limit
                return "TEXT"
            elif self.dialect == "snowflake":
                # Snowflake VARCHAR can be very large
                if max_length > 16000000:
                    return "VARCHAR(16777216)"
                return f"VARCHAR({min(int(max_length * 1.5), 16777216)})"
            else:
                # Other databases - cap at reasonable size
                return f"VARCHAR({min(int(max_length * 1.5), 4000)})"

        return self.type_map.get(dtype_str, "VARCHAR(1000)")

    def _add_foreign_keys(self, relationships: list[dict[str, Any]]) -> None:
        """
        Add foreign key constraints to DDL statements.

        Args:
            relationships: List of relationship dictionaries
        """
        for rel in relationships:
            child_table = rel["child_table"]
            parent_table = rel["parent_table"]
            fk_columns = rel["foreign_keys"]

            if child_table in self.ddl_statements:
                # Add ALTER TABLE statement for foreign key
                for fk_col in fk_columns:
                    fk_name = f"FK_{child_table}_{parent_table}_{fk_col}"
                    alter_stmt = (
                        f"\nALTER TABLE {self._quote_identifier(child_table)} "
                        f"ADD CONSTRAINT {self._quote_identifier(fk_name)} "
                        f"FOREIGN KEY ({self._quote_identifier(f'parent_{fk_col}')}) "
                        f"REFERENCES {self._quote_identifier(parent_table)}({self._quote_identifier(fk_col)});"
                    )
                    self.ddl_statements[child_table] += alter_stmt

    def _quote_identifier(self, identifier: str) -> str:
        """
        Quote identifier based on dialect.

        Args:
            identifier: Identifier to quote

        Returns:
            Quoted identifier
        """
        if self.dialect == "mysql":
            return f"`{identifier}`"
        else:  # snowflake, postgres, sqlite use double quotes
            return f'"{identifier}"'

    def save_ddl(self, output_file: str | Path) -> None:
        """
        Save all DDL statements to a file.

        Args:
            output_file: Path to output file
        """
        output_file = Path(output_file)

        with open(output_file, "w") as f:
            f.write("-- DDL Statements generated by YAML Shredder\n")
            f.write(f"-- Dialect: {self.dialect.upper()}\n")
            f.write(f"-- Tables: {len(self.ddl_statements)}\n\n")

            for table_name, ddl in self.ddl_statements.items():
                f.write(f"-- Table: {table_name}\n")
                f.write(ddl)
                f.write("\n\n")

        print(f"DDL saved to: {output_file}")

    def print_ddl(self) -> None:
        """Print all DDL statements to console."""
        print(f"\n{'=' * 60}")
        print("SQL DDL STATEMENTS")
        print(f"{'=' * 60}")
        print(f"Dialect: {self.dialect.upper()}")
        print(f"Tables: {len(self.ddl_statements)}\n")

        for table_name, ddl in self.ddl_statements.items():
            print(f"-- {table_name}")
            print(ddl)
            print()


def generate_snowflake_ddl(
    tables: dict[str, pd.DataFrame],
    relationships: list[dict[str, Any]] | None = None,
    output_file: str | Path | None = None,
) -> dict[str, str]:
    """
    Quick function to generate Snowflake DDL.

    Args:
        tables: Dictionary of table_name -> DataFrame
        relationships: Optional relationships
        output_file: Optional file to save DDL

    Returns:
        Dictionary of DDL statements
    """
    generator = DDLGenerator(dialect="snowflake")
    ddl = generator.generate_ddl(tables, relationships)

    if output_file:
        generator.save_ddl(output_file)

    return ddl
