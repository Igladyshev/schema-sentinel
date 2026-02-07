# Schema Sentinel Wiki

Welcome to the Schema Sentinel wiki! This wiki provides comprehensive documentation for using and contributing to Schema Sentinel, a powerful tool for comparing database metadata across different environments.

## 📚 Table of Contents

- **[Getting Started](Getting-Started.md)** - Installation and quick start guide
- **[Architecture](Architecture.md)** - System architecture and design
- **[Development](Development.md)** - Development environment setup and guidelines
- **[Contributing](Contributing.md)** - How to contribute to the project
- **[Security](Security.md)** - Security guidelines and best practices
- **[Future Development Plan](Future-Development-Plan.md)** - Roadmap and upcoming features

## 🎯 What is Schema Sentinel?

Schema Sentinel is a comprehensive tool for **data engineers**, **DBAs**, and **analytics teams** working with **Snowflake** and needing to track schema changes across development, staging, and production environments.

### Key Features

- **📊 Comprehensive Metadata Extraction** - Extract complete schema information including tables, columns, views, procedures, functions, constraints, and more
- **💾 Version Control for Schema** - Store metadata snapshots in SQLite for historical tracking
- **🔍 Intelligent Comparison** - Compare metadata between different environments with detailed diff reports
- **📝 Multiple Report Formats** - Generate reports in Markdown, HTML, and JSON formats
- **🏢 Snowflake Native** - Built specifically for Snowflake with deep integration
- **🔌 Extensible** - Architecture supports additional database platforms
- **🚀 Fast & Efficient** - Optimized queries and parallel processing
- **🔒 Secure** - Best practices for credential management and data security

## 🎓 Use Cases

- **Environment Synchronization** - Ensure dev, staging, and production schemas are aligned
- **Change Tracking** - Monitor schema evolution over time
- **Deployment Validation** - Verify schema changes after deployments
- **Compliance & Auditing** - Maintain schema change history for compliance requirements
- **Migration Planning** - Identify differences before major migrations
- **Documentation** - Auto-generate schema documentation

## 📋 Requirements

- Python 3.9 or higher
- [uv](https://github.com/astral-sh/uv) - Modern Python package manager
- Snowflake account with appropriate permissions

## 🚀 Quick Start

```bash
# Clone the repository
git clone https://github.com/Igladyshev/schema-sentinel.git
cd schema-sentinel

# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh  # Linux/macOS

# Set up environment and install dependencies
./setup.sh

# Configure your environment
cp resources/examples/.env.example .env
# Edit .env with your Snowflake credentials
```

See [Getting Started](Getting-Started.md) for detailed installation and configuration instructions.

## 📊 Project Status

**Current Version**: v2.1.0
**Status**: Active Development 🚧

This project is being actively developed and prepared for production use. See the [Future Development Plan](Future-Development-Plan.md) for upcoming features and roadmap.

## 🤝 Community

- **Issues**: [GitHub Issues](https://github.com/Igladyshev/schema-sentinel/issues)
- **Discussions**: [GitHub Discussions](https://github.com/Igladyshev/schema-sentinel/discussions)
- **Contributing**: See our [Contributing Guide](Contributing.md)

## 📄 License

This project is licensed under the Apache License 2.0 - see the [LICENSE](https://github.com/Igladyshev/schema-sentinel/blob/master/LICENSE) file for details.

---

**Made with ❤️ for the data engineering community**
