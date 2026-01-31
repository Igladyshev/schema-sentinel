# Pre-Release Checklist for Open Source

Use this checklist before making your first public release or pushing to a public repository.

## 🔒 Security Review

- [x] Removed all hardcoded credentials from source code
- [x] Deleted files with AWS keys, passwords, API tokens
- [x] Enhanced `.gitignore` to prevent future credential commits
- [x] Replaced company-specific account identifiers
- [ ] **MANUAL**: Clear all Jupyter notebook outputs
  ```bash
  # If jupyter is installed:
  jupyter nbconvert --clear-output --inplace *.ipynb

  # Or manually in Jupyter: Cell -> All Output -> Clear
  ```
- [ ] **CRITICAL**: Review git history for previously committed secrets
  ```bash
  # Check for potential secrets in git history
  git log -p | grep -i "password\|secret\|key\|token" | head -20

  # If secrets found, use git-filter-repo or BFG Repo-Cleaner
  # See: https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository
  ```

## 🏢 Proprietary Information

- [x] Removed company name references (`caesars`, `Caesars`)
- [x] Replaced internal database names (`SDP` → `MY_DATABASE`)
- [x] Removed business-specific table names and logic
- [x] Replaced internal Snowflake account names
- [x] Removed internal user references
- [x] Deleted company-specific configuration directories
- [ ] **MANUAL**: Review and update Jupyter notebooks with generic examples

## 📝 Documentation

- [x] Updated README.md with generic examples
- [x] Created configuration templates (.example files)
- [x] Added SANITIZATION_SUMMARY.md documenting changes
- [x] Enhanced .env.example with new configuration options
- [x] Created db.properties.example template
- [ ] Update SECURITY.md with actual security contact email (currently placeholder)
- [ ] Review CONTRIBUTING.md - ensure no internal references
- [ ] Review CHANGELOG.md - add sanitization changes if needed

## 🔧 Code Quality

- [ ] Run tests to ensure refactoring didn't break functionality
  ```bash
  pytest
  ```
- [ ] Run linting
  ```bash
  ruff check .
  ruff format --check .
  ```
- [ ] Run type checking
  ```bash
  mypy sql_comparison
  ```
- [ ] Test with generic configuration to ensure it works

## 🌍 Environment Variables

Users will need to set these environment variables. Document them:

- [ ] `SNOWFLAKE_ACCOUNT` - Their Snowflake account identifier
- [ ] `SNOWFLAKE_USER` - Their username or email
- [ ] `SNOWFLAKE_EMAIL_DOMAIN` - (Optional) For SSO authentication
- [ ] `REPORT_AUTHOR` - (Optional) For report metadata
- [ ] Verify all required variables are documented in .env.example

## 📦 Repository Setup

- [ ] Update repository description on GitHub
- [ ] Add topics/tags: `snowflake`, `database`, `metadata`, `schema-comparison`, `data-engineering`
- [ ] Set up GitHub Discussions (optional but recommended)
- [ ] Enable Issues if not already enabled
- [ ] Configure branch protection rules for `master`/`main`
- [ ] Set up GitHub Actions secrets (if any CI/CD needs them)

## 📜 License and Legal

- [x] LICENSE file exists (Apache 2.0)
- [ ] Verify LICENSE applies to all code
- [ ] Add license headers to source files if required by your org
- [ ] If using third-party code, verify license compatibility

## 🎯 Final Checks

- [ ] Create a fresh clone and test installation
  ```bash
  git clone <your-repo-url> /tmp/test-clone
  cd /tmp/test-clone
  ./setup.sh
  # Test basic functionality
  ```
- [ ] Verify no `.env` or `*.properties` files are tracked
  ```bash
  git ls-files | grep -E '\.env$|\.properties$'
  # Should only return .env.example and template files
  ```
- [ ] Check for any TODO comments related to sanitization
  ```bash
  git grep -i "TODO.*sanitize\|FIXME.*proprietary"
  ```
- [ ] Review open issues/PRs for any proprietary information

## 🚀 Release Preparation

- [ ] Update version number in `pyproject.toml`
- [ ] Update CHANGELOG.md with sanitization changes
- [ ] Create release notes highlighting:
  - Breaking changes (configuration now required)
  - Migration guide for existing users
  - New environment variable requirements
- [ ] Tag the release
  ```bash
  git tag -a v2.1.0 -m "First open source release"
  git push origin v2.1.0
  ```

## 📢 Communication

If this was previously used internally:

- [ ] Notify internal users about configuration changes
- [ ] Provide migration guide
- [ ] Update internal documentation/wiki
- [ ] Consider hosting a brief Q&A session

## ✅ Ready for Public Release

Once all items are checked:

```bash
# Make repository public on GitHub:
# Settings → Danger Zone → Change repository visibility → Make public

# Or push to a new public repository
git remote add public https://github.com/yourusername/sql-comparison.git
git push public master
```

---

## 🆘 If You Find Secrets After Release

1. **Immediately** rotate/invalidate the exposed secrets
2. Remove secrets from git history using git-filter-repo or BFG Repo-Cleaner
3. Force push cleaned history (if repository is new/not widely used)
4. If widely used, document the incident and remediation
5. Consider security advisory on GitHub

---

**Date Sanitization Completed**: January 30, 2026
**Reviewed By**: [Your Name]
**Next Review Date**: Before first public release
