import json

import sqlalchemy as db
from sqlalchemy import select, ForeignKey

from . import CommonBase


class TableConstraint(CommonBase):
    __tablename__ = "table_constraints"
    table_constraint_id = db.Column(db.String, primary_key=True)
    table_constraint_schema_id = db.Column(db.String, ForeignKey("schemas.schema_id"))
    table_id = db.Column(db.String, ForeignKey("tables.table_id"))
    table_constraint_name = db.Column(db.String)
    constraint_type = db.Column(db.String)
    is_deferrable = db.Column(db.String, default="NO")
    initially_deferred = db.Column(db.String, default="NO")
    enforced = db.Column(db.String, default="NO")
    comment = db.Column(db.String)
    created = db.Column(db.String)
    last_altered = db.Column(db.String)
    rely = db.Column(db.String)

    def save(self, session) -> None:
        if not session.execute(self.exists()).first():
            session.add(self)
            session.commit()

    def exists(self) -> str:
        return select(TableConstraint).filter_by(table_constraint_id=self.table_constraint_id)

    def __get_id__(self) -> str:
        id = json.loads(self.table_id)
        id["table_constraint_name"] = self.table_constraint_name
        return json.dumps(id)
