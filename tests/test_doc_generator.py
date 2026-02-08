"""Tests for markdown document generator."""

import pytest

from yaml_shredder.doc_generator import MarkdownDocGenerator, generate_doc_from_yaml


@pytest.fixture
def sample_yaml_file(tmp_path):
    """Create a sample YAML file for testing."""
    yaml_content = """
deployment:
  code: TEST_001
  version: 1.0.0
communities:
  - id: 1
    name: Community_A
  - id: 2
    name: Community_B
actions:
  - action_type: REPORT
    action_code: test_report
    schedule: daily
  - action_type: SENSOR
    action_code: test_sensor
    schedule: hourly
"""
    yaml_file = tmp_path / "test_config.yaml"
    yaml_file.write_text(yaml_content)
    return yaml_file


@pytest.fixture
def sample_db(tmp_path, sample_yaml_file):
    """Create a sample SQLite database from YAML."""
    import yaml

    from yaml_shredder.data_loader import SQLiteLoader
    from yaml_shredder.table_generator import TableGenerator

    # Load YAML
    with open(sample_yaml_file) as f:
        data = yaml.safe_load(f)

    # Generate tables and load to DB
    table_gen = TableGenerator()
    tables = table_gen.generate_tables(data, root_table_name="TEST", source_file=sample_yaml_file)

    db_path = tmp_path / "test.db"
    loader = SQLiteLoader(db_path)
    loader.connect()
    loader.load_tables(tables, if_exists="replace", create_indexes=True)
    loader.disconnect()

    return db_path


def test_markdown_doc_generator_init(sample_db):
    """Test MarkdownDocGenerator initialization."""
    doc_gen = MarkdownDocGenerator(sample_db)
    assert doc_gen.db_path == sample_db
    assert doc_gen.connection is None


def test_markdown_doc_generator_init_nonexistent_db(tmp_path):
    """Test MarkdownDocGenerator with nonexistent database."""
    with pytest.raises(FileNotFoundError):
        MarkdownDocGenerator(tmp_path / "nonexistent.db")


def test_markdown_doc_generator_connect(sample_db):
    """Test database connection."""
    doc_gen = MarkdownDocGenerator(sample_db)
    doc_gen.connect()
    assert doc_gen.connection is not None
    doc_gen.disconnect()
    assert doc_gen.connection is None


def test_get_tables(sample_db):
    """Test retrieving list of tables."""
    doc_gen = MarkdownDocGenerator(sample_db)
    doc_gen.connect()
    tables = doc_gen.get_tables()
    doc_gen.disconnect()

    assert len(tables) > 0
    assert isinstance(tables, list)
    assert all(isinstance(t, str) for t in tables)


def test_get_table_data(sample_db):
    """Test retrieving table data."""
    doc_gen = MarkdownDocGenerator(sample_db)
    doc_gen.connect()

    tables = doc_gen.get_tables()
    if tables:
        df = doc_gen.get_table_data(tables[0])
        assert not df.empty or len(df.columns) > 0

    doc_gen.disconnect()


def test_get_table_schema(sample_db):
    """Test retrieving table schema."""
    doc_gen = MarkdownDocGenerator(sample_db)
    doc_gen.connect()

    tables = doc_gen.get_tables()
    if tables:
        schema = doc_gen.get_table_schema(tables[0])
        assert isinstance(schema, list)
        assert all(isinstance(col, tuple) and len(col) == 2 for col in schema)

    doc_gen.disconnect()


def test_generate_markdown(sample_db, tmp_path):
    """Test markdown generation."""
    doc_gen = MarkdownDocGenerator(sample_db)
    output_path = tmp_path / "output.md"

    markdown = doc_gen.generate_markdown(output_path=output_path)

    # Check markdown content
    assert "# Database Documentation:" in markdown or "# test" in markdown.lower()
    assert "## Table of Contents" in markdown
    assert "### Schema" in markdown
    assert "### Data" in markdown

    # Check file was created
    assert output_path.exists()
    content = output_path.read_text()
    assert content == markdown


def test_generate_markdown_with_custom_name(sample_db):
    """Test markdown generation with custom document name."""
    doc_gen = MarkdownDocGenerator(sample_db)

    markdown = doc_gen.generate_markdown(doc_name="Custom Test Document")

    assert "# Custom Test Document" in markdown


def test_dataframe_to_markdown(sample_db):
    """Test DataFrame to markdown table conversion."""
    import pandas as pd

    doc_gen = MarkdownDocGenerator(sample_db)

    df = pd.DataFrame({"col1": [1, 2, 3], "col2": ["a", "b", "c"]})

    markdown_table = doc_gen._dataframe_to_markdown(df)

    assert "col1" in markdown_table
    assert "col2" in markdown_table
    assert "|" in markdown_table
    assert "---" in markdown_table


def test_dataframe_to_markdown_long_values(sample_db):
    """Test DataFrame to markdown with truncation."""
    import pandas as pd

    doc_gen = MarkdownDocGenerator(sample_db)

    long_value = "x" * 100
    df = pd.DataFrame({"col": [long_value]})

    markdown_table = doc_gen._dataframe_to_markdown(df, max_col_width=50)

    assert "..." in markdown_table


def test_generate_doc_from_yaml(sample_yaml_file, tmp_path):
    """Test convenience function for generating docs from YAML."""
    output_dir = tmp_path / "output"
    output_dir.mkdir()

    output_path = generate_doc_from_yaml(yaml_path=sample_yaml_file, output_dir=output_dir, keep_db=False)

    # Check output file
    assert output_path.exists()
    assert output_path.suffix == ".md"
    assert output_path.stem == sample_yaml_file.stem

    # Check database was removed
    db_path = output_dir / f"{sample_yaml_file.stem}.db"
    assert not db_path.exists()


def test_generate_doc_from_yaml_keep_db(sample_yaml_file, tmp_path):
    """Test convenience function keeping the database."""
    output_dir = tmp_path / "output"
    output_dir.mkdir()

    output_path = generate_doc_from_yaml(yaml_path=sample_yaml_file, output_dir=output_dir, keep_db=True)

    # Check both output file and database exist
    assert output_path.exists()

    db_path = output_dir / f"{sample_yaml_file.stem}.db"
    assert db_path.exists()


def test_generate_doc_from_yaml_with_max_depth(sample_yaml_file, tmp_path):
    """Test document generation with depth control."""
    output_dir = tmp_path / "output"
    output_dir.mkdir()

    output_path = generate_doc_from_yaml(yaml_path=sample_yaml_file, output_dir=output_dir, max_depth=1, keep_db=False)

    assert output_path.exists()
    content = output_path.read_text()
    assert len(content) > 0
