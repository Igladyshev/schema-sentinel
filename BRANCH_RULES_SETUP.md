# Quick Start: Setting Up Branch Rules

This guide will help you apply the branch protection rules to your repository.

## What Has Been Created

✅ **Branch protection rulesets** for `master` and `dev` branches  
✅ **Comprehensive documentation** in [BRANCHING.md](BRANCHING.md)  
✅ **Updated contribution guidelines** in [CONTRIBUTING.md](CONTRIBUTING.md)

## Applying the Branch Rules

The branch protection rules are defined in `.github/rulesets/` as JSON files. GitHub does not automatically apply these from the repository - you need to import them manually.

### Step-by-Step Instructions

#### 1. Navigate to Repository Settings

Go to your repository on GitHub:
```
https://github.com/Igladyshev/schema-sentinel
```

Then click on **Settings** (you need admin access).

#### 2. Access Rulesets

In the left sidebar, under "Code and automation", click:
- **Rules** → **Rulesets**

Or go directly to:
```
https://github.com/Igladyshev/schema-sentinel/settings/rules
```

#### 3. Import Master Branch Protection

1. Click **New ruleset** → **New branch ruleset**
2. Click **Import a ruleset** (at the bottom)
3. Open the file `.github/rulesets/master-branch-protection.json` from this repository
4. Copy the entire content
5. Paste it into the import dialog
6. Click **Create** or **Import**

This will set up:
- ✅ Require PR reviews (1 approval minimum)
- ✅ Require all CI checks to pass
- ✅ Block force pushes
- ✅ Block branch deletion
- ✅ Require linear history

#### 4. Import Dev Branch Rules

1. Click **New ruleset** → **New branch ruleset** again
2. Click **Import a ruleset**
3. Open the file `.github/rulesets/dev-branch-rules.json`
4. Copy the entire content
5. Paste it into the import dialog
6. Click **Create** or **Import**

This will set up:
- ✅ Require lint checks to pass
- ✅ Block branch deletion
- ⚠️ Allow direct pushes (for rapid development)

#### 5. Verify the Rules

After importing both rulesets, you should see:
- **Master Branch Protection** - Active
- **Dev Branch Rules** - Active

You can click on each to review the applied rules.

## Alternative: Using GitHub API

If you prefer to use the GitHub API:

```bash
# Set your GitHub token
export GITHUB_TOKEN="your_personal_access_token"

# Apply master branch protection
curl -X POST \
  -H "Authorization: token $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github+json" \
  https://api.github.com/repos/Igladyshev/schema-sentinel/rulesets \
  -d @.github/rulesets/master-branch-protection.json

# Apply dev branch rules  
curl -X POST \
  -H "Authorization: token $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github+json" \
  https://api.github.com/repos/Igladyshev/schema-sentinel/rulesets \
  -d @.github/rulesets/dev-branch-rules.json
```

## Verifying the Setup

### Test Master Branch Protection

1. Try to push directly to master (should be blocked):
   ```bash
   git checkout master
   git commit --allow-empty -m "test"
   git push origin master
   # Should fail with: "required status checks must pass"
   ```

2. Create a PR to master (should require approvals)

### Test Dev Branch

1. Push directly to dev (should work):
   ```bash
   git checkout dev
   git commit --allow-empty -m "test"
   git push origin dev
   # Should succeed after lint checks pass
   ```

## Next Steps

1. **Read the branching strategy**: See [BRANCHING.md](BRANCHING.md) for the full workflow
2. **Update your team**: Share the branching strategy with all contributors
3. **Start using the workflow**: Create feature branches from `dev`
4. **Monitor CI**: Ensure all CI checks are passing before merging

## Troubleshooting

### "I can't import the ruleset"

- Make sure you have **admin access** to the repository
- Verify the JSON is valid (you can use a JSON validator)
- Check that you're in the correct repository

### "The rules aren't working"

- Verify the rulesets are set to **Active** (not Disabled or Evaluate)
- Check the branch name matches exactly (case-sensitive)
- Ensure the rulesets were imported successfully

### "I need to bypass the rules"

- Repository administrators can bypass rules when necessary
- Use this sparingly and document why it was needed
- Re-enable strict enforcement after the exception

## Questions?

If you have questions or run into issues:
- Open an issue with the `question` label
- Contact the repository maintainers
- Refer to [GitHub's Rulesets documentation](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets)

---

**Important**: These rulesets are version-controlled in this repository. Any changes to the rules should be made by updating the JSON files and re-importing them.
