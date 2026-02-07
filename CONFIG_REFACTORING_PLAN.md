# Configuration Refactoring Plan

## Current State Analysis

### Global Variables Identified

#### 1. **schema_sentinel/__init__.py**
```python
PROJECT_NAME = "schema-sentinel"
TEMP_DIR = os.getenv("TEMP") if os.name == "nt" else "/tmp"
LOG_FILE = os.path.join(TEMP_DIR, "schema-sentinel.log")
LOG_LEVEL = os.getenv("LOG_LEVEL") or "INFO"
PROJECT_HOME = os.path.dirname(os.path.join(os.path.abspath("./"), PROJECT_NAME))
RESOURCES_PATH = os.path.join(PROJECT_HOME, "resources")
META_DB_PATH = os.path.join(RESOURCES_PATH, "meta-db")
```

#### 2. **schema_sentinel/metadata_manager/model/__init__.py** (DUPLICATE)
```python
# Same variables duplicated here
PROJECT_NAME = "schema-sentinel"
TEMP_DIR = ...
LOG_FILE = ...
LOG_LEVEL = ...
PROJECT_HOME = ...
RESOURCES_PATH = ...
META_DB_PATH = ...
ATTRIBUTES_TO_EXCLUDE = [...]  # Large list of excluded attributes
```

#### 3. **schema_sentinel/metadata_manager/enums.py**
```python
DATA_RETENTION_TIME_IN_DAYS = 7
```

#### 4. **schema_sentinel/metadata_manager/utils.py**
```python
ACCOUNT_MAP = {"dev": "...", "staging": "...", "prod": "..."}
ENV_MAP = {"dev": "DEV", "staging": "STAGING", "prod": "PROD"}
CUSTOM_VIEW_FILTERS = {...}  # Complex nested dict for business logic
```

#### 5. **Scattered Path Definitions**
- Multiple scripts use hardcoded paths like:
  - `Path("resources/meta-db/schema-sentinel.db")`
  - `Path("resources/master-mpm/...")`
  - Output directories in example scripts

---

## Difficulty Assessment: **MEDIUM** ⚠️

### Why Medium (not Easy):
1. **Duplicate Definitions**: Variables defined in 2 places (`__init__.py` and `model/__init__.py`)
2. **Import Dependencies**: Many modules import these directly
3. **Path Calculation Logic**: `PROJECT_HOME` uses runtime path resolution
4. **Logging Setup**: Log configuration happens at module import time
5. **Testing Impact**: Will need to update all tests

### Why Medium (not Hard):
1. **No Complex State**: Variables are simple constants/paths
2. **No Threading Issues**: No concurrent modification concerns
3. **Clear Boundaries**: All config is at module level
4. **Small Codebase**: Limited number of files to update

---

## Proposed Solution: Configuration Manager

### Architecture

```
schema_sentinel/
├── config/
│   ├── __init__.py         # Exports ConfigManager singleton
│   ├── manager.py          # ConfigManager class
│   ├── defaults.py         # Default configuration values
│   └── schema.py           # Config validation schema (optional)
├── config.yaml             # User configuration file (optional)
└── .env                    # Environment variables (existing)
```

### Implementation Plan

#### Phase 1: Create Configuration Manager (2-3 hours)
**File: `schema_sentinel/config/manager.py`**

```python
from pathlib import Path
from typing import Dict, Any, Optional
import os
from dataclasses import dataclass, field
import yaml
from functools import lru_cache


@dataclass
class PathConfig:
    """Path-related configuration."""
    project_name: str = "schema-sentinel"
    project_home: Optional[Path] = None
    temp_dir: Optional[Path] = None
    resources_dir: Optional[Path] = None
    meta_db_dir: Optional[Path] = None

    def __post_init__(self):
        # Auto-calculate paths if not provided
        if self.project_home is None:
            self.project_home = Path(os.path.dirname(
                os.path.join(os.path.abspath("./"), self.project_name)
            ))

        if self.temp_dir is None:
            self.temp_dir = Path(os.getenv("TEMP", "/tmp"))

        if self.resources_dir is None:
            self.resources_dir = self.project_home / "resources"

        if self.meta_db_dir is None:
            self.meta_db_dir = self.resources_dir / "meta-db"


@dataclass
class LogConfig:
    """Logging configuration."""
    level: str = "INFO"
    file: Optional[Path] = None
    format: str = "%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s"

    def __post_init__(self):
        self.level = os.getenv("LOG_LEVEL", self.level)
        if self.file is None:
            temp_dir = os.getenv("TEMP", "/tmp")
            self.file = Path(temp_dir) / "schema-sentinel.log"


@dataclass
class DatabaseConfig:
    """Database-related configuration."""
    data_retention_days: int = 7
    account_map: Dict[str, str] = field(default_factory=lambda: {
        "dev": os.getenv("SNOWFLAKE_DEV_ACCOUNT", "YOUR_DEV_ACCOUNT"),
        "staging": os.getenv("SNOWFLAKE_STAGING_ACCOUNT", "YOUR_STAGING_ACCOUNT"),
        "prod": os.getenv("SNOWFLAKE_PROD_ACCOUNT", "YOUR_PROD_ACCOUNT"),
    })
    env_map: Dict[str, str] = field(default_factory=lambda: {
        "dev": "DEV",
        "staging": "STAGING",
        "prod": "PROD",
    })


@dataclass
class MetadataConfig:
    """Metadata extraction configuration."""
    attributes_to_exclude: list = field(default_factory=lambda: [
        "database_id", "table_id", "environment", "version",
        "created", "last_altered", "schema_id", "id", "column_id",
        "last_suspended", "table_constraint_id", "column_constraint_id",
        "referential_constraint_id", "view_id", "pipe_id", "task_id",
        "stream_id", "function_id", "procedure_id", "last_ddl",
        "stale_after", "bytes", "row_count",
    ])
    custom_view_filters: Dict[str, Any] = field(default_factory=dict)


class ConfigManager:
    """Centralized configuration manager for Schema Sentinel."""

    _instance: Optional['ConfigManager'] = None

    def __init__(self, config_file: Optional[Path] = None):
        """Initialize configuration manager.

        Args:
            config_file: Optional path to YAML config file
        """
        self.paths = PathConfig()
        self.logging = LogConfig()
        self.database = DatabaseConfig()
        self.metadata = MetadataConfig()

        # Load from file if provided
        if config_file and config_file.exists():
            self._load_from_file(config_file)

    @classmethod
    def get_instance(cls, config_file: Optional[Path] = None) -> 'ConfigManager':
        """Get singleton instance of ConfigManager."""
        if cls._instance is None:
            cls._instance = cls(config_file)
        return cls._instance

    @classmethod
    def reset(cls):
        """Reset singleton instance (useful for testing)."""
        cls._instance = None

    def _load_from_file(self, config_file: Path):
        """Load configuration from YAML file."""
        with open(config_file) as f:
            config_data = yaml.safe_load(f)

        # Update configurations from file
        if "paths" in config_data:
            for key, value in config_data["paths"].items():
                if hasattr(self.paths, key):
                    setattr(self.paths, key, Path(value) if value else None)

        if "logging" in config_data:
            for key, value in config_data["logging"].items():
                if hasattr(self.logging, key):
                    setattr(self.logging, key, value)

        if "database" in config_data:
            for key, value in config_data["database"].items():
                if hasattr(self.database, key):
                    setattr(self.database, key, value)

        if "metadata" in config_data:
            for key, value in config_data["metadata"].items():
                if hasattr(self.metadata, key):
                    setattr(self.metadata, key, value)

    def to_dict(self) -> Dict[str, Any]:
        """Export configuration as dictionary."""
        return {
            "paths": {
                "project_name": self.paths.project_name,
                "project_home": str(self.paths.project_home),
                "temp_dir": str(self.paths.temp_dir),
                "resources_dir": str(self.paths.resources_dir),
                "meta_db_dir": str(self.paths.meta_db_dir),
            },
            "logging": {
                "level": self.logging.level,
                "file": str(self.logging.file),
                "format": self.logging.format,
            },
            "database": {
                "data_retention_days": self.database.data_retention_days,
                "account_map": self.database.account_map,
                "env_map": self.database.env_map,
            },
            "metadata": {
                "attributes_to_exclude": self.metadata.attributes_to_exclude,
                "custom_view_filters": self.metadata.custom_view_filters,
            },
        }


# Convenience function for getting config
@lru_cache(maxsize=1)
def get_config() -> ConfigManager:
    """Get the global configuration manager instance."""
    # Look for config file in common locations
    config_locations = [
        Path("schema_sentinel_config.yaml"),
        Path.home() / ".schema-sentinel" / "config.yaml",
        Path("/etc/schema-sentinel/config.yaml"),
    ]

    for config_file in config_locations:
        if config_file.exists():
            return ConfigManager.get_instance(config_file)

    return ConfigManager.get_instance()
```

#### Phase 2: Update All Imports (1-2 hours)

**Before:**
```python
from schema_sentinel import PROJECT_HOME, RESOURCES_PATH, META_DB_PATH
```

**After:**
```python
from schema_sentinel.config import get_config

config = get_config()
project_home = config.paths.project_home
resources_path = config.paths.resources_dir
meta_db_path = config.paths.meta_db_dir
```

#### Phase 3: Create Configuration File Template (30 min)

**File: `schema_sentinel_config.example.yaml`**

```yaml
# Schema Sentinel Configuration
# Copy this file to schema_sentinel_config.yaml and customize

# Path configuration
paths:
  # project_name: "schema-sentinel"  # Uncomment to override
  # project_home: null  # Auto-detected if not set
  # temp_dir: null  # Uses system temp dir if not set
  # resources_dir: null  # Auto-calculated from project_home
  # meta_db_dir: null  # Auto-calculated from resources_dir

# Logging configuration
logging:
  level: "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
  # file: null  # Uses temp_dir/schema-sentinel.log if not set
  format: "%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s"

# Database configuration
database:
  data_retention_days: 7
  account_map:
    dev: "${SNOWFLAKE_DEV_ACCOUNT:YOUR_DEV_ACCOUNT}"
    staging: "${SNOWFLAKE_STAGING_ACCOUNT:YOUR_STAGING_ACCOUNT}"
    prod: "${SNOWFLAKE_PROD_ACCOUNT:YOUR_PROD_ACCOUNT}"
  env_map:
    dev: "DEV"
    staging: "STAGING"
    prod: "PROD"

# Metadata extraction configuration
metadata:
  # Attributes to exclude from comparison
  attributes_to_exclude:
    - database_id
    - table_id
    - environment
    - version
    - created
    - last_altered
    # ... (full list)

  # Custom view filters for business logic
  custom_view_filters:
    FILTER_BY_ACCOUNT:
      TABLE_LIST: []
    EXCLUDE:
      TABLE_LIST: []
```

#### Phase 4: Migration Strategy (2-3 hours)

1. **Create backward compatibility layer** in `schema_sentinel/__init__.py`:
   ```python
   from schema_sentinel.config import get_config

   # Backward compatibility - deprecated
   _config = get_config()
   PROJECT_NAME = _config.paths.project_name
   PROJECT_HOME = str(_config.paths.project_home)
   RESOURCES_PATH = str(_config.paths.resources_dir)
   META_DB_PATH = str(_config.paths.meta_db_dir)
   TEMP_DIR = str(_config.paths.temp_dir)
   LOG_FILE = str(_config.logging.file)
   LOG_LEVEL = _config.logging.level

   import warnings
   warnings.warn(
       "Direct import of config variables is deprecated. "
       "Use 'from schema_sentinel.config import get_config' instead.",
       DeprecationWarning,
       stacklevel=2
   )
   ```

2. **Update each module gradually**:
   - Start with leaf modules (no dependencies)
   - Move to intermediate modules
   - Finally update top-level modules

3. **Remove duplicates** from `model/__init__.py`

4. **Update all hardcoded paths** in scripts and notebooks

#### Phase 5: Testing (1-2 hours)

1. Update `tests/conftest.py` with config fixtures:
   ```python
   @pytest.fixture
   def test_config():
       """Provide test configuration."""
       from schema_sentinel.config import ConfigManager
       config = ConfigManager()
       config.paths.project_home = Path("/tmp/test-schema-sentinel")
       config.paths.resources_dir = Path("/tmp/test-resources")
       return config
   ```

2. Add tests for ConfigManager
3. Run full test suite to verify no breakage

---

## Implementation Roadmap

### Total Estimated Time: **8-12 hours**

1. ✅ **Phase 1**: Create ConfigManager (2-3h)
2. ✅ **Phase 2**: Create config file template (30m)
3. ✅ **Phase 3**: Add backward compatibility (1h)
4. ✅ **Phase 4**: Update core modules (2-3h)
5. ✅ **Phase 5**: Update remaining files (2-3h)
6. ✅ **Phase 6**: Testing and validation (1-2h)
7. ✅ **Phase 7**: Documentation (1h)

### Risk Mitigation

- **Backward Compatibility**: Keep old imports working with deprecation warnings
- **Incremental Changes**: Update one module at a time
- **Comprehensive Testing**: Run tests after each phase
- **Rollback Plan**: Git branches for easy rollback

---

## Benefits

1. **✅ Single Source of Truth**: All configuration in one place
2. **✅ Easier Testing**: Mock configuration easily
3. **✅ User Customization**: YAML config file for user overrides
4. **✅ Environment Variables**: Support for 12-factor app pattern
5. **✅ Type Safety**: Dataclass-based configuration with type hints
6. **✅ Validation**: Can add schema validation later
7. **✅ No Import Duplication**: Remove duplicate definitions
8. **✅ Better Organization**: Clear separation of concerns

---

## Files to Update

### Core Files (Must Update)
- [x] Create: `schema_sentinel/config/__init__.py`
- [x] Create: `schema_sentinel/config/manager.py`
- [ ] Update: `schema_sentinel/__init__.py` (backward compat)
- [ ] Update: `schema_sentinel/metadata_manager/model/__init__.py` (remove duplicates)
- [ ] Update: `schema_sentinel/metadata_manager/utils.py` (use config)
- [ ] Update: `schema_sentinel/metadata_manager/enums.py` (use config)

### Script Files (Should Update)
- [ ] `yaml_shredder_cli.py`
- [ ] `example_sqlite_workflow.py`
- [ ] `example_ddl_generation.py`
- [ ] `test_yaml_shredder.py`
- [ ] `generate_mpm_schema.py`

### Notebook Files (Optional Update)
- [ ] `MPM Comparison and Migration.ipynb`
- [ ] `MPM Test Data Loading.ipynb`

### Test Files
- [ ] `tests/conftest.py` (add config fixtures)
- [ ] Create: `tests/test_config.py` (test ConfigManager)

---

## Alternative: Simpler Approach

If the full ConfigManager is too much, a **simpler option** (4-6 hours):

1. **Consolidate to single file**: `schema_sentinel/config.py`
2. **Keep simple module-level variables** but only in ONE place
3. **Add environment variable support**
4. **Update imports** to use single source

This would be **EASIER** but less flexible for future growth.

---

## Recommendation

**Go with full ConfigManager approach** because:
1. Project is growing (YAML Shredder added)
2. Users need customization options
3. Testing will be easier
4. Modern, maintainable approach
5. Time investment (8-12h) is reasonable for long-term benefits

The refactoring is **MEDIUM difficulty** and **HIGH value** for the project's future.
