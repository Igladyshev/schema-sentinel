import json
import logging as log
import os

import pandas as pd
from sqlalchemy import and_
from sqlalchemy.orm import sessionmaker

from schema_sentinel.metadata_manager.model import compare_obj
from schema_sentinel.metadata_manager.model.column import Column
from schema_sentinel.metadata_manager.model.column_constraint import ColumnConstraint
from schema_sentinel.metadata_manager.model.constraint import Constraint
from schema_sentinel.metadata_manager.model.database import Database
from schema_sentinel.metadata_manager.model.function import Function
from schema_sentinel.metadata_manager.model.procedure import Procedure
from schema_sentinel.metadata_manager.model.schema import Schema
from schema_sentinel.metadata_manager.model.stream import Stream
from schema_sentinel.metadata_manager.model.table import Table
from schema_sentinel.metadata_manager.model.table_constraint import TableConstraint
from schema_sentinel.metadata_manager.model.task import Task
from schema_sentinel.metadata_manager.model.view import View

from .engine import SfAlchemyEngine, SqLiteAqlAlchemyEngine
from .enums import DbObjectType
from .model.metadata_container import MetaData
from .model.metadata_utils import (
    get_columns,
    get_constraints,
    get_database,
    get_functions,
    get_imported_keys,
    get_pipes,
    get_procedures,
    get_referential_constraints,
    get_schemas,
    get_stages,
    get_streams,
    get_table_constraints,
    get_tables,
    get_tasks,
    get_views,
)


def get_default_schemas() -> tuple:
    """
    Get schemas from environment variable or return empty tuple to include all schemas.
    Set SNOWFLAKE_SCHEMAS environment variable as comma-separated list.
    Example: SNOWFLAKE_SCHEMAS="PUBLIC,INFORMATION_SCHEMA,ANALYTICS"
    """
    schemas_env = os.getenv("SNOWFLAKE_SCHEMAS", "")
    if schemas_env:
        return tuple(s.strip() for s in schemas_env.split(",") if s.strip())
    return ()  # Empty tuple means all schemas


def init_comparison() -> {}:
    comparison = {}
    for value in DbObjectType.list():
        comparison[value] = {}
    return comparison


def get_db_objects(
    database_name: str,
    engine: SfAlchemyEngine,
    meta_engine: SqLiteAqlAlchemyEngine,
    schemas: tuple = None,
    version: str = "0.1.0",
    environment: str = "dev",
) -> MetaData:
    if schemas is None:
        schemas = get_default_schemas()
    session = sessionmaker(bind=meta_engine)()
    database_df = get_database(database_name=database_name, engine=engine)

    db = Database(
        version=version,
        environment=environment,
        database_name=database_name,
        database_owner=database_df.database_owner,
        is_transient=database_df.is_transient,
        comment=database_df.comment,
        created=db_timestamp_to_string(database_df.created),
        last_altered=db_timestamp_to_string(database_df.last_altered),
        retention_time=database_df.retention_time,
    )
    # TODO: add version increment
    db.database_id = db.__get_id__()
    db.save(session=session)
    log.info(f"Schemas to include are {schemas}")
    db_objects: MetaData = MetaData(
        database_object=db, schemas_to_include=schemas, db_timestamp_to_string=db_timestamp_to_string
    )

    db_objects.save_schemas(schemas_df=get_schemas(database=db, engine=engine), session=session)

    db_objects.constraints = get_constraints(database_name=database_name, engine=engine)
    db_objects.tables = get_tables(database_name=database_name, engine=engine)
    db_objects.columns = get_columns(database_name=database_name, engine=engine)
    db_objects.views = get_views(database_name=database_name, engine=engine)
    db_objects.procedures = get_procedures(database_name=database_name, engine=engine)
    db_objects.functions = get_functions(database_name=database_name, engine=engine)
    db_objects.streams = get_streams(database_name=database_name, engine=engine)
    db_objects.tasks = get_tasks(database_name=database_name, engine=engine)
    db_objects.pipes = get_pipes(database_name=database_name, engine=engine)
    db_objects.table_constraints = get_table_constraints(database_name=database_name, engine=engine)
    db_objects.referential_constraints = get_referential_constraints(database_name=database_name, engine=engine)

    db_objects.column_constraints = get_imported_keys(database_name=database_name, engine=engine)
    db_objects.stages = get_stages(database_name=database_name, engine=engine)

    db_objects.save(session=session)
    return db_objects


def db_timestamp_to_string(db_timestamp) -> str:
    if not db_timestamp:
        return ""
    return str(db_timestamp)


def save_metadata(
    engine: SfAlchemyEngine,
    environment: str,
    version: str,
    meta_engine: SqLiteAqlAlchemyEngine,
    database_name: str,
    schemas: tuple = None,
) -> MetaData:
    if schemas is None:
        schemas = get_default_schemas()
    metadata = get_db_objects(
        database_name=database_name,
        engine=engine,
        meta_engine=meta_engine,
        schemas=schemas,
        version=version,
        environment=environment,
    )
    return metadata


def compare_db_objects(
    source_db: MetaData,
    source_env: str,
    target_db: MetaData,
    target_env: str,
    engine: SqLiteAqlAlchemyEngine,
    schemas: list = None,
):
    if schemas is None:
        schemas = get_default_schemas()
    Session = sessionmaker(bind=engine)
    session = Session()
    database: Database = source_db.database_object
    database.database_id = f"{database.database_name} ({source_env} vs {target_env} comparison)"
    database.environment = f"{source_env}->{target_env}"
    database.version = "comparison"
    database.save(session)

    diffs: MetaData = MetaData(
        database_object=database, schemas_to_include=schemas, db_timetasmp_to_string=db_timestamp_to_string
    )

    diffs.tables = diff_df(source_db.tables, target_db.tables)
    diffs.columns = diff_df(source_db.columns, target_db.columns)
    diffs.views = diff_df(source_db.views, target_db.views)
    diffs.streams = diff_df(source_db.streams, target_db.streams)
    # diffs.pipes = diff_df(source_db.pipes, target_db.pipes)
    diffs.tasks = diff_df(source_db.tasks, target_db.tasks)
    diffs.procedures = diff_df(source_db.procedures, target_db.procedures)
    diffs.functions = diff_df(source_db.functions, target_db.functions)
    diffs.table_constraints = diff_df(source_db.table_constraints, target_db.table_constraints)
    diffs.referential_constraints = diff_df(source_db.referential_constraints, target_db.referential_constraints)
    diffs.stages = diff_df(source_db.stages, target_db.stages)
    diffs.column_constraints = diff_df(source_db.column_constraints, target_db.column_constraints)
    diffs.constraints = diff_df(source_db.constraints, target_db.constraints)

    diffs.save(session=session)
    log.info(
        f"Database {source_db.database_object.database_name} comparison report [{source_env}] to [{target_env}]:\n {diffs}"
    )
    return diffs


def diff_df(df1, df2, how="left"):
    """
    Find Difference of rows for given two dataframes
    this function is not symmetric, means
          diff(x, y) != diff(y, x)
    however
          diff(x, y, how='left') == diff(y, x, how='right')

    Ref: https://stackoverflow.com/questions/18180763/set-difference-for-pandas/40209800#40209800
    """
    if (df1.columns != df2.columns).any():
        raise ValueError("Two dataframe columns must match")

    if df1.equals(df2):
        names = list(df1.columns)
        return pd.DataFrame(columns=names)
    elif how == "right":
        return pd.concat([df2, df1, df1]).drop_duplicates(keep=False)
    elif how == "left":
        return pd.concat([df1, df2, df2]).drop_duplicates(keep=False)
    else:
        raise ValueError('how parameter supports only "left" or "right keywords"')


def compare(src_database: Database, trg_database: Database, session):
    comparison: {} = init_comparison()
    db_key = f"{src_database.database_name}"
    if src_database.environment != trg_database.environment and src_database.version == trg_database.version:
        db_key = f"{db_key}:{src_database.environment}->{trg_database.environment}"

    if src_database.version != trg_database.version and src_database.environment == trg_database.environment:
        db_key = f"{db_key}:{src_database.version}->{trg_database.version}"

    comparison[DbObjectType.DATABASE.value][db_key] = compare_obj(src_database, trg_database)

    src_schemas = session.query(Schema).filter(Schema.database_id == src_database.database_id).all()
    for src_schema in src_schemas:
        schema_key = f"{src_schema.schema_name} [{db_key}]"
        trg_schema = (
            session.query(Schema)
            .filter(and_(Schema.database_id == trg_database.database_id, Schema.schema_name == src_schema.schema_name))
            .first()
        )
        if trg_schema:
            comparison[DbObjectType.SCHEMA.value][schema_key] = compare_obj(src_schema, trg_schema)
        else:
            comparison[DbObjectType.SCHEMA.value][schema_key] = {"left": src_schema.__class__.__name__, "right": None}
            continue

        src_tables = session.query(Table).filter(Table.schema_id == src_schema.schema_id).all()
        for src_table in src_tables:
            table_key = f"{src_schema.schema_name}.{src_table.table_name} [{db_key}]"
            trg_table = (
                session.query(Table)
                .filter(and_(Table.schema_id == trg_schema.schema_id, Table.table_name == src_table.table_name))
                .first()
            )
            if trg_table:
                comp = compare_obj(src_table, trg_table)
                if comp:
                    comparison[DbObjectType.TABLE.value][table_key] = comp
            else:
                comparison[DbObjectType.TABLE.value][table_key] = {"left": src_table.__class__.__name__, "right": None}
                continue

            src_columns = session.query(Column).filter(Column.table_id == src_table.table_id).all()
            for src_column in src_columns:
                column_key = f"{src_schema.schema_name}.{src_table.table_name}.{src_column.column_name} [{db_key}]"
                trg_column = (
                    session.query(Column)
                    .filter(and_(Column.table_id == trg_table.table_id, Column.column_name == src_column.column_name))
                    .first()
                )
                if trg_column:
                    comparison[DbObjectType.COLUMN.value][column_key] = compare_obj(src_column, trg_column)
                else:
                    comparison[DbObjectType.COLUMN.value][column_key] = {
                        "left": src_column.__class__.__name__,
                        "right": None,
                    }
                    continue

                src_column_constraints = (
                    session.query(ColumnConstraint).filter(ColumnConstraint.pk_column_id == src_column.column_id).all()
                )
                for src_column_constraint in src_column_constraints:
                    id = json.loads(src_column_constraint.column_constraint_id)
                    id["pk_column_id"]["version"] = trg_database.version
                    id["fk_column_id"]["version"] = trg_database.version
                    id["pk_column_id"]["environment"] = trg_database.environment
                    id["fk_column_id"]["environment"] = trg_database.environment
                    trg_column_constraint_id = json.dumps(id)

                    constraint_name = src_column_constraint.fk_name
                    column_constraint_key = (
                        f"{src_schema.schema_name}.{src_table.table_name}.{src_column.column_name}"
                        f".{constraint_name} [{db_key}]"
                    )
                    trg_column_constraint = (
                        session.query(ColumnConstraint)
                        .filter(ColumnConstraint.column_constraint_id == trg_column_constraint_id)
                        .first()
                    )
                    if trg_column_constraint:
                        comparison[DbObjectType.COLUMN_CONSTRAINT.value][column_constraint_key] = compare_obj(
                            src_column_constraint, trg_column_constraint
                        )
                    else:
                        comparison[DbObjectType.COLUMN_CONSTRAINT.value][column_constraint_key] = {
                            "left": src_column_constraint.__class__.__name__,
                            "right": None,
                        }
                        continue

            src_table_constraints = (
                session.query(TableConstraint).filter(TableConstraint.table_id == src_table.table_id).all()
            )
            for src_table_constraint in src_table_constraints:
                table_constraint_key = (
                    f"{src_table_constraint.table_constraint_name}.{src_schema.schema_name}"
                    f".{src_table.table_name} [{db_key}]"
                )
                trg_table_constraint = (
                    session.query(TableConstraint)
                    .filter(
                        and_(
                            TableConstraint.table_id == trg_table.table_id,
                            TableConstraint.table_constraint_name == src_table_constraint.table_constraint_name,
                        )
                    )
                    .first()
                )
                if trg_table_constraint:
                    comparison[DbObjectType.TABLE_CONSTRAINT.value][table_constraint_key] = compare_obj(
                        src_table_constraint, trg_table_constraint
                    )
                else:
                    comparison[DbObjectType.TABLE_CONSTRAINT.value][table_constraint_key] = {
                        "left": src_table_constraint.__class__.__name__,
                        "right": None,
                    }
                    continue

            src_constraints = session.query(Constraint).filter(Constraint.table_id == src_table.table_id).all()
            for src_constraint in src_constraints:
                constraint_key = (
                    f"{src_schema.schema_name}.{src_table.table_name}.{src_constraint.constraint_name} [{db_key}]"
                )
                trg_constraint = (
                    session.query(Constraint)
                    .filter(
                        and_(
                            Constraint.table_id
                            == (
                                trg_table.table_id.replace(
                                    f'"version": {trg_database.version}', f'"version": {src_database.version}'
                                )
                            ).replace(
                                f'"environment": {trg_database.environment}',
                                f'"environment": {src_database.environment}',
                            ),
                            Constraint.constraint_name == src_constraint.constraint_name,
                        )
                    )
                    .first()
                )
                if trg_constraint:
                    comparison[DbObjectType.CONSTRAINT.value][constraint_key] = compare_obj(
                        src_constraint, trg_constraint
                    )
                else:
                    comparison[DbObjectType.CONSTRAINT.value][constraint_key] = {
                        "left": src_constraint.__class__.__name__,
                        "right": None,
                    }
                    continue

        src_views = session.query(View).filter(View.schema_id == src_schema.schema_id).all()
        for src_view in src_views:
            view_key = f"{src_schema.schema_name}.{src_view.view_name} [{db_key}]"
            trg_view = (
                session.query(View)
                .filter(and_(View.schema_id == trg_schema.schema_id, View.view_name == src_view.view_name))
                .first()
            )
            if trg_view:
                comparison[DbObjectType.VIEW.value][view_key] = compare_obj(src_view, trg_view)
            else:
                comparison[DbObjectType.VIEW.value][view_key] = {"left": src_view.__class__.__name__, "right": None}
                continue

        src_functions = session.query(Function).filter(Function.schema_id == src_schema.schema_id).all()
        for src_function in src_functions:
            function_key = f"{src_schema.schema_name}.{src_function.function_name} [{db_key}]"
            trg_function = (
                session.query(Function)
                .filter(
                    and_(
                        Function.schema_id == trg_schema.schema_id,
                        Function.function_name == src_function.function_name,
                        Function.argument_signature == src_function.argument_signature,
                    )
                )
                .first()
            )
            if trg_function:
                comparison[DbObjectType.FUNCTION.value][function_key] = compare_obj(src_function, trg_function)
            else:
                comparison[DbObjectType.FUNCTION.value][function_key] = {
                    "left": src_function.__class__.__name__,
                    "right": None,
                }
                continue

        src_procedures = session.query(Procedure).filter(Procedure.schema_id == src_schema.schema_id).all()
        for src_procedure in src_procedures:
            procedure_key = f"{src_schema.schema_name}.{src_procedure.procedure_name} [{db_key}]"
            trg_procedure = (
                session.query(Procedure)
                .filter(
                    and_(
                        Procedure.schema_id == trg_schema.schema_id,
                        Procedure.procedure_name == src_procedure.procedure_name,
                        Procedure.argument_signature == src_procedure.argument_signature,
                    )
                )
                .first()
            )
            if trg_procedure:
                comparison[DbObjectType.PROCEDURE.value][procedure_key] = compare_obj(src_procedure, trg_procedure)
            else:
                comparison[DbObjectType.PROCEDURE.value][procedure_key] = {
                    "left": src_procedure.__class__.__name__,
                    "right": None,
                }
                continue

        # src_stages = session.query(Stage).filter(Stage.schema_id == src_schema.schema_id).all()
        # for src_stage in src_stages:
        #     stage_key = f"{src_schema.schema_name}.{src_stage.stage_name} [{db_key}]"
        #     trg_stage = session.query(Stage).filter(and_(
        #         Stage.schema_id == trg_schema.schema_id,
        #         Stage.stage_name == src_stage.stage_name
        #     )).first()
        #     if trg_stage:
        #         comparison[DbObjectType.STAGE.value][stage_key] = compare_obj(src_stage, trg_stage)
        #     else:
        #         comparison[DbObjectType.STAGE.value][stage_key] = {"left": src_stage.__class__.__name__,
        #                                                            "right": None}
        #         continue

        src_streams = session.query(Stream).filter(Stream.schema_id == src_schema.schema_id).all()
        for src_stream in src_streams:
            stream_key = f"{schema_key}.{src_stream.stream_name}"
            trg_stream = (
                session.query(Stream)
                .filter(and_(Stream.schema_id == trg_schema.schema_id, Stream.stream_name == src_stream.stream_name))
                .first()
            )
            if trg_stream:
                comparison[DbObjectType.STREAM.value][stream_key] = compare_obj(src_stream, trg_stream)
            else:
                comparison[DbObjectType.STREAM.value][stream_key] = {
                    "left": src_stream.__class__.__name__,
                    "right": None,
                }
                continue

        # src_pipes = session.query(Pipe).filter(Pipe.schema_id == src_schema.schema_id).all()
        # for src_pipe in src_pipes:
        #     pipe_key = f"{src_schema.schema_name}.{src_pipe.pipe_name} [{db_key}]"
        #     trg_pipe = session.query(Pipe).filter(and_(
        #         Pipe.schema_id == trg_schema.schema_id,
        #         Pipe.pipe_name == src_pipe.pipe_name
        #     )).first()
        #     if trg_pipe:
        #         comparison[DbObjectType.PIPE.value][pipe_key] = compare_obj(src_pipe, trg_pipe)
        #     else:
        #         comparison[DbObjectType.PIPE.value][pipe_key] = {"left": src_pipe.__class__.__name__, "right": None}
        #         continue

        src_tasks = session.query(Task).filter(Task.schema_id == src_schema.schema_id).all()
        for src_task in src_tasks:
            task_key = f"{src_schema.schema_name}.{src_task.task_name} [{db_key}]"
            trg_task = (
                session.query(Task)
                .filter(and_(Task.schema_id == trg_schema.schema_id, Task.task_name == src_task.task_name))
                .first()
            )
            if trg_task:
                comparison[DbObjectType.TASK.value][task_key] = compare_obj(src_task, trg_task)
            else:
                comparison[DbObjectType.TASK.value][task_key] = {"left": src_task.__class__.__name__, "right": None}
                continue

    return comparison
