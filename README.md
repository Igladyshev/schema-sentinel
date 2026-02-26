# Schema Sentinel

[![CI](https://github.com/Igladyshev/schema-sentinel/actions/workflows/ci.yml/badge.svg)](https://github.com/Igladyshev/schema-sentinel/actions/workflows/ci.yml)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python Version](https://img.shields.io/badge/python-3.13%2B-blue)](https://www.python.org/downloads/)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)

A comprehensive data processing and schema management toolkit for data engineers and analysts. Schema Sentinel provides powerful tools for transforming nested YAML/JSON data into relational structures, generating dynamic schemas, comparing data, and tracking database schema changes.

Perfect for **data engineers**, **analytics teams**, and **DBAs** working with complex configuration files, API responses, nested data structures, or needing to track schema changes across environments.

## 🎯 Key Features

### YAML Shredder - Transform Nested Data
- **🔄 Automatic Schema Generation** - Dynamically infer JSON Schema from YAML/JSON files with auto-detection of types and patterns
- **📊 Relational Table Conversion** - Convert deeply nested YAML/JSON into normalized relational tables with automatic relationship mapping
- **🗄️ Multi-Database DDL Generation** - Generate SQL DDL for Snowflake, PostgreSQL, MySQL, and SQLite
- **⚡ Data Loading** - Load transformed data directly into SQLite databases with automatic indexing
- **🔍 Structure Analysis** - Analyze and identify nested structures, arrays, and potential table candidates
- **📄 Markdown Documentation** - Generate comprehensive markdown documentation from YAML files with table schemas and data
- **🔃 YAML Comparison** - Compare two YAML files with schema comparison and row-level data diff
- **🔑 Primary Key Detection** - Auto-detect primary keys (id, code, name columns) for intelligent data matching
- **💻 CLI & Python API** - Command-line interface and Python API for seamless integration

### Schema Comparison (Bonus)
- **📋 Metadata Extraction** - Extract complete schema information from Snowflake databases
- **💾 Version Control** - Store metadata snapshots in SQLite for historical tracking
- **🔎 Environment Comparison** - Compare schemas between dev, staging, and production
- **📝 Multiple Report Formats** - Generate comparison reports in Markdown, HTML, and JSON
- **🔒 Secure** - Best practices for credential management and data security

## 🎓 Use Cases

### YAML Shredder Use Cases
- **Configuration Management** - Transform YAML configs into queryable database tables
- **API Response Processing** - Convert nested JSON API responses into relational format
- **Data Pipeline Transformation** - Normalize complex nested data for analytics
- **Schema Discovery** - Automatically infer schemas from example data
- **Multi-Source Integration** - Combine data from different YAML/JSON sources
- **Data Versioning** - Track changes in configuration files over time
- **Configuration Drift Detection** - Compare YAML configs across environments to identify differences

### Schema Comparison Use Cases
- **Environment Synchronization** - Ensure dev, staging, and production schemas are aligned
- **Change Tracking** - Monitor database schema evolution over time
- **Deployment Validation** - Verify schema changes after deployments
- **Compliance & Auditing** - Maintain schema change history for compliance
- **Migration Planning** - Identify schema differences before migrations

## 📋 Requirements

- Python 3.13 or higher
- [uv](https://github.com/astral-sh/uv) - Modern Python package manager
- Snowflake account (optional, only for schema comparison features)

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/Igladyshev/schema-sentinel.git
cd schema-sentinel

# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh  # Linux/macOS
# or
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"  # Windows

# Set up environment and install dependencies
./setup.sh

# Or manually:
uv venv
source .venv/bin/activate  # Linux/macOS or .venv\Scripts\activate on Windows
uv pip install -e ".[dev,jupyter]"
```

### Quick Start - YAML Processing

#### Command Line Interface

Schema Sentinel provides organized command groups for different tasks:

**YAML Processing Commands** (`schema-sentinel yaml`)
```bash
# Analyze YAML structure
uv run schema-sentinel yaml analyze config.yaml

# Generate JSON schema
uv run schema-sentinel yaml schema config.yaml -o schema.json

# Generate relational tables
uv run schema-sentinel yaml tables config.yaml -o output/ -f csv

# Generate SQL DDL
uv run schema-sentinel yaml ddl config.yaml -o schema.sql -d snowflake

# Load data into SQLite
uv run schema-sentinel yaml load config.yaml -db output.db -r CONFIG

# Complete workflow: analyze → tables → DDL → load
uv run schema-sentinel yaml shred config.yaml -db output.db -r CONFIG

# Generate markdown documentation
uv run schema-sentinel yaml doc config.yaml -o docs/

# Compare two YAML files (schema only)
uv run schema-sentinel yaml compare file1.yaml file2.yaml -o comparison.md

# Compare with row-level data diff (auto primary key detection)
uv run schema-sentinel yaml compare file1.yaml file2.yaml --data -o comparison.md
```

**Schema Management Commands** (`schema-sentinel schema`)
```bash
# Extract Snowflake schema metadata
uv run schema-sentinel schema extract MY_DATABASE --env prod

# Compare two schema snapshots
uv run schema-sentinel schema compare snapshot1 snapshot2 -o report.md
```

#### Python API
```python
from yaml_shredder import TableGenerator, DDLGenerator, SQLiteLoader
from yaml_shredder.doc_generator import generate_doc_from_yaml
from pathlib import Path

# Load and convert YAML to tables
table_gen = TableGenerator()
tables = table_gen.generate_tables(data, root_table_name="CONFIG")

# Generate SQL DDL
ddl_gen = DDLGenerator(dialect="sqlite")
ddl = ddl_gen.generate_ddl(tables, table_gen.relationships)

# Load into SQLite
loader = SQLiteLoader("output.db")
loader.load_tables(tables)

# Generate markdown documentation
output_path = generate_doc_from_yaml(
    yaml_path=Path("config.yaml"),
    output_dir=Path("docs/"),
    max_depth=None,  # Full flattening (or 0 for no flattening, 1 for first level)
    keep_db=False    # Remove temporary database after generation
)
```

#### YAML Comparison

**CLI:**
```bash
# Schema comparison only (table structures, row counts)
uv run schema-sentinel yaml compare config1.yaml config2.yaml

# Full comparison with row-level data diff (auto primary key detection)
uv run schema-sentinel yaml compare config1.yaml config2.yaml --data -o comparison.md
```

**Python API:**
```python
from pathlib import Path
from yaml_shredder import YAMLComparator

# Create comparator
comparator = YAMLComparator(output_dir=Path("./temp_dbs"))

# Schema comparison only
report = comparator.compare_yaml_files(
    yaml1_path=Path("config1.yaml"),
    yaml2_path=Path("config2.yaml"),
    output_report=Path("comparison.md"),
    keep_dbs=False,
    root_table_name="root"
)

# Full comparison with row-level data diff
full_report = comparator.compare_yaml_files_full(
    yaml1_path=Path("config1.yaml"),
    yaml2_path=Path("config2.yaml"),
    output_report=Path("comparison.md"),
    keep_dbs=False,
    root_table_name="root"
)

# Data comparison only (between existing databases)
data_report = comparator.compare_data(
    db1_path=Path("db1.db"),
    db2_path=Path("db2.db")
)
print(data_report)
```

### Configuration (For Schema Comparison)

For Snowflake schema comparison features, create `.env` with credentials:
```bash
SNOWFLAKE_ACCOUNT=your_account
SNOWFLAKE_USER=your_username
SNOWFLAKE_PASSWORD=your_password
SNOWFLAKE_WAREHOUSE=your_warehouse
SNOWFLAKE_DATABASE=your_database
SNOWFLAKE_ROLE=your_role
SNOWFLAKE_SCHEMAS=PUBLIC,ANALYTICS  # Optional
```

## 📖 Documentation

### YAML Shredder
- **[YAML Shredder CLI Guide](resources/documents/YAML_SHREDDER_CLI.md)** - Complete CLI reference and examples
- **[Notebooks Guide](resources/documents/NOTEBOOKS.md)** - Jupyter notebooks for data comparison and analysis
- Generic Table Comparison - See `MPM Comparison and Migration.ipynb` for examples

### General Documentation
- **[📚 Project Wiki](wiki/)** - Comprehensive documentation hub
  - [Getting Started](wiki/Getting-Started.md) - Installation and quick start
  - [Architecture](wiki/Architecture.md) - System design and architecture
  - [Development Guide](wiki/Development.md) - Development environment and guidelines
  - [Contributing Guide](wiki/Contributing.md) - How to contribute
  - [Security Guide](wiki/Security.md) - Security best practices
  - [Future Development Plan](wiki/Future-Development-Plan.md) - Roadmap and upcoming features
- [Installation & Setup Guide](README.md#-quick-start)
- [Development Guide](resources/documents/DEVELOPMENT.md) - Detailed development instructions
- [Contributing Guide](resources/documents/CONTRIBUTING.md) - How to contribute
- [Security Policy](resources/documents/SECURITY.md) - Security guidelines and reporting
- [Changelog](resources/documents/CHANGELOG.md) - Version history
- [Production Checklist](resources/documents/PRODUCTION_CHECKLIST.md) - Production readiness guide

## 🛠️ Development

### Setup Development Environment

```bash
# Install with development dependencies
uv pip install -e ".[dev,jupyter]"

# Install pre-commit hooks
pre-commit install

# Run tests
make test

# Format code
make format

# Lint code
make lint
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=schema_sentinel --cov-report=html

# Run specific test file
pytest tests/test_metadata.py
```

### Code Quality

```bash
# Format code with Ruff
ruff format .

# Lint code
ruff check .

# Type checking
mypy schema_sentinel/

# Run all pre-commit hooks
pre-commit run --all-files
```

## 🏗️ Architecture

```
schema-sentinel/
├── schema_sentinel/              # Main package
│   ├── __init__.py             # Package initialization
│   ├── config/                  # Configuration management
│   │   ├── __init__.py
│   │   └── manager.py          # ConfigManager class
│   ├── markdown_utils/          # Markdown report generation
│   │   └── markdown.py
│   └── metadata_manager/        # Core metadata management
│       ├── engine.py           # Database connection engines
│       ├── metadata.py         # Metadata extraction logic
│       ├── changeset.py        # Change detection and tracking
│       ├── enums.py            # Enumerations and constants
│       ├── utils.py            # Utility functions
│       ├── model/              # Data models
│       │   ├── database.py     # Database model
│       │   ├── schema.py       # Schema model
│       │   ├── table.py        # Table model
│       │   ├── column.py       # Column model
│       │   ├── view.py         # View model
│       │   ├── procedure.py    # Stored procedure model
│       │   ├── function.py     # Function model
│       │   ├── constraint.py   # Constraint models
│       │   └── ...             # Other object models
│       └── lookup/             # Reference data
│           └── sql_data_type.py
├── yaml_shredder/               # YAML/JSON processing toolkit
│   ├── __init__.py
│   ├── schema_generator.py     # Auto JSON Schema generation
│   ├── structure_analyzer.py   # Nested structure analysis
│   ├── table_generator.py      # Relational table conversion
│   ├── ddl_generator.py        # SQL DDL generation
│   └── data_loader.py          # SQLite data loading
├── resources/                   # Configuration and templates
│   ├── examples/               # Example files and configurations
│   │   ├── .env.example        # Environment variables template
│   │   ├── example_sqlite_workflow.py  # SQLite workflow example
│   │   └── ...                 # Other example files
│   ├── db.properties           # Database config template
│   ├── datacompy/templates/    # Report templates
│   ├── meta-db/                # SQLite metadata storage
│   └── migrations-ddl/         # DDL migration procedures
├── tests/                       # Test suite
│   ├── test_config.py          # Configuration tests
│   ├── test_imports.py         # Import tests
│   └── ...                     # Other test files
├── docs/                        # API documentation (pdoc)
├── wiki/                        # Project wiki and guides
└── notebooks/                   # Jupyter notebooks
    ├── MPM Comparison and Migration.ipynb
    └── ...
```

### Supported Database Objects

- ✅ Databases
- ✅ Schemas
- ✅ Tables (with columns, data types, nullability)
- ✅ Views
- ✅ Materialized Views
- ✅ Stored Procedures
- ✅ Functions (UDFs)
- ✅ Primary Keys
- ✅ Foreign Keys
- ✅ Unique Constraints
- ✅ Streams
- ✅ Tasks
- ✅ Pipes
- ✅ Stages

## 🤝 Contributing

We welcome contributions! This is an open source project and we'd love your help to make it better.

### How to Contribute

1. **Fork the repository**
2. **Create a feature branch** from `dev` (`git checkout -b feature/amazing-feature`)
3. **Make your changes**
4. **Add tests** for your changes
5. **Ensure tests pass** (`pytest`)
6. **Format code** (`ruff format .`)
7. **Commit changes** (`git commit -m 'feat: add amazing feature'`)
8. **Push to branch** (`git push origin feature/amazing-feature`)
9. **Open a Pull Request** to merge into `dev` branch

See [CONTRIBUTING.md](resources/documents/CONTRIBUTING.md) for detailed guidelines and [BRANCHING.md](resources/documents/BRANCHING.md) for our branching strategy.

### Development Guidelines

- Follow [PEP 8](https://pep8.org/) style guide (enforced by Ruff)
- Add tests for new features
- Update documentation
- Use conventional commit messages
- Ensure CI passes before requesting review

## 📄 License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## 🔒 Security

Security is a top priority. Please see [SECURITY.md](resources/documents/SECURITY.md) for:
- Reporting vulnerabilities
- Security best practices
- Credential management guidelines

**Never commit credentials or sensitive data to the repository.**

## 🌟 Acknowledgments

- Built with modern Python tooling: [uv](https://github.com/astral-sh/uv), [Ruff](https://github.com/astral-sh/ruff)
- Powered by [SQLAlchemy](https://www.sqlalchemy.org/) and [Snowflake SQLAlchemy](https://github.com/snowflakedb/snowflake-sqlalchemy)
- Inspired by the need for better database change management in data engineering

## 📊 Project Status

**Current Status**: Active Development 🚧

This project is being actively developed and prepared for production use. We're working towards v2.1.0 with:
- ✅ Modern Python packaging (pyproject.toml)
- ✅ Comprehensive testing framework
- ✅ CI/CD pipelines
- ✅ Documentation
- 🚧 Enhanced metadata extraction
- 🚧 Additional database support
- 🚧 Web UI (planned)

### Roadmap

- **v2.1.0** - Current release with uv support, modern tooling
- **v2.2.0** - DuckDB integration, enhanced data comparator, PostgreSQL & MySQL support
- **v2.3.0** - REST API, CLI interface, Oracle & SQL Server support
- **v3.0.0** - Web UI, multi-user support, RBAC, CI/CD integration

📋 See the detailed [Future Development Plan](wiki/Future-Development-Plan.md) for comprehensive roadmap and planned features

## 📚 References

This section lists the key markdown documentation files in the repository:

- Project README: [README.md](README.md)

- Root documentation (in resources/documents/):
    - [Branching Strategy](resources/documents/BRANCHING.md)
    - [Branch Rules Setup](resources/documents/BRANCH_RULES_SETUP.md)
    - [Changelog](resources/documents/CHANGELOG.md)
    - [Contributing Guide](resources/documents/CONTRIBUTING.md)
    - [Development Guide](resources/documents/DEVELOPMENT.md)
    - [Notebooks Guide](resources/documents/NOTEBOOKS.md)
    - [Pre-Release Checklist](resources/documents/PRE_RELEASE_CHECKLIST.md)
    - [Production Checklist](resources/documents/PRODUCTION_CHECKLIST.md)
    - [PR Description Template](resources/documents/PR_DESCRIPTION.md)
    - [Security Policy](resources/documents/SECURITY.md)
    - [YAML Shredder CLI Guide](resources/documents/YAML_SHREDDER_CLI.md)

- Wiki documentation:
    - [Wiki README](wiki/README.md)
    - [Home](wiki/Home.md)
    - [Getting Started](wiki/Getting-Started.md)
    - [Architecture](wiki/Architecture.md)
    - [Development](wiki/Development.md)
    - [Contributing](wiki/Contributing.md)
    - [Security](wiki/Security.md)
    - [Future Development Plan](wiki/Future-Development-Plan.md)

- Tests documentation:
    - [Tests README](tests/README.md)

- GitHub metadata and templates:
    - [Copilot Instructions](.github/copilot-instructions.md)
    - [Ruleset README](.github/rulesets/README.md)
    - [Pull Request Template](.github/pull_request_template.md)

- Datacompy report templates:
    - [Header Template](resources/datacompy/templates/header.md)
    - [Row Summary Template](resources/datacompy/templates/row_summary.md)
    - [Favorite Column Summary Template](resources/datacompy/templates/fav_column_summary.md)
    - [Column Comparison Template](resources/datacompy/templates/column_comparison.md)
    - [Column Summary Template](resources/datacompy/templates/column_summary.md)

## 💬 Support & Community

- **Issues**: [GitHub Issues](https://github.com/Igladyshev/schema-sentinel/issues)
- **Discussions**: [GitHub Discussions](https://github.com/Igladyshev/schema-sentinel/discussions)
- **Questions**: Use the `question` issue template

## 📈 Stats

![GitHub stars](https://img.shields.io/github/stars/Igladyshev/schema-sentinel?style=social)
![GitHub forks](https://img.shields.io/github/forks/Igladyshev/schema-sentinel?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/Igladyshev/schema-sentinel?style=social)

---

**Made with ❤️ for the data engineering community**

If you find this project useful, please consider giving it a ⭐️ on GitHub!
