import json

import sqlalchemy as db
from sqlalchemy import select, ForeignKey

from . import CommonBase


class ReferentialConstraint(CommonBase):
    __tablename__ = "referential_constraints"
    referential_constraint_id = db.Column(db.String, primary_key=True)
    foreign_key_constraint_id = db.Column(db.String, ForeignKey("constraints.constraint_id"))
    unique_constraint_id = db.Column(db.String, ForeignKey("constraints.constraint_id"))
    fk_name = db.Column(db.String)
    pk_name = db.Column(db.String)

    match_option = db.Column(db.String)
    update_rule = db.Column(db.String)
    delete_rule = db.Column(db.String)
    comment = db.Column(db.String)
    created = db.Column(db.String)
    last_altered = db.Column(db.String)

    def save(self, session) -> None:
        if not session.execute(self.exists()).first():
            session.add(self)
            session.commit()

    def exists(self) -> str:
        return select(ReferentialConstraint).filter_by(
            foreign_key_constraint_id=self.foreign_key_constraint_id,
            unique_constraint_id=self.unique_constraint_id,
        )

    def __get_id__(self) -> str:
        return json.dumps(
            {
                "foreign_key_constraint_id": json.loads(self.foreign_key_constraint_id),
                "unique_constraint_id": json.loads(self.unique_constraint_id),
            }
        )
