# Development Guide

This guide provides detailed instructions for setting up a development environment and contributing to Schema Sentinel.

## Development Environment Setup

### Prerequisites

- Python 3.9 or higher
- [uv](https://github.com/astral-sh/uv) package manager
- Git
- Text editor or IDE (VS Code recommended)

### Quick Setup

```bash
# Option 1: Use the setup script
./setup.sh

# Option 2: Manual setup
uv venv
source .venv/bin/activate  # Linux/macOS or .venv\Scripts\activate on Windows
uv pip install -e ".[dev,jupyter]"

# Option 3: Use Makefile
make init
source .venv/bin/activate
```

### Installing Pre-commit Hooks

Pre-commit hooks ensure code quality before each commit:

```bash
pre-commit install
```

This will automatically run:
- Code formatting with Ruff
- Linting checks
- Type checking with mypy
- Other quality checks

## Project Structure

```
schema-sentinel/
├── schema_sentinel/              # Main package
│   ├── __init__.py              # Package initialization
│   ├── markdown_utils/           # Markdown generation
│   │   ├── __init__.py
│   │   └── markdown.py
│   └── metadata_manager/         # Core functionality
│       ├── __init__.py
│       ├── changeset.py         # Change tracking
│       ├── engine.py            # Database engines
│       ├── enums.py             # Enumerations
│       ├── metadata.py          # Metadata handling
│       ├── utils.py             # Utilities
│       ├── lookup/              # Reference data
│       │   ├── __init__.py
│       │   └── sql_data_type.py
│       └── model/               # Data models
│           ├── __init__.py
│           ├── column.py        # Column metadata
│           ├── table.py         # Table metadata
│           ├── database.py      # Database metadata
│           └── ...              # Other models
├── resources/                    # Configuration and templates
│   ├── db.properties            # Database config template
│   └── datacompy/               # Comparison templates
├── tests/                        # Test suite
├── notebooks/                    # Jupyter notebooks
├── wiki/                         # Project wiki
├── docs/                         # API documentation
├── pyproject.toml               # Project configuration
├── Makefile                     # Common commands
└── README.md                    # Project documentation
```

## Development Workflow

### 1. Create a Feature Branch

Follow the branching strategy outlined in [BRANCHING.md](https://github.com/Igladyshev/schema-sentinel/blob/master/BRANCHING.md):

```bash
# Ensure you're on the dev branch
git checkout dev
git pull origin dev

# Create your feature branch
git checkout -b feature/your-feature-name
```

### 2. Make Your Changes

- Write clear, concise code
- Follow the coding standards (see below)
- Add tests for new features
- Update documentation as needed

### 3. Run Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_metadata.py

# Run with coverage
pytest --cov=schema_sentinel --cov-report=html

# Run tests matching a pattern
pytest -k "test_table"

# Run with verbose output
pytest -v

# Stop on first failure
pytest -x

# Run last failed tests
pytest --lf
```

### 4. Check Code Quality

```bash
# Format code (auto-fixes issues)
ruff format .

# Check code style
ruff check .

# Fix auto-fixable issues
ruff check --fix .

# Type checking
mypy schema_sentinel/

# Run all pre-commit hooks
pre-commit run --all-files
```

### 5. Commit Your Changes

Use conventional commit messages:

```bash
git add .
git commit -m "feat: add your feature description"
```

**Commit Message Format:**
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `test:` - Adding or updating tests
- `refactor:` - Code refactoring
- `chore:` - Maintenance tasks
- `style:` - Code style changes

### 6. Push and Create Pull Request

```bash
git push origin feature/your-feature-name
```

Then create a Pull Request on GitHub targeting the `dev` branch.

## Common Development Tasks

### Running Tests

```bash
pytest                    # Run all tests
pytest tests/test_*.py    # Run specific test file
pytest -v                 # Verbose output
pytest --cov              # With coverage report
```

### Code Formatting and Linting

```bash
# Format code
ruff format .

# Check code style
ruff check .

# Fix auto-fixable issues
ruff check --fix .

# Type checking
mypy schema_sentinel/

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

### Building Documentation

```bash
# Generate API documentation with pdoc
pdoc schema_sentinel -o docs/

# View documentation locally
python -m http.server -d docs/
```

## Coding Standards

### Python Style Guide

We follow [PEP 8](https://pep8.org/) with modifications enforced by Ruff:

- **Line length**: 120 characters
- **Indentation**: 4 spaces (no tabs)
- **Imports**: Organized automatically with isort (via Ruff)
- **Naming conventions**:
  - Classes: `PascalCase`
  - Functions/methods: `snake_case`
  - Constants: `UPPER_SNAKE_CASE`
  - Private methods: `_leading_underscore`

### Type Hints

Add type hints to all function signatures:

```python
def extract_metadata(database: str, schema: str) -> MetadataContainer:
    """Extract metadata from specified database and schema."""
    pass
```

### Docstrings

Use Google-style docstrings for all public functions and classes:

```python
def extract_metadata(database: str, schema: str) -> MetadataContainer:
    """Extract metadata from specified database and schema.

    Args:
        database: Name of the database to extract from
        schema: Name of the schema to extract from

    Returns:
        MetadataContainer with extracted metadata

    Raises:
        ConnectionError: If database connection fails
        ValueError: If database or schema not found
    """
    pass
```

### Comments

- Explain "why", not "what" (code should be self-documenting)
- Use comments sparingly and only when necessary
- Keep comments up-to-date with code changes

## Testing Guidelines

### Test Structure

- Place tests in `tests/` directory
- Mirror the source code structure
- Name test files `test_*.py`
- Name test functions `test_*`

### Writing Tests

```python
# tests/test_metadata.py
import pytest
from schema_sentinel.metadata_manager.model.table import Table

def test_table_creation():
    """Test that table metadata is correctly created."""
    # Arrange
    table_name = "test_table"
    schema_name = "public"
    
    # Act
    table = Table(name=table_name, schema_name=schema_name)
    
    # Assert
    assert table.name == table_name
    assert table.schema_name == schema_name
```

### Test Quality

- **One assertion per test** when possible
- **Clear test names** that describe what is being tested
- **Use fixtures** for common setup (see `tests/conftest.py`)
- **Mock external dependencies** (databases, APIs)
- **Test edge cases** and error conditions

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

## Adding New Features

### Adding a New Database Object Type

1. Create a new model in `schema_sentinel/metadata_manager/model/`
2. Add extraction logic in `metadata.py`
3. Update comparison logic in `changeset.py`
4. Add templates in `resources/datacompy/templates/`
5. Add tests for the new object type

### Adding Support for a New Database

1. Create a new engine class in `engine.py`
2. Implement metadata extraction queries
3. Add connection configuration handling
4. Update documentation
5. Add comprehensive tests

## Troubleshooting

### Common Issues

**Issue: Import errors after installation**
```bash
# Solution: Reinstall in editable mode
uv pip install -e .
```

**Issue: SQLAlchemy version conflicts**
```bash
# The project uses SQLAlchemy 1.4.x
# Check installed version
pip show sqlalchemy
```

**Issue: Snowflake connection issues**
- Verify credentials in `.env` file
- Check network access to Snowflake
- Verify `~/.snowflake/connections.toml` if using SSO

**Issue: Tests failing**
```bash
# Clear pytest cache
pytest --cache-clear

# Reinstall dependencies
uv pip install -e ".[dev,jupyter]"
```

## Performance Tips

- Use connection pooling for database connections
- Cache metadata when possible
- Use batch operations for large datasets
- Profile code with `pytest-profiling` if needed

## Git Workflow

### Feature Development

```bash
# Create a feature branch
git checkout -b feature/your-feature-name

# Make changes and commit
git add .
git commit -m "feat: description of changes"

# Push to remote
git push origin feature/your-feature-name

# Create Pull Request on GitHub
```

### Keeping Your Branch Updated

```bash
# Update from dev branch
git checkout dev
git pull origin dev
git checkout feature/your-feature-name
git merge dev
```

## IDE Configuration

### VS Code

The repository includes VS Code workspace settings in `.vscode/`:

- Python interpreter configuration
- Recommended extensions
- Debugging configurations
- Task runners

**Recommended Extensions:**
- Python (Microsoft)
- Pylance
- Ruff
- GitLens
- Jupyter

## Resources

- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/en/14/)
- [Snowflake SQLAlchemy](https://docs.snowflake.com/en/user-guide/sqlalchemy.html)
- [uv Documentation](https://github.com/astral-sh/uv)
- [Ruff Documentation](https://docs.astral.sh/ruff/)
- [pytest Documentation](https://docs.pytest.org/)
- [Pydantic Documentation](https://docs.pydantic.dev/)

## Getting Help

- Check the [README](https://github.com/Igladyshev/schema-sentinel/blob/master/README.md)
- Review existing [GitHub Issues](https://github.com/Igladyshev/schema-sentinel/issues)
- Ask questions in [GitHub Discussions](https://github.com/Igladyshev/schema-sentinel/discussions)
- Refer to the [Contributing Guide](Contributing.md)

## Next Steps

- Explore the [Architecture](Architecture.md) to understand the system design
- Check the [Future Development Plan](Future-Development-Plan.md) for planned features
- Review the [Contributing Guidelines](Contributing.md) for contribution process
