from __future__ import annotations

import logging as log
import warnings
from abc import abstractmethod

import pandas as pd
from sqlalchemy.exc import MovedIn20Warning

warnings.filterwarnings("ignore", category=MovedIn20Warning)  # Suppress SQLAlchemy 2.0 warning
from sqlalchemy.ext.declarative import declarative_base  # noqa: E402

from schema_sentinel.config import get_config  # noqa: E402

# Get configuration manager instance
_config = get_config()

# Use config manager for attributes to exclude
ATTRIBUTES_TO_EXCLUDE = _config.metadata.attributes_to_exclude

# Backward compatibility - deprecated path variables
PROJECT_HOME = str(_config.paths.project_home)
RESOURCES_PATH = str(_config.paths.resources_dir)
META_DB_PATH = str(_config.paths.meta_db_dir)

Base = declarative_base()


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
