import pandas as pd
from sqlalchemy import text

from ..engine import DBEngineStrategy, SfAlchemyEngine
from .database import Database


def get_table_constraints_old(database: str, engine: SfAlchemyEngine) -> pd.DataFrame:
    statement = f"""select * from INFORMATION_SCHEMA.TABLE_CONSTRAINTS WHERE CONSTRAINT_CATALOG = '{database.replace('"', "")}'"""
    success, result = engine.execute(statement=statement, columns=["name"])
    return result


def get_schemas(database: Database, engine: SfAlchemyEngine) -> pd.DataFrame:
    database_name = database.database_name.replace('"', "")
    statement = f"""select * from INFORMATION_SCHEMA.SCHEMATA WHERE CATALOG_NAME = '{database_name.replace('"', "")}'"""
    success, result = engine.execute(statement=statement, columns=["name"])
    return result


def to_lower_case(string_array: list) -> list:
    return [x.lower() for x in string_array]


def get_imported_keys(database_name: str, engine: SfAlchemyEngine) -> pd.DataFrame:
    statement = f"show imported keys in database {database_name}"
    success, result = engine.execute(statement=statement, columns=["name"])
    return result


def get_stages(database_name: str, engine: SfAlchemyEngine) -> pd.DataFrame:
    statement = f"show stages in database {database_name}"
    success, result = engine.execute(statement=statement, columns=["name"])
    return result


def get_table_constraints(database_name: str, engine: SfAlchemyEngine) -> pd.DataFrame:
    statement = f"""
select * from INFORMATION_SCHEMA.table_constraints where constraint_catalog='{database_name.replace('"', "")}'
order by constraint_catalog, constraint_schema, table_name, constraint_type, constraint_name"""
    success, result = engine.execute(statement=statement, columns=["name"])
    return result


def get_referential_constraints(database_name: str, engine: SfAlchemyEngine) -> pd.DataFrame:
    statement = f"""
select * from INFORMATION_SCHEMA.referential_constraints where constraint_catalog='{database_name.replace('"', "")}'
order by constraint_schema, constraint_name;"""
    success, result = engine.execute(statement=statement, columns=["name"])
    result.columns = result.columns.str.lower()
    return result


def get_views(database_name: str, engine: DBEngineStrategy) -> pd.DataFrame:
    statement = f"show views in database {database_name}"
    success, result = engine.execute(statement=statement, columns=["name"])
    result = result[result["schema_name"] != "INFORMATION_SCHEMA"].copy()
    return result


def get_procedures(database_name: str, engine: SfAlchemyEngine) -> pd.DataFrame:
    success, result = engine.execute(statement=get_procedures_sql(database=database_name), columns=["name"])
    result.columns = result.columns.str.lower()
    return result


def get_functions(database_name: str, engine: SfAlchemyEngine) -> pd.DataFrame:
    success, result = engine.execute(statement=get_functions_sql(database=database_name), columns=["name"])
    result.columns = result.columns.str.lower()
    return result


def get_columns(database_name: str, engine: SfAlchemyEngine) -> pd.DataFrame:
    success, result = engine.execute(statement=get_columns_sql(database=database_name), columns=["name"])
    result.columns = result.columns.str.lower()
    return result


def get_tables(database_name: str, engine: SfAlchemyEngine) -> pd.DataFrame:
    success, result = engine.execute(statement=get_tables_sql(database=database_name), columns=["name"])
    result.columns = result.columns.str.lower()
    return result


def get_columns_sql(database):
    statement = f"""
        select
            *
        from information_schema.columns
        WHERE table_catalog='{database.replace('"', "")}'
        order by table_schema, table_name, ordinal_position;"""
    return statement


def get_tables_sql(database):
    database_name = database.replace('"', "")
    statement = f"""
        select
            table_catalog,
            table_schema,
            table_name,
            table_owner,
            table_type,
            is_transient,
            clustering_key,
            row_count,
            bytes,
            retention_time,
            created,
            last_altered,
            last_ddl,
            last_ddl_by,
            auto_clustering_on,
            comment
        from information_schema.tables
        where table_catalog = '{database_name}'
        and table_type = 'BASE TABLE'
        order by table_schema, table_name;"""
    return statement


def get_procedures_sql(database: str):
    database_name = database.replace('"', "")
    statement = f"""
            SELECT
                procedure_catalog,
                procedure_schema,
                procedure_name,
                procedure_owner,
                argument_signature,
                data_type,
                character_maximum_length,
                character_octet_length,
                numeric_precision,
                numeric_precision_radix,
                numeric_scale,
                procedure_language,
                procedure_definition,
                TO_VARCHAR(CREATED::TIMESTAMP_TZ, 'YYYY-MM-DD HH:mi:SS TZHTZM') AS created,
                TO_VARCHAR(LAST_ALTERED::TIMESTAMP_TZ, 'YYYY-MM-DD HH:mi:SS TZHTZM') AS last_altered,
                comment
            FROM INFORMATION_SCHEMA.PROCEDURES
            WHERE PROCEDURE_CATALOG = '{database_name.replace('"', "")}'
            ORDER BY PROCEDURE_SCHEMA, PROCEDURE_NAME"""
    return statement


def get_functions_sql(database):
    database_name = database.replace('"', "")
    statement = f"""
            select
                function_schema,
                function_name,
                function_owner,
                argument_signature,
                data_type,
                character_maximum_length,
                character_octet_length,
                numeric_precision,
                numeric_precision_radix,
                numeric_scale,
                function_language,
                function_definition,
                volatility,
                is_null_call,
                is_secure,
                to_varchar(created::timestamp_tz, 'yyyy-mm-dd hh:mi:ss tzhtzm') as created,
                to_varchar(last_altered::timestamp_tz, 'yyyy-mm-dd hh:mi:ss tzhtzm') as last_altered,
                comment,
                is_external,
                api_integration,
                context_headers,
                max_batch_rows,
                request_translator,
                response_translator,
                compression,
                packages,
                imports,
                handler,
                target_path,
                runtime_version,
                installed_packages,
                is_memoizable
            from information_schema.functions
            where function_catalog = '{database_name.replace('"', "")}'
            ORDER BY FUNCTION_SCHEMA, FUNCTION_NAME"""
    return statement


def get_tasks(database_name: str, engine: SfAlchemyEngine) -> pd.DataFrame:
    success, tasks = engine.execute(statement=f"""show tasks in database {database_name};""", columns=["name"])
    return tasks


def get_pipes(database_name: str, engine: SfAlchemyEngine) -> pd.DataFrame:
    statement = f"""
    select
        pipe_catalog,
        pipe_schema,
        pipe_name,
        pipe_owner,
        definition,
        is_autoingest_enabled,
        notification_channel_name,
        created,
        last_altered,
        comment,
        pattern
    from INFORMATION_SCHEMA.PIPES
    WHERE PIPE_CATALOG = '{database_name.replace('"', "")}'"""
    success, pipes = engine.execute(statement=statement, columns=["name"])
    return pipes


def get_streams(database_name: str, engine: SfAlchemyEngine) -> pd.DataFrame:
    success, streams = engine.execute(statement=f"show streams in database {database_name};", columns=["name"])
    return streams


def get_database(database_name: str, engine: SfAlchemyEngine) -> pd.DataFrame:
    statement = f"""
select database_owner, is_transient, comment, created, ifnull(last_altered, created) as last_altered,
    to_varchar(retention_time) as "retention_time"
from INFORMATION_SCHEMA.databases WHERE DATABASE_NAME='{database_name.replace('"', "")}'"""
    success, database_df = engine.execute(statement=statement, columns=["name"])
    return database_df.iloc[0]


GET_CONSTRAINTS_SQL = """
select
    'PRIMARY KEY' as "constraint_type",
    "database_name",
    "schema_name",
    "table_name",
    "constraint_name",
    listagg("column_name", ', ') within group(order by "key_sequence") as "constraint_details",
    NULL AS "reference_key",
    Null as "update_rule",
    Null as "delete_rule",
    max("created_on") as "created"
from primary_keys
group by "database_name",
    "schema_name",
    "table_name",
    "constraint_name"

union all

select
    'UNIQUE KEY' as "constraint_type",
    "database_name",
    "schema_name",
    "table_name",
    "constraint_name",
    listagg("column_name", ', ') within group(order by "key_sequence") as "constraint_details",
    NULL AS "reference_key",
    Null as "update_rule",
    Null as "delete_rule",
    max("created_on") as "created"
from unique_keys
group by "database_name",
    "schema_name",
    "table_name",
    "constraint_name"

union all

select
    *
from default_constraints

union all

select
    'FOREIGN KEY' as "constraint_type",
    "fk_database_name",
    "fk_schema_name",
    "fk_table_name",
    "fk_name",
    listagg("fk_column_name", ', ') within group(order by "key_sequence") as "constraint_details",
    concat("pk_database_name", '.', "pk_schema_name", '.', "pk_name") as "reference_key",
    max("update_rule") as "update_rule",
    max("delete_rule") as "delete_rule",
    max("created_on") as "created"
from imported_keys ik
group by "fk_database_name",
    "fk_schema_name",
    "fk_table_name",
    "fk_name",
    "pk_database_name",
    "pk_schema_name",
    "pk_name";
"""


def get_constraints(database_name: str, engine: SfAlchemyEngine) -> pd.DataFrame:
    conn = engine.get_conn()
    statement = f"show imported keys in database {database_name};"
    conn.execute(text(statement))
    statement = """create or replace temporary table imported_keys as
select * from table(result_scan(last_query_id()));"""
    conn.execute(text(statement))
    statement = f"show primary keys in database {database_name};"
    conn.execute(text(statement))
    statement = """create or replace temporary table primary_keys as
select * from table(result_scan(last_query_id()));"""
    conn.execute(text(statement))
    statement = f"show unique keys in database {database_name};"
    conn.execute(text(statement))
    statement = """create or replace temporary table unique_keys as
select * from table(result_scan(last_query_id()));"""
    conn.execute(text(statement))
    statement = f"""
create or replace temporary table default_constraints as
select
    'DEFAULT CONSTRAINT' as constraint_type,
    table_catalog,
    table_schema,
    table_name as tn,
    'DF_' || column_name as constraint_name,
    column_default as constraint_details,
    NULL as reference_key,
    Null as "update_rule",
    Null as "delete_rule",
    NULL as created
from information_schema.columns
where column_default is not null
and table_catalog = '{database_name}'"""
    conn.execute(text(statement))
    df = pd.read_sql(text(GET_CONSTRAINTS_SQL.replace("$DB_NAME", database_name)), conn)
    return df
