import json

import sqlalchemy as db
from sqlalchemy import ForeignKey, select

from . import CommonBase


class Schema(CommonBase):
    __tablename__ = "schemas"
    database_id = db.Column(db.String, ForeignKey("databases.database_id"), primary_key=True)
    schema_id = db.Column(db.String, primary_key=True)
    schema_name = db.Column(db.String, primary_key=True)

    schema_owner = db.Column(db.String)
    is_transient = db.Column(db.String, default="NO")
    comment = db.Column(db.String)
    created = db.Column(db.String)
    last_altered = db.Column(db.String)
    retention_time = db.Column(db.Integer)

    def save(self, session) -> None:
        if not session.execute(self.exists()).first():
            session.add(self)
            session.commit()

    def exists(self) -> str:
        return select(Schema).filter_by(schema_id=self.__get_id__())

    def __get_id__(self) -> str:
        id = json.loads(self.database_id)
        id["schema_name"] = self.schema_name
        return json.dumps(id)
