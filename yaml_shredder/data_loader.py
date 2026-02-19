"""Load generated tables into databases."""

import sqlite3
from pathlib import Path

import duckdb
import pandas as pd


class SQLiteLoader:
    """Load DataFrames into SQLite database."""

    def __init__(self, db_path: str | Path):
        """
        Initialize SQLite loader.

        Args:
            db_path: Path to SQLite database file (will be created if doesn't exist)
        """
        self.db_path = Path(db_path)
        # Ensure parent directory exists
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.connection = None
        self.loaded_tables = []

    def connect(self) -> None:
        """Establish connection to SQLite database."""
        self.connection = sqlite3.connect(str(self.db_path))
        print(f"Connected to SQLite database: {self.db_path}")

    def disconnect(self) -> None:
        """Close database connection."""
        if self.connection:
            self.connection.close()
            self.connection = None
            print("Database connection closed")

    def load_tables(
        self,
        tables: dict[str, pd.DataFrame],
        if_exists: str = "replace",
        create_indexes: bool = True,
    ) -> None:
        """
        Load multiple tables into SQLite.

        Args:
            tables: Dictionary of table_name -> DataFrame
            if_exists: How to behave if table exists ('fail', 'replace', 'append')
            create_indexes: Whether to create indexes on foreign key columns
        """
        if not self.connection:
            self.connect()

        self.loaded_tables = []

        for table_name, df in tables.items():
            self._load_table(table_name, df, if_exists)
            self.loaded_tables.append(table_name)

            if create_indexes:
                self._create_indexes(table_name, df)

        print(f"\n✓ Loaded {len(tables)} tables into {self.db_path}")

    def _load_table(self, table_name: str, df: pd.DataFrame, if_exists: str = "replace") -> None:
        """
        Load a single table into SQLite.

        Args:
            table_name: Name of the table
            df: DataFrame to load
            if_exists: How to behave if table exists
        """
        # Convert boolean columns to integers for SQLite
        df_copy = df.copy()
        for col in df_copy.columns:
            if df_copy[col].dtype == "bool":
                df_copy[col] = df_copy[col].astype(int)

        df_copy.to_sql(table_name, self.connection, if_exists=if_exists, index=False)
        print(f"  Loaded {len(df_copy)} rows into table: {table_name}")

    def _create_indexes(self, table_name: str, df: pd.DataFrame) -> None:
        """
        Create indexes on key columns.

        Args:
            table_name: Name of the table
            df: DataFrame to analyze for index creation
        """
        cursor = self.connection.cursor()

        # Create index on id column if exists
        if "id" in [c.lower() for c in df.columns]:
            id_col = next(c for c in df.columns if c.lower() == "id")
            index_name = f"idx_{table_name}_id"
            try:
                cursor.execute(f'CREATE INDEX IF NOT EXISTS "{index_name}" ON "{table_name}" ("{id_col}")')
            except sqlite3.OperationalError:
                pass  # Index might already exist

        # Create indexes on foreign key columns (parent_*)
        fk_columns = [c for c in df.columns if c.startswith("parent_")]
        for fk_col in fk_columns:
            index_name = f"idx_{table_name}_{fk_col}"
            try:
                cursor.execute(f'CREATE INDEX IF NOT EXISTS "{index_name}" ON "{table_name}" ("{fk_col}")')
            except sqlite3.OperationalError:
                # Index may already exist or table structure doesn't allow it; safe to ignore
                pass

        self.connection.commit()

    def execute_ddl(self, ddl_statements: dict[str, str]) -> None:
        """
        Execute DDL statements to create tables.

        Args:
            ddl_statements: Dictionary of table_name -> CREATE TABLE statement
        """
        if not self.connection:
            self.connect()

        cursor = self.connection.cursor()

        for table_name, ddl in ddl_statements.items():
            # SQLite doesn't support ALTER TABLE ADD CONSTRAINT for foreign keys
            # Skip ALTER statements
            statements = ddl.split(";")
            for stmt in statements:
                stmt = stmt.strip()
                if stmt and not stmt.startswith("ALTER TABLE"):
                    try:
                        cursor.execute(stmt)
                    except sqlite3.OperationalError as e:
                        print(f"Warning: Could not execute DDL for {table_name}: {e}")

        self.connection.commit()
        print(f"✓ Executed DDL for {len(ddl_statements)} tables")

    def query(self, sql: str) -> pd.DataFrame:
        """
        Execute a SQL query and return results as DataFrame.

        Args:
            sql: SQL query to execute

        Returns:
            Query results as DataFrame
        """
        if not self.connection:
            self.connect()

        return pd.read_sql_query(sql, self.connection)

    def get_table_info(self, table_name: str) -> pd.DataFrame:
        """
        Get schema information for a table.

        Args:
            table_name: Name of the table

        Returns:
            DataFrame with table schema information
        """
        return self.query(f'PRAGMA table_info("{table_name}")')

    def list_tables(self) -> list[str]:
        """
        List all tables in the database.

        Returns:
            List of table names
        """
        cursor = self.connection.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        return [row[0] for row in cursor.fetchall()]

    def print_summary(self) -> None:
        """Print summary of loaded database."""
        if not self.connection:
            print("Not connected to database")
            return

        print(f"\n{'=' * 60}")
        print("DATABASE SUMMARY")
        print(f"{'=' * 60}")
        print(f"Database: {self.db_path}")
        print(f"Size: {self.db_path.stat().st_size / 1024:.1f} KB")

        tables = self.list_tables()
        print(f"\nTables: {len(tables)}")

        for table in tables:
            cursor = self.connection.cursor()
            cursor.execute(f'SELECT COUNT(*) FROM "{table}"')
            count = cursor.fetchone()[0]
            print(f"  - {table}: {count} rows")

    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()


def load_to_sqlite(
    tables: dict[str, pd.DataFrame],
    db_path: str | Path,
    if_exists: str = "replace",
    create_indexes: bool = True,
) -> SQLiteLoader:
    """
    Quick function to load tables into SQLite.

    Args:
        tables: Dictionary of table_name -> DataFrame
        db_path: Path to SQLite database
        if_exists: How to behave if table exists
        create_indexes: Whether to create indexes

    Returns:
        SQLiteLoader instance (still connected)
    """
    loader = SQLiteLoader(db_path)
    loader.connect()
    loader.load_tables(tables, if_exists, create_indexes)
    return loader


class DuckDBLoader:
    """Load DataFrames into DuckDB database - high-performance alternative to SQLite."""

    def __init__(self, db_path: str | Path | None = None):
        """
        Initialize DuckDB loader.

        Args:
            db_path: Path to DuckDB database file. If None, uses in-memory database.
        """
        self.db_path = Path(db_path) if db_path else None
        if self.db_path:
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.connection = None
        self.loaded_tables = []

    def connect(self) -> None:
        """Establish connection to DuckDB database."""
        if self.db_path:
            self.connection = duckdb.connect(str(self.db_path))
            print(f"Connected to DuckDB database: {self.db_path}")
        else:
            self.connection = duckdb.connect(":memory:")
            print("Connected to in-memory DuckDB database")

    def disconnect(self) -> None:
        """Close database connection."""
        if self.connection:
            self.connection.close()
            self.connection = None
            print("Database connection closed")

    def load_tables(
        self,
        tables: dict[str, pd.DataFrame],
        if_exists: str = "replace",
        create_indexes: bool = True,
    ) -> None:
        """
        Load multiple tables into DuckDB.

        Args:
            tables: Dictionary of table_name -> DataFrame
            if_exists: How to behave if table exists ('fail', 'replace', 'append')
            create_indexes: Whether to create indexes on foreign key columns
        """
        if not self.connection:
            self.connect()

        self.loaded_tables = []

        for table_name, df in tables.items():
            self._load_table(table_name, df, if_exists)
            self.loaded_tables.append(table_name)

            if create_indexes:
                self._create_indexes(table_name, df)

        print(f"\n✓ Loaded {len(tables)} tables into DuckDB")

    def _load_table(self, table_name: str, df: pd.DataFrame, if_exists: str = "replace") -> None:
        """
        Load a single table into DuckDB.

        Args:
            table_name: Name of the table
            df: DataFrame to load
            if_exists: How to behave if table exists
        """
        # Drop table if exists and if_exists is 'replace'
        if if_exists == "replace":
            self.connection.execute(f'DROP TABLE IF EXISTS "{table_name}"')

        # Register DataFrame as a view first, then create table
        self.connection.register(f"__{table_name}", df)
        self.connection.execute(f'CREATE TABLE "{table_name}" AS SELECT * FROM "__{table_name}"')
        self.connection.execute(f'DROP VIEW "__{table_name}"')

        row_count = self.connection.execute(f'SELECT COUNT(*) FROM "{table_name}"').fetchall()[0][0]
        print(f"  Loaded {row_count} rows into table: {table_name}")

    def _create_indexes(self, table_name: str, df: pd.DataFrame) -> None:
        """
        Create indexes on key columns.

        Args:
            table_name: Name of the table
            df: DataFrame to analyze for index creation
        """
        # Create index on id column if exists
        if "id" in [c.lower() for c in df.columns]:
            id_col = next(c for c in df.columns if c.lower() == "id")
            index_name = f"idx_{table_name}_id"
            try:
                self.connection.execute(f'CREATE INDEX IF NOT EXISTS "{index_name}" ON "{table_name}" ("{id_col}")')
            except Exception:
                pass  # Index might already exist

        # Create indexes on foreign key columns (parent_*)
        fk_columns = [c for c in df.columns if c.startswith("parent_")]
        for fk_col in fk_columns:
            index_name = f"idx_{table_name}_{fk_col}"
            try:
                self.connection.execute(f'CREATE INDEX IF NOT EXISTS "{index_name}" ON "{table_name}" ("{fk_col}")')
            except Exception:
                # Index may already exist or table structure doesn't allow it; safe to ignore
                pass

    def execute_ddl(self, ddl_statements: dict[str, str]) -> None:
        """
        Execute DDL statements to create tables.

        Args:
            ddl_statements: Dictionary of table_name -> CREATE TABLE statement
        """
        if not self.connection:
            self.connect()

        for table_name, ddl in ddl_statements.items():
            # Split on semicolons and execute each statement
            statements = ddl.split(";")
            for stmt in statements:
                stmt = stmt.strip()
                if stmt:
                    try:
                        self.connection.execute(stmt)
                    except Exception as e:
                        print(f"Warning: Could not execute DDL for {table_name}: {e}")

        print(f"✓ Executed DDL for {len(ddl_statements)} tables")

    def query(self, sql: str) -> pd.DataFrame:
        """
        Execute a SQL query and return results as DataFrame.

        Args:
            sql: SQL query to execute

        Returns:
            Query results as DataFrame
        """
        if not self.connection:
            self.connect()

        return self.connection.execute(sql).df()

    def get_table_info(self, table_name: str) -> pd.DataFrame:
        """
        Get schema information for a table.

        Args:
            table_name: Name of the table

        Returns:
            DataFrame with table schema information (column_name, column_type)
        """
        result = self.connection.execute(f"DESCRIBE {table_name}").df()
        # Keep only essential columns for clean output
        return result[["column_name", "column_type"]].rename(columns={"column_name": "name", "column_type": "type"})

    def list_tables(self) -> list[str]:
        """
        List all tables in the database.

        Returns:
            List of table names
        """
        result = self.connection.execute(
            "SELECT table_name FROM information_schema.tables WHERE table_schema='main'"
        ).fetchall()
        return [row[0] for row in result]

    def print_summary(self) -> None:
        """Print summary of loaded database."""
        if not self.connection:
            print("Not connected to database")
            return

        print(f"\n{'=' * 60}")
        print("DUCKDB DATABASE SUMMARY")
        print(f"{'=' * 60}")
        if self.db_path:
            size_kb = self.db_path.stat().st_size / 1024 if self.db_path.exists() else 0
            print(f"Database: {self.db_path}")
            print(f"Size: {size_kb:.1f} KB")
        else:
            print("Database: In-memory")

        tables = self.list_tables()
        print(f"\nTables: {len(tables)}")

        for table in tables:
            count = self.connection.execute(f'SELECT COUNT(*) FROM "{table}"').fetchall()[0][0]
            print(f"  - {table}: {count} rows")

    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()


def load_to_duckdb(
    tables: dict[str, pd.DataFrame],
    db_path: str | Path | None = None,
    if_exists: str = "replace",
    create_indexes: bool = True,
) -> DuckDBLoader:
    """
    Quick function to load tables into DuckDB.

    Args:
        tables: Dictionary of table_name -> DataFrame
        db_path: Path to DuckDB database (or None for in-memory)
        if_exists: How to behave if table exists
        create_indexes: Whether to create indexes

    Returns:
        DuckDBLoader instance (still connected)
    """
    loader = DuckDBLoader(db_path)
    loader.connect()
    loader.load_tables(tables, if_exists, create_indexes)
    return loader
