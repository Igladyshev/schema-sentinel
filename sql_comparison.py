import os
import typer
import logging as log
import pandas as pd

from sql_comparison import RESOURCES_PATH, get_engine, get_metadata_engine, validate, load_comparator, get_user, load_db
from sql_comparison.markdown_utils.markdown import comparison_to_markdown, db_to_markdown
from sql_comparison.metadata_manager.model.comparison import Comparison
from sql_comparison.metadata_manager.metadata import save_metadata, db_timestamp_to_string, compare
from sql_comparison.metadata_manager.model import Base

from sql_comparison.metadata_manager.engine import SqLiteAqlAlchemyEngine, get_config_dict, SfAlchemyEngine

app = typer.Typer()


@app.command()
def init_metadata(metadata_db: str = "metadata.db"):
    """
    Initializes an SqLite database to keep metadata
    :param metadata_db: a string with name of SqlLite database name
    :return: None
    """
    engine = get_metadata_engine(metadata_db=metadata_db)
    engine.connect()
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

@app.command()
def db_doc (env: str,
            version: str,
            database_name: str = "MY_DATABASE",
            metadata_db: str = "metadata.db"):

    database, session = load_db(database_name=database_name, environment=env, version=version, metadata_db=metadata_db)
    document = db_to_markdown(database=database, session=session)
    document.dump(f"{database.__name__()}", RESOURCES_PATH)


@app.command()
def comparison_report (source_env: str,
                target_env: str,
                database_name: str = "MY_DATABASE",
                metadata_db: str = "metadata.db",
                src_version: str = "0.1.0",
                trg_version: str = "0.1.0"):

    one, two, session = load_comparator(source_env, target_env, database_name, metadata_db, src_version, trg_version)
    document = comparison_to_markdown(one, two, session)
    document.dump(f"{one.__name__()} -> {two.__name__()}", RESOURCES_PATH)


@app.command()
def sql_compare(source_env: str,
                target_env: str,
                database_name: str = "MY_DATABASE",
                metadata_db: str = "metadata.db",
                src_version: str = "0.1.0",
                trg_version: str = "0.1.0"):
    """
    Compares two databases metadata previously loaded into metadata store. Generates the Markdown document

    NOTE: You could try to compare two arbitrary databases and still get comparison report,
          but it would be massive and making no sense.
    USE CASES:
        Within CI/CD pipeline
        1. Load the database metadata before change and tag it with {BEFORE_VERSION}
        2. Apply schema changes using DB Migrator
        3. Load the database metadata and tag it with {AFTER_VERSION}
        4. Generate comparison report
        5. Pause pipeline and wait for user input whether to continue the CI/CD job or abort it, according to user's input
        6. When abort was the choice, execute rollback script (this functionality needs to be implemented in DB Migrator)

    The comparison uses pandas.diff_df([left, right], 'left') method and produces
    :param source_env: a string: dev, staging, prod. Required
    :param target_env: a string: dev, staging, prod. Required
    :param database_name: the database alias/name
    :param src_version:
    :param trg_version:
    :param metadata_db: the name of the SqLite metadata database
    """
    one, two, session = load_comparator(source_env, target_env, database_name, metadata_db, src_version, trg_version)

    left: {} = compare(one, two, session)

    Comparison.save_comparison(comparison_dict=left,
                    src_database_id=one.database_id,
                    trg_database_id=two.database_id,
                    session=session,
                    db_timestamp_to_string=db_timestamp_to_string,
                    user=get_user())

    document = comparison_to_markdown(one, two, session)
    document.dump(f"{one.__get_name__()} -> {two.__get_name__()})", RESOURCES_PATH)

    right: {} = compare(two, one, session)
    Comparison.save_comparison(comparison_dict=right,
                    src_database_id=two.database_id,
                    trg_database_id=one.database_id,
                    session=session,
                    db_timestamp_to_string=db_timestamp_to_string,
                    user=get_user())

    document = comparison_to_markdown(two, one, session)
    document.dump(f"{two.__get_name__()} -> {one.__get_name__()})", RESOURCES_PATH)


@app.command()
def load_metadata(
        environment: str,
        version: str = "0.1.0",
        database_name: str = "MY_DATABASE",
        metadata_db: str = "metadata.db"):

    (engine, schemas, database_name) = get_engine(
        env=environment, resources_path=RESOURCES_PATH, alias=database_name
    )
    if environment == "local":
        environment = engine.env

    metadata_engine: SqLiteAqlAlchemyEngine = get_metadata_engine(metadata_db=metadata_db)

    save_metadata(
         engine=engine,
         environment=environment,
         database_name=database_name,
         schemas=schemas,
         meta_engine=metadata_engine,
         version=version)


if __name__ == "__main__":
    app()

