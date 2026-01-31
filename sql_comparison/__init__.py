import base64
import getpass
import logging as log
import os

from alembic.ddl import DefaultImpl
from sqlalchemy import and_
from sqlalchemy.dialects import registry
from sqlalchemy.orm import sessionmaker

from sql_comparison.metadata_manager.engine import SfAlchemyEngine, SqLiteAqlAlchemyEngine, get_config_dict
from sql_comparison.metadata_manager.enums import ConnectMode, Environment
from sql_comparison.metadata_manager.model.database import Database
from sql_comparison.metadata_manager.utils import get_config

PROJECT_NAME = "sql-comparison"
TEMP_DIR = os.getenv("TEMP") if os.name == "nt" else "/tmp"
LOG_FILE = os.path.join(TEMP_DIR, "sql-comparison.log")
LOG_LEVEL = os.getenv("LOG_LEVEL") if os.getenv("LOG_LEVEL") is not None else "INFO"

PROJECT_HOME = os.path.dirname(os.path.join(os.path.abspath("./"), PROJECT_NAME))
RESOURCES_PATH = os.path.join(PROJECT_HOME, "resources")
META_DB_PATH = os.path.join(RESOURCES_PATH, "meta-db")

log.basicConfig(
    level=LOG_LEVEL,
    format="%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s",
    handlers=[log.FileHandler(LOG_FILE), log.StreamHandler()],
)


class SqLiteImpl(DefaultImpl):
    __dialect__ = "sqlite"


class SnowflakeImpl(DefaultImpl):
    __dialect__ = "snowflake"


def get_metadata_engine(metadata_db: str) -> SqLiteAqlAlchemyEngine:
    url = f"sqlite:///{META_DB_PATH}/{metadata_db}"
    sqlite_engine = SqLiteAqlAlchemyEngine(env=None, config={"database": metadata_db, "user": get_user(), "url": url})
    engine = sqlite_engine.get_engine()
    return engine


def get_engine(env: str, resources_path: str, alias: str) -> (SfAlchemyEngine, list, str):
    """
    Get an SqlAlchemy engine based on environment. SSO connection mode is used
    :param env: environment, one of the following: dev, non_prod, cert and prod
    :param resources_path: resources folder path where to get an environment for provided alias
    :param alias: system alias or database identifier for configuration lookup
    :return: sqlalchemy.Engine
    """
    config = get_config(env, os.path.join(resources_path, alias))
    user = config.get(section="DB_CONNECTION", option="username")
    if env == "local":
        env = config.get("GENERAL", "env")

    database_name = config.get("DB_CONNECTION", "database")
    schemas = config.get("GENERAL", "schemas").split(",")

    private_key = b""
    private_key_passphrase = None

    if os.environ.get("PRIVATE_KEY"):
        private_key = base64.b64decode(os.environ.get("PRIVATE_KEY"))
        private_key_passphrase = os.environ.get("PRIVATE_KEY_PASSPHRASE")

    connect_mode = ConnectMode.SSO.value if not private_key_passphrase else ConnectMode.KEY_PAIR.value

    if connect_mode == ConnectMode.KEY_PAIR.value:
        config_dictionary = get_config_dict(
            config,
            private_key=private_key,
            password=private_key_passphrase,
            connect_mode=connect_mode,
            user=user,
            cache_column_metadata=True,
        )
    elif connect_mode == ConnectMode.SSO.value:
        config_dictionary = get_config_dict(
            config,
            private_key=private_key,
            password="",
            connect_mode=connect_mode,
            user=user,
            cache_column_metadata=True,
        )

    registry.register("snowflake", "snowflake.sqlalchemy", "dialect")
    db_engine: SfAlchemyEngine = SfAlchemyEngine(config=config_dictionary)
    db_engine.database = database_name
    db_engine.env = env

    return db_engine, schemas, database_name


def get_user():
    """
    Get the username for authentication.
    Can be customized via SNOWFLAKE_USER environment variable,
    or will use system username with optional email domain.

    :return: Username for Snowflake authentication (e.g., user@domain.com)
    """
    # Check if user is explicitly set in environment
    if os.getenv("SNOWFLAKE_USER"):
        return os.getenv("SNOWFLAKE_USER")

    # Otherwise, use system username with optional email domain
    username = getpass.getuser()
    email_domain = os.getenv("SNOWFLAKE_EMAIL_DOMAIN", "")

    if email_domain:
        return f"{username}@{email_domain}"
    return username


def load_db(database_name: str, version: str, environment: str, metadata_db: str = "metadata.db") -> Database:
    engine: SqLiteAqlAlchemyEngine = get_metadata_engine(metadata_db=metadata_db)
    Session = sessionmaker(bind=engine)
    session = Session()

    query = session.query(Database).filter(
        and_(Database.database_name == database_name, Database.version == version, Database.environment == environment)
    )
    if not query.count():
        raise Exception(f"Database {database_name} v.{version} could not be found in {environment} environment")

    return query.one(), session


def load_comparator(
    source_env: str, target_env: str, database_name: str, metadata_db: str, src_version: str, trg_version: str
):
    validate(source_env, target_env, database_name, src_version, trg_version)

    one, session = load_db(
        database_name=database_name, metadata_db=metadata_db, version=src_version, environment=source_env
    )

    two, session = load_db(
        database_name=database_name, metadata_db=metadata_db, version=trg_version, environment=target_env
    )

    return one, two, session


def validate(source_env: str, target_env: str, alias: str, src_version: str, trg_version: str) -> bool:
    # Validate alias is provided
    if not alias or not alias.strip():
        raise Exception("Database alias must be provided. Use --alias parameter to specify your database identifier.")

    if source_env not in Environment.list():
        raise Exception(f"{Environment.list()} are the only environments supported.")

    if source_env == target_env and src_version == trg_version:
        raise Exception("Comparing a database to itself does not make any sense!")
