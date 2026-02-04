# Contributing to Schema Sentinel

First off, thank you for considering contributing to Schema Sentinel! It's people like you that make open source such a great community.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Branching Strategy](#branching-strategy)
- [How Can I Contribute?](#how-can-i-contribute)
- [Development Setup](#development-setup)
- [Pull Request Process](#pull-request-process)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)

## Code of Conduct

This project and everyone participating in it is governed by our commitment to fostering an open and welcoming environment. We pledge to make participation in our project a harassment-free experience for everyone.

### Our Standards

**Positive behaviors include:**
- Using welcoming and inclusive language
- Being respectful of differing viewpoints and experiences
- Gracefully accepting constructive criticism
- Focusing on what is best for the community
- Showing empathy towards other community members

**Unacceptable behaviors include:**
- Trolling, insulting/derogatory comments, and personal or political attacks
- Public or private harassment
- Publishing others' private information without explicit permission
- Other conduct which could reasonably be considered inappropriate in a professional setting

## Branching Strategy

We use a simple two-branch strategy for this project:

- **`master`** - Protected production branch with strict rules (requires PR reviews and all CI checks)
- **`dev`** - Development branch for feature integration (lighter protection, allows direct pushes)

For detailed information about our branching workflow, see the [Branching Strategy](https://github.com/Igladyshev/schema-sentinel/blob/master/BRANCHING.md) document.

**Quick workflow:**
1. Create feature branches from `dev`: `git checkout -b feature/your-feature`
2. Open PRs to merge features into `dev`
3. When ready for release, create PR from `dev` to `master`

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check existing issues to avoid duplicates. When creating a bug report, include as many details as possible:

- **Use a clear and descriptive title**
- **Describe the exact steps to reproduce the problem**
- **Provide specific examples** (code snippets, database schemas, etc.)
- **Describe the behavior you observed** and what you expected
- **Include error messages and stack traces**
- **Specify your environment** (OS, Python version, database version)

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion:

- **Use a clear and descriptive title**
- **Provide a step-by-step description** of the suggested enhancement
- **Explain why this enhancement would be useful**
- **List examples** of where this enhancement would help

### Your First Code Contribution

Unsure where to begin? Look for issues labeled:
- `good first issue` - Good for newcomers
- `help wanted` - Extra attention is needed
- `documentation` - Documentation improvements

### Pull Requests

1. Fork the repository
2. Create a feature branch from `dev` (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for your changes
5. Ensure all tests pass
6. Commit your changes with clear messages
7. Push to your branch
8. Open a Pull Request to merge into `dev`

## Development Setup

### Prerequisites

- Python 3.9 or higher
- [uv](https://github.com/astral-sh/uv) package manager
- Git

### Setup Steps

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/schema-sentinel.git
cd schema-sentinel

# Add upstream remote
git remote add upstream https://github.com/Igladyshev/schema-sentinel.git

# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create virtual environment and install dependencies
uv venv
source .venv/bin/activate  # Linux/macOS or .venv\Scripts\activate on Windows
uv pip install -e ".[dev,jupyter]"

# Install pre-commit hooks
pre-commit install
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=schema_sentinel --cov-report=html

# Run specific test file
pytest tests/test_imports.py

# Run tests matching a pattern
pytest -k "test_metadata"
```

### Code Quality Checks

```bash
# Format code
ruff format .

# Lint code
ruff check .

# Fix auto-fixable issues
ruff check --fix .

# Type checking
mypy schema_sentinel/
```

## Pull Request Process

### Before Submitting

1. **Update documentation** for any changed functionality
2. **Add tests** that prove your fix/feature works
3. **Update CHANGELOG.md** with your changes under the `[Unreleased]` section
4. **Ensure CI passes** - all tests and checks must pass
5. **Run pre-commit hooks** - `pre-commit run --all-files`

### PR Title Format

Use conventional commit style:
- `feat: add support for PostgreSQL metadata extraction`
- `fix: resolve connection timeout in Snowflake queries`
- `docs: improve README setup instructions`
- `test: add tests for column comparison`
- `refactor: simplify metadata container logic`
- `chore: update dependencies`

### PR Description Template

```markdown
## Description
Brief description of changes

## Motivation
Why are these changes needed?

## Changes
- List of specific changes made

## Testing
How was this tested?

## Screenshots (if applicable)
Add screenshots for UI changes

## Checklist
- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
- [ ] All tests pass locally
- [ ] Code follows style guidelines
- [ ] Pre-commit hooks pass
```

### Review Process

1. **Initial Review** - Maintainers will review within 3-5 business days
2. **Feedback** - Address any requested changes
3. **Approval** - Once approved, maintainers will merge your PR
4. **Recognition** - Your contribution will be recognized in the release notes

## Coding Standards

### Python Style Guide

We follow [PEP 8](https://pep8.org/) with some modifications enforced by Ruff:

- **Line length**: 120 characters
- **Indentation**: 4 spaces (no tabs)
- **Imports**: Organized with `isort` (automatic with Ruff)
- **Naming conventions**:
  - Classes: `PascalCase`
  - Functions/methods: `snake_case`
  - Constants: `UPPER_SNAKE_CASE`
  - Private methods: `_leading_underscore`

### Documentation

**Docstrings**: Use Google-style docstrings for all public functions/classes

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

**Type hints**: Add type hints to all function signatures

**Comments**: Explain "why", not "what" (code should be self-documenting)

### Git Commit Messages

- Use present tense ("Add feature" not "Added feature")
- Use imperative mood ("Move cursor to..." not "Moves cursor to...")
- Limit first line to 72 characters
- Reference issues and pull requests after the first line

Example:
```
feat: add PostgreSQL metadata extraction support

Implements metadata extraction for PostgreSQL databases including:
- Table and column metadata
- Index information
- Foreign key constraints

Closes #123
```

## Testing Guidelines

### Test Structure

- Place tests in `tests/` directory
- Mirror the source code structure
- Name test files `test_*.py`
- Name test functions `test_*`

### Test Quality

- **One assertion per test** when possible
- **Clear test names** that describe what is being tested
- **Use fixtures** for common setup (see `tests/conftest.py`)
- **Mock external dependencies** (databases, APIs)
- **Test edge cases** and error conditions

### Example Test

```python
def test_table_metadata_extraction(sample_database_config):
    """Test that table metadata is correctly extracted."""
    # Arrange
    engine = create_test_engine(sample_database_config)
    
    # Act
    metadata = extract_table_metadata(engine, "test_table")
    
    # Assert
    assert metadata.name == "test_table"
    assert len(metadata.columns) > 0
    assert metadata.schema_name == "public"
```

### Test Coverage

- Aim for at least 80% code coverage
- All new features must include tests
- Bug fixes should include regression tests

## Database Support

When adding support for a new database:

1. Create engine class in `schema_sentinel/metadata_manager/engine.py`
2. Implement metadata extraction queries
3. Add comprehensive tests with mocked database
4. Update documentation
5. Add example configuration

## Documentation

### What to Document

- New features and functionality
- API changes
- Configuration options
- Migration guides for breaking changes
- Examples and use cases

### Where to Document

- **README.md** - High-level overview and quick start
- **wiki/** - Detailed guides and tutorials
- **Docstrings** - In-code documentation
- **CHANGELOG.md** - Version history and changes

## Questions?

- Open an issue with the `question` label
- Join discussions in existing issues
- Check the [Documentation](https://github.com/Igladyshev/schema-sentinel/wiki)
- Review the [Development Guide](Development.md)

## Recognition

Contributors will be recognized in:
- README.md contributors section
- Release notes
- Project documentation

Thank you for contributing! 🎉

## Additional Resources

- [Development Guide](Development.md) - Detailed development instructions
- [Architecture Guide](Architecture.md) - System architecture and design
- [Future Development Plan](Future-Development-Plan.md) - Planned features and roadmap
- [Security Guide](Security.md) - Security best practices
