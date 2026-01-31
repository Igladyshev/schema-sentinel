import json

import sqlalchemy as db
from sqlalchemy import ForeignKey, select

from . import CommonBase


class Constraint(CommonBase):
    __tablename__ = "constraints"
    constraint_id = db.Column(db.String, primary_key=True)
    table_id = db.Column(db.String, ForeignKey("tables.table_id"))
    constraint_name = db.Column(db.String)
    constraint_type = db.Column(db.String)
    constraint_details = db.Column(db.String)
    reference_key = db.Column(db.String, ForeignKey("constraints.constraint_id"))
    comment = db.Column(db.String)
    update_rule = db.Column(db.String, default="NO ACTION")
    delete_rule = db.Column(db.String, default="NO ACTION")
    created = db.Column(db.String)

    def save(self, session) -> None:
        if not session.execute(self.exists()).first():
            session.add(self)
            session.commit()

    def exists(self) -> str:
        return select(Constraint).filter_by(constraint_id=self.constraint_id)

    def __get_id__(self) -> str:
        id = json.loads(self.table_id)
        id["constraint_name"] = self.constraint_name
        return json.dumps(id)
