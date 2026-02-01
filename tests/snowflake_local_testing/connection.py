"""Snowflake connection management utilities."""

import os
from typing import Optional
from contextlib import contextmanager
from pathlib import Path
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization

import snowflake.connector
from snowflake.connector import SnowflakeConnection
from dotenv import load_dotenv


class SnowflakeConnectionManager:
    """Manages Snowflake database connections with environment variable configuration."""

    def __init__(
        self,
        account: Optional[str] = None,
        user: Optional[str] = None,
        password: Optional[str] = None,
        warehouse: Optional[str] = None,
        database: Optional[str] = None,
        schema: Optional[str] = None,
        role: Optional[str] = None,
        private_key_path: Optional[str] = None,
        private_key_passphrase: Optional[str] = None,
        authenticator: Optional[str] = None,
    ):
        """
        Initialize Snowflake connection manager.

        Supports multiple authentication methods:
        - Password authentication (user + password)
        - Key pair authentication (user + private_key_path)
        - External browser authentication (authenticator='externalbrowser')
        - OAuth authentication (authenticator='oauth')

        Args:
            account: Snowflake account identifier
            user: Snowflake username
            password: Snowflake password (for password auth)
            warehouse: Snowflake warehouse name
            database: Snowflake database name
            schema: Snowflake schema name
            role: Snowflake role name
            private_key_path: Path to private key file (for key pair auth)
            private_key_passphrase: Passphrase for encrypted private key
            authenticator: Authentication method (e.g., 'externalbrowser', 'oauth')
        """
        load_dotenv()

        self.account = account or os.getenv("SNOWFLAKE_ACCOUNT")
        self.user = user or os.getenv("SNOWFLAKE_USER")
        self.password = password or os.getenv("SNOWFLAKE_PASSWORD")
        self.warehouse = warehouse or os.getenv("SNOWFLAKE_WAREHOUSE")
        self.database = database or os.getenv("SNOWFLAKE_DATABASE")
        self.schema = schema or os.getenv("SNOWFLAKE_SCHEMA")
        self.role = role or os.getenv("SNOWFLAKE_ROLE")
        self.private_key_path = private_key_path or os.getenv("SNOWFLAKE_PRIVATE_KEY_PATH")
        self.private_key_passphrase = private_key_passphrase or os.getenv("SNOWFLAKE_PRIVATE_KEY_PASSPHRASE")
        self.authenticator = authenticator or os.getenv("SNOWFLAKE_AUTHENTICATOR")

        self._connection: Optional[SnowflakeConnection] = None
        self._private_key: Optional[bytes] = None

    def _load_private_key(self) -> bytes:
        """
        Load and parse private key from file.

        Returns:
            Parsed private key in DER format

        Raises:
            FileNotFoundError: If private key file doesn't exist
            ValueError: If private key cannot be parsed
        """
        if not self.private_key_path:
            raise ValueError("Private key path not provided")

        key_path = Path(self.private_key_path).expanduser()
        if not key_path.exists():
            raise FileNotFoundError(f"Private key file not found: {key_path}")

        with open(key_path, "rb") as key_file:
            private_key_data = key_file.read()

        # Parse the private key with optional passphrase
        passphrase = None
        if self.private_key_passphrase:
            passphrase = self.private_key_passphrase.encode()

        try:
            private_key = serialization.load_pem_private_key(
                private_key_data,
                password=passphrase,
                backend=default_backend()
            )
        except Exception as e:
            raise ValueError(f"Failed to load private key: {e}")

        # Serialize to DER format for Snowflake
        pkb = private_key.private_bytes(
            encoding=serialization.Encoding.DER,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )

        return pkb

    def connect(self) -> SnowflakeConnection:
        """
        Establish connection to Snowflake using configured authentication method.

        Authentication priority:
        1. Key pair authentication (if private_key_path provided)
        2. External authenticator (if authenticator provided)
        3. Password authentication (if password provided)

        Returns:
            SnowflakeConnection: Active Snowflake connection

        Raises:
            ValueError: If required credentials are missing or invalid
        """
        if not self.account or not self.user:
            raise ValueError(
                "Missing required Snowflake credentials. "
                "Please provide at least account and user."
            )

        # Prepare connection parameters
        connection_params: dict[str, str | bytes] = {
            "account": self.account,
            "user": self.user,
        }

        # Add optional parameters if provided
        if self.warehouse:
            connection_params["warehouse"] = self.warehouse
        if self.database:
            connection_params["database"] = self.database
        if self.schema:
            connection_params["schema"] = self.schema
        if self.role:
            connection_params["role"] = self.role

        # Determine authentication method (priority order)
        if self.private_key_path:
            # Key pair authentication
            if not self._private_key:
                self._private_key = self._load_private_key()
            connection_params["private_key"] = self._private_key
        elif self.authenticator:
            # External authenticator (e.g., externalbrowser, oauth)
            connection_params["authenticator"] = self.authenticator
        elif self.password:
            # Password authentication
            connection_params["password"] = self.password
        else:
            raise ValueError(
                "No valid authentication method provided. "
                "Please provide password, private_key_path, or authenticator."
            )

        self._connection = snowflake.connector.connect(**connection_params)
        return self._connection

    def disconnect(self) -> None:
        """Close the Snowflake connection."""
        if self._connection:
            self._connection.close()
            self._connection = None

    @contextmanager
    def get_connection(self):
        """
        Context manager for Snowflake connections.

        Yields:
            SnowflakeConnection: Active connection that will be closed automatically

        Example:
            >>> manager = SnowflakeConnectionManager()
            >>> with manager.get_connection() as conn:
            ...     cursor = conn.cursor()
            ...     cursor.execute("SELECT CURRENT_VERSION()")
        """
        connection = self.connect()
        try:
            yield connection
        finally:
            self.disconnect()

    def execute_query(self, query: str, params: Optional[dict] = None) -> list[dict]:
        """
        Execute a SQL query and return results as list of dictionaries.

        Args:
            query: SQL query to execute
            params: Optional query parameters

        Returns:
            List of dictionaries containing query results
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)

                # Fetch column names
                columns = [desc[0] for desc in cursor.description]

                # Fetch all rows and convert to dictionaries
                results = []
                for row in cursor.fetchall():
                    results.append(dict(zip(columns, row)))

                return results
            finally:
                cursor.close()
