from __future__ import annotations

import logging as log
import os
from abc import abstractmethod

import pandas as pd
from sqlalchemy.ext.declarative import declarative_base

ATTRIBUTES_TO_EXCLUDE = [
    "database_id",
    "table_id",
    "environment",
    "version",
    "created",
    "last_altered",
    "schema_id",
    "id",
    "column_id",
    "last_suspended",
    "table_constraint_id",
    "column_constraint_id",
    "referential_constraint_id",
    "view_id",
    "pipe_id",
    "task_id",
    "stream_id",
    "function_id",
    "procedure_id",
    "last_ddl",
    "stale_after",
    "bytes",
    "row_count",
]
PROJECT_NAME = "schema-sentinel"
TEMP_DIR = os.getenv("TEMP") if os.name == "nt" else "/tmp"
LOG_FILE = os.path.join(TEMP_DIR, "schema-sentinel.log")
LOG_LEVEL = os.getenv("LOG_LEVEL") if os.getenv("LOG_LEVEL") is not None else "INFO"

PROJECT_HOME = os.path.dirname(os.path.join(os.path.abspath("./"), PROJECT_NAME))
RESOURCES_PATH = os.path.join(PROJECT_HOME, "resources")
META_DB_PATH = os.path.join(RESOURCES_PATH, "meta-db")

log.basicConfig(
    level=LOG_LEVEL,
    format="%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s",
    handlers=[log.FileHandler(LOG_FILE), log.StreamHandler()],
)


def compare_obj(left, right) -> {}:
    comparison = {"left": left.__class__.__name__, "right": right.__class__.__name__, "differences": {}}
    for attribute, left_val in left.__dict__.items():
        if attribute in ATTRIBUTES_TO_EXCLUDE or attribute.startswith("_") or attribute.endswith("_id"):
            continue

        try:
            right_val = getattr(right, attribute)
        except Exception:
            right_val = None

        if left_val != right_val:
            if attribute.endswith("_definition"):
                left_val = left_val[0:100] if len(left_val) >= 100 else left_val
                right_val = right_val[0:100] if len(right_val) >= 100 else right_val
            else:
                left_val_no_env = drop_environment(str(left_val).upper())
                right_val_no_env = drop_environment(str(right_val).upper())
                if left_val_no_env == right_val_no_env:
                    continue
            log.debug(f"Values are not equal: left {left_val}, right {right_val}")
            comparison["differences"][attribute] = [left_val, right_val]

    return comparison


def drop_environment(s: str) -> str:
    if s is None:
        return ""

    for x in ["US_NONPROD_", "US_NON_PROD_", "US_DEV_", "US_CERT_", "US_PROD_"]:
        if x in s:
            return s.replace(x, "")


Base = declarative_base()


class CommonBase(Base):
    __abstract__ = True

    @abstractmethod
    def __get_id__(self):
        pass

    def __get_header__(self) -> list:
        header = []
        for attribute, _value in self.__dict__.items():
            if attribute.startswith("_"):
                continue
            header.append(attribute)
        return header

    def __get_values__(self) -> list:
        row: list = []
        for attribute, value in self.__dict__.items():
            if attribute.startswith("_"):
                continue
            row.append(value)
        return row

    def __get_df__(self, columns=None) -> pd.DataFrame:
        if columns is None:
            columns = ["Attribute", "Value"]
        data = []

        for attribute, value in self.__dict__.items():
            if attribute.startswith("_"):
                continue
            data.append([attribute, value])

        df = pd.DataFrame(data=data, columns=columns)
        return df

    def __get_row__(self) -> pd.DataFrame:
        return pd.DataFrame(data=[self.__get_values__()], columns=self.__get_header__())

    def __side_by_side__(self, other):
        if self.__class__.__name__ != other.__class__.__name__:
            raise Exception(f"{other.__class__.__name__} is not {self.__class__.__name__}")
        left = self.__get_df__(["Attribute", "Left"])
        right = other.__get_df__(["Attribute", "Right"])
        return pd.merge(left, right, on="Attribute")

    def __repr__(self) -> str:
        representation = f"{self.__class__}("
        for attribute, value in self.__dict__.items():
            if attribute in ATTRIBUTES_TO_EXCLUDE or attribute.startswith("_"):
                continue
            representation += f"{attribute}:[{value if value else ''}], "
        representation += ")"
        return representation

    @staticmethod
    def __to_df__(data: list, columns: list) -> pd.DataFrame:
        df = None
        for item in data:
            row: pd.DataFrame = item.__get_row__()
            if df is None:
                df = row
            else:
                df = pd.concat([df, row])

        if df is None:
            return pd.DataFrame(columns=columns)

        df = df.reset_index()

        if columns:
            return df[columns]

        return df
