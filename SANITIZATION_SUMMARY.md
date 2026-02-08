# Data Sanitization Summary

This document tracks the sanitization of proprietary data from the codebase to ensure no confidential information is committed to version control.

## Overview

All proprietary business data, deployment codes, and identifiable information have been replaced with generic, randomly-generated equivalents that maintain the same structure and format.

## Changes Made

### 1. Proprietary Data Exclusions (.gitignore)

**Added to .gitignore:**
- `resources/master-mpm/` - Contains proprietary MPM YAML configuration files (already excluded)
- `notebooks/` - May contain proprietary analysis and data exploration (newly added)

These directories and their contents will never be committed to the repository.

### 2. Code References Sanitized

All proprietary references have been replaced with generic, randomly-generated equivalents:

**Deployment Codes:**
- Format: Two-letter code + underscore + three-digit number
- Examples used: `XY_123`, `AB_456`, `CD_789`, `EF_012`

**Domain Codes:**
- Format: Two-letter codes
- Examples used: `XY`, `AB`, `CD`, `EF`

**Community/Business Names:**
- Format: Generic region/location names
- Examples used: `Region_Alpha`, `Region_Beta`, `Region_Gamma`, `Region_Delta`

**Database Stage Names:**
- Format: `GENERIC_REPORTING.<DEPLOYMENT_CODE>.REPORTING`
- Example: `GENERIC_REPORTING.XY_123.REPORTING`

### 3. Files Modified

**Example Scripts:**
- `resources/examples/example_ddl_generation.py`
- `resources/examples/example_sqlite_workflow.py`
- `resources/examples/example_yaml_comparison.py`
- `resources/examples/test_yaml_shredder.py`
- `resources/examples/test_schema_generation.py`
- `resources/examples/test_mpm_parser.py`
- `resources/examples/test_mpm_schema.py`
- `resources/examples/test_mpm_snowpark.py`

**Documentation:**
- `tests/README.md` - Updated directory structure examples

**Configuration:**
- `.gitignore` - Added exclusions for proprietary data directories

### 4. Test Data Strategy

**Tests that Reference Proprietary Data:**
All MPM-related test files now:
1. Reference generic codes (XY_123, AB_456, etc.)
2. Include `pytest.mark.skipif` decorators to skip when proprietary data is unavailable
3. Clearly document that they require local proprietary data files

**For External Contributors:**
The test suite works without proprietary data. All core functionality tests use generic test data or mock objects.

**For Internal Development:**
If you have access to proprietary MPM files, place them in `resources/master-mpm/` (gitignored) and tests will automatically detect and use them.

## Verification Checklist

- [x] All proprietary deployment codes replaced
- [x] All proprietary business/community names replaced
- [x] Proprietary data directories added to .gitignore
- [x] Notebooks directory added to .gitignore
- [x] Documentation updated with generic examples
- [x] Test files use generic references
- [x] No hardcoded credentials or API keys present

## Data Classification

**Proprietary/Confidential (Never Commit):**
- Actual MPM YAML files in `resources/master-mpm/`
- Real deployment codes matching actual business entities
- Real business/community names
- Analysis notebooks with real data
- Database files with real data

**Generic/Public (Safe to Commit):**
- Generic deployment codes (XY_123, AB_456, CD_789, EF_012)
- Generic community names (Region_Alpha, Region_Beta, etc.)
- Example YAML files in `resources/examples/`
- Test data structures
- Documentation

## Maintenance

When adding new code or examples:
1. Use generic codes (XY_123, AB_456, etc.) instead of real deployment codes
2. Use generic names (Region_Alpha, etc.) instead of real business names
3. Store any real data files in gitignored directories
4. Update this document if new sanitization patterns are needed

## Questions?

If you're unsure whether data is proprietary:
- Real deployment codes that map to real businesses → Proprietary
- Real business/property names → Proprietary
- Example/test data with generic names → Safe to commit
- When in doubt, ask or add to .gitignore

---

**Last Updated:** February 8, 2026
**Maintained By:** Engineering Team
