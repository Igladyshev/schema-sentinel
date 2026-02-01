"""Snowflake local testing utilities."""

from .connection import SnowflakeConnectionManager
from .mock import (
    MockSnowflakeConnection,
    MockSnowflakeCursor,
    MockSnowflakeConnectionManager,
)
from .mpm_parser import MPMConfig
from .mpm_snowpark import (
    MPMSnowparkSaver,
    DEPLOYMENT_STRUCT,
    COMMUNITY_STRUCT,
    SENSOR_ACTION_STRUCT,
    REPORT_ACTION_STRUCT,
)
from .schema import MPM_SCHEMA

__all__ = [
    "SnowflakeConnectionManager",
    "MockSnowflakeConnection",
    "MockSnowflakeCursor",
    "MockSnowflakeConnectionManager",
    "MPMConfig",
    "MPMSnowparkSaver",
    "DEPLOYMENT_STRUCT",
    "COMMUNITY_STRUCT",
    "SENSOR_ACTION_STRUCT",
    "REPORT_ACTION_STRUCT",
    "MPM_SCHEMA",
]

__version__ = "0.1.0"


def main() -> None:
    """CLI entry point."""
    print("Snowflake Local Testing Utilities")
    print(f"Version: {__version__}")
    print("\nUse this package to test Snowflake code locally with mocks.")
    print("See README.md for usage examples.")
