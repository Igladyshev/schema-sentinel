"""Mock Snowflake connection for local testing without actual Snowflake instance."""

from contextlib import contextmanager


class MockSnowflakeCursor:
    """Mock Snowflake cursor for testing."""

    def __init__(self, return_data: list | None = None):
        """
        Initialize mock cursor.

        Args:
            return_data: Data to return from fetchall()
        """
        self.return_data = return_data or []
        self.description = []
        self._executed_queries = []
        self._closed = False

    def execute(self, query: str, params: dict | None = None) -> "MockSnowflakeCursor":
        """
        Mock execute method.

        Args:
            query: SQL query
            params: Query parameters

        Returns:
            Self for chaining
        """
        self._executed_queries.append({"query": query, "params": params})

        # Set up description based on return data
        if self.return_data and len(self.return_data) > 0:
            first_row = self.return_data[0]
            if isinstance(first_row, dict):
                self.description = [(col, None, None, None, None, None, None) for col in first_row]
        return self

    def fetchall(self) -> list:
        """
        Return all mock data.

        Returns:
            List of rows (tuples or dicts)
        """
        # Convert dicts to tuples if needed
        if self.return_data and isinstance(self.return_data[0], dict):
            return [tuple(row.values()) for row in self.return_data]
        return self.return_data

    def fetchone(self) -> tuple | None:
        """
        Return first row of mock data.

        Returns:
            First row or None
        """
        data = self.fetchall()
        return data[0] if data else None

    def close(self) -> None:
        """Close the cursor."""
        self._closed = True

    @property
    def rowcount(self) -> int:
        """Return number of rows."""
        return len(self.return_data)


class MockSnowflakeConnection:
    """Mock Snowflake connection for testing."""

    def __init__(self, mock_data: dict | None = None):
        """
        Initialize mock connection.

        Args:
            mock_data: Dictionary mapping queries to their results
        """
        self.mock_data = mock_data or {}
        self._closed = False
        self._cursors = []

    def cursor(self) -> MockSnowflakeCursor:
        """
        Create a mock cursor.

        Returns:
            MockSnowflakeCursor instance
        """
        # Get data for the next query if available
        cursor = MockSnowflakeCursor()
        self._cursors.append(cursor)
        return cursor

    def close(self) -> None:
        """Close the connection."""
        self._closed = True


class MockSnowflakeConnectionManager:
    """Mock version of SnowflakeConnectionManager for testing."""

    def __init__(self, mock_results: list[dict] | None = None):
        """
        Initialize mock connection manager.

        Args:
            mock_results: List of dictionaries to return from queries
        """
        self.mock_results = mock_results or []
        self.account = "test_account"
        self.user = "test_user"
        self.password = "test_password"
        self.warehouse = "test_warehouse"
        self.database = "test_database"
        self.schema = "test_schema"
        self.role = "test_role"
        self._connection = None
        self._executed_queries = []

    def connect(self) -> MockSnowflakeConnection:
        """Return mock connection."""
        self._connection = MockSnowflakeConnection()
        return self._connection

    def disconnect(self) -> None:
        """Mock disconnect."""
        if self._connection:
            self._connection.close()
            self._connection = None

    @contextmanager
    def get_connection(self):
        """Context manager for mock connection."""
        connection = self.connect()
        try:
            yield connection
        finally:
            self.disconnect()

    def execute_query(self, query: str, params: dict | None = None) -> list[dict]:
        """
        Mock query execution.

        Args:
            query: SQL query
            params: Query parameters

        Returns:
            Mock results
        """
        self._executed_queries.append({"query": query, "params": params})
        return self.mock_results

    def get_executed_queries(self) -> list[dict]:
        """
        Get list of executed queries for assertions.

        Returns:
            List of executed queries with parameters
        """
        return self._executed_queries
