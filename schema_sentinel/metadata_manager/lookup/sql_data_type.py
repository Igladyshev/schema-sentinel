from dataclasses import dataclass
from typing import Dict


@dataclass
class SqlDataTypeCategory:
    name: str


@dataclass
class SqlDataType:
    name: str
    category: SqlDataTypeCategory
    notes: str


def load_data_types() -> Dict[str, SqlDataType]:
    """
    Function loads a dictionary of SQL Data Types
    :return: Dict[SqlDataType]
    """
    data_types: Dict[str, SqlDataType]
    for category in SQL_DATA_TYPE.keys():
        sql_data_type_category: SqlDataTypeCategory = SqlDataTypeCategory(category)
        data_types[category] = list()
        for data_type in SQL_DATA_TYPE[category]:
            sql_data_type = SqlDataType(name=data_type["name"],
                                        category=sql_data_type_category,
                                        notes=data_type["notes"] if "notes" in data_type else None)
            data_types[category].append(sql_data_type)


SQL_DATA_TYPE: Dict = {
    "Numeric Data Types": [
        {
            "name": "NUMBER",
            "notes": "Default precision and scale are (38,0)."
        },
        {
            "name": "DECIMAL",
            "notes": "Synonymous with NUMBER. Default precision and scale are (38,0)."
        },
        {
            "name": "NUMERIC",
            "notes": "Synonymous with NUMBER. Default precision and scale are (38,0)."
        },
        {
            "name": "INT",
            "notes": "Synonymous with NUMBER except precision and scale cannot be specified."
        },
        {
            "name": "INTEGER",
            "notes": "Synonymous with NUMBER except precision and scale cannot be specified."
        },
        {
            "name": "BIGINT",
            "notes": "Synonymous with NUMBER except precision and scale cannot be specified."
        },
        {
            "name": "SMALLINT",
            "notes": "Synonymous with NUMBER except precision and scale cannot be specified."
        },
        {
            "name": "TINYINT",
            "notes": "Synonymous with NUMBER except precision and scale cannot be specified."
        },
        {
            "name": "BYTEINT",
            "notes": "Synonymous with NUMBER except precision and scale cannot be specified."
        },
        {
            "name": "FLOAT",
            "notes": "A known issue in Snowflake displays FLOAT, FLOAT4, FLOAT8, REAL, DOUBLE, and DOUBLE PRECISION as FLOAT even though they are stored as DOUBLE"
        },
        {
            "name": "FLOAT4",
            "notes": "A known issue in Snowflake displays FLOAT, FLOAT4, FLOAT8, REAL, DOUBLE, and DOUBLE PRECISION as FLOAT even though they are stored as DOUBLE"
        },
        {
            "name": "FLOAT8",
            "notes": "A known issue in Snowflake displays FLOAT, FLOAT4, FLOAT8, REAL, DOUBLE, and DOUBLE PRECISION as FLOAT even though they are stored as DOUBLE"
        },
        {
            "name": "DOUBLE",
            "notes": "Synonymous with FLOAT."
        },
        {
            "name": "DOUBLE PRECISION",
            "notes": "Synonymous with FLOAT."
        },
        {
            "name": "REAL",
            "notes": "Synonymous with FLOAT."
        }
    ],
    "String & Binary Data Types":[
        {
            "name": "VARCHAR",
            "notes": "Default (and maximum) is 16,777,216 bytes."
        },
        {
            "name": "CHAR",
            "notes": "Synonymous with VARCHAR except default length is VARCHAR(1)."
        },
        {
            "name": "CHARACTER",
            "notes": "Synonymous with VARCHAR except default length is VARCHAR(1)."
        },
        {
            "name": "TEXT",
            "notes": "Synonymous with VARCHAR"
        },
        {
            "name": "BINARY"
        },
        {
            "name": "VARBINARY",
            "notes": "Synonymous with BINARY"
        },
    ],
    "Logical Data Types": [
        {
            "name": "BOOLEAN",
            "notes": "Currently only supported for accounts provisioned after January 25, 2016."
        }
    ],
    "Date & Time Data Types": [
        {
            "name": "DATE",
        },
        {
            "name": "DATETIME",
            "notes": "Alias for TIMESTAMP_NTZ"
        },
        {
            "name": "TIME",
        },
        {
            "name": "TIMESTAMP",
            "notes": "Alias for one of the TIMESTAMP variations (TIMESTAMP_NTZ by default)."
        },
        {
            "name": "TIMESTAMP_LTZ",
            "notes": "TIMESTAMP with local time zone; time zone, if provided, is not stored."
        },
        {
            "name": "TIMESTAMP_NTZ",
            "notes": "TIMESTAMP with no time zone; time zone, if provided, is not stored."
        },
        {
            "name": "TIMESTAMP_TZ",
            "notes": "TIMESTAMP with time zone."
        }
    ],
    "Semi-structured Data Types": [
        {
            "name": "VARIANT",
        },
        {
            "name": "OBJECT",
        },
        {
            "name": "ARRAY",
        }
    ],
    "Geospatial Data Types": [
        {
            "name": "GEOGRAPHY",
        },
        {
            "name": "GEOMETRY",
        }
    ]
}
