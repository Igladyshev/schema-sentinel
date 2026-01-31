import json
import sqlalchemy as db
from sqlalchemy import select, ForeignKey
from . import CommonBase


class Column(CommonBase):
    __tablename__ = "columns"
    column_id = db.Column(db.String, primary_key=True)
    table_id = db.Column(db.String, ForeignKey("tables.table_id"))
    column_name = db.Column(db.String)
    ordinal_position = db.Column(db.Integer)
    column_default = db.Column(db.String)
    is_nullable = db.Column(db.String, default="YES")
    data_type = db.Column(db.String)
    character_maximum_length = db.Column(db.Integer)
    character_octet_length = db.Column(db.Integer)
    numeric_precision = db.Column(db.Integer)
    numeric_precision_radix = db.Column(db.Integer)
    numeric_scale = db.Column(db.Integer)
    datetime_precision = db.Column(db.Integer)
    is_identity = db.Column(db.String, default="NO")
    identity_generation = db.Column(db.String)
    identity_start = db.Column(db.String)
    identity_increment = db.Column(db.String)
    comment = db.Column(db.String)

    def save(self, session) -> None:
        if not session.execute(self.exists()).first():
            session.add(self)
            session.commit()

    def exists(self) -> str:
        return select(Column).filter_by(
            column_id=self.column_id
        )

    def __get_id__(self) -> str:
        id = json.loads(self.table_id)
        id["column_name"] = self.column_name
        return json.dumps(id)
    
    def __data_type__(self) -> str:
        if self.data_type in ['VARCHAR', 'TEXT']:
            data_type = f"{self.data_type}({self.character_maximum_length})"
        elif self.data_type == "NUMBER":
            data_type = f"{self.data_type}({self.numeric_precision}, {self.numeric_scale})"
        elif self.data_type in ["TIMESTAMP_NTZ", "TIMESTAMP_LTZ", "TIMESTAMP_TZ"]:
            data_type = f"{self.data_type}({self.datetime_presision})"
        else:
            data_type = self.data_type
        return data_type
