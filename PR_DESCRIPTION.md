# Pull Request: YAML Comparison & CLI Reorganization

## What does this PR do?

**New Features:**
- Add YAML comparison feature - compare two YAML files by converting to SQLite databases and analyzing differences
- Implement `YAMLComparator` class with methods for loading, comparing, and reporting
- Add `compare` command to YAML CLI group for easy YAML file comparison

**Refactoring:**
- Reorganize CLI into logical command groups (`yaml` and `schema`)
- Move all YAML/JSON processing commands under `yaml` group
- Move Snowflake schema operations under `schema` group

**Tests:**
- Add comprehensive CLI test suite with 40+ test cases
- Add YAML comparator test suite with 10 tests
- Cover command structure, options, error handling, and integration workflows

**Documentation:**
- Add YAML_COMPARISON.md guide
- Add CLI_STRUCTURE.md with migration guide
- Update README with new CLI structure and examples

## Why?

This PR enhances Schema Sentinel with two major improvements:

1. **YAML Comparison Feature** - Enables configuration drift detection, version comparison, and deployment validation by comparing YAML files structurally
   - Use case: Compare dev vs prod configurations
   - Use case: Track configuration changes over time
   - Use case: Validate config changes before deployment

2. **CLI Organization** - Improves usability and discoverability by grouping related commands
   - Better command discovery through logical grouping
   - More scalable structure for future features
   - Industry-standard CLI organization pattern

**Commits:** 3
**Branch:** `feature/yaml-comparer` → `dev`

## How to test?

### Test YAML Comparison
```bash
# Compare two YAML files
uv run schema-sentinel yaml compare file1.yaml file2.yaml -o report.md

# With database preservation
uv run schema-sentinel yaml compare config1.yaml config2.yaml --keep-dbs --root-name deployment
```

### Test CLI Reorganization
```bash
# Check help output shows command groups
uv run schema-sentinel --help

# Test yaml commands
uv run schema-sentinel yaml --help
uv run schema-sentinel yaml analyze config.yaml
uv run schema-sentinel yaml shred config.yaml -db test.db

# Test schema commands
uv run schema-sentinel schema --help
uv run schema-sentinel schema extract MY_DB --env dev
```

### Run Tests
```bash
# Run all tests
uv run pytest tests/ -v

# Run specific test suites
uv run pytest tests/test_yaml_comparator.py -v
uv run pytest tests/test_cli.py -v
```

## Notes

⚠️ **BREAKING CHANGE** - CLI commands moved from root level to command groups

### Migration Required

| Old Command | New Command |
|-------------|-------------|
| `schema-sentinel analyze` | `schema-sentinel yaml analyze` |
| `schema-sentinel schema` | `schema-sentinel yaml schema` |
| `schema-sentinel tables` | `schema-sentinel yaml tables` |
| `schema-sentinel ddl` | `schema-sentinel yaml ddl` |
| `schema-sentinel load` | `schema-sentinel yaml load` |
| `schema-sentinel shred` | `schema-sentinel yaml shred` |
| `schema-sentinel compare-yaml` | `schema-sentinel yaml compare` |
| `schema-sentinel extract` | `schema-sentinel schema extract` |
| `schema-sentinel compare` | `schema-sentinel schema compare` |

### Files Changed
- **New files:**
  - `schema_sentinel/yaml_comparator.py` - Core comparison logic
  - `tests/test_yaml_comparator.py` - Comparator tests
  - `tests/test_cli.py` - CLI tests
  - `.github/workflows/pr-description.yml` - Auto PR description generator
  - `resources/examples/example_yaml_comparison.py` - Usage example
  - `CLI_STRUCTURE.md` - CLI documentation
  - `YAML_COMPARISON.md` - Comparison guide

- **Modified files:**
  - `schema_sentinel/cli.py` - CLI reorganization
  - `schema_sentinel/__init__.py` - Export YAMLComparator
  - `README.md` - Updated documentation

### Documentation
- See [CLI_STRUCTURE.md](CLI_STRUCTURE.md) for complete CLI reference
- See [YAML_COMPARISON.md](YAML_COMPARISON.md) for YAML comparison guide
- All changes backward compatible via Python API

---

<details>
<summary>📋 Detailed Commit List</summary>

Based on recent commits:
- Add YAML comparison feature with YAMLComparator class
- Reorganize CLI into command groups (yaml and schema)
- Add comprehensive CLI test suite
- Update documentation with new structure

</details>
