from configparser import ConfigParser
import os


def get_html(file_name):
    with open(file_name, "r") as file:
        html = file.read()
    return html


def get_config(env: str, resources_path: str) -> ConfigParser:
    """
    Reads a config file for and environment and returns a ConfigParser instance
    :param env: Environment: dev, nonprod, cert or prod
    :param resources_path: Resource path, where the config files are stored
    :return: ConfigParser instance
    """
    config = ConfigParser()
    config.read_file(open(os.path.join(resources_path, f"db-{env}.properties")), "r")
    return config

def snake_case_split(s) -> str:
    """
    The function would split a word in snake_case to separate words with first capital letter.
    This was done to sve some space in page width when creating pdf

    :param s: snake_case string like user_access_report
    :return: split header as "User Access Report"
    """
    return " ".join(x.capitalize() for x in s.split("_"))


def camel_case_split(s):
    """
    The function would split a word in camelCase to separate words.
    This was done to sve some space in page width when creating pdf

    :param s: camelCase string like userAccessReport
    :return: split header as "user Access Report"
    """
    idx = list(map(str.isupper, s))
    # mark change of case
    l = [0]
    for (i, (x, y)) in enumerate(zip(idx, idx[1:])):
        if x and not y:  # "Ul"
            l.append(i)
        elif not x and y:  # "lU"
            l.append(i + 1)
    l.append(len(s))
    # for "lUl", index of "U" will pop twice, have to filer it
    return " ".join([s[x:y] for x, y in zip(l, l[1:]) if x < y])

GET_SCHEMA_DISCREPANCY_SQL = f"""
SELECT
    "SCHEMA_DISCREPANCY_ID",
    "ENVIRONMENT",
    "DATABASE_NAME",
    "SCHEMA_NAME",
    "DB_OBJECT_TYPE",
    "DB_OBJECT_NAME",
    "DB_OBJECT_PARENT_TYPE",
    "DB_OBJECT_PARENT_NAME",
    "DDL",
    "ACTION",
    "ACTION_APPROVED_BY",
    "ACTION_APPROVED_AT",
    "KEEP_UNTIL",
    "OBJECT_DEPENDENCIES",
    "SYSTEM_CREATE_DATETIME",
    "SYSTEM_UPDATE_DATETIME"
FROM "MIGRATIONS"."SCHEMA_DISCREPANCY"
WHERE
    "ENVIRONMENT" = :environment
    AND "database_name" = :database_name
    AND "SCHEMA_NAME"=:schema_name
    AND "db_object_type"=:db_object_type
    AND "db_object_name"=:db_object_name
"""

ACCOUNT_MAP = {
    "dev": "YOUR_DEV_ACCOUNT",
    "staging": "YOUR_STAGING_ACCOUNT",
    "prod": "YOUR_PROD_ACCOUNT",
}

ENV_MAP = {"dev": "DEV", "staging": "STAGING", "prod": "PROD"}

# Example: Custom view filters for specific business logic
# This is a template - customize based on your data model
CUSTOM_VIEW_FILTERS = {
    # Example: Filter views that need specific row-level security
    "FILTER_BY_ACCOUNT": {
        "TABLE_LIST": [
            # Add your table names here
            # "ORDERS",
            # "TRANSACTIONS",
        ],
        "FILTER": """AS {alias} WHERE EXISTS(
            SELECT *
            FROM SCHEMA.ACCOUNT AS A
            WHERE {alias}.ACCOUNT_ID = A.ACCOUNT_ID)""",
    },
    # Example: Exclude test data
    "FILTER_OUT_TEST": {
        "TABLE_LIST": [
            # "ACCOUNT",
        ],
        "FILTER": "WHERE NOT IS_TEST",
    },
    # Example: Tables/views that don't need filtering
    "NO_FILTER": {
        "VIEWS": [
            # "REFERENCE_DATA",
            # "LOOKUP_TABLES",
        ]
    },
    # Example: Tables to exclude from comparison
    "EXCLUDE": {
        "TABLE_LIST": [
            # "TEMP_TABLE",
            # "STAGING_TABLE",
        ]
    },
}


def exclude_table(table_name: str) -> bool:
    """Check if table should be excluded from processing"""
    return table_name in CUSTOM_VIEW_FILTERS.get("EXCLUDE", {}).get("TABLE_LIST", [])


def get_filter(table_name: str) -> str:
    """
    Get custom filter for a table based on configuration.
    This is a template - customize based on your business logic.
    """
    view_filter = ""

    # Check each filter configuration
    for filter_name, config in CUSTOM_VIEW_FILTERS.items():
        if filter_name == "EXCLUDE" or filter_name == "NO_FILTER":
            continue

        if table_name in config.get("TABLE_LIST", []):
            view_filter = config["FILTER"]
            if "{alias}" in view_filter:
                view_filter = view_filter.replace("{alias}", get_alias(table_name))
            break

    return view_filter


def get_alias(table_name: str) -> str:
    alias = "".join(x[0].upper() for x in table_name.split("_"))
    alias += get_random_string(1)
    return alias


import random
import string


def get_random_string(length):
    # choose from all lowercase letter
    letters = string.ascii_lowercase
    result_str = "".join(random.choice(letters) for i in range(length))
    return result_str
