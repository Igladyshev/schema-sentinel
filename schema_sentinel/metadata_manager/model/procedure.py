import json

import sqlalchemy as db
from sqlalchemy import ForeignKey, select

from . import CommonBase


class Procedure(CommonBase):
    __tablename__ = "procedures"
    procedure_id = db.Column(db.String, primary_key=True)
    argument_signature = db.Column(db.String)
    schema_id = db.Column(db.String, ForeignKey("schemas.schema_id"))
    procedure_name = db.Column(db.String)
    procedure_owner = db.Column(db.String)
    data_type = db.Column(db.String)
    character_maximum_length = db.Column(db.Integer)
    character_octet_length = db.Column(db.Integer)
    numeric_precision = db.Column(db.Integer)
    numeric_precision_radix = db.Column(db.Integer)
    numeric_scale = db.Column(db.Integer)
    datetime_presision = db.Column(db.Integer)
    procedure_language = db.Column(db.String)
    procedure_definition = db.Column(db.String)
    comment = db.Column(db.String)
    created = db.Column(db.String)
    last_altered = db.Column(db.String)

    def save(self, session) -> None:
        if not session.execute(self.exists()).first():
            session.add(self)
            session.commit()

    def exists(self) -> str:
        return select(Procedure).filter_by(procedure_id=self.procedure_id)

    def __get_id__(self) -> str:
        id = json.loads(self.schema_id)
        id["procedure_name"] = self.procedure_name
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
