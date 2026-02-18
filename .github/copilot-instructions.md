# GitHub Copilot Instructions - Data Engineering

## Profile & Tech Stack
- **Primary Language:** Python 3.13+
- **Data Platforms:** Snowflake, PostgreSQL, MySQL, SQLite
- **Tools:** SQL, YAML, GitLab CI/CD, Schema Management, GitHub Actions
- **Testing Framework:** pytest
- **Documentation:** Google-style docstrings, Markdown for README and docs
- **Style Guide:** PEP 8 with some project-specific conventions
- **Style:** Functional and Modular. Prefer Type Hinting and Pydantic for data validation.

## Workflow & Validation Requirements
- **Tooling:** This project uses `uv` for dependency and task management.
- **Mandatory Checks:** After making any code changes, YOU MUST verify the changes by running:
  1. `uv run ruff check --fix .` (to lint and auto-fix issues)
  2. `uv run ruff format` (to ensure consistent styling)
- **Zero-Error Policy:** Do not consider a task "Done" or "Complete" if there are remaining Ruff linting errors or formatting inconsistencies.
- **Execution:** Always attempt to run these commands using the terminal/agent capabilities before presenting the final solution.

## Coding Preferences
- **Snowflake:** Use upper-case for SQL keywords. Prefer `snowflake-connector-python` or `Snowpark` patterns.
- **YAML Handling:** When writing "shredders" or parsers, ensure strict schema validation.
- **Error Handling:** Use explicit try-except blocks with logging. Avoid bare `except:`.
- **Testing:** Generate `pytest` suites for all new utility functions.

## Documentation
- Use Google-style docstrings.
- Always include a brief "How it works" comment for complex SQL transformations.
