"""MPM YAML configuration parser and validator."""

import re
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml
from jsonschema import ValidationError, validate

from .schema import MPM_SCHEMA


class MPMConfig:
    """
    Parser and validator for MPM (Master Project Management) YAML configuration files.
    """

    def __init__(self, yaml_path: str | Path):
        """
        Initialize MPM configuration from YAML file.

        Args:
            yaml_path: Path to the YAML configuration file

        Raises:
            FileNotFoundError: If YAML file doesn't exist
            yaml.YAMLError: If YAML is malformed
            ValidationError: If YAML doesn't match schema
        """
        self.yaml_path = Path(yaml_path)
        if not self.yaml_path.exists():
            raise FileNotFoundError(f"YAML file not found: {yaml_path}")

        with open(self.yaml_path) as f:
            self.data = yaml.safe_load(f)

        # Normalize dates to ensure all start_date values are datetime objects
        self._normalize_dates(self.data)

        # Validate against schema
        validate(instance=self.data, schema=MPM_SCHEMA)

    def _normalize_dates(self, obj: Any) -> None:
        """
        Normalize all date values to datetime objects.
        Converts string dates to datetime and adds missing seconds.

        Args:
            obj: Object to normalize (dict, list, or primitive)
        """
        if isinstance(obj, dict):
            for key, value in obj.items():
                if key == "start_date" and isinstance(value, str):
                    # Parse string date and ensure it has seconds
                    if re.match(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}$", value):
                        # Missing seconds, add :00
                        value = f"{value}:00"
                    # Convert to datetime object
                    try:
                        obj[key] = datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
                    except ValueError:
                        # If parsing fails, leave as-is
                        pass
                elif isinstance(value, (dict, list)):
                    self._normalize_dates(value)
        elif isinstance(obj, list):
            for item in obj:
                self._normalize_dates(item)

    @property
    def deployment_version(self) -> str:
        """Get deployment version."""
        return self.data["deployment_version"]

    @property
    def domain_code(self) -> str:
        """Get domain code."""
        return self.data["domain_code"]

    @property
    def warehouse_config(self) -> dict[str, Any]:
        """Get warehouse configuration."""
        return self.data["warehouse"]

    @property
    def internal_stage(self) -> str:
        """Get internal stage path."""
        return self.data["internal_stage"]

    @property
    def external_stage(self) -> str:
        """Get external stage path."""
        return self.data["external_stage"]

    @property
    def domain_timezone(self) -> str:
        """Get domain timezone."""
        return self.data["domain_timezone"]

    @property
    def communities(self) -> list[dict[str, Any]]:
        """Get list of communities."""
        return self.data["communities"]

    @property
    def actions(self) -> list[dict[str, Any]]:
        """Get list of all actions."""
        return self.data["actions"]

    def get_deployment_info(self) -> dict[str, Any]:
        """
        Extract deployment information as a single record.

        Returns:
            Dictionary containing deployment metadata with warehouse as nested object
        """
        return {
            "deployment_version": self.deployment_version,
            "domain_code": self.domain_code,
            "warehouse": self.warehouse_config,
            "internal_stage": self.internal_stage,
            "external_stage": self.external_stage,
            "domain_timezone": self.domain_timezone,
        }

    def get_communities_list(self) -> list[dict[str, Any]]:
        """
        Extract communities as a list.

        Returns:
            List of community dictionaries with deployment context
        """
        return [
            {
                "deployment_version": self.deployment_version,
                "domain_code": self.domain_code,
                "community_id": community["id"],
                "community_name": community["name"],
            }
            for community in self.communities
        ]

    def get_sensor_actions(self) -> list[dict[str, Any]]:
        """
        Extract SENSOR type actions.

        Returns:
            List of sensor action dictionaries with nested objects as variants
        """
        sensors = []
        for action in self.actions:
            if action["action_type"] == "SENSOR":
                sensors.append(
                    {
                        "deployment_version": self.deployment_version,
                        "domain_code": self.domain_code,
                        "action_type": action["action_type"],
                        "action_code": action["action_code"],
                        "abbreviation": action["abbreviation"],
                        "dataset": action.get("dataset"),
                        "source_system": action.get("source_system"),
                        "date_range_function": action.get("date_range_function"),
                        "schedule": action["schedule"],
                        "parents": action.get("parents", []),
                        "query_reference": action["query_reference"],
                        "start_date": action.get("start_date"),
                    }
                )
        return sensors

    def get_report_actions(self) -> list[dict[str, Any]]:
        """
        Extract REPORT type actions.

        Returns:
            List of report action dictionaries with nested objects as variants
        """
        reports = []
        for action in self.actions:
            if action["action_type"] == "REPORT":
                reports.append(
                    {
                        "deployment_version": self.deployment_version,
                        "domain_code": self.domain_code,
                        "action_type": action["action_type"],
                        "action_code": action["action_code"],
                        "abbreviation": action["abbreviation"],
                        "report_name": action.get("report_name"),
                        "report_file_pattern": action.get("report_file_name_pattern"),
                        "communities": action.get("communities", []),
                        "consumer_tags": action.get("consumer_tags"),
                        "date_range_function": action.get("date_range_function"),
                        "schedule": action["schedule"],
                        "parents": action.get("parents", []),
                        "query_reference": action["query_reference"],
                        "header_information": action.get("header_information"),
                        "pii_information": action.get("pii_information"),
                        "start_date": action.get("start_date"),
                    }
                )
        return reports

    @staticmethod
    def validate_yaml_file(yaml_path: str | Path) -> tuple[bool, str | None]:
        """
        Validate a YAML file against the MPM schema without loading full config.

        Args:
            yaml_path: Path to YAML file

        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            path = Path(yaml_path)
            if not path.exists():
                return False, f"File not found: {yaml_path}"

            with open(path) as f:
                data = yaml.safe_load(f)

            validate(instance=data, schema=MPM_SCHEMA)
            return True, None
        except FileNotFoundError as e:
            return False, str(e)
        except yaml.YAMLError as e:
            return False, f"YAML parsing error: {e}"
        except ValidationError as e:
            return False, f"Schema validation error: {e.message}"
        except Exception as e:
            return False, f"Unexpected error: {e}"
