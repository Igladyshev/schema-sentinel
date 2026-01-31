# Development Guide

## Quick Start

### Environment Setup

```bash
# Option 1: Use the setup script
./setup.sh

# Option 2: Manual setup
uv venv
source .venv/bin/activate
uv pip install -e ".[dev,jupyter]"

# Option 3: Use Makefile
make init
source .venv/bin/activate
```

### Activating the Environment

```bash
source .venv/bin/activate
```

## Common Tasks

### Running Tests

```bash
pytest                    # Run all tests
pytest tests/test_*.py    # Run specific test file
pytest -v                 # Verbose output
pytest --cov              # With coverage report
```

### Code Quality

```bash
# Format code (using ruff)
ruff format .

# Check code style
ruff check .

# Fix auto-fixable issues
ruff check --fix .

# Type checking
mypy sql_comparison/

# Run all pre-commit hooks
pre-commit run --all-files
```

### Working with Jupyter Notebooks

```bash
# Start Jupyter Lab
jupyter lab

# Start Jupyter Notebook
jupyter notebook

# Convert notebook to Python script
jupyter nbconvert --to script notebook.ipynb
```

## Project Structure

```
sql-comparison/
├── sql_comparison/              # Main package
│   ├── __init__.py             # Package initialization
│   ├── markdown_utils/          # Markdown generation
│   │   ├── __init__.py
│   │   └── markdown.py
│   └── metadata_manager/        # Core functionality
│       ├── __init__.py
│       ├── changeset.py        # Change tracking
│       ├── engine.py           # Database engines
│       ├── enums.py            # Enumerations
│       ├── metadata.py         # Metadata handling
│       ├── utils.py            # Utilities
│       ├── lookup/             # Reference data
│       │   ├── __init__.py
│       │   └── sql_data_type.py
│       └── model/              # Data models
│           ├── __init__.py
│           ├── column.py       # Column metadata
│           ├── table.py        # Table metadata
│           ├── database.py     # Database metadata
│           └── ...             # Other models
├── resources/                   # Configuration and templates
│   ├── db.properties           # Database config template
│   ├── bootstrap*.css          # UI styles
│   └── datacompy/              # Comparison templates
├── tests/                       # Test suite (to be created)
├── notebooks/                   # Jupyter notebooks
├── pyproject.toml              # Project configuration
├── Makefile                    # Common commands
├── README.md                   # Project documentation
└── setup.sh                    # Quick setup script
```

## Key Components

### Metadata Manager

The core of the project - handles database metadata extraction and storage:

- **Engine** (`engine.py`): Database connection and query execution
- **Models** (`model/`): ORM models for metadata objects
- **Metadata** (`metadata.py`): Metadata extraction logic
- **Changeset** (`changeset.py`): Change tracking and comparison

### Supported Database Objects

- Databases
- Schemas
- Tables
- Columns
- Views
- Procedures
- Functions
- Constraints (Primary Key, Foreign Key, Unique)
- Streams
- Tasks
- Pipes
- Stages

## Configuration

### Database Connection

Database connections are configured using `.properties` files:

```properties
# resources/db.properties
account=your_account
user=your_username
password=your_password
warehouse=your_warehouse
database=your_database
schema=your_schema
role=your_role
```

### Environment Variables

```bash
TEMP_DIR=/tmp                    # Temporary directory
LOG_LEVEL=INFO                   # Logging level (DEBUG, INFO, WARNING, ERROR)
```

## Adding New Features

### Adding a New Database Object Type

1. Create a new model in `sql_comparison/metadata_manager/model/`
2. Add extraction logic in `metadata.py`
3. Update comparison logic in `changeset.py`
4. Add templates in `resources/datacompy/templates/`

### Adding Support for a New Database

1. Create a new engine class in `engine.py`
2. Implement metadata extraction queries
3. Add connection configuration handling
4. Update documentation

## Troubleshooting

### Common Issues

**Issue**: Import errors after installation
```bash
# Solution: Reinstall in editable mode
uv pip install -e .
```

**Issue**: SQLAlchemy version conflicts
```bash
# Solution: The project uses SQLAlchemy 1.4.x
# Check installed version: pip show sqlalchemy
```

**Issue**: Snowflake connection issues
```bash
# Solution: Verify credentials and network access
# Check ~/.snowflake/connections.toml
```

## Testing

### Writing Tests

Create test files in the `tests/` directory:

```python
# tests/test_metadata.py
import pytest
from sql_comparison.metadata_manager.model.table import Table

def test_table_creation():
    table = Table(name="test_table", schema_name="public")
    assert table.name == "test_table"
```

### Running Specific Tests

```bash
pytest tests/test_metadata.py::test_table_creation  # Run specific test
pytest -k "table"                                    # Run tests matching pattern
pytest -x                                            # Stop on first failure
pytest --lf                                          # Run last failed tests
```

## Git Workflow

```bash
# Create a feature branch
git checkout -b feature/your-feature-name

# Make changes and commit
git add .
git commit -m "Description of changes"

# Push to remote
git push origin feature/your-feature-name
```

## Performance Tips

- Use connection pooling for database connections
- Cache metadata when possible
- Use batch operations for large datasets
- Profile code with `pytest-profiling` if needed

## Resources

- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/en/14/)
- [Snowflake SQLAlchemy](https://docs.snowflake.com/en/user-guide/sqlalchemy.html)
- [uv Documentation](https://github.com/astral-sh/uv)
- [Ruff Documentation](https://docs.astral.sh/ruff/)
