# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Modern Python packaging with `pyproject.toml`
- Development environment setup with `uv` package manager
- Comprehensive documentation (README, DEVELOPMENT, CONTRIBUTING)
- VS Code workspace configuration
- Makefile for common development tasks
- GitHub Actions CI/CD workflows
- Pre-commit hooks configuration
- Basic test suite with pytest
- Code quality tools (Ruff for linting/formatting, mypy for type checking)
- Jupyter notebook support
- Production readiness checklist

### Changed
- Updated dependencies to latest compatible versions
- Improved `.gitignore` for modern Python development
- Reorganized project structure

### Fixed
- Merged unrelated git histories between dev and master branches

## [2.0.5] - 2023-09-26

### Added
- Initial project structure
- Snowflake metadata extraction
- SQLite storage for metadata
- Basic comparison functionality
- Metadata models for database objects

[Unreleased]: https://github.com/Igladyshev/sql-comparison/compare/v2.0.5...HEAD
[2.0.5]: https://github.com/Igladyshev/sql-comparison/releases/tag/v2.0.5
