# SQL Comparison

[![CI](https://github.com/Igladyshev/schema-sentinel/actions/workflows/ci.yml/badge.svg)](https://github.com/Igladyshev/schema-sentinel/actions/workflows/ci.yml)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue)](https://www.python.org/downloads/)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)

A powerful tool for comparing database metadata across different environments. This project extracts database schema information, stores it in SQLite for versioning, and generates detailed comparison reports highlighting differences between database environments.

Perfect for **data engineers**, **DBAs**, and **analytics teams** working with **Snowflake** and needing to track schema changes across development, staging, and production environments.

## 🎯 Key Features

- **📊 Comprehensive Metadata Extraction** - Extract complete schema information including tables, columns, views, procedures, functions, constraints, and more
- **💾 Version Control for Schema** - Store metadata snapshots in SQLite for historical tracking
- **🔍 Intelligent Comparison** - Compare metadata between different environments with detailed diff reports
- **📝 Multiple Report Formats** - Generate reports in Markdown, HTML, and JSON formats
- **🏢 Snowflake Native** - Built specifically for Snowflake with deep integration
- **🔌 Extensible** - Architecture supports additional database platforms
- **🚀 Fast & Efficient** - Optimized queries and parallel processing
- **🔒 Secure** - Best practices for credential management and data security

## 🎓 Use Cases

- **Environment Synchronization** - Ensure dev, staging, and production schemas are aligned
- **Change Tracking** - Monitor schema evolution over time
- **Deployment Validation** - Verify schema changes after deployments
- **Compliance & Auditing** - Maintain schema change history for compliance requirements
- **Migration Planning** - Identify differences before major migrations
- **Documentation** - Auto-generate schema documentation

## 📋 Requirements

- Python 3.9 or higher
- [uv](https://github.com/astral-sh/uv) - Modern Python package manager
- Snowflake account with appropriate permissions

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

### Configuration

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` with your Snowflake credentials:
   ```bash
   SNOWFLAKE_ACCOUNT=your_account
   SNOWFLAKE_USER=your_username
   SNOWFLAKE_PASSWORD=your_password
   SNOWFLAKE_WAREHOUSE=your_warehouse
   SNOWFLAKE_DATABASE=your_database
   SNOWFLAKE_ROLE=your_role

   # Optional: Specify schemas to include (comma-separated)
   # If not set, all schemas in the database will be included
   SNOWFLAKE_SCHEMAS=PUBLIC,ANALYTICS,STAGING,MARTS
   ```

### Basic Usage

```python
from schema_sentinel.metadata_manager import extract_metadata, compare_metadata

# Extract metadata from source environment
source_metadata = extract_metadata(
    account="prod_account",
    database="ANALYTICS_DB",
    schema="PUBLIC"
)

# Extract metadata from target environment
target_metadata = extract_metadata(
    account="dev_account",
    database="ANALYTICS_DB",
    schema="PUBLIC"
)

# Compare and generate report
comparison = compare_metadata(source_metadata, target_metadata)
comparison.generate_report("differences.md")
```

## 📖 Documentation

- **[📚 Project Wiki](wiki/)** - Comprehensive documentation hub
  - [Getting Started](wiki/Getting-Started.md) - Installation and quick start
  - [Architecture](wiki/Architecture.md) - System design and architecture
  - [Development Guide](wiki/Development.md) - Development environment and guidelines
  - [Contributing Guide](wiki/Contributing.md) - How to contribute
  - [Security Guide](wiki/Security.md) - Security best practices
  - [Future Development Plan](wiki/Future-Development-Plan.md) - Roadmap and upcoming features
- [Installation & Setup Guide](README.md#-quick-start)
- [Development Guide](DEVELOPMENT.md) - Detailed development instructions
- [Contributing Guide](CONTRIBUTING.md) - How to contribute
- [Security Policy](SECURITY.md) - Security guidelines and reporting
- [Changelog](CHANGELOG.md) - Version history
- [Production Checklist](PRODUCTION_CHECKLIST.md) - Production readiness guide

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

## 🏗️ Architecture

```
schema-sentinel/
├── schema_sentinel/              # Main package
│   ├── __init__.py             # Package initialization
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
├── resources/                   # Configuration and templates
│   ├── db.properties           # Database config template
│   ├── datacompy/templates/    # Report templates
│   └── migrations-ddl/         # DDL migration procedures
├── tests/                       # Test suite
├── notebooks/                   # Jupyter notebooks for exploration
└── docs/                        # Documentation
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

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines and [BRANCHING.md](BRANCHING.md) for our branching strategy.

### Development Guidelines

- Follow [PEP 8](https://pep8.org/) style guide (enforced by Ruff)
- Add tests for new features
- Update documentation
- Use conventional commit messages
- Ensure CI passes before requesting review

## 📄 License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## 🔒 Security

Security is a top priority. Please see [SECURITY.md](SECURITY.md) for:
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
