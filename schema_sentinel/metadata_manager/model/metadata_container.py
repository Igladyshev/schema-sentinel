import json
import logging as log

import pandas as pd
from typing import List, Dict

from . import CommonBase
from .constraint import Constraint
from .database import Database
from .schema import Schema
from .table import Table
from .view import View
from .column import Column
from .column_constraint import ColumnConstraint
from .function import Function
from .pipe import Pipe
from .procedure import Procedure
from .referential_constraint import ReferentialConstraint
from .stage import Stage
from .stream import Stream
from .table_constraint import TableConstraint
from .task import Task
from ..enums import DbObjectType


class MetaData:
    database_object: Database
    schemas: Dict[str, Schema] = []
    schemas_to_include: List[str]
    tables: pd.DataFrame = None
    columns: pd.DataFrame = None
    views: pd.DataFrame = None
    streams: pd.DataFrame = None
    pipes: pd.DataFrame = None
    tasks: pd.DataFrame = None
    procedures: pd.DataFrame = None
    functions: pd.DataFrame = None
    table_constraints: pd.DataFrame = None
    referential_constraints: pd.DataFrame = None
    constraints: pd.DataFrame = None
    stages: pd.DataFrame = None
    column_constraints: pd.DataFrame = None
    metadata: Dict[str, Dict[str, CommonBase]] = {}

    def __init__(self,
                 database_object: Database,
                 schemas_to_include: List[str],
                 db_timestamp_to_string):
        self.database_object = database_object
        self.metadata[DbObjectType.DATABASE] = {database_object.database_id: database_object}
        log.info(f"Metadata schemas to include are {schemas_to_include}")
        self.schemas_to_include = schemas_to_include
        self.db_timestamp_to_string = db_timestamp_to_string

    def save(self, session):
        log.info(f"Save tables")
        self.save_tables(session=session)
        log.info(f"Save columns")
        self.save_columns(session=session)
        log.info(f"Save constraints")
        self.save_constraints(session=session)
        log.info(f"Save column constraints")
        self.save_column_constraints(session=session)
        log.info(f"Save functions")
        self.save_functions(session=session)
        log.info(f"Save pipes")
        self.save_pipes(session=session)
        log.info(f"Save procedures")
        self.save_procedures(session=session)
        log.info(f"Save referential constraints")
        self.save_referential_constraints(session=session)
        log.info(f"Save stages")
        self.save_stages(session=session)
        log.info(f"Save streams")
        self.save_streams(session=session)
        log.info(f"Save table_constraints")
        self.save_table_constraints(session=session)
        log.info(f"Save tasks")
        self.save_tasks(session=session)
        log.info(f"Save views")
        self.save_views(session=session)

    def database_id(self) -> str:
        return self.database_object.__get_id__()

    def get_schema_id(self, schema_name: str) -> str:
        id = json.loads(self.database_id())
        id["schema_name"] = schema_name
        return json.dumps(id)

    def get_table_id(self, schema_name: str, table_name: str) -> str:
        id = json.loads(self.get_schema_id(schema_name))
        id["table_name"] = table_name
        return json.dumps(id)

    def get_constraint_id(self, schema_name: str, constraint_name: str) -> str:
        id = json.loads(self.get_schema_id(schema_name))
        id["constraint_name"] = constraint_name
        return json.dumps(id)

    def get_table_constraint_id(self, table_id:str, constraint_name: str) -> str:
        id = json.loads(table_id)
        id["constraint_name"] = constraint_name
        return json.dumps(id)

    def get_view_id(self, schema_name: str, view_name: str) -> str:
        id = json.loads(self.get_schema_id(schema_name))
        id["view_name"] = view_name
        return json.dumps(id)

    def get_task_id(self, schema_name: str, task_name: str) -> str:
        id = json.loads(self.get_schema_id(schema_name))
        id["task_name"] = task_name
        return json.dumps(id)

    def get_stream_id(self, schema_name: str, stream_name: str) -> str:
        id = json.loads(self.get_schema_id(schema_name))
        id["stream_name"] = stream_name
        return json.dumps(id)

    def get_pipe_id(self, schema_name: str, pipe_name: str) -> str:
        id = json.loads(self.get_schema_id(schema_name))
        id["pipe_name"] = pipe_name
        return json.dumps(id)

    def get_stage_id(self, schema_name: str, stage_name: str) -> str:
        id = json.loads(self.get_schema_id(schema_name))
        id["stage_name"] = stage_name
        return json.dumps(id)

    def get_column_id(self, schema_name: str, table_name: str, column_name: str) -> str:
        id = json.loads(self.get_table_id(schema_name, table_name))
        id["column_name"] = column_name
        return json.dumps(id)

    def get_procedure_id(self, schema_name: str, procedure_name: str, argument_signature: str) -> str:
        id = json.loads(self.get_schema_id(schema_name))
        id["procedure_name"] = procedure_name
        id["argument_signature"] = argument_signature
        return json.dumps(id)

    def get_function_id(self, schema_name: str, function_name: str, argument_signature: str) -> str:
        id = json.loads(self.get_schema_id(schema_name))
        id["function_name"] = function_name
        id["argument_signature"] = argument_signature
        return json.dumps(id)

    def save_tables(self, session) -> bool:
        self.metadata[DbObjectType.TABLE] = {}
        for index, df in self.tables.iterrows():
            table = Table(
                schema_id=self.get_schema_id(df['table_schema']),
                table_id=self.get_table_id(df['table_schema'], df['table_name']),
                table_name=df['table_name'],
                table_owner=df['table_owner'],
                table_type=df['table_type'],
                is_transient=df['is_transient'],
                clustering_key=df['clustering_key'],
                row_count=df['row_count'],
                comment=df['comment'],
                bytes=df['bytes'],
                retention_time=df['retention_time'],
                created=self.db_timestamp_to_string(df['created']),
                last_altered=self.db_timestamp_to_string(df['last_altered']),
                last_ddl=self.db_timestamp_to_string(df['last_ddl']),
                last_ddl_by=df['last_ddl_by'],
                auto_clustering_on=df['auto_clustering_on'],
                change_tracking='True',
                is_external='False',
                enable_schema_evolution='False',
                owner_role_type='DATABASE',
                is_event='False'
            )
            table.save(session=session)
            self.metadata[DbObjectType.TABLE][table.table_id] = table

        return True

    def save_column_constraints(self, session) -> bool:
        self.metadata[DbObjectType.COLUMN_CONSTRAINT] = {}
        for index, df in self.column_constraints.iterrows():

            column_constraint = ColumnConstraint(
                pk_column_id=self.get_column_id(df['pk_schema_name'], df['pk_table_name'], df['pk_column_name']),
                pk_constraint_id=self.get_constraint_id(df['pk_schema_name'], df["pk_name"]),
                fk_column_id=self.get_column_id(df['fk_schema_name'], df['fk_table_name'], df['fk_column_name']),
                fk_constraint_id=self.get_constraint_id(df['fk_schema_name'], df["fk_name"]),
                pk_name=df["pk_name"],
                fk_name=df["fk_name"],
                key_sequence=df['key_sequence'],
                comment=df['comment'],
                created=self.db_timestamp_to_string(df['created_on']),
                deferrability=df['deferrability'],
                rely=df['rely'],
                update_rule=df['update_rule'],
                delete_rule=df['delete_rule']
            )
            column_constraint.column_constraint_id = column_constraint.__get_id__()

            column_constraint.save(session=session)
            self.metadata[DbObjectType.COLUMN_CONSTRAINT][column_constraint.column_constraint_id] = column_constraint

        return True

    def save_referential_constraints(self, session) -> bool:
        self.metadata[DbObjectType.REFERENTIAL_CONSTRAINT] = {}
        for index, df in self.referential_constraints.iterrows():
            referential_constraint = ReferentialConstraint(
                foreign_key_constraint_id=self.get_constraint_id(df['constraint_schema'], df['constraint_name']),
                unique_constraint_id=self.get_constraint_id(df['unique_constraint_schema'], df['unique_constraint_name']),
                fk_name = df['constraint_name'],
                pk_name = df['unique_constraint_name'],
                match_option=df['match_option'],
                update_rule=df['update_rule'],
                delete_rule=df['delete_rule'],
                comment=df['comment'],
                created=self.db_timestamp_to_string(df['created']),
                last_altered=self.db_timestamp_to_string(df['last_altered'])
            )
            referential_constraint.referential_constraint_id = referential_constraint.__get_id__()
            referential_constraint.save(session=session)
            self.metadata[DbObjectType.REFERENTIAL_CONSTRAINT][referential_constraint.referential_constraint_id] = referential_constraint

        return True

    def save_table_constraints(self, session) -> bool:
        self.metadata[DbObjectType.TABLE_CONSTRAINT] = {}
        for index, df in self.table_constraints.iterrows():
            table_constraint = TableConstraint(
                table_id=self.get_table_id(df['table_schema'], df['table_name']),
                table_constraint_name=df['constraint_name'],
                constraint_type=df['constraint_type'],
                is_deferrable=df['is_deferrable'],
                initially_deferred=df['initially_deferred'],
                enforced=df['enforced'],
                comment=df['comment'],
                created=self.db_timestamp_to_string(df['created']),
                last_altered=self.db_timestamp_to_string(df['last_altered']),
                rely=df['rely']
            )
            table_constraint.table_constraint_id = table_constraint.__get_id__()
            table_constraint.save(session=session)
            self.metadata[DbObjectType.TABLE_CONSTRAINT][table_constraint.table_constraint_id] = table_constraint

        return True

    def save_constraints(self, session) -> bool:
        self.metadata[DbObjectType.CONSTRAINT] = {}
        for index, df in self.constraints.iterrows():
            constraint = Constraint(
                table_id=self.get_table_id(df['schema_name'], df['table_name']),
                constraint_name=df['constraint_name'],
                constraint_type=df['constraint_type'],
                constraint_details=df['constraint_details'],
                reference_key=df['reference_key'],
                created=self.db_timestamp_to_string(df['created']),
                update_rule=df['update_rule'],
                delete_rule=df['delete_rule']
            )
            constraint.constraint_id = constraint.__get_id__()
            constraint.save(session=session)
            self.metadata[DbObjectType.CONSTRAINT][constraint.constraint_id] = constraint

        return True

    def save_tasks(self, session) -> bool:
        self.metadata[DbObjectType.TASK] = {}
        for index, df in self.tasks.iterrows():
            try:
                task = Task(
                    id=str(df['id']),
                    task_id=self.get_task_id(df['schema_name'], df['name']),
                    schema_id=self.get_schema_id(df['schema_name']),
                    task_name=df['name'],
                    task_owner=df['owner'],
                    warehouse=df['warehouse'],
                    schedule=df['schedule'],
                    predecessors=df['predecessors'],
                    state=df['state'],
                    definition=df['definition'],
                    condition=df['condition'],
                    allow_overlapping_execution=df['allow_overlapping_execution'],
                    error_integration=df['error_integration'],
                    comment=df['comment'],
                    last_committed=self.db_timestamp_to_string(df['last_committed_on']),
                    last_suspended=self.db_timestamp_to_string(df['last_suspended_on']),
                    owner_role_type=df['owner_role_type'],
                    config=df['config'],
                    created=self.db_timestamp_to_string(df['created_on'])
                )

                task.save(session=session)
                self.metadata[DbObjectType.TASK][task.task_id] = task

            except Exception as e:
                log.error(f"Failed to save task: {task}, exception: {e}")
                import ipdb;
                ipdb.set_trace()

        return True

    def save_streams(self, session) -> bool:
        self.metadata[DbObjectType.STREAM] = {}
        failed_rows = []
        for index, df in self.streams.iterrows():
            try:
                stream = Stream(
                    schema_id=self.get_schema_id(df['schema_name']),
                    stream_id=self.get_stream_id(df['schema_name'], df['name']),
                    stream_name=df['name'],
                    stream_owner=df['owner'],
                    comment=df['comment'],
                    table_name=df['table_name'],
                    source_type=df['source_type'],
                    base_tables=df['base_tables'],
                    type=df['type'],
                    stale=df['stale'],
                    mode=df['mode'],
                    stale_after=self.db_timestamp_to_string(df['stale_after']),
                    invalid_reason=df['invalid_reason'],
                    owner_role_type=df['owner_role_type'],
                    created=self.db_timestamp_to_string(df['created_on'])
                )

                stream.save(session=session)
                self.metadata[DbObjectType.STREAM][stream.stream_id] = stream

            except Exception as e:
                log.error(f"Exception saving column:{stream}: {e}")
                failed_rows.append(stream.stream_id)
                import ipdb;
                ipdb.set_trace()

        return True

    def save_stages(self, session) -> bool:
        self.metadata[DbObjectType.STAGE] = {}
        for index, df in self.stages.iterrows():
            stage = Stage(
                schema_id=self.get_schema_id(df['schema_name']),
                stage_id=self.get_stage_id(df['schema_name'], df['name']),
                stage_name=df['name'],
                stage_owner=df['owner'],
                stage_url=df['url'],
                stage_region=df['region'],
                stage_type=df['type'],
                comment=df['comment'],
                created=self.db_timestamp_to_string(df['created_on']),
                has_credentials=df['has_credentials'],
                has_encryption_key=df['has_encryption_key'],
                cloud=df['cloud'],
                notification_channel=df['notification_channel'],
                storage_integration=df['storage_integration'],
            )

            stage.save(session=session)
            self.metadata[DbObjectType.STAGE][stage.stage_id] = stage

        return True

    def save_pipes(self, session) -> bool:
        self.metadata[DbObjectType.SCHEMA] = {}
        for index, df in self.pipes.iterrows():
            pipe = Pipe(
                schema_id=self.get_schema_id(df['pipe_schema']),
                pipe_id=self.get_pipe_id(df['pipe_schema'], df['pipe_name']),
                pipe_name=df['pipe_name'],
                pipe_owner=df['pipe_owner'],
                pipe_definition=df['definition'],
                is_autoingest_enabled=df['is_autoingest_enabled'],
                notification_channel_name=df['notification_channel_name'],
                comment=df['comment'],
                created=self.db_timestamp_to_string(df['created']),
                last_altered=self.db_timestamp_to_string(df['last_altered']),
                pattern=df['pattern']
            )

            pipe.save(session=session)
            self.metadata[DbObjectType.SCHEMA][pipe.pipe_id] = pipe

        return True

    def save_functions(self, session) -> bool:
        self.metadata[DbObjectType.FUNCTION] = {}
        for index, df in self.functions.iterrows():
            function = Function(
                schema_id=self.get_schema_id(df['function_schema']),
                function_id=self.get_function_id(df['function_schema'], df['function_name'],
                                                           df['argument_signature']),
                function_name=df['function_name'],
                function_owner=df['function_owner'],
                argument_signature=df['argument_signature'],
                data_type=df['data_type'],
                character_maximum_length=df['character_maximum_length'],
                character_octet_length=df['character_octet_length'],
                numeric_precision=df['numeric_precision'],
                numeric_precision_radix=df['numeric_precision_radix'],
                numeric_scale=df['numeric_scale'],
                function_language=df['function_language'],
                function_definition=df['function_definition'],
                volatility=df['volatility'],
                is_null_call=df['is_null_call'],
                is_secure=df['is_secure'],
                comment=df['comment'],
                created=self.db_timestamp_to_string(df['created']),
                last_altered=self.db_timestamp_to_string(df['last_altered']),
                is_external=df['is_external'],
                api_integration=df['api_integration'],
                context_headers=df['context_headers'],
                max_batch_rows=df['max_batch_rows'],
                compression=df['compression'],
                packages=df['packages'],
                runtime_version=df['runtime_version'],
                installed_packages=df['installed_packages'],
                is_memoizable=df['is_memoizable']
            )
            function.save(session=session)
            self.metadata[DbObjectType.FUNCTION][function.function_id] = function

        return True

    def save_procedures(self, session) -> bool:
        self.metadata[DbObjectType.PROCEDURE] = {}
        for index, df in self.procedures.iterrows():
            procedure = Procedure(
                procedure_id=self.get_procedure_id(df['procedure_schema'], df['procedure_name'], df['argument_signature']),
                schema_id=self.get_schema_id(df['procedure_schema']),
                procedure_name=df['procedure_name'],
                procedure_owner=df['procedure_owner'],
                argument_signature=df['argument_signature'],
                data_type=df['data_type'],
                character_maximum_length=df['character_maximum_length'],
                character_octet_length=df['character_octet_length'],
                numeric_precision=df['numeric_precision'],
                numeric_precision_radix=df['numeric_precision_radix'],
                numeric_scale=df['numeric_scale'],
                procedure_language=df['procedure_language'],
                procedure_definition=df['procedure_definition'],
                comment=df['comment'],
                created=self.db_timestamp_to_string(df['created']),
                last_altered=self.db_timestamp_to_string(df['last_altered'])
            )
            procedure.save(session=session)
            self.metadata[DbObjectType.PROCEDURE][procedure.procedure_id] = procedure

        return True

    def save_columns(self, session) -> bool:
        self.metadata[DbObjectType.COLUMN] = {}
        failed_rows = []
        saved_rows = []
        for index, df in self.columns.iterrows():

            column: Column = Column(
                column_id=self.get_column_id(df['table_schema'], df['table_name'], df['column_name']),
                table_id=self.get_table_id(df['table_schema'], df['table_name']),
                column_name=df['column_name'],
                ordinal_position=df['ordinal_position'],
                column_default=df['column_default'],
                is_nullable=df['is_nullable'],
                data_type=df['data_type'],
                character_maximum_length=df['character_maximum_length'],
                character_octet_length=df['character_octet_length'],
                numeric_precision=df['numeric_precision'],
                numeric_precision_radix=df['numeric_precision_radix'],
                numeric_scale=df['numeric_scale'],
                datetime_precision=df['datetime_precision'],
                is_identity=df['is_identity'],
                identity_generation=df['identity_generation'],
                identity_start=df['identity_start'],
                identity_increment=df['identity_increment'],
                comment=df['comment']
            )

            try:
                column.save(session=session)
                self.metadata[DbObjectType.COLUMN][column.column_id] = column
                saved_rows.append(column.column_id)
            except Exception:
                import ipdb; ipdb.set_trace()
                failed_rows.append(column.column_id)

        if len(failed_rows) > 0:
            for x in failed_rows:
                log.error(f"failed to save column: {x}")

        return True

    def save_views(self, session) -> bool:
        self.metadata[DbObjectType.VIEW] = {}
        for index, df in self.views.iterrows():
            view = View(
                schema_id=self.get_schema_id(df['schema_name']),
                view_id=self.get_view_id(df['schema_name'], df['name']),
                view_name=df['name'],
                view_owner=df['owner'],
                view_definition=df['text'],
                is_secure=df['is_secure'],
                is_materialized=df['is_materialized'],
                change_tracking=df['change_tracking'],
                created=self.db_timestamp_to_string(df['created_on']),
                owner_role_type=df['owner_role_type'],
                comment=df['comment']
            )
            view.save(session=session)
            self.metadata[DbObjectType.VIEW][view.view_id] = view
        return True


    def save_schemas(self, schemas_df: pd.DataFrame, session):
        self.metadata[DbObjectType.SCHEMA] = {}
        for index, schema in schemas_df.iterrows():
            schema_object = Schema(
                database_id=self.database_object.database_id,
                schema_id=self.get_schema_id(schema["schema_name"]),
                schema_name=schema["schema_name"],
                schema_owner=schema["schema_owner"],
                is_transient=schema["is_transient"],
                comment=schema["comment"],
                created=self.db_timestamp_to_string(schema["created"]),
                last_altered=self.db_timestamp_to_string(schema["last_altered"]),
                retention_time=schema["retention_time"]
            )
            schema_object.save(session=session)
            self.schemas.append(schema_object)
            self.metadata[DbObjectType.SCHEMA][schema_object.schema_id] = schema_object

