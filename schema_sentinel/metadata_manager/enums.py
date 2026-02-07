from dataclasses import dataclass
from enum import Enum

from schema_sentinel.config import get_config

# Get configuration manager instance
_config = get_config()


class ChangeSetUpdateAction(Enum):
    IGNORE = 0
    EXECUTE = 1
    ERROR = 2
    ASK = 3


class ExceptionAction(Enum):
    RAISE = 0
    CONTINUE = 1
    ASK = 2


class ConnectMode(Enum):
    SSO = 0
    PWD = 1
    KEY_PAIR = 2


class StreamSourceType(Enum):
    TABLE = 0
    VIEW = 1


class StreamMode(Enum):
    APPEND_ONLY = 0
    INSERT_ONLY = 1


class DbObjectType(Enum):
    DATABASE = ("database",)
    SCHEMA = ("schema",)
    STAGE = ("stage",)
    TABLE = ("table",)
    VIEW = ("view",)
    COLUMN = ("column",)
    PRIMARY_KEY = ("primary key",)
    UNIQUE_KEY = ("unique key",)
    FOREIGN_KEY = ("foreign key",)
    PROCEDURE = ("procedure",)
    FUNCTION = ("function",)
    STREAM = ("stream",)
    PIPE = ("pipe",)
    TASK = ("task",)
    PARAMETER = "parameter"


class DbFolderType(Enum):
    DATABASE = ((DbObjectType.DATABASE, "01"),)
    SCHEMA = ((DbObjectType.SCHEMA, "02"),)
    STAGE = ((DbObjectType.STAGE, "04"),)
    TABLE = ((DbObjectType.TABLE, "05"),)
    VIEW = ((DbObjectType.VIEW, "06"),)
    STREAM = ((DbObjectType.STREAM, "07"),)
    TASK = ((DbObjectType.TASK, "08"),)
    PROCEDURE = (DbObjectType.PROCEDURE, "09")


@dataclass
class Message:
    subject: str
    text: str


@dataclass
class DiffCategoryItem:
    id: int
    name: str
    message: Message


# Use config manager for data retention setting
DATA_RETENTION_TIME_IN_DAYS = _config.database.data_retention_days


class DbObjectType(Enum):
    DATABASE = "database"
    SCHEMA = "schema"
    TABLE = "table"
    COLUMN = "column"
    TABLE_CONSTRAINT = "table_constraint"
    COLUMN_CONSTRAINT = "column_constraint"
    REFERENTIAL_CONSTRAINT = "referential_constraint"
    VIEW = "view"
    PIPE = "pipe"
    STAGE = "stage"
    STREAM = "stream"
    TASK = "task"
    PROCEDURE = "procedure"
    FUNCTION = "function"
    CONSTRAINT = "constraint"

    @staticmethod
    def list():
        return [e.value for e in DbObjectType]


class Environment(Enum):
    DEV = "dev"
    NON_PROD = "non_prod"
    CERT = "cert"
    PROD = "prod"

    @staticmethod
    def list():
        return [e.value for e in Environment]


class ConstraintType(Enum):
    PRIMARY_KEY = "primary key"
    UNIQUE_KEY = "unique"
    FOREIGN_KEY = "foreign key"

    @staticmethod
    def list():
        return [e.value for e in ConstraintType]


class StageType(Enum):
    INTERNAL_NAMED = "internal named"
    EXTERNAL_NAMED = "external named"


class DiffCategory(Enum):
    TYPE = (
        DiffCategoryItem(
            0,
            "object type",
            Message(subject="object type", text="{} object {} is different from {}"),
        ),
    )
    NAME = (
        DiffCategoryItem(
            1,
            "object name",
            Message(subject="object name", text="{} object {} is not in the list {}"),
        ),
    )
    COMMENT = (
        DiffCategoryItem(
            2,
            "object comment",
            Message(subject="object comment", text="{} object {} is different from {}"),
        ),
    )
    QUOTED_IDENTIFIER = (
        DiffCategoryItem(
            3,
            "quoted identifier",
            Message(subject="object comment", text="{} object {} is different from {}"),
        ),
    )
    DATABASE_SCHEMAS = (
        DiffCategoryItem(
            4,
            "database schemas",
            Message(subject="object comment", text="{} object {} is different from {}"),
        ),
    )
    SCHEMA_TABLES = (
        DiffCategoryItem(
            5,
            "schema tables",
            Message(subject="object comment", text="{} object {} is different from {}"),
        ),
    )
    TABLE_COLUMNS = (
        DiffCategoryItem(
            6,
            "table columns",
            Message(subject="object comment", text="{} object {} is different from {}"),
        ),
    )
    PARAMETERS = (
        DiffCategoryItem(
            6,
            "parameters",
            Message(subject="object comment", text="{} object {} is different from {}"),
        ),
    )
    PRIMARY_KEY = (
        DiffCategoryItem(
            7,
            "primary key",
            Message(subject="object comment", text="{} object {} is different from {}"),
        ),
    )
    UNIQUE_KEYS = (
        DiffCategoryItem(
            8,
            "unique keys",
            Message(subject="object comment", text="{} object {} is different from {}"),
        ),
    )
    FOREIGN_KEYS = (
        DiffCategoryItem(
            9,
            "foreign keys",
            Message(subject="object comment", text="{} object {} is different from {}"),
        ),
    )
    COLUMN_DATA_TYPE = (
        DiffCategoryItem(
            10,
            "column data type",
            Message(subject="object comment", text="{} object {} is different from {}"),
        ),
    )
    NUMBER_SCALE = (
        DiffCategoryItem(
            10,
            "number scale",
            Message(subject="object comment", text="{} object {} is different from {}"),
        ),
    )
    NUMBER_PRECISION = (
        DiffCategoryItem(
            11,
            "number precision",
            Message(subject="object comment", text="{} object {} is different from {}"),
        ),
    )
    DATA_LENGTH = (
        DiffCategoryItem(
            12,
            "column length",
            Message(subject="object comment", text="{} object {} is different from {}"),
        ),
    )
    COLUMN_NULLABLE = (
        DiffCategoryItem(
            13,
            "is nullable",
            Message(subject="object comment", text="{} object {} is different from {}"),
        ),
    )
    COLUMN_DEFAULT = (
        DiffCategoryItem(
            14,
            "column default",
            Message(subject="object comment", text="{} object {} is different from {}"),
        ),
    )
    COLUMN_UNIQUE = (
        DiffCategoryItem(
            15,
            "is unique",
            Message(subject="object comment", text="{} object {} is different from {}"),
        ),
    )
    COLUMN_IS_PK = (
        DiffCategoryItem(
            16,
            "is in primary key",
            Message(subject="object comment", text="{} object {} is different from {}"),
        ),
    )
    COLUMN_FOREIGN_KEY = DiffCategoryItem(
        17,
        "column is not in foreign key",
        Message(
            subject="column is not in foreign key",
            text="{} object {} is different from {}",
        ),
    )
