# Security Guide

Security is a top priority for Schema Sentinel. This guide outlines security best practices, vulnerability reporting procedures, and secure configuration guidelines.

## Supported Versions

We release patches for security vulnerabilities for the following versions:

| Version | Supported          |
| ------- | ------------------ |
| 2.1.x   | ✅ Yes             |
| 2.0.x   | ❌ No              |
| < 2.0   | ❌ No              |

## Reporting a Vulnerability

We take the security of Schema Sentinel seriously. If you believe you have found a security vulnerability, please report it to us as described below.

### Where to Report

**⚠️ Please do NOT report security vulnerabilities through public GitHub issues.**

Instead, please report them via:
- **Email**: Contact the repository maintainers
- **GitHub Security Advisories**: Use the private vulnerability reporting feature

### Response Timeline

You should receive a response within **48 hours**. If for some reason you do not, please follow up via email to ensure we received your original message.

### What to Include

Please include the following information in your report:

- **Type of vulnerability** (e.g., SQL injection, credential exposure, etc.)
- **Full paths** of source file(s) related to the vulnerability
- **Location** of the affected source code (tag/branch/commit or direct URL)
- **Special configuration** required to reproduce the issue
- **Step-by-step instructions** to reproduce the issue
- **Proof-of-concept or exploit code** (if possible)
- **Impact** of the issue, including how an attacker might exploit it

This information will help us triage your report more quickly.

### Disclosure Policy

When we receive a security bug report, we will:

1. **Confirm the problem** and determine the affected versions
2. **Audit code** to find any similar problems
3. **Prepare fixes** for all supported releases
4. **Release new security patch versions** as soon as possible
5. **Publicly disclose** the vulnerability after a fix is available

## Security Best Practices

### Credentials Management

**❌ Never commit credentials to the repository:**

- Use environment variables for sensitive information
- Use `.env` files (already added to `.gitignore`)
- Consider using secret management tools:
  - AWS Secrets Manager
  - HashiCorp Vault
  - Azure Key Vault
  - GCP Secret Manager
  - 1Password
  - LastPass

### Example Secure Configuration

**✅ Good Practice:**

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

# Validate that all required variables are set
if not all(config.values()):
    raise ValueError("Missing required environment variables")
```

**❌ Bad Practice:**

```python
# DON'T DO THIS!
config = {
    "account": "my_account",
    "user": "admin",
    "password": "secret123",  # Never hardcode credentials!
}
```

### Environment Variables Template

Always provide a `.env.example` file (safe to commit):

```
# Snowflake Configuration
SNOWFLAKE_ACCOUNT=your_account
SNOWFLAKE_USER=your_user
SNOWFLAKE_PASSWORD=your_password
SNOWFLAKE_WAREHOUSE=your_warehouse
SNOWFLAKE_DATABASE=your_database
SNOWFLAKE_ROLE=your_role

# Optional: Specify schemas (comma-separated)
SNOWFLAKE_SCHEMAS=PUBLIC,ANALYTICS
```

Users should copy this to `.env` and fill in their actual values:

```bash
cp .env.example .env
# Edit .env with your credentials
```

## Database Security

### Connection Security

**✅ Always use SSL/TLS for database connections:**

```python
# Snowflake connections use SSL/TLS by default
connection_params = {
    "account": os.getenv("SNOWFLAKE_ACCOUNT"),
    "user": os.getenv("SNOWFLAKE_USER"),
    "password": os.getenv("SNOWFLAKE_PASSWORD"),
    # SSL is enabled by default in Snowflake connector
}
```

**✅ Use IAM authentication when available:**

```python
# For AWS-based Snowflake accounts
connection_params = {
    "account": os.getenv("SNOWFLAKE_ACCOUNT"),
    "authenticator": "externalbrowser",  # Use SSO
    "warehouse": os.getenv("SNOWFLAKE_WAREHOUSE"),
}
```

### Access Control

**Principle of Least Privilege:**

- Use read-only accounts for metadata extraction
- Create dedicated service accounts
- Rotate credentials regularly (every 90 days recommended)
- Never share production credentials
- Use different credentials for each environment (dev, staging, prod)

**Example Snowflake Permissions:**

```sql
-- Create a read-only role for metadata extraction
CREATE ROLE METADATA_READER;

-- Grant usage on warehouse, database, and schemas
GRANT USAGE ON WAREHOUSE compute_wh TO ROLE METADATA_READER;
GRANT USAGE ON DATABASE analytics_db TO ROLE METADATA_READER;
GRANT USAGE ON ALL SCHEMAS IN DATABASE analytics_db TO ROLE METADATA_READER;

-- Grant SELECT on information_schema and account_usage
GRANT SELECT ON ALL TABLES IN SCHEMA analytics_db.information_schema TO ROLE METADATA_READER;
GRANT IMPORTED PRIVILEGES ON DATABASE snowflake TO ROLE METADATA_READER;

-- Assign role to user
GRANT ROLE METADATA_READER TO USER metadata_service_user;
```

## Data Security

### Metadata Sensitivity

**⚠️ Important:** Database metadata can be sensitive and may reveal:

- Database structure and design
- Column names that might indicate business logic
- Security configurations
- Access patterns

**Best Practices:**

- Treat metadata reports as confidential
- Store reports securely with appropriate access controls
- Encrypt reports at rest and in transit
- Be cautious when sharing metadata snapshots
- Sanitize metadata before sharing externally

### SQLite Storage Security

If storing metadata in SQLite:

```python
# Secure SQLite file permissions
import os
import stat

db_file = "metadata.db"

# Set file permissions to owner read/write only (0600)
os.chmod(db_file, stat.S_IRUSR | stat.S_IWUSR)
```

## SQL Injection Prevention

Schema Sentinel reads database metadata but does not execute user-provided SQL. However, security measures are still important:

**✅ Good Practices:**

1. **Parameterized Queries**: Always use parameterized queries with SQLAlchemy
2. **Input Validation**: Validate database object names
3. **Prepared Statements**: Use prepared statements when applicable

```python
# ✅ Good: Parameterized query
query = text("SELECT * FROM information_schema.tables WHERE table_name = :table_name")
result = connection.execute(query, {"table_name": user_input})

# ❌ Bad: String concatenation (vulnerable to SQL injection)
query = f"SELECT * FROM information_schema.tables WHERE table_name = '{user_input}'"
```

## Dependency Security

### Monitoring Dependencies

We use several tools to monitor dependency vulnerabilities:

- **Dependabot**: Automated dependency updates
- **GitHub Security Advisories**: Vulnerability notifications
- **pip-audit**: Regular security audits

### Running Security Audits

```bash
# Install pip-audit
pip install pip-audit

# Run security audit
pip-audit

# Check specific packages
pip-audit --requirement requirements.txt
```

### Keeping Dependencies Updated

```bash
# Update dependencies
uv pip list --outdated

# Update specific package
uv pip install --upgrade package-name

# Update all packages (use with caution)
uv pip install --upgrade -r requirements.txt
```

## Secure Development Practices

### Code Review

All code changes must be reviewed for:
- Credential exposure
- SQL injection vulnerabilities
- Insecure data handling
- Proper error handling (don't expose sensitive information in errors)

### Pre-commit Hooks

Use pre-commit hooks to catch security issues:

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/PyCQA/bandit
    rev: 1.7.4
    hooks:
      - id: bandit
        args: ['-c', 'pyproject.toml']
  
  - repo: https://github.com/Yelp/detect-secrets
    rev: v1.4.0
    hooks:
      - id: detect-secrets
        args: ['--baseline', '.secrets.baseline']
```

### Environment Separation

- **Development**: Use test databases with sample data
- **Staging**: Mirror production but with sanitized data
- **Production**: Restricted access, audit logging enabled

## Security Checklist

Before deploying or sharing code:

- [ ] No hardcoded credentials
- [ ] No secrets in version control
- [ ] Environment variables used for configuration
- [ ] SSL/TLS enabled for database connections
- [ ] Least privilege access configured
- [ ] Dependencies up to date
- [ ] Security audit passed (pip-audit)
- [ ] Pre-commit hooks configured
- [ ] Error messages don't expose sensitive information
- [ ] Logging doesn't include credentials
- [ ] File permissions set correctly
- [ ] Documentation updated with security notes

## Logging Security

**✅ Safe Logging:**

```python
import logging

logger = logging.getLogger(__name__)

# Log without sensitive data
logger.info(f"Connecting to database: {database_name}")
logger.info("Authentication successful")
```

**❌ Unsafe Logging:**

```python
# DON'T DO THIS!
logger.info(f"Connecting with password: {password}")  # Never log credentials!
logger.debug(f"Query: {query_with_sensitive_data}")
```

## Incident Response

If you discover a security incident:

1. **Immediately** revoke compromised credentials
2. **Rotate** all potentially affected credentials
3. **Audit** logs for unauthorized access
4. **Document** the incident
5. **Report** to the security team
6. **Review** and update security procedures

## Security Updates

### Staying Informed

- **Watch** this repository for security updates
- **Enable** GitHub security advisories
- **Subscribe** to release notifications
- **Review** CHANGELOG.md for security patches

### Applying Updates

```bash
# Update to latest secure version
git pull origin master
uv pip install --upgrade schema-sentinel

# Verify version
python -c "import schema_sentinel; print(schema_sentinel.__version__)"
```

## Known Security Considerations

### Current Considerations

1. **Metadata Exposure**: Schema information is sensitive
2. **Credential Management**: Proper credential handling is critical
3. **Report Distribution**: Reports may contain confidential schema details
4. **SQLite Storage**: Local storage security depends on file permissions

### Future Enhancements

See [Future Development Plan](Future-Development-Plan.md) for planned security enhancements:
- Enhanced credential encryption
- Audit logging capabilities
- Role-based access control (when web UI is added)

## Compliance

Schema Sentinel can help with compliance requirements by:

- Tracking schema changes for audit trails
- Documenting database structures
- Monitoring configuration drift
- Maintaining historical records

However, ensure you comply with:
- **GDPR**: If handling EU data
- **HIPAA**: If handling healthcare data
- **SOC 2**: If providing services to enterprise customers
- **PCI DSS**: If handling payment card data

## Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [SQLAlchemy Security](https://docs.sqlalchemy.org/en/14/core/security.html)
- [Snowflake Security](https://docs.snowflake.com/en/user-guide/security.html)
- [Python Security Best Practices](https://python.readthedocs.io/en/latest/library/security_warnings.html)

## Acknowledgments

We appreciate the security research community and will acknowledge researchers who responsibly disclose vulnerabilities (unless they prefer to remain anonymous).

---

**Security is everyone's responsibility. When in doubt, ask!**
