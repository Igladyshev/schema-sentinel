# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [3.0.2] - 2026-02-08

### Added
- **YAML Comparator**: Compare two YAML files by loading them into SQLite databases
  - Structural comparison (tables, schemas, row counts)
  - Data comparison with detailed statistics
  - Markdown report generation
  - CLI command: `schema-sentinel yaml compare`
  - Python API for programmatic access
- **CLI Test Suite**: Comprehensive tests for all CLI commands (40+ test cases)
  - Tests for all yaml group commands
  - Tests for schema group commands
  - Error handling and validation tests
  - Integration workflow tests

### Changed
- **CLI Organization**: Reorganized commands into logical groups
  - `yaml` group: analyze, schema, tables, ddl, load, shred, compare (7 commands)
  - `schema` group: extract, compare (2 commands)
  - Improved command structure and discoverability
- **Documentation**: Updated README with new CLI structure and YAML comparison examples

### Fixed
- Fixed yaml module shadowing issue in CLI
- Fixed numpy int64 to Python int conversion in comparator
- Fixed function name conflicts between commands
- Fixed JSON serialization for complex analysis results
- Improved error handling and exception chaining

## [3.0.1] - 2026-02-07

### Fixed
- Minor bug fixes and improvements

## [3.0.0] - 2026-02-07

### Added
- **YAML Shredder**: Complete toolkit for transforming nested YAML/JSON into relational tables
  - Automatic JSON Schema generation from YAML/JSON examples
  - Relational table conversion with automatic relationship mapping
  - Multi-database DDL generation (Snowflake, PostgreSQL, MySQL, SQLite)
  - SQLite data loader with automatic indexing
  - Structure analysis and pattern detection
  - CLI interface with 6 commands (analyze, schema, tables, ddl, load, all)
  - Python API for programmatic access
- **Configuration Management System**: Centralized configuration with ConfigManager class
  - PathConfig for project paths and directories
  - LogConfig for logging settings
  - DatabaseConfig for database connections and retention
  - MetadataConfig for metadata extraction settings
  - YAML configuration file support (`schema_sentinel_config.yaml`)
  - Environment variable integration
  - Singleton pattern for global access
  - Comprehensive test suite (16 tests)
- **Generic Table Comparison Framework**: Universal data comparison tool
  - Auto-discovery of tables and structures
  - Flexible grouping and comparison logic
  - Works with any table structure
  - Batch comparison reports
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
- **Project Positioning**: Repositioned as comprehensive data processing toolkit
  - YAML Shredder as primary feature
  - Schema comparison as bonus feature
- **README.md**: Complete rewrite emphasizing YAML Shredder capabilities
  - Generic use cases (configuration management, API processing, data pipelines)
  - Updated key features and documentation structure
  - Snowflake now optional (only for schema comparison)
- **Documentation**: Generalized all examples to be non-MPM-specific
  - YAML_SHREDDER_CLI.md with generic configuration examples
  - Updated all documentation to show diverse use cases
- **Configuration**: Consolidated scattered global variables
  - Removed duplicate definitions from `metadata_manager/model/__init__.py`
  - Centralized ACCOUNT_MAP, ENV_MAP, CUSTOM_VIEW_FILTERS in config
  - Backward compatible with existing code
- Updated dependencies to latest compatible versions
- Improved `.gitignore` for modern Python development
- Reorganized project structure

### Fixed
- Merged unrelated git histories between dev and master branches
- DateTime handling in YAML schema generation
- Syntax errors in DDL generator
- SQLite type mappings for proper data type inference

## [2.0.5] - 2023-09-26

### Added
- Initial project structure
- Snowflake metadata extraction
- SQLite storage for metadata
- Basic comparison functionality
- Metadata models for database objects

[Unreleased]: https://github.com/Igladyshev/schema-sentinel/compare/v3.0.0...HEAD
[3.0.0]: https://github.com/Igladyshev/schema-sentinel/compare/v2.0.5...v3.0.0
[2.0.5]: https://github.com/Igladyshev/schema-sentinel/releases/tag/v2.0.5
