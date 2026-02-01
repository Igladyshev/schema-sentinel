# Getting Started

This guide will help you get Schema Sentinel up and running on your system.

## Prerequisites

Before you begin, ensure you have the following:

- **Python 3.9 or higher** installed on your system
- **[uv](https://github.com/astral-sh/uv)** - Modern Python package manager
- **Snowflake account** with appropriate permissions
- **Git** for version control

## Installation

### 1. Install uv Package Manager

If you don't have `uv` installed, install it first:

**Linux/macOS:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows:**
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### 2. Clone the Repository

```bash
git clone https://github.com/Igladyshev/schema-sentinel.git
cd schema-sentinel
```

### 3. Set Up the Environment

**Option 1: Use the setup script (recommended)**
```bash
./setup.sh
```

**Option 2: Manual setup**
```bash
# Create virtual environment
uv venv

# Activate virtual environment
source .venv/bin/activate  # Linux/macOS
# or
.venv\Scripts\activate  # Windows

# Install dependencies
uv pip install -e ".[dev,jupyter]"
```

**Option 3: Use Makefile**
```bash
make init
source .venv/bin/activate
```

## Configuration

### 1. Create Environment File

Copy the example environment file:

```bash
cp .env.example .env
```

### 2. Configure Snowflake Credentials

Edit the `.env` file with your Snowflake credentials:

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

**⚠️ Important Security Notes:**
- Never commit the `.env` file to version control
- The `.env` file is already in `.gitignore`
- Use secure credential management for production environments

### 3. Install Pre-commit Hooks (for developers)

If you plan to contribute to the project:

```bash
pre-commit install
```

## Basic Usage

### Extract Metadata from Snowflake

```python
from schema_sentinel.metadata_manager import extract_metadata

# Extract metadata from source environment
metadata = extract_metadata(
    account="your_account",
    database="ANALYTICS_DB",
    schema="PUBLIC"
)
```

### Compare Two Environments

```python
from schema_sentinel.metadata_manager import extract_metadata, compare_metadata

# Extract from source
source_metadata = extract_metadata(
    account="prod_account",
    database="ANALYTICS_DB",
    schema="PUBLIC"
)

# Extract from target
target_metadata = extract_metadata(
    account="dev_account",
    database="ANALYTICS_DB",
    schema="PUBLIC"
)

# Compare and generate report
comparison = compare_metadata(source_metadata, target_metadata)
comparison.generate_report("differences.md")
```

## Verification

Verify your installation by running the tests:

```bash
# Activate the virtual environment if not already active
source .venv/bin/activate

# Run tests
pytest

# Run with coverage
pytest --cov=schema_sentinel --cov-report=html
```

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
- Verify your credentials in the `.env` file
- Ensure your Snowflake account is accessible
- Check network connectivity
- Verify you have the correct permissions in Snowflake

**Issue: uv command not found**
```bash
# Ensure uv is in your PATH
# Try reinstalling uv or restart your terminal
```

## Next Steps

Now that you have Schema Sentinel installed, you can:

1. **Explore the [Architecture](Architecture.md)** to understand how the system works
2. **Read the [Development Guide](Development.md)** if you want to contribute
3. **Check out the [Future Development Plan](Future-Development-Plan.md)** to see what's coming next
4. **Review the [Security Guide](Security.md)** for best practices

## Additional Resources

- [Main README](https://github.com/Igladyshev/schema-sentinel/blob/master/README.md)
- [Contributing Guidelines](Contributing.md)
- [GitHub Issues](https://github.com/Igladyshev/schema-sentinel/issues)
- [GitHub Discussions](https://github.com/Igladyshev/schema-sentinel/discussions)
