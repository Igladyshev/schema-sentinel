import json
import logging as log
import numpy as np
from datetime import datetime
from typing import Dict

import pandas as pd
import sqlalchemy as db
from sqlalchemy import select, ForeignKey
from schema_sentinel.metadata_manager.enums import DbObjectType
from schema_sentinel.metadata_manager.model.function import Function

from schema_sentinel.metadata_manager.model.procedure import Procedure
from schema_sentinel.metadata_manager.model.task import Task
from schema_sentinel.metadata_manager.model.view import View
from . import CommonBase

class Comparison(CommonBase):
    __tablename__ = "comparisons"
    object_type = db.Column(db.String, primary_key=True)
    comparison_key = db.Column(db.String, primary_key=True)
    source_database_id = db.Column(db.String, ForeignKey("databases.database_id"))
    target_database_id = db.Column(db.String, ForeignKey("databases.database_id"))
    comparison_value = db.Column(db.String)
    comparison_performed_by = db.Column(db.String)
    created = db.Column(db.String)

    def save(self, session) -> None:
        if not session.execute(self.exists()).first():
            session.add(self)
            session.commit()

    def exists(self) -> str:
        return select(Comparison).filter_by(object_type=self.object_type, comparison_key=self.comparison_key)

    @staticmethod
    def is_empty(comparison_value) -> bool:
        return not ("differences" in comparison_value.keys() and comparison_value["differences"] != {}
                    or comparison_value["right"] is None)


    @staticmethod
    def save_comparison(comparison_dict: Dict,
                        src_database_id: str,
                        trg_database_id: str,
                        session,
                        db_timestamp_to_string,
                        user: str):
    
        i = 0
        for db_object_type in comparison_dict.keys():
            for comparison_key in comparison_dict[db_object_type].keys():
                if Comparison.is_empty(comparison_dict[db_object_type][comparison_key]):
                    continue
                comp_val = json.dumps(
                    {"key": comparison_key, "comparison": comparison_dict[db_object_type][comparison_key]})
                comparison = Comparison(
                    object_type=db_object_type,
                    comparison_key=comparison_key,
                    source_database_id=src_database_id,
                    target_database_id=trg_database_id,
                    comparison_value=comp_val,
                    created=db_timestamp_to_string(datetime.now()),
                    comparison_performed_by=user
                )
                comparison.save(session=session)
                log.debug(f"saved comparison={comparison.diffs}")
 
    @property
    def one_diffs(self) -> pd.DataFrame:
        
        if not self.comparison_value:
            return pd.DataFrame(columns=["Attribute", "Left", "Right"])
        diffs = json.loads(self.comparison_value)

        comparison_key = diffs["key"] if "key" in diffs.keys() else self.comparison_key
        object_name = comparison_key.split(" ")[0]
        comparison_database_key = comparison_key.split(" ")[1].replace("[", "").replace("]", "") if ' ' in comparison_key else comparison_key
        data = {}
        if "comparison" in diffs.keys():
            comparison = diffs["comparison"]

            left_object_type = comparison["left"] if "left" in comparison.keys() else self.object_type
            right_object_type = comparison["right"] if "right" in comparison.keys() and comparison["right"] else None
            data = comparison["differences"] if "differences" in comparison.keys() else {}
        
        data_array = []
        if data:
            for attribute in data.keys():
                left = data[attribute][0] if not attribute.endswith("definition") else "code is different"
                right = data[attribute][1] if not attribute.endswith("definition") else ""
                data_array.append([attribute, left, right])
        else:
            data_array.append([''] * 3)

        diff_df = pd.DataFrame(data=data_array, columns=["Attribute", "Left", "Right"])
        diff_df.insert(loc=0, column="DB Key",
                       value=almost_empty_array_of(comparison_database_key, len(data_array)),
                       allow_duplicates=True)
        diff_df.insert(loc=1, column="Left Object",
                       value=almost_empty_array_of(left_object_type, len(data_array)),
                       allow_duplicates=True)
        diff_df.insert(loc=2, column="Right Object",
                       value=almost_empty_array_of(right_object_type if right_object_type else "Not present",
                                                   len(data_array)),
                       allow_duplicates=True)
        diff_df.insert(loc=3, column="Object Name",
                       value=almost_empty_array_of([object_name], len(data_array)),
                       allow_duplicates=True)
        return diff_df

    def both_diffs(self, session) -> pd.DataFrame:
        
        if not self.comparison_value:
            return pd.DataFrame(columns=["Attribute", "Left", "Right"])
        diffs = json.loads(self.comparison_value)

        comparison_key = diffs["key"]
        object_name = self.object_type
        comparison_database_key = comparison_key.split(" ")[1].replace("[", "").replace("]", "")
        comparison_object_name = comparison_key.split(" ")[0]
        
        data = {}
        if "comparison" in diffs.keys():
            comparison = diffs["comparison"]

            left_object_type = comparison["left"]
            right_object_type = comparison["right"]
            data = comparison["differences"]
        
        data_array = []
        if data:
            
            for attribute in data.keys():
                if not attribute.endswith("definition"):
                    left = data[attribute][0]
                    right = data[attribute][1]
                    data_array.append([attribute, left, right])
                else:
                    
                    left_object_id = f"{self.source_database_id}.{comparison_object_name}"
                    right_object_id = f"{self.target_database_id}.{comparison_object_name}"
                    left_code, right_code = ''

                    if left_object_type == DbObjectType.PROCEDURE.value:
                        left_object:Procedure = session.query(Procedure).filter(Procedure.procedure_id == left_object_id).one()
                        left_code = get_code(comparison_object_name, left_object, Procedure)
                        right_object: Procedure = session.query(Procedure).filter(Procedure.procedure_id == left_object_id).one()
                        right_code = get_code(comparison_object_name, right_object, Procedure)
                        
                    elif left_object_type == DbObjectType.FUNCTION.value:
                        left_object: Function = session.query(Function).filter(Function.function_id == left_object_id).one()
                        left_code = get_code(comparison_object_name, left_object, Function)
                        right_object: Function = session.query(Function).filter(Function.function_id == right_object_id).one()
                        right_code = get_code(comparison_object_name, right_object, Function)
                        
                    elif left_object_type == DbObjectType.VIEW.value:
                        left_object: View = session.query(View).filter(View.view_id == left_object_id).one()
                        left_code = get_code(comparison_object_name, left_object, View)
                        right_object: View = session.query(View).filter(View.view_id == right_object_id).one()
                        right_code = get_code(comparison_object_name, right_object, View)
                    elif left_object_type == DbObjectType.TASK.value:
                        left_object: Task = session.query(Task).filter(Task.task_id == left_object_id).one()
                        left_code = get_code(comparison_object_name, left_object, Task)
                        right_object: Task = session.query(Task).filter(Task.task_id == right_object_id).one()
                        right_code = get_code(comparison_object_name, right_object, Task)
                    data_array.append([attribute, left_code, right_code])        
                    
        else:
            data_array.append([''] * 3)

        diff_df = pd.DataFrame(data=data_array, columns=["Attribute", "Left", "Right"])
        diff_df.insert(loc=0, column="DB Key",
                       value=almost_empty_array_of(comparison_database_key, len(data_array)),
                       allow_duplicates=True)
        diff_df.insert(loc=1, column="Left Object",
                       value=almost_empty_array_of(left_object_type, len(data_array)),
                       allow_duplicates=True)
        diff_df.insert(loc=2, column="Right Object",
                       value=almost_empty_array_of(right_object_type if right_object_type else "Not present",
                                                   len(data_array)),
                       allow_duplicates=True)
        diff_df.insert(loc=3, column="Object Name",
                       value=almost_empty_array_of([object_name], len(data_array)),
                       allow_duplicates=True)
        return diff_df

def almost_empty_array_of(value: str, elements_number: int = 1) -> [str]:
     array = [''] * elements_number
     array[0] = value
     return array
 

def get_code(comparison_object_name, db_object, klass) -> str:
    if klass == Procedure:
        argument_signature = {"\t\n".join(db_object.argument_signature.split(","))}
        return f"""CREATE OR REPLACE PROCEDURE {comparison_object_name} ({argument_signature})
    RETURNS {db_object.__data_type__()}
    LANGUAGE {db_object.procedure_language}
    COMMENT {db_object.comment}
AS
{db_object.procedure_definition}
"""
    elif klass == Function:
        argument_signature = {"\t\n".join(db_object.argument_signature.split(","))}
        return f"""CREATE OR REPLACE FUNCTION {comparison_object_name} ({argument_signature})
    RETURNS {db_object.__data_type__()}
    COMMENT {db_object.comment}
AS
{db_object.function_definition}
"""
    elif klass == Task:
        return f"""CREATE OR REPLACE TASK {comparison_object_name}
    ERROR_INTEGRATION {db_object.error_integration}
    WAREHOUSE {db_object.warehouse}
    COMMENT {db_object.comment}
    SCHEDULE='{db_object.schedule}'
AS
    {db_object.definition}
"""
    elif klass == View:
        return f"""CREATE OR REPLACE VIEW {comparison_object_name}
AS
    {db_object.view_definition}
"""     