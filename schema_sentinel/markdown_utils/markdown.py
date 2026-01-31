import getpass
import logging as log
import os

from snakemd import Document
import datetime
import pandas as pd

from sqlalchemy.sql.elements import and_

from ..metadata_manager.model.column import Column
from ..metadata_manager.model.comparison import Comparison
from ..metadata_manager.model.database import Database
from ..metadata_manager.model.function import Function
from ..metadata_manager.model.pipe import Pipe
from ..metadata_manager.model.procedure import Procedure
from ..metadata_manager.model.schema import Schema
from ..metadata_manager.model.stage import Stage
from ..metadata_manager.model.stream import Stream
from ..metadata_manager.model.table import Table
from ..metadata_manager.model.table_constraint import TableConstraint
from ..metadata_manager.model.task import Task
from ..metadata_manager.model.view import View


def comparison_to_markdown(src_database: Database,
                           trg_database: Database,
                           session) -> Document:
    header_level = 1
    header = f"{src_database.__get_name__()} -> {trg_database.__get_name__()})"
    log.info(f"Writing {header} comparison report to Markdown")
    doc: Document = Document()

    # Get author from environment or use system username
    author = os.getenv("REPORT_AUTHOR", getpass.getuser())

    doc.add_raw(f"""
    ---
    author: {author}
    date:   {datetime.datetime.now().strftime('%a %m %y')}
    """)

    doc.add_heading(f"{header} comparison report")
    doc.add_horizontal_rule()
    doc.add_heading("Compared databases", level=header_level)
    doc.add_block(src_database.__side_by_side__(trg_database).to_markdown())
    header_level += 1

    doc.add_heading("DB Objects existing in the LEFT database and not present in the RIGHT database", level=header_level)
    comparisons = session.query(Comparison).filter(
        and_(Comparison.source_database_id == src_database.database_id,
             Comparison.target_database_id == trg_database.database_id,
             Comparison.comparison_value.like('%"comparison": {"left": "%", "right": null}%'))).all()
    differences = None

    for comparison in comparisons:
        differences = pd.concat([differences, comparison.one_diff()]) if differences is not None else comparison.one_diff()

    doc.add_block(differences.to_markdown())
    differences = None

    doc.add_heading("Both sides are different", level=header_level)

    comparisons = session.query(Comparison).filter(
        and_(Comparison.source_database_id == src_database.database_id,
             Comparison.target_database_id == trg_database.database_id,
             Comparison.comparison_value.not_like('%"comparison": {"left": "%", "right": null}%'))).all()

    for comparison in comparisons:
        differences = pd.concat([differences, comparison.both_diffs()]) if differences is not None else comparison.both_diffs()

    doc.add_block(differences.to_markdown())




    return doc


def db_to_markdown(database: Database,
                   session) -> Document:
    header = f"{database.__get_name__()}"
    log.info(f"Writing {header} database to Markdown")
    doc: Document = Document()

    # Get author from environment or use system username
    author = os.getenv(\"REPORT_AUTHOR\", getpass.getuser())

    doc.add_raw(f\"\"\"
    ---
    author: {author}
    date:   {datetime.datetime.now().strftime('%a %m %y')}
    """)

    doc.add_heading(f"{header} database documentation")
    doc.add_horizontal_rule()
    doc.add_block(database.__get_df__().to_markdown())

    schemas = session.query(Schema).filter(
        and_(Schema.database_id == database.database_id)).all()
    header_level = 1
    doc.add_heading(f"{database.database_name} schemas", level=header_level)
    doc.add_block(
        Schema.__to_df__(schemas, columns=["schema_name", "created", "last_altered", "comment"]).to_markdown())

    header_level = 2
    for schema in schemas:
        schema_md = schema.schema_name.replace("_", "\\_")
        doc.add_heading(f"Schema: {schema.schema_name}", level=header_level)
        doc.add_block(schema.__get_df__().to_markdown())

        tables = session.query(Table).filter(Table.schema_id == schema.schema_id).all()
        if tables is not None:
            header_level += 1
            df = Table.__to_df__(
                tables,
                ["table_name", "created", "last_altered", "comment"])
            if df.size:
                doc.add_heading(f"{schema_md} Tables", level=header_level)
                doc.add_block(df.to_markdown())
            header_level -= 1

            header_level += 1
            for table in tables:
                table_md = table.table_name.replace("_", "\\_")
                doc.add_heading(f"Table  {schema.schema_name}.{table_md} ", level=header_level)
                doc.add_block(table.__get_df__().to_markdown())

                get_object_doc(
                    data=session.query(Column).filter(Column.table_id == table.table_id).all(),
                    klass=Column,
                    columns=["column_name", "ordinal_position", "is_nullable", "character_maximum_length",
                             "numeric_precision", "numeric_scale", "datetime_precision"],
                    header=f"Table {schema.schema_name}.{table_md} columns",
                    doc=doc,
                    header_level=header_level
                )

                get_object_doc(
                    data=session.query(TableConstraint).filter(TableConstraint.table_id == table.table_id).all(),
                    klass=TableConstraint,
                    columns=["table_constraint_name", "constraint_type", "is_deferrable", "created", "last_altered"],
                    header=f"Table {schema.schema_name}.{table_md} constraints",
                    doc=doc,
                    header_level=header_level)

            header_level -= 1

        get_object_doc(
            data=session.query(View).filter(View.schema_id == schema.schema_id).all(),
            klass=View,
            columns=["view_name", "created", "is_secure", "is_materialized", "enable_schema_evolution", "comment"],
            header=f"{schema_md} Views",
            doc=doc,
            header_level=header_level)

        get_object_doc(
            data=session.query(Procedure).filter(Procedure.schema_id == schema.schema_id).all(),
            klass=Procedure,
            columns=["procedure_name", "data_type", "argument_signature", "created", "last_altered", "comment"],
            header=f"{schema_md} Procedures",
            doc=doc,
            header_level=header_level
        )

        get_object_doc(
            data=session.query(Function).filter(Function.schema_id == schema.schema_id).all(),
            klass=Function,
            columns=["function_name", "data_type", "argument_signature", "created", "last_altered", "comment"],
            header=f"{schema_md} Functions",
            doc=doc,
            header_level=header_level
        )

        get_object_doc(
            data=session.query(Stage).filter(Stage.schema_id == schema.schema_id).all(),
            klass=Stage,
            columns=["stage_name", "stage_url", "stage_type", "storage_integration", "created", "comment"],
            header=f"{schema_md} Stages",
            doc=doc,
            header_level=header_level
        )

        get_object_doc(
            data=session.query(Pipe).filter(Pipe.schema_id == schema.schema_id).all(),
            klass=Pipe,
            columns=["pipe_name", "pipe_definition", "notification_channel_name", "pattern", "created", "last_altered"],
            header=f"{schema_md} Pipes",
            doc=doc,
            header_level=header_level
        )

        get_object_doc(
            data=session.query(Stream).filter(Stream.schema_id == schema.schema_id).all(),
            klass=Stream,
            columns=["stream_name", "table_name", "source_type", "base_tables", "type", "stale", "invalid_reason", "created", "comment"],
            header=f"{schema_md} Streams",
            doc=doc,
            header_level=header_level
        )

        get_object_doc(
            data=session.query(Task).filter(Task.schema_id == schema.schema_id).all(),
            klass=Stream,
            columns=["id", "task_name", "warehouse", "schedule", "state", "condition", "error_integration",
                     "config", "last_committed", "last_suspended", "created", "comment"],
            header=f"{schema_md} Streams",
            doc=doc,
            header_level=header_level
        )

    return doc


def get_object_doc(data, klass, columns: list, header: str, doc: Document, header_level: int = 0):
    header_level += 1
    if data:
        doc.add_heading(header, level=header_level)
        df: pd.DataFrame = klass.__to_df__(data, columns)
        if df.size:
            doc.add_block(df.to_markdown())
    header_level -= 1
