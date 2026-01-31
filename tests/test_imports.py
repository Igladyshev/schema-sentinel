"""Basic tests to verify package installation and imports."""
import pytest


def test_package_import():
    """Test that the schema_sentinel package can be imported."""
    import schema_sentinel

    assert schema_sentinel.PROJECT_NAME == "schema-sentinel"


def test_core_dependencies():
    """Test that core dependencies are available."""
    import sqlalchemy
    import pandas
    import snowflake.connector
    import alembic

    assert sqlalchemy.__version__.startswith("1.4")
    assert pandas.__version__ is not None
    assert snowflake.connector.__version__ is not None
    assert alembic.__version__ is not None


def test_metadata_manager_imports():
    """Test that metadata_manager modules can be imported."""
    from schema_sentinel.metadata_manager import engine, metadata, enums
    from schema_sentinel.metadata_manager.model import database, table, column

    assert engine is not None
    assert metadata is not None
    assert enums is not None
    assert database is not None
    assert table is not None
    assert column is not None


def test_markdown_utils_imports():
    """Test that markdown_utils modules can be imported."""
    from schema_sentinel.markdown_utils import markdown

    assert markdown is not None
