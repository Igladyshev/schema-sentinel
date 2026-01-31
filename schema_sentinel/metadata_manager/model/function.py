import json

import sqlalchemy as db
from sqlalchemy import ForeignKey, select

from . import CommonBase


class Function(CommonBase):
    __tablename__ = "functions"
    function_id = db.Column(db.String, primary_key=True)
    argument_signature = db.Column(db.String, primary_key=True)
    schema_id = db.Column(db.String, ForeignKey("schemas.schema_id"))
    function_name = db.Column(db.String)
    function_owner = db.Column(db.String)
    data_type = db.Column(db.String)
    character_maximum_length = db.Column(db.Integer)
    character_octet_length = db.Column(db.Integer)
    numeric_precision = db.Column(db.Integer)
    numeric_precision_radix = db.Column(db.Integer)
    numeric_scale = db.Column(db.Integer)
    datetime_scale = db.Column(db.Integer)
    function_language = db.Column(db.String)
    function_definition = db.Column(db.String)
    volatility = db.Column(db.String)
    is_null_call = db.Column(db.String)
    is_secure = db.Column(db.String)
    comment = db.Column(db.String)
    created = db.Column(db.String)
    last_altered = db.Column(db.String)
    is_external = db.Column(db.String)
    api_integration = db.Column(db.String)
    context_headers = db.Column(db.String)
    max_batch_rows = db.Column(db.Integer)
    compression = db.Column(db.String)
    packages = db.Column(db.String)
    runtime_version = db.Column(db.String)
    installed_packages = db.Column(db.String)
    is_memoizable = db.Column(db.String)

    def save(self, session) -> None:
        if not session.execute(self.exists()).first():
            session.add(self)
            session.commit()

    def exists(self) -> str:
        return select(Function).filter_by(function_id=self.function_id)

    def __get_id__(self) -> str:
        id = json.loads(self.schema_id)
        id["function_name"] = self.function_name
        id["argument_signature"] = self.argument_signature
        return json.dumps(id)

    def __data_type__(self) -> str:
        if self.data_type in ["VARCHAR", "TEXT"]:
            data_type = f"{self.data_type}({self.character_maximum_length})"
        elif self.data_type == "NUMBER":
            data_type = f"{self.data_type}({self.numeric_precision}, {self.numeric_scale})"
        elif self.data_type in ["TIMESTAMP_NTZ", "TIMESTAMP_LTZ", "TIMESTAMP_TZ"]:
            data_type = f"{self.data_type}({self.datetime_presision})"
        else:
            data_type = self.data_type
        return data_type
