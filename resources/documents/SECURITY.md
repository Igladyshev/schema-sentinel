# Security Policy

## Supported Versions

We release patches for security vulnerabilities for the following versions:

| Version | Supported          |
| ------- | ------------------ |
| 2.1.x   | :white_check_mark: |
| 2.0.x   | :x:                |
| < 2.0   | :x:                |

## Reporting a Vulnerability

We take the security of SQL Comparison seriously. If you believe you have found a security vulnerability, please report it to us as described below.

### Where to Report

**Please do NOT report security vulnerabilities through public GitHub issues.**

Instead, please report them via email to:
- **Email**: [Your security contact email]

You should receive a response within 48 hours. If for some reason you do not, please follow up via email to ensure we received your original message.

### What to Include

Please include the following information in your report:

- Type of vulnerability
- Full paths of source file(s) related to the vulnerability
- Location of the affected source code (tag/branch/commit or direct URL)
- Any special configuration required to reproduce the issue
- Step-by-step instructions to reproduce the issue
- Proof-of-concept or exploit code (if possible)
- Impact of the issue, including how an attacker might exploit it

This information will help us triage your report more quickly.

### Disclosure Policy

When we receive a security bug report, we will:

1. Confirm the problem and determine the affected versions
2. Audit code to find any similar problems
3. Prepare fixes for all supported releases
4. Release new security patch versions as soon as possible

### Comments on this Policy

If you have suggestions on how this process could be improved, please submit a pull request.

## Security Best Practices

### Credentials Management

**Never commit credentials to the repository:**

- Use environment variables for sensitive information
- Use `.env` files (added to `.gitignore`)
- Consider using secret management tools:
  - AWS Secrets Manager
  - HashiCorp Vault
  - Azure Key Vault
  - GCP Secret Manager

### Database Connections

**Secure your database connections:**

- Always use SSL/TLS for database connections
- Use IAM authentication when available
- Rotate credentials regularly
- Use least-privilege access principles
- Never share production credentials

### Example Secure Configuration

```python
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

config = {
    "account": os.getenv("SNOWFLAKE_ACCOUNT"),
    "user": os.getenv("SNOWFLAKE_USER"),
    "password": os.getenv("SNOWFLAKE_PASSWORD"),
    "warehouse": os.getenv("SNOWFLAKE_WAREHOUSE"),
    "database": os.getenv("SNOWFLAKE_DATABASE"),
    "role": os.getenv("SNOWFLAKE_ROLE"),
}
```

### Environment Variables Template

Create a `.env.example` file (safe to commit):

```
SNOWFLAKE_ACCOUNT=your_account
SNOWFLAKE_USER=your_user
SNOWFLAKE_PASSWORD=your_password
SNOWFLAKE_WAREHOUSE=your_warehouse
SNOWFLAKE_DATABASE=your_database
SNOWFLAKE_ROLE=your_role
```

Users should copy this to `.env` and fill in their actual values.

## Security Updates

Subscribe to security advisories:
- Watch this repository for security updates
- Enable GitHub security advisories
- Star the repository to stay informed

## Known Security Considerations

### SQL Injection

This tool reads database metadata but does not execute user-provided SQL. However:
- Database object names are parameterized in queries
- User input should still be validated
- Use prepared statements when applicable

### Data Exposure

- Metadata may contain sensitive schema information
- Reports should be handled securely
- Consider access controls for generated reports
- Be cautious when sharing metadata snapshots

### Dependency Vulnerabilities

- We use Dependabot to monitor dependencies
- Security patches are prioritized
- Run `pip-audit` regularly to check for vulnerabilities

## Acknowledgments

We appreciate the security research community and will acknowledge researchers who responsibly disclose vulnerabilities (unless they prefer to remain anonymous).
