"""Snowflake Snowpark struct types and data persistence for MPM entities."""

from typing import Any

from snowflake.snowpark import DataFrame, Session
from snowflake.snowpark.functions import col
from snowflake.snowpark.table import WhenMatchedClause, WhenNotMatchedClause
from snowflake.snowpark.types import (
    StringType,
    StructField,
    StructType,
    TimestampType,
    VariantType,
)

# Struct type definitions

DEPLOYMENT_STRUCT = StructType(
    [
        StructField("deployment_version", StringType(), nullable=False),
        StructField("domain_code", StringType(), nullable=False),
        StructField("warehouse", VariantType(), nullable=False),
        StructField("internal_stage", StringType(), nullable=False),
        StructField("external_stage", StringType(), nullable=False),
        StructField("domain_timezone", StringType(), nullable=False),
    ]
)


COMMUNITY_STRUCT = StructType(
    [
        StructField("deployment_version", StringType(), nullable=False),
        StructField("domain_code", StringType(), nullable=False),
        StructField("community_id", StringType(), nullable=False),
        StructField("community_name", StringType(), nullable=False),
    ]
)


SENSOR_ACTION_STRUCT = StructType(
    [
        StructField("deployment_version", StringType(), nullable=False),
        StructField("domain_code", StringType(), nullable=False),
        StructField("action_type", StringType(), nullable=False),
        StructField("action_code", StringType(), nullable=False),
        StructField("abbreviation", StringType(), nullable=False),
        StructField("dataset", StringType(), nullable=True),
        StructField("source_system", StringType(), nullable=True),
        StructField("date_range_function", StringType(), nullable=True),
        StructField("schedule", VariantType(), nullable=False),
        StructField("parents", VariantType(), nullable=True),
        StructField("query_reference", VariantType(), nullable=False),
        StructField("start_date", TimestampType(), nullable=True),
    ]
)


REPORT_ACTION_STRUCT = StructType(
    [
        StructField("deployment_version", StringType(), nullable=False),
        StructField("domain_code", StringType(), nullable=False),
        StructField("action_type", StringType(), nullable=False),
        StructField("action_code", StringType(), nullable=False),
        StructField("abbreviation", StringType(), nullable=False),
        StructField("report_name", StringType(), nullable=True),
        StructField("report_file_pattern", StringType(), nullable=True),
        StructField("communities", VariantType(), nullable=True),
        StructField("consumer_tags", VariantType(), nullable=True),
        StructField("date_range_function", StringType(), nullable=True),
        StructField("schedule", VariantType(), nullable=False),
        StructField("parents", VariantType(), nullable=True),
        StructField("query_reference", VariantType(), nullable=False),
        StructField("header_information", VariantType(), nullable=True),
        StructField("pii_information", VariantType(), nullable=True),
        StructField("start_date", TimestampType(), nullable=True),
    ]
)


class MPMSnowparkSaver:
    """
    Snowpark-based persistence layer for MPM configuration entities.
    """

    def __init__(self, session: Session, database: str = "MPM_CONFIG", schema: str = "REPORTING"):
        """
        Initialize the saver with a Snowpark session.

        Args:
            session: Active Snowpark session
            database: Target database name
            schema: Target schema name
        """

        self.session = session
        self.database = database
        self.schema = schema
        self._ensure_schema_exists()

    def _ensure_schema_exists(self) -> None:
        """Ensure target database and schema exist."""
        # Skip for local testing mode - DDL not supported
        try:
            # Check if local testing mode by looking at connection type
            from snowflake.snowpark.mock._connection import MockServerConnection

            if isinstance(getattr(self.session, "_conn", None), MockServerConnection):
                # Local testing mode detected, skip DDL
                return
        except ImportError:
            pass

        self.session.sql(f"CREATE DATABASE IF NOT EXISTS {self.database}").collect()
        self.session.sql(f"CREATE SCHEMA IF NOT EXISTS {self.database}.{self.schema}").collect()

    def _get_full_table_name(self, table_name: str) -> str:
        """Get fully qualified table name."""
        return f"{self.database}.{self.schema}.{table_name}"

    def save_deployment(
        self, deployment_data: dict[str, Any], table_name: str = "deployment", mode: str = "merge"
    ) -> DataFrame:
        """
        Save deployment configuration to Snowflake using merge.

        Args:
            deployment_data: Deployment dictionary from MPMConfig.get_deployment_info()
            table_name: Target table name
            mode: Write mode ('merge', 'append', 'overwrite', 'errorifexists')

        Returns:
            Snowpark DataFrame containing the deployment data
        """
        df = self.session.create_dataframe([deployment_data], schema=DEPLOYMENT_STRUCT)
        full_table_name = self._get_full_table_name(table_name)

        if mode == "merge":
            # Create table if it doesn't exist
            try:
                self.session.sql(f"SELECT 1 FROM {full_table_name} LIMIT 1").collect()
            except Exception:
                df.write.mode("overwrite").save_as_table(full_table_name)
                return df

            # Create temp view for source data
            temp_view = f"temp_deployment_{id(df)}"
            df.create_or_replace_temp_view(temp_view)

            # Merge on deployment_version and domain_code
            target = self.session.table(full_table_name)
            source = self.session.table(temp_view)

            join_expr = (col("target.deployment_version") == col("source.deployment_version")) & (
                col("target.domain_code") == col("source.domain_code")
            )

            clauses = [
                WhenMatchedClause().update(
                    {
                        "warehouse": col("source.warehouse"),
                        "internal_stage": col("source.internal_stage"),
                        "external_stage": col("source.external_stage"),
                        "domain_timezone": col("source.domain_timezone"),
                    }
                ),
                WhenNotMatchedClause().insert(
                    {
                        "deployment_version": col("source.deployment_version"),
                        "domain_code": col("source.domain_code"),
                        "warehouse": col("source.warehouse"),
                        "internal_stage": col("source.internal_stage"),
                        "external_stage": col("source.external_stage"),
                        "domain_timezone": col("source.domain_timezone"),
                    }
                ),
            ]

            target.merge(source, join_expr, clauses)
        else:
            df.write.mode(mode).save_as_table(full_table_name)

        return df

    def save_communities(
        self,
        communities_data: list[dict[str, Any]],
        table_name: str = "retail_property",
        mode: str = "merge",
    ) -> DataFrame:
        """
        Save communities list to Snowflake using merge.

        Args:
            communities_data: Communities list from MPMConfig.get_communities_list()
            table_name: Target table name
            mode: Write mode ('merge', 'append', 'overwrite', 'errorifexists')

        Returns:
            Snowpark DataFrame containing the communities data
        """
        if not communities_data:
            return self.session.create_dataframe([], schema=COMMUNITY_STRUCT)

        df = self.session.create_dataframe(communities_data, schema=COMMUNITY_STRUCT)
        full_table_name = self._get_full_table_name(table_name)

        if mode == "merge":
            # Create table if it doesn't exist
            try:
                self.session.sql(f"SELECT 1 FROM {full_table_name} LIMIT 1").collect()
            except Exception:
                df.write.mode("overwrite").save_as_table(full_table_name)
                return df

            # Create temp view for source data
            temp_view = f"temp_communities_{id(df)}"
            df.create_or_replace_temp_view(temp_view)

            # Merge on deployment_version, domain_code, and community_id
            target = self.session.table(full_table_name)
            source = self.session.table(temp_view)

            join_expr = (
                (col("target.deployment_version") == col("source.deployment_version"))
                & (col("target.domain_code") == col("source.domain_code"))
                & (col("target.community_id") == col("source.community_id"))
            )

            clauses = [
                WhenMatchedClause().update(
                    {
                        "community_name": col("source.community_name"),
                    }
                ),
                WhenNotMatchedClause().insert(
                    {
                        "deployment_version": col("source.deployment_version"),
                        "domain_code": col("source.domain_code"),
                        "community_id": col("source.community_id"),
                        "community_name": col("source.community_name"),
                    }
                ),
            ]

            target.merge(source, join_expr, clauses)
        else:
            df.write.mode(mode).save_as_table(full_table_name)

        return df

    def save_sensor_actions(
        self,
        sensor_data: list[dict[str, Any]],
        table_name: str = "sensor",
        mode: str = "merge",
    ) -> DataFrame:
        """
        Save sensor actions to Snowflake using merge.

        Args:
            sensor_data: Sensor actions from MPMConfig.get_sensor_actions()
            table_name: Target table name
            mode: Write mode ('merge', 'append', 'overwrite', 'errorifexists')

        Returns:
            Snowpark DataFrame containing the sensor actions data
        """
        if not sensor_data:
            return self.session.create_dataframe([], schema=SENSOR_ACTION_STRUCT)

        df = self.session.create_dataframe(sensor_data, schema=SENSOR_ACTION_STRUCT)
        full_table_name = self._get_full_table_name(table_name)

        if mode == "merge":
            # Create table if it doesn't exist
            try:
                self.session.sql(f"SELECT 1 FROM {full_table_name} LIMIT 1").collect()
            except Exception:
                df.write.mode("overwrite").save_as_table(full_table_name)
                return df

            # Create temp view for source data
            temp_view = f"temp_sensor_{id(df)}"
            df.create_or_replace_temp_view(temp_view)

            # Merge on deployment_version, domain_code, and action_code
            target = self.session.table(full_table_name)
            source = self.session.table(temp_view)

            join_expr = (
                (col("target.deployment_version") == col("source.deployment_version"))
                & (col("target.domain_code") == col("source.domain_code"))
                & (col("target.action_code") == col("source.action_code"))
            )

            clauses = [
                WhenMatchedClause().update(
                    {
                        "action_type": col("source.action_type"),
                        "abbreviation": col("source.abbreviation"),
                        "dataset": col("source.dataset"),
                        "source_system": col("source.source_system"),
                        "date_range_function": col("source.date_range_function"),
                        "schedule": col("source.schedule"),
                        "parents": col("source.parents"),
                        "query_reference": col("source.query_reference"),
                        "start_date": col("source.start_date"),
                    }
                ),
                WhenNotMatchedClause().insert(
                    {
                        "deployment_version": col("source.deployment_version"),
                        "domain_code": col("source.domain_code"),
                        "action_type": col("source.action_type"),
                        "action_code": col("source.action_code"),
                        "abbreviation": col("source.abbreviation"),
                        "dataset": col("source.dataset"),
                        "source_system": col("source.source_system"),
                        "date_range_function": col("source.date_range_function"),
                        "schedule": col("source.schedule"),
                        "parents": col("source.parents"),
                        "query_reference": col("source.query_reference"),
                        "start_date": col("source.start_date"),
                    }
                ),
            ]

            target.merge(source, join_expr, clauses)
        else:
            df.write.mode(mode).save_as_table(full_table_name)

        return df

    def save_report_actions(
        self,
        report_data: list[dict[str, Any]],
        table_name: str = "report",
        mode: str = "merge",
    ) -> DataFrame:
        """
        Save report actions to Snowflake using merge.

        Args:
            report_data: Report actions from MPMConfig.get_report_actions()
            table_name: Target table name
            mode: Write mode ('merge', 'append', 'overwrite', 'errorifexists')

        Returns:
            Snowpark DataFrame containing the report actions data
        """
        if not report_data:
            return self.session.create_dataframe([], schema=REPORT_ACTION_STRUCT)

        df = self.session.create_dataframe(report_data, schema=REPORT_ACTION_STRUCT)
        full_table_name = self._get_full_table_name(table_name)

        if mode == "merge":
            # Create table if it doesn't exist
            try:
                self.session.sql(f"SELECT 1 FROM {full_table_name} LIMIT 1").collect()
            except Exception:
                df.write.mode("overwrite").save_as_table(full_table_name)
                return df

            # Create temp view for source data
            temp_view = f"temp_report_{id(df)}"
            df.create_or_replace_temp_view(temp_view)

            # Merge on deployment_version, domain_code, and action_code
            target = self.session.table(full_table_name)
            source = self.session.table(temp_view)

            join_expr = (
                (col("target.deployment_version") == col("source.deployment_version"))
                & (col("target.domain_code") == col("source.domain_code"))
                & (col("target.action_code") == col("source.action_code"))
            )

            clauses = [
                WhenMatchedClause().update(
                    {
                        "action_type": col("source.action_type"),
                        "abbreviation": col("source.abbreviation"),
                        "report_name": col("source.report_name"),
                        "report_file_pattern": col("source.report_file_pattern"),
                        "communities": col("source.communities"),
                        "consumer_tags": col("source.consumer_tags"),
                        "date_range_function": col("source.date_range_function"),
                        "schedule": col("source.schedule"),
                        "parents": col("source.parents"),
                        "query_reference": col("source.query_reference"),
                        "header_information": col("source.header_information"),
                        "pii_information": col("source.pii_information"),
                        "start_date": col("source.start_date"),
                    }
                ),
                WhenNotMatchedClause().insert(
                    {
                        "deployment_version": col("source.deployment_version"),
                        "domain_code": col("source.domain_code"),
                        "action_type": col("source.action_type"),
                        "action_code": col("source.action_code"),
                        "abbreviation": col("source.abbreviation"),
                        "report_name": col("source.report_name"),
                        "report_file_pattern": col("source.report_file_pattern"),
                        "communities": col("source.communities"),
                        "consumer_tags": col("source.consumer_tags"),
                        "date_range_function": col("source.date_range_function"),
                        "schedule": col("source.schedule"),
                        "parents": col("source.parents"),
                        "query_reference": col("source.query_reference"),
                        "header_information": col("source.header_information"),
                        "pii_information": col("source.pii_information"),
                        "start_date": col("source.start_date"),
                    }
                ),
            ]

            target.merge(source, join_expr, clauses)
        else:
            df.write.mode(mode).save_as_table(full_table_name)

        return df

    def save_all(
        self,
        deployment_data: dict[str, Any],
        communities_data: list[dict[str, Any]],
        sensor_data: list[dict[str, Any]],
        report_data: list[dict[str, Any]],
        mode: str = "merge",
    ) -> dict[str, int]:
        """
        Save all MPM entities to Snowflake in one operation.

        Args:
            deployment_data: Deployment configuration
            communities_data: Communities list
            sensor_data: Sensor actions
            report_data: Report actions
            mode: Write mode for all tables

        Returns:
            Dictionary with counts of records saved
        """
        self.save_deployment(deployment_data, mode=mode)
        self.save_communities(communities_data, mode=mode)
        self.save_sensor_actions(sensor_data, mode=mode)
        self.save_report_actions(report_data, mode=mode)

        return {
            "deployments": 1,
            "communities": len(communities_data),
            "sensor_actions": len(sensor_data),
            "report_actions": len(report_data),
        }

    def read_deployment(self, deployment_version: str) -> DataFrame | None:
        """
        Read deployment configuration from Snowflake.

        Args:
            deployment_version: Deployment version to retrieve

        Returns:
            DataFrame with deployment data or None if not found
        """
        table_name = self._get_full_table_name("deployment")
        try:
            df = self.session.table(table_name).filter(f"deployment_version = '{deployment_version}'")
            return df if df.count() > 0 else None
        except Exception:
            return None

    def read_communities(self, deployment_version: str) -> DataFrame | None:
        """
        Read communities for a deployment from Snowflake.

        Args:
            deployment_version: Deployment version to retrieve

        Returns:
            DataFrame with communities or None if not found
        """
        table_name = self._get_full_table_name("retail_property")
        try:
            df = self.session.table(table_name).filter(f"deployment_version = '{deployment_version}'")
            return df if df.count() > 0 else None
        except Exception:
            return None

    def read_sensor_actions(self, deployment_version: str) -> DataFrame | None:
        """
        Read sensor actions for a deployment from Snowflake.

        Args:
            deployment_version: Deployment version to retrieve

        Returns:
            DataFrame with sensor actions or None if not found
        """
        table_name = self._get_full_table_name("sensor")
        try:
            df = self.session.table(table_name).filter(f"deployment_version = '{deployment_version}'")
            return df if df.count() > 0 else None
        except Exception:
            return None

    def read_report_actions(self, deployment_version: str) -> DataFrame | None:
        """
        Read report actions for a deployment from Snowflake.

        Args:
            deployment_version: Deployment version to retrieve

        Returns:
            DataFrame with report actions or None if not found
        """
        table_name = self._get_full_table_name("report")
        try:
            df = self.session.table(table_name).filter(f"deployment_version = '{deployment_version}'")
            return df if df.count() > 0 else None
        except Exception:
            return None
