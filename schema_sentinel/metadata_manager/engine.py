import logging as log
import os
from abc import ABC, abstractmethod
from configparser import ConfigParser

import pandas as pd
import snowflake.connector
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from snowflake.sqlalchemy import URL
from sqlalchemy import MetaData, create_engine, text
from sqlalchemy.engine import Engine

from .enums import ConnectMode


class DBEngineStrategy(ABC):
    engine = None
    conn = None
    metadata: MetaData = None
    connect_mode = ConnectMode.KEY_PAIR.value
    env: str = "dev"
    url: str = None

    def __init__(self, config: dict, env: str = "dev"):
        self.account = config.get("account")
        self.user = config.get("user")
        self.warehouse = config.get("warehouse")
        self.database = config.get("database")
        self.private_key = config.get("private_key") if "private_key" in config else b""
        self.role = config.get("role")
        self.engine = None
        self.private_key_passphrase = config.get("private_key_passphrase") if "private_key_passphrase" in config else ""
        self.default_schema = config.get("schema")
        self.connect_mode = config.get("connect_mode")
        self.env = env
        self.url = config.get("url")

    @abstractmethod
    def get_engine(self):
        pass

    @abstractmethod
    def get_conn(self):
        pass

    @abstractmethod
    def close(self):
        pass

    def __del__(self):
        self.close()

    @abstractmethod
    def execute(self, statement, parameters=None, columns=None, schema=None):
        pass

    def decode_private_key(self, password):
        p_key = serialization.load_pem_private_key(
            self.private_key, password=password.encode(), backend=default_backend()
        )

        pkb = p_key.private_bytes(
            encoding=serialization.Encoding.DER,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )

        return pkb


class SqLiteAqlAlchemyEngine(DBEngineStrategy):
    metadata: MetaData = None
    engine: Engine = None
    url: str = None

    def __int__(self, config: dict, env: str, url: str):
        config["url"] = url
        super().__init__(env=None, config=config)

    def get_engine(self):
        if self.engine is None:
            self.engine = create_engine(url=self.url)
        return self.engine

    def close(self):
        if self.engine:
            self.engine.dispose()

    def execute(self, statement, parameters=None, columns=None, schema=None):
        log.debug(f"statement=[{statement}]")
        conn = self.get_conn()

        if not columns:
            if parameters is not None:
                conn.execute(text(statement), parameters)
            else:
                conn.execute(text(statement))
            return True, None

        if parameters is not None:
            results = pd.read_sql(sql=text(statement), con=conn, params=parameters)
        else:
            results = pd.read_sql(sql=text(statement), con=conn)

        return True, results

    def get_conn(self):
        return self.get_engine()


class SfAlchemyEngine(DBEngineStrategy):
    snowflake.connector.paramstyle = "numeric"

    def get_engine(self):
        if self.engine is None:
            if self.connect_mode == ConnectMode.SSO.value:
                self.engine = create_engine(
                    URL(
                        account=self.account,
                        user=self.user,
                        warehouse=self.warehouse,
                        database=self.database,
                        role=self.role,
                        cache_column_metadata=True,
                        schema=self.default_schema,
                        authenticator="externalbrowser",
                    )
                )
            if self.connect_mode == ConnectMode.PWD.value:
                self.engine = create_engine(
                    URL(
                        account=self.account,
                        user=self.user,
                        warehouse=self.warehouse,
                        database=self.database,
                        role=self.role,
                        cache_column_metadata=True,
                        schema=self.default_schema,
                        password=os.getenv("SNOWFLAKE_PASSWORD"),
                    )
                )
            if self.connect_mode == ConnectMode.KEY_PAIR.value:
                pkb = self.decode_private_key(self.private_key_passphrase)
                self.engine = create_engine(
                    URL(
                        account=self.account,
                        user=self.user,
                        warehouse=self.warehouse,
                        database=self.database,
                        role=self.role,
                        cache_column_metadata=True,
                        schema=self.default_schema,
                    ),
                    connect_args={
                        "private_key": pkb,
                    },
                )

        return self.engine

    def get_conn(self):
        if self.conn is None:
            engine = self.get_engine()
            self.conn = engine.connect().execution_options(autocommit=False)
        return self.conn

    def close(self):
        if self.conn is not None:
            self.conn.close()
        if self.engine is not None:
            self.engine.dispose()

    def execute(self, statement, parameters=None, columns=None, schema=None):
        log.debug(f"statement=[{statement}]")
        conn = self.get_conn()
        if schema is not None:
            conn.execute(f"USE SCHEMA {schema};")

        if columns is None:
            conn.execute("BEGIN")
            if parameters is not None:
                conn.execute(text(statement), parameters)
            else:
                conn.execute(text(statement))
            conn.execute("COMMIT")
            return True, None

        if parameters is not None:
            results = pd.read_sql(sql=text(statement), con=conn, params=parameters)
        else:
            results = pd.read_sql(sql=text(statement), con=conn)

        return True, results


class SfConnectorEngine(DBEngineStrategy):
    def get_engine(self, schema=None):
        pkb = self.decode_private_key(self.private_key_passphrase)

        if self.engine is None:
            snowflake.connector.paramstyle = "numeric"
            self.engine = snowflake.connector.connect(
                user=self.user,
                private_key=pkb,
                account=self.account,
                warehouse=self.warehouse,
                database=self.database,
                schema=self.default_schema,
                role=self.role,
                autocommit=False,
            )
        return self.engine

    def get_conn(self):
        if self.conn is None:
            if self.connect_mode == ConnectMode.SSO.value:
                snowflake.connector.paramstyle = "numeric"
                self.conn = snowflake.connector.connect(
                    account=self.account,
                    user=self.user,
                    role=self.role,
                    database=self.database,
                    schema=self.schema,
                    warehouse=self.warehouse,
                    authenticator="externalbrowser",
                )

            if self.connect_mode == ConnectMode.PWD.value:
                self.conn = snowflake.connector.connect(
                    account=self.account,
                    user=self.user,
                    role=self.role,
                    database=self.database,
                    schema=self.schema,
                    warehouse=self.warehouse,
                    password=os.getenv("SNOWFLAKE_PASSWORD"),
                )

            if self.connect_mode == ConnectMode.KEY_PAIR.value:
                pkb = self.decode_private_key(self.private_key_passphrase)
                self.conn = snowflake.connector.connect(
                    account=self.account,
                    user=self.user,
                    role=self.role,
                    database=self.database,
                    schema=self.default_schema,
                    warehouse=self.warehouse,
                    private_key=pkb,
                )
        return self.conn

    def close(self):
        if self.engine is not None:
            self.engine.close()

    def execute(self, statement, parameters=None, columns=None, schema=None):
        log.debug(f"statement=[{statement}]")
        conn = self.get_engine()

        if schema is not None:
            conn.cursor().execute(f"USE SCHEMA {schema};")

        if columns is None:
            conn.cursor().execute(statement, parameters)
            conn.commit()
            return True, None

        if parameters is not None:
            results = pd.read_sql(text(statement), conn, *parameters)
        else:
            results = pd.read_sql(text(statement), conn)

        return True, results


def get_config_dict(
    config: ConfigParser,
    *,
    private_key: bytes,
    password: str,
    connect_mode: int = ConnectMode.KEY_PAIR.value,
    user: str = None,
    cache_column_metadata=False,
):
    db_section = "DB_CONNECTION"
    config_map = {
        "account": config.get(db_section, "account"),
        "warehouse": config.get(db_section, "warehouse"),
        "user": user,
        "database": config.get(db_section, "database"),
        "role": config.get(db_section, "role"),
        "schema": config.get(db_section, "schema"),
        "connect_mode": connect_mode,
        "cache_column_metadata": cache_column_metadata,
        "timezone": "America/Los_Angeles",
    }
    if connect_mode == ConnectMode.PWD.value:
        config_map["password"] = password
    elif connect_mode == ConnectMode.KEY_PAIR.value:
        config_map["private_key"] = private_key
        config_map["private_key_passphrase"] = password

    return config_map
