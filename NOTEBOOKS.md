# Notebooks - Important Note

The Jupyter notebooks in this project may contain example data and company-specific references. Before sharing or publishing:

1. **Clear all outputs**: Run "Clear All Outputs" in Jupyter before committing
2. **Update example data**: Replace any company-specific:
   - Email addresses (e.g., change `user@company.com` to `user@example.com`)
   - Database names (e.g., change proprietary names to `ANALYTICS_DB`, `MY_DATABASE`)
   - Account identifiers
   - User names

## Notebooks in this project:

- **SQLLite + SQLAlchemy.ipynb**: Examples of metadata storage and querying
- **Pandas Diff.ipynb**: Examples of database comparison using pandas
- **Object Comparison.ipynb**: Object-level comparison examples

## Recommended cleanup:

```bash
# Clear all notebook outputs before committing
jupyter nbconvert --clear-output --inplace *.ipynb
```

Or use the Jupyter interface: `Cell -> All Output -> Clear`
