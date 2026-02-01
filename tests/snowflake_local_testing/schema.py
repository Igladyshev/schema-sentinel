"""JSON Schema for MPM (Master Project Management) YAML configuration files."""

MPM_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "MPM Configuration",
    "description": "Schema for Master Project Management deployment configuration",
    "type": "object",
    "$defs": {
        "warehouse": {
            "type": "object",
            "required": ["auto_suspend", "max_cluster_count", "scaling_policy", "warehouse_size", "warehouse_type"],
            "properties": {
                "auto_suspend": {"type": "integer", "minimum": 0, "description": "Auto-suspend timeout in seconds"},
                "max_cluster_count": {"type": "integer", "minimum": 1, "maximum": 10},
                "scaling_policy": {"type": "string", "enum": ["STANDARD", "ECONOMY"]},
                "warehouse_size": {
                    "type": "string",
                    "enum": ["XSMALL", "SMALL", "MEDIUM", "LARGE", "XLARGE", "2XLARGE", "3XLARGE", "4XLARGE"],
                },
                "warehouse_type": {"type": "string", "description": "Warehouse type (e.g., SNOWPARK-OPTIMIZED)"},
            },
        },
        "community": {
            "type": "object",
            "required": ["id", "name"],
            "properties": {
                "id": {
                    "oneOf": [{"type": "string"}, {"type": "integer"}],
                    "description": "Unique community identifier (alphanumeric, will be converted to string)",
                },
                "name": {"type": "string", "minLength": 1, "description": "Community name"},
            },
        },
        "schedule": {
            "type": "object",
            "required": ["crontab", "timezone"],
            "properties": {
                "crontab": {
                    "type": "string",
                    "pattern": "^([0-9*,\\-/]+ ){4}[0-9*,\\-/]+$",
                    "description": "Cron expression",
                },
                "timezone": {"type": "string", "description": "Timezone for schedule"},
            },
        },
        "query_reference": {
            "type": "object",
            "required": ["database_name", "query"],
            "properties": {
                "database_name": {"type": "string", "minLength": 1},
                "query": {"type": "string", "minLength": 1},
                "query_version": {"type": "string"},
            },
        },
        "consumer_tags": {
            "type": "object",
            "properties": {
                "AML": {"type": "boolean"},
                "Finance": {"type": "boolean"},
                "Regulatory": {"type": "boolean"},
            },
        },
        "header_information": {"type": ["object", "null"], "description": "Header information for reports"},
        "pii_information": {"type": "object", "description": "PII field information"},
    },
    "required": [
        "deployment_version",
        "domain_code",
        "warehouse",
        "internal_stage",
        "external_stage",
        "domain_timezone",
        "communities",
        "actions",
    ],
    "properties": {
        "deployment_version": {
            "type": "string",
            "pattern": "^\\d+\\.\\d+\\.\\d+$",
            "description": "Deployment version in semantic version format (e.g., 0.0.5)",
        },
        "domain_code": {"type": "string", "minLength": 2, "maxLength": 10, "description": "Domain code identifier"},
        "internal_stage": {
            "type": "string",
            "pattern": '^[A-Z_]+\\.(("[A-Z_0-9]+")|([A-Z_0-9]+))\\.[A-Z_]+$',
            "description": "Internal stage path in format: DATABASE.SCHEMA.STAGE (schema name may be quoted)",
        },
        "external_stage": {
            "type": "string",
            "pattern": "^[A-Z_]+\\.[A-Z_]+\\.[A-Z_]+$",
            "description": "External stage path in format: DATABASE.SCHEMA.STAGE",
        },
        "domain_timezone": {"type": "string", "description": "Domain timezone (e.g., US / Eastern)"},
        "warehouse": {"$ref": "#/$defs/warehouse"},
        "warehouse": {"$ref": "#/$defs/warehouse"},
        "communities": {"type": "array", "minItems": 0, "items": {"$ref": "#/$defs/community"}},
        "actions": {
            "type": "array",
            "minItems": 1,
            "items": {
                "type": "object",
                "required": ["action_type", "action_code", "abbreviation", "schedule", "parents", "query_reference"],
                "properties": {
                    "action_type": {"type": "string", "enum": ["REPORT", "SENSOR"]},
                    "action_code": {"type": "string", "minLength": 1},
                    "abbreviation": {"type": "string", "minLength": 1, "maxLength": 20},
                    "communities": {"type": "array", "items": {"type": "string"}},
                    "dataset": {"type": "string", "description": "Dataset name for SENSOR actions"},
                    "source_system": {"type": "string", "description": "Source system for SENSOR actions"},
                    "consumer_tags": {"$ref": "#/$defs/consumer_tags"},
                    "date_range_function": {"type": "string", "description": "Function to calculate date range"},
                    "header_information": {"$ref": "#/$defs/header_information"},
                    "parents": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Parent action dependencies",
                    },
                    "pii_information": {"$ref": "#/$defs/pii_information"},
                    "query_reference": {"$ref": "#/$defs/query_reference"},
                    "report_file_name_pattern": {
                        "type": "string",
                        "description": "File name pattern for REPORT actions",
                    },
                    "report_name": {"type": "string", "description": "Report name for REPORT actions"},
                    "schedule": {"$ref": "#/$defs/schedule"},
                    "start_date": {
                        "description": "Start date as datetime object or string in format YYYY-MM-DD HH:MM:SS"
                    },
                },
                "if": {"properties": {"action_type": {"const": "SENSOR"}}},
                "then": {"required": ["dataset", "source_system"]},
                "else": {"required": ["report_name", "report_file_name_pattern", "consumer_tags"]},
            },
        },
    },
}
