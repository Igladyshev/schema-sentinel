# Notebooks - Important Note

The Jupyter notebooks in this project may contain example data and company-specific references. Before sharing or publishing:

1. **Clear all outputs**: Run "Clear All Outputs" in Jupyter before committing
2. **Update example data**: Replace any company-specific:
   - Email addresses (e.g., change `user@company.com` to `user@example.com`)
   - Database names (e.g., change proprietary names to `ANALYTICS_DB`, `MY_DATABASE`)
   - Account identifiers
   - User names

## Notebooks in this project:

- **YAML_Shredder_Demo.ipynb**: Comprehensive demonstration of YAML Shredder and Comparator features
- **SQLLite + SQLAlchemy.ipynb**: Examples of metadata storage and querying
- **Pandas Diff.ipynb**: Examples of database comparison using pandas
- **Object Comparison.ipynb**: Object-level comparison examples

---

## YAML Shredder Demo Notebook

**File:** `notebooks/YAML_Shredder_Demo.ipynb`

### What it demonstrates:

This notebook provides a comprehensive, hands-on guide to using Schema Sentinel's YAML Shredder and Comparator tools. It covers:

1. **Structure Analysis** - Analyze nested YAML/JSON structures
2. **Table Generation** - Convert nested data into normalized relational tables
3. **Database Loading** - Store tables in SQLite with indexes
4. **DDL Generation** - Create SQL schemas for Snowflake (example pattern can be adapted to other database dialects)
5. **YAML Comparison** - Compare two YAML files to detect configuration drift
6. **Report Generation** - Generate detailed markdown comparison reports
7. **Documentation Generation** - Auto-generate markdown docs from YAML files

### How to test/verify:

#### Prerequisites:
```bash
# Ensure you have the required dependencies installed
pip install -e .
# or
uv pip install -e .

# Install Jupyter if not already installed
pip install jupyter
```

#### Running the notebook:
```bash
# Navigate to the repository root
cd /path/to/schema-sentinel

# Launch Jupyter
jupyter notebook notebooks/YAML_Shredder_Demo.ipynb
```

#### Verification steps:

1. **Run all cells sequentially** (Cell → Run All)
   - Verify no errors occur
   - Check that all outputs display correctly

2. **Check Section 1 (Setup)** 
   - Confirms yaml_shredder package is importable
   - Displays version information

3. **Check Section 4 (Structure Analysis)**
   - Verify output shows analyzed YAML structure
   - Should display nested element counts and types

4. **Check Section 5 (Table Generation)**
   - Verify tables are generated (e.g., CONFIG_V1, CONFIG_V2, SERVICES, etc.)
   - Check table schemas are displayed correctly

5. **Check Section 6 (SQLite Loading)**
   - Verify database file is created in temp directory
   - Check summary shows loaded tables

6. **Check Section 7 (DDL Generation)**
   - Verify SQL DDL statements are generated
   - Should show CREATE TABLE statements for Snowflake dialect

7. **Check Section 8-9 (YAML Comparison)**
   - Verify comparison between config_v1.yaml and config_v2.yaml
   - Check row count differences are displayed
   - Verify comparison report is generated

8. **Check Section 10 (Documentation)**
   - Verify markdown documentation is generated
   - Check preview shows proper formatting

9. **Check Section 11 (Summary)**
   - Verify summary of capabilities is displayed
   - Check list of generated files

10. **Verify temp files are created**
    - The notebook creates files in `/tmp/yaml_shredder_demo/`
    - Check that config files, databases, and reports are created

### What reviewers should look for:

#### Code Quality:
- [ ] Notebook cells are well-organized and logically structured
- [ ] Each section has clear markdown descriptions
- [ ] Code is well-commented where needed
- [ ] Examples use realistic, production-like configurations

#### Functionality:
- [ ] All imports work correctly
- [ ] Each feature demonstration completes without errors
- [ ] Output is clear and informative
- [ ] Temporary files are created in appropriate locations

#### Documentation:
- [ ] Section headers clearly describe what's being demonstrated
- [ ] Markdown cells provide context and explanations
- [ ] Code comments explain non-obvious operations
- [ ] Summary section provides clear takeaways

#### Educational Value:
- [ ] Examples progress from simple to complex
- [ ] Each section builds on previous knowledge
- [ ] Real-world use cases are highlighted
- [ ] Output demonstrates the value of each feature

#### Data Safety:
- [ ] No sensitive or company-specific data in examples
- [ ] All outputs should be cleared before committing (see cleanup section below)
- [ ] Example data uses generic names (example.com, CONFIG, etc.)

#### Edge Cases:
- [ ] Handles nested structures correctly
- [ ] Works with arrays and objects
- [ ] Properly handles YAML and JSON formats
- [ ] Demonstrates both simple and complex configurations

### Expected outputs:

When run successfully, the notebook should generate:
- **Temporary directory**: `/tmp/yaml_shredder_demo/`
- **YAML files**: `config_v1.yaml`, `config_v2.yaml`
- **Database files**: `config.db`, plus comparison databases
- **Comparison report**: `comparison_report.md`
- **Documentation**: Markdown files in `docs/` subdirectory

### Troubleshooting:

**Import errors:**
- Ensure the package is installed: `pip install -e .`
- Check Python path includes the repository root

**Missing dependencies:**
- Install Jupyter: `pip install jupyter`
- Install pandas: `pip install pandas`
- Install PyYAML: `pip install pyyaml`

**Permission errors:**
- Check write permissions to `/tmp/`
- Try running with appropriate permissions

---

## Recommended cleanup:

```bash
# Clear all notebook outputs before committing
jupyter nbconvert --clear-output --inplace *.ipynb
```

Or use the Jupyter interface: `Cell -> All Output -> Clear`
