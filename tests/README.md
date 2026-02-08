# Tests README

## Running Tests

Most tests can be run without any special setup:

```bash
pytest tests/
```

## MPM-Specific Tests

Some tests reference proprietary MPM YAML files located in `resources/master-mpm/`. These files are **not included in the public repository** for privacy reasons.

Tests that require MPM data:
- `test_mpm_schema.py`
- `test_mpm_parser.py`
- `test_mpm_snowpark.py`

These tests will be **skipped** if the `resources/master-mpm/` directory is not present.

### For Internal Development

If you have access to the MPM data files, place them in:
```
resources/master-mpm/
├── XY/
│   └── XY_123-mpm.yaml
├── AB/
│   └── AB_456-mpm.yaml
├── CD/
│   └── CD_789-mpm.yaml
└── EF/
    └── EF_012-mpm.yaml
```

The tests will automatically detect and use these files if available.

### For External Contributors

You can safely ignore these test files - they test proprietary functionality not needed for general YAML Shredder usage. Focus on:
- `test_config.py` - Configuration management tests
- `test_imports.py` - Import validation tests
- Other generic tests as added

All core functionality has tests that don't require proprietary data.
