# GitHub Branch Rulesets

This directory contains branch protection rules defined as JSON files that can be imported into GitHub.

## Files

- `master-branch-protection.json` - Protection rules for the master branch
- `dev-branch-rules.json` - Rules for the dev branch

## How to Apply These Rules

### Method 1: Using GitHub Web Interface (Recommended)

1. Go to your repository on GitHub
2. Navigate to **Settings** → **Rules** → **Rulesets**
3. Click **New ruleset** → **New branch ruleset**
4. Click **Import a ruleset**
5. Copy the content from the appropriate JSON file
6. Paste it into the import dialog
7. Review and save

### Method 2: Using GitHub API

You can also apply these rules using the GitHub REST API:

```bash
# Apply master branch protection
curl -X POST \
  -H "Authorization: token YOUR_TOKEN" \
  -H "Accept: application/vnd.github+json" \
  https://api.github.com/repos/OWNER/REPO/rulesets \
  -d @master-branch-protection.json

# Apply dev branch rules
curl -X POST \
  -H "Authorization: token YOUR_TOKEN" \
  -H "Accept: application/vnd.github+json" \
  https://api.github.com/repos/OWNER/REPO/rulesets \
  -d @dev-branch-rules.json
```

## Rule Customization

### Master Branch Protection

The master branch has strict protection:
- Requires 1 pull request approval
- All CI status checks must pass
- Prevents branch deletion
- Prevents force pushes
- Requires linear history

### Dev Branch Rules

The dev branch has lighter protection:
- Requires only lint checks to pass
- Prevents branch deletion
- Allows direct pushes for rapid development

### Modifying Rules

To modify these rules:

1. Edit the JSON file with your desired changes
2. Re-import using Method 1 or 2 above
3. Commit the changes to version control

### Understanding Bypass Actors

The `bypass_actors` section specifies who can bypass these rules:
- `actor_id: 5` with `RepositoryRole` typically refers to repository administrators
- `bypass_mode: always` means they can always bypass

**Important**: The `actor_id: 5` is a common default for repository admin role, but this may vary depending on your specific repository configuration. When importing these rulesets:

1. GitHub will automatically map the role if it exists
2. If the role mapping fails, you can adjust it in the GitHub UI after import
3. Alternatively, remove the `bypass_actors` section entirely if you want no bypasses

To find the correct `actor_id` for your repository:
- Navigate to Settings → Collaborators and teams
- Use the GitHub API: `GET /repos/{owner}/{repo}/collaborators` to see role IDs
- Or simply let GitHub handle the mapping during import

## Common Rule Types

Available rule types include:
- `pull_request` - Require pull request reviews
- `required_status_checks` - Require specific CI checks to pass
- `deletion` - Prevent branch deletion
- `non_fast_forward` - Prevent force pushes
- `required_linear_history` - Require linear history
- `required_signatures` - Require signed commits

## Documentation

For more information about the branching strategy, see [BRANCHING.md](../../BRANCHING.md) in the repository root.

For GitHub Rulesets documentation, visit:
https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/about-rulesets
