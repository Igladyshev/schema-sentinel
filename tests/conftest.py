"""Test configuration and fixtures."""

import pytest


@pytest.fixture
def sample_database_config():
    """Sample database configuration for testing."""
    return {
        "account": "test_account",
        "user": "test_user",
        "password": "test_password",
        "warehouse": "test_warehouse",
        "database": "test_database",
        "schema": "test_schema",
        "role": "test_role",
    }
