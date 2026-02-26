# Branching Strategy

This document outlines the branching strategy and branch protection rules for the Schema Sentinel project.

## Overview

We use a simple two-branch strategy:
- **`master`**: The protected production branch
- **`dev`**: The development/feature branch

## Branch Descriptions

### Master Branch

The `master` branch represents the stable, production-ready code. It is protected with strict rules to ensure code quality and stability.

**Protection Rules:**
- ✅ Requires pull request reviews (minimum 1 approval)
- ✅ All CI checks must pass before merging:
  - Tests on Python 3.9, 3.10, 3.11, 3.12
  - Code linting and formatting checks
  - Type checking
- ✅ Cannot be deleted
- ✅ Force pushes are disabled
- ✅ Linear history required (no merge commits)
- ✅ Stale reviews are dismissed on new pushes

**When to use:**
- Merging completed, tested, and reviewed features
- Creating release tags
- Production deployments

### Dev Branch

The `dev` branch is the primary development branch where features are integrated and tested together.

**Protection Rules:**
- ✅ Basic linting checks required
- ✅ Cannot be deleted
- ⚠️ Allows direct pushes (for rapid development)
- ⚠️ Less strict than master

**When to use:**
- Merging feature branches
- Integration testing
- Pre-release testing
- Collaborative development

## Workflow

### Feature Development

1. **Create a feature branch** from `dev`:
   ```bash
   git checkout dev
   git pull origin dev
   git checkout -b feature/your-feature-name
   ```

2. **Develop your feature** with regular commits:
   ```bash
   git add .
   git commit -m "feat: add your feature description"
   ```

3. **Push your feature branch**:
   ```bash
   git push origin feature/your-feature-name
   ```

4. **Create a Pull Request** to merge into `dev`:
   - Add a clear description
   - Link related issues
   - Request reviews from team members

5. **After review and approval**, merge to `dev`

### Release Process

1. **Test thoroughly on `dev`** branch
   
2. **Create a Pull Request** from `dev` to `master`:
   - Ensure all CI checks pass
   - Get required approvals
   - Verify all tests pass

3. **Merge to `master`** once approved

4. **Tag the release** on master:
   ```bash
   git checkout master
   git pull origin master
   git tag -a v1.0.0 -m "Release version 1.0.0"
   git push origin v1.0.0
   ```

### Hotfix Process

For urgent fixes to production:

1. **Create hotfix branch** from `master`:
   ```bash
   git checkout master
   git pull origin master
   git checkout -b hotfix/critical-fix
   ```

2. **Implement the fix** and test thoroughly

3. **Create PR to `master`** with clear description of the issue

4. **After merging to master**, also merge back to `dev`:
   ```bash
   git checkout dev
   git merge master
   git push origin dev
   ```

## Branch Naming Conventions

- **Feature branches**: `feature/description` or `feature/issue-number-description`
- **Bug fixes**: `fix/description` or `bugfix/issue-number-description`
- **Hotfixes**: `hotfix/description`
- **Documentation**: `docs/description`
- **Refactoring**: `refactor/description`
- **Chores**: `chore/description`

## Pull Request Guidelines

### To Dev Branch
- At least one approval recommended (but not required)
- All automated checks must pass
- Keep PRs focused and reasonably sized
- Include tests for new features

### To Master Branch
- **Mandatory**: At least one approval required
- **Mandatory**: All CI checks must pass
- Comprehensive testing required
- Updated documentation
- CHANGELOG.md updated

## CI/CD Integration

Both `master` and `dev` branches trigger CI workflows on push and pull requests:

- **Test Suite**: Runs on Python 3.9, 3.10, 3.11, 3.12
- **Linting**: Ruff format and lint checks
- **Type Checking**: mypy validation
- **Coverage**: Code coverage reporting

## Bypassing Rules

Repository administrators can bypass branch protection rules when absolutely necessary. This should be used sparingly and only in exceptional circumstances.

## Updating Branch Rules

Branch protection rules are defined in `.github/rulesets/`:
- `master-branch-protection.json` - Rules for master branch
- `dev-branch-rules.json` - Rules for dev branch

To modify these rules:
1. Edit the appropriate JSON file
2. Create a PR with the changes
3. Get approval from repository maintainers
4. After merge, rules will be applied (may require manual import in GitHub Settings)

## Questions?

If you have questions about the branching strategy or need clarification on the workflow, please:
- Open an issue with the `question` label
- Refer to [CONTRIBUTING.md](CONTRIBUTING.md) for general contribution guidelines
- Contact the repository maintainers

---

**Note**: These branch rules help maintain code quality and stability. Following these guidelines ensures a smooth development and release process for the entire team.
