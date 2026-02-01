# Architecture

This document describes the architecture and design of Schema Sentinel, providing an overview of how the system works and how its components interact.

## System Overview

Schema Sentinel is designed as a modular system for extracting, storing, and comparing database metadata across different environments. The architecture emphasizes extensibility, maintainability, and performance.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Schema Sentinel                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌────────────────┐  ┌─────────────────┐  ┌────────────────┐ │
│  │   Extraction   │─▶│    Storage      │◀─│   Comparison   │ │
│  │     Layer      │  │     Layer       │  │      Layer     │ │
│  └────────────────┘  └─────────────────┘  └────────────────┘ │
│         │                     │                     │          │
│         ▼                     ▼                     ▼          │
│  ┌────────────────────────────────────────────────────────┐   │
│  │              Metadata Models & Objects                 │   │
│  └────────────────────────────────────────────────────────┘   │
│                              │                                 │
│                              ▼                                 │
│  ┌────────────────────────────────────────────────────────┐   │
│  │                  Report Generation                     │   │
│  │            (Markdown, HTML, JSON)                      │   │
│  └────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
         │                     │                     │
         ▼                     ▼                     ▼
  ┌──────────┐          ┌──────────┐         ┌──────────┐
  │ Snowflake│          │  SQLite  │         │  Reports │
  │ Database │          │ Storage  │         │  Output  │
  └──────────┘          └──────────┘         └──────────┘
```

## Core Components

### 1. Metadata Manager (`schema_sentinel/metadata_manager/`)

The metadata manager is the heart of the application, responsible for coordinating all metadata operations.

**Key Modules:**

- **`engine.py`** - Database connection engines
  - Manages connections to different database types
  - Handles authentication and session management
  - Provides query execution interface

- **`metadata.py`** - Metadata extraction logic
  - Extracts schema information from databases
  - Coordinates extraction across multiple object types
  - Handles batch operations and parallel processing

- **`changeset.py`** - Change detection and tracking
  - Compares metadata between environments
  - Identifies additions, deletions, and modifications
  - Generates detailed difference reports

- **`enums.py`** - Enumerations and constants
  - Defines object types, statuses, and categories
  - Ensures type safety and consistency

- **`utils.py`** - Utility functions
  - Common helper functions
  - Data transformation utilities
  - Validation logic

### 2. Data Models (`schema_sentinel/metadata_manager/model/`)

Comprehensive models representing all database objects:

- **`database.py`** - Database metadata model
- **`schema.py`** - Schema metadata model
- **`table.py`** - Table metadata with columns
- **`column.py`** - Column definitions with data types
- **`view.py`** - View metadata
- **`procedure.py`** - Stored procedure metadata
- **`function.py`** - Function/UDF metadata
- **`constraint.py`** - Constraint models (PK, FK, Unique)
- And more...

**Model Features:**
- Pydantic-based validation
- Type safety with Python type hints
- Serialization/deserialization support
- Relationship mapping between objects

### 3. Report Generation (`schema_sentinel/markdown_utils/`)

Generates human-readable reports in multiple formats:

- **Markdown Reports** - Detailed comparison reports
- **HTML Reports** - Web-viewable formatted reports
- **JSON Reports** - Machine-readable structured data

**Report Templates:**
Located in `resources/datacompy/templates/`
- `header.md` - Report header template
- `column_summary.md` - Column comparison template
- `row_summary.md` - Row comparison template
- And more...

### 4. Lookup Data (`schema_sentinel/metadata_manager/lookup/`)

Reference data and mappings:

- **`sql_data_type.py`** - SQL data type definitions and mappings
- Standardizes data types across different database engines
- Provides type conversion and compatibility information

## Project Structure

```
schema-sentinel/
├── schema_sentinel/              # Main package
│   ├── __init__.py              # Package initialization
│   ├── markdown_utils/           # Markdown report generation
│   │   └── markdown.py
│   └── metadata_manager/         # Core metadata management
│       ├── engine.py            # Database connection engines
│       ├── metadata.py          # Metadata extraction logic
│       ├── changeset.py         # Change detection and tracking
│       ├── enums.py             # Enumerations and constants
│       ├── utils.py             # Utility functions
│       ├── model/               # Data models
│       │   ├── database.py      # Database model
│       │   ├── schema.py        # Schema model
│       │   ├── table.py         # Table model
│       │   ├── column.py        # Column model
│       │   ├── view.py          # View model
│       │   ├── procedure.py     # Stored procedure model
│       │   ├── function.py      # Function model
│       │   ├── constraint.py    # Constraint models
│       │   └── ...              # Other object models
│       └── lookup/              # Reference data
│           └── sql_data_type.py
├── resources/                    # Configuration and templates
│   ├── db.properties            # Database config template
│   ├── datacompy/templates/     # Report templates
│   └── migrations-ddl/          # DDL migration procedures
├── tests/                        # Test suite
├── notebooks/                    # Jupyter notebooks for exploration
└── docs/                         # API documentation
```

## Supported Database Objects

Schema Sentinel can extract and compare the following database objects:

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

## Data Flow

### 1. Metadata Extraction Flow

```
User Request
    │
    ▼
Database Engine (engine.py)
    │
    ▼
Query Database (Snowflake)
    │
    ▼
Parse Results (metadata.py)
    │
    ▼
Create Model Objects (model/*)
    │
    ▼
Store in SQLite (optional)
    │
    ▼
Return Metadata Container
```

### 2. Comparison Flow

```
Source Metadata ─┐
                 │
Target Metadata ─┼─▶ Changeset (changeset.py)
                 │       │
                 │       ▼
                 │   Detect Differences
                 │       │
                 │       ▼
                 │   Generate Changes
                 │       │
                 └───────┼─▶ Report Generator
                         │
                         ▼
                   Output Reports
                   (Markdown/HTML/JSON)
```

## Database Engine Architecture

The engine layer provides an abstraction for different database types:

```python
class Engine:
    """Base engine class"""
    def connect()
    def execute_query()
    def extract_metadata()
    def disconnect()

class SnowflakeEngine(Engine):
    """Snowflake-specific implementation"""
    # Snowflake-specific queries and handling
```

**Current Support:**
- ✅ Snowflake (fully supported)
- 🚧 PostgreSQL (planned)
- 🚧 MySQL (planned)
- 🚧 DuckDB (planned - see [Future Development Plan](Future-Development-Plan.md))

## Extensibility Points

### Adding a New Database Engine

1. Create a new engine class in `engine.py`
2. Implement the required interface methods
3. Add database-specific metadata extraction queries
4. Update connection configuration handling

### Adding a New Object Type

1. Create a model in `schema_sentinel/metadata_manager/model/`
2. Add extraction logic in `metadata.py`
3. Update comparison logic in `changeset.py`
4. Add report templates in `resources/datacompy/templates/`

## Technology Stack

- **Python 3.9+** - Core language
- **SQLAlchemy 1.4.x** - Database abstraction and ORM
- **Pydantic 2.0+** - Data validation and models
- **Snowflake SQLAlchemy** - Snowflake connector
- **Pandas** - Data manipulation
- **Jinja2** - Template engine for reports
- **Markdown/HTML** - Report generation
- **pytest** - Testing framework
- **Ruff** - Linting and formatting
- **mypy** - Type checking
- **uv** - Package management

## Performance Considerations

### Optimization Strategies

1. **Parallel Processing** - Extract metadata from multiple schemas in parallel
2. **Connection Pooling** - Reuse database connections
3. **Batch Operations** - Process multiple objects in single queries
4. **Caching** - Cache metadata when appropriate
5. **Incremental Updates** - Only extract changes when possible

### Scalability

The architecture is designed to handle:
- Large numbers of database objects (1000+ tables)
- Multiple concurrent extractions
- Historical tracking over long periods
- Large comparison reports

## Security Architecture

### Credential Management

- Environment variable-based configuration
- Support for external secret managers
- No credentials in code or version control

### Data Security

- Metadata is sensitive - treat as confidential
- Reports may contain schema details
- Access control for generated reports

See [Security Guide](Security.md) for detailed security information.

## Future Architecture Enhancements

See the [Future Development Plan](Future-Development-Plan.md) for planned architectural improvements including:

- DuckDB integration for enhanced comparison capabilities
- Extensible plugin architecture for database engines
- Enhanced data comparison with configurable rules
- REST API layer
- Web UI for visualization

## Additional Resources

- [Development Guide](Development.md) - How to work with the codebase
- [Contributing Guide](Contributing.md) - How to contribute
- [API Documentation](https://github.com/Igladyshev/schema-sentinel/tree/master/docs)
